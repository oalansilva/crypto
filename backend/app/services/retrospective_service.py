"""Retrospective service — generates auto-retrospective reports after feature homologation.

This service is the feedback loop for the orchestrator (Alan) to read and improve workflow.
"""

from __future__ import annotations

import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.workflow_database import get_workflow_db
from app.workflow_models import (
    Change,
    WorkItem,
    WorkItemState,
    WorkItemType,
    WorkflowApproval,
    WorkflowHandoff,
)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parents[3]
RETRO_DIR = REPO_ROOT / "docs" / "retrospectives"
RETRO_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Data collection
# ---------------------------------------------------------------------------


def _as_utc(dt: Optional[datetime]) -> Optional[datetime]:
    """Normalize DB datetimes so SQLite and Postgres behave the same in arithmetic."""
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def collect_retrospective_data(db: Session, change: Change) -> Dict[str, Any]:
    """Collect all metrics needed for a retrospective from the workflow DB.

    Returns a structured dict with stage times, cycles, blockers, and bugs.
    """
    work_items = (
        db.query(WorkItem)
        .filter(WorkItem.change_pk == change.id)
        .order_by(WorkItem.created_at.asc())
        .all()
    )

    # Stage time tracking via handoffs
    handoffs = (
        db.query(WorkflowHandoff)
        .filter(
            WorkflowHandoff.change_pk == change.id,
            WorkflowHandoff.scope == "change",
        )
        .order_by(WorkflowHandoff.created_at.asc())
        .all()
    )

    # Approval cycles
    approvals = (
        db.query(WorkflowApproval)
        .filter(
            WorkflowApproval.change_pk == change.id,
            WorkflowApproval.scope == "change",
        )
        .order_by(WorkflowApproval.created_at.asc())
        .all()
    )

    # Blockers: work items in blocked state
    blockers = [wi for wi in work_items if wi.state == WorkItemState.blocked]

    # Open bugs at this point
    open_bugs = [
        wi
        for wi in work_items
        if wi.type == WorkItemType.bug
        and wi.state not in [WorkItemState.done, WorkItemState.canceled]
    ]

    # Stage times derived from handoffs
    stage_times: Dict[str, Dict[str, Any]] = {}
    stage_order = ["PO", "DESIGN", "DEV", "QA"]
    for stage in stage_order:
        stage_handoffs = [h for h in handoffs if h.to_role == stage]
        if stage_handoffs:
            first = _as_utc(stage_handoffs[0].created_at)
            # End is either the next stage start or now
            next_stage_idx = stage_order.index(stage) + 1
            next_start = None
            for next_stage in stage_order[next_stage_idx:]:
                next_handoffs = [h for h in handoffs if h.to_role == next_stage]
                if next_handoffs:
                    next_start = _as_utc(next_handoffs[0].created_at)
                    break
            end = next_start or datetime.now(timezone.utc)
            duration = end - first
            stage_times[stage] = {
                "start": first,
                "end": end,
                "duration_seconds": duration.total_seconds(),
                "cycles": len(stage_handoffs),
            }
        else:
            stage_times[stage] = {
                "start": None,
                "end": None,
                "duration_seconds": 0,
                "cycles": 0,
            }

    # Total time from first activity to now (or last completed stage)
    started_at = _as_utc(change.created_at)
    homologated_at = _as_utc(change.updated_at)
    total_seconds = (homologated_at - started_at).total_seconds()

    # Count blocker events (work items that entered blocked state)
    blocker_events = [
        {
            "work_item_id": wi.id,
            "title": wi.title,
            "started_at": wi.created_at.isoformat() if wi.created_at else None,
            "resolved_at": (
                (wi.stage_completed_at or wi.updated_at).isoformat()
                if wi.state != WorkItemState.blocked
                else None
            ),
        }
        for wi in blockers
    ]

    # Review cycles per gate from approvals
    gate_cycles: Dict[str, int] = {}
    for a in approvals:
        gate_cycles[a.gate] = gate_cycles.get(a.gate, 0) + 1

    return {
        "change_id": change.change_id,
        "title": change.title,
        "card_number": change.card_number,
        "status": change.status,
        "started_at": started_at.isoformat(),
        "homologated_at": homologated_at.isoformat(),
        "total_seconds": total_seconds,
        "stage_times": stage_times,
        "gate_cycles": gate_cycles,
        "blocker_events": blocker_events,
        "open_bugs": [{"id": wi.id, "title": wi.title} for wi in open_bugs],
        "total_blocker_seconds": sum(
            (
                datetime.now(timezone.utc)
                - (
                    _as_utc(wi.created_at)
                    if wi.state == WorkItemState.blocked
                    else _as_utc(wi.stage_completed_at) or _as_utc(wi.created_at)
                )
            ).total_seconds()
            for wi in blockers
        ),
    }


# ---------------------------------------------------------------------------
# Classification
# ---------------------------------------------------------------------------

THRESHOLDS = {
    "review_cycles_warning": 3,
    "blocker_hours_warning": 48,
    "open_bugs_warning": 2,
}


def classify_retrospective(data: Dict[str, Any]) -> str:
    """Classify a retrospective: sem_problemas | com_ressalvas | problemática."""
    total_cycles = sum(data.get("gate_cycles", {}).values())
    blocker_hours = data.get("total_blocker_seconds", 0) / 3600
    open_bugs = len(data.get("open_bugs", []))

    if total_cycles > THRESHOLDS["review_cycles_warning"]:
        return "com_ressalvas"
    if blocker_hours > THRESHOLDS["blocker_hours_warning"]:
        return "problemática"
    if open_bugs > THRESHOLDS["open_bugs_warning"]:
        return "problemática"

    # Check if any stage had excessive cycles
    for stage, info in data.get("stage_times", {}).items():
        if info.get("cycles", 0) > THRESHOLDS["review_cycles_warning"]:
            return "com_ressalvas"

    return "sem_problemas"


def classification_badge(cls: str) -> str:
    badges = {
        "sem_problemas": "🟢 Sem Problemas",
        "com_ressalvas": "🟡 Com Ressalvas",
        "problemática": "🔴 Problemática",
    }
    return badges.get(cls, cls)


# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------


def format_duration(seconds: float) -> str:
    """Format seconds into 'Xd Xh' or 'Xh Xm' string."""
    if seconds < 60:
        return f"{seconds:.0f}s"
    total_minutes = int(seconds / 60)
    hours = total_minutes // 60
    minutes = total_minutes % 60
    if hours >= 24:
        days = hours // 24
        hours = hours % 24
        return f"{days}d {hours}h"
    if minutes > 0:
        return f"{hours}h {minutes}m"
    return f"{hours}h"


def _render_stage_table(data: Dict[str, Any]) -> str:
    """Render the stage metrics table in Markdown."""
    lines = [
        "| Stage | Tempo | Ciclos | Observação |",
        "|-------|-------|--------|------------|",
    ]
    stage_notes = {
        "PO": "Planejamento e artefatos",
        "DESIGN": "Design e prototipagem",
        "DEV": "Implementação",
        "QA": "Validação e testes",
    }
    for stage in ["PO", "DESIGN", "DEV", "QA"]:
        info = data["stage_times"].get(stage, {})
        duration_str = format_duration(info.get("duration_seconds", 0))
        cycles = info.get("cycles", 0)
        note = stage_notes.get(stage, "")
        lines.append(f"| {stage} | {duration_str} | {cycles} | {note} |")
    return "\n".join(lines)


def _render_risk_table(data: Dict[str, Any], classification: str) -> str:
    """Render the risk classification table."""
    total_cycles = sum(data.get("gate_cycles", {}).values())
    blocker_hours = data.get("total_blocker_seconds", 0) / 3600
    open_bugs = len(data.get("open_bugs", []))

    cycles_status = "🔴" if total_cycles > 3 else "🟡" if total_cycles > 2 else "🟢"
    blocker_status = "🔴" if blocker_hours > 48 else "🟡" if blocker_hours > 24 else "🟢"
    bugs_status = "🔴" if open_bugs > 2 else "🟡" if open_bugs > 1 else "🟢"

    cycles_impl = "Excesso de revisões atrasa o fluxo" if total_cycles > 3 else "Dentro do limite"
    blocker_impl = (
        "Blocker crítico"
        if blocker_hours > 48
        else "Blocker aceitável" if blocker_hours > 0 else "Sem blockers"
    )
    bugs_impl = "Bugs em aberto comprometem qualidade" if open_bugs > 2 else "Bugs controlados"

    badge = classification_badge(classification)

    lines = [
        "| Indicador | Valor | Limite | Status | Implicação para o Fluxo |",
        "|-----------|-------|--------|--------|--------------------------|",
        f"| Ciclos de Revisão | {total_cycles} | 3 | {cycles_status} | {cycles_impl} |",
        f"| Blocker Total | {blocker_hours:.1f}h | 48h | {blocker_status} | {blocker_impl} |",
        f"| Bugs Abertos | {open_bugs} | 2 | {bugs_status} | {bugs_impl} |",
        "",
        f"**Resultado:** {badge}",
    ]
    return "\n".join(lines)


def _render_blocker_events(data: Dict[str, Any]) -> str:
    """Render blocker events table."""
    events = data.get("blocker_events", [])
    if not events:
        return "| Nenhum blocker registrado |"

    lines = [
        "| Início | Motivo | Status |",
        "|--------|--------|--------|",
    ]
    for e in events:
        lines.append(
            f"| {e.get('started_at', 'N/A')} | {e.get('title', 'N/A')} | {'Bloqueado' if not e.get('resolved_at') else 'Resolvido'} |"
        )
    return "\n".join(lines)


def _generate_heuristic_insights(
    data: Dict[str, Any], prev_data: Optional[Dict[str, Any]] = None
) -> Dict[str, str]:
    """Generate insights heuristically (without LLM) based on the data.

    Returns dict with: process_analysis, improvement_from_previous,
    regression_from_previous, actionable_recommendation_for_orchestrator
    """
    insights = {
        "process_analysis": "",
        "improvement_from_previous": "",
        "regression_from_previous": "",
        "actionable_recommendation_for_orchestrator": "",
    }

    # Process analysis
    stage_analysis = []
    for stage in ["PO", "DESIGN", "DEV", "QA"]:
        info = data["stage_times"].get(stage, {})
        cycles = info.get("cycles", 0)
        duration_str = format_duration(info.get("duration_seconds", 0))
        if cycles > 1:
            stage_analysis.append(
                f"- **{stage}**: {cycles} ciclos de revisão, tempo total {duration_str}."
            )
        elif cycles == 1 and info.get("duration_seconds", 0) > 0:
            stage_analysis.append(f"- **{stage}**: 1 ciclo, {duration_str}.")

    if stage_analysis:
        insights["process_analysis"] = "Ciclos de revisão por stage:\n" + "\n".join(stage_analysis)
    else:
        insights["process_analysis"] = "Fluxo sem ciclos extras de revisão detectados."

    total_cycles = sum(data.get("gate_cycles", {}).values())
    if total_cycles > 3:
        insights[
            "process_analysis"
        ] += f"\n\n⚠️ Total de {total_cycles} ciclos de revisão — acima do limiar de 3."

    # Blockers
    blocker_count = len(data.get("blocker_events", []))
    if blocker_count > 0:
        insights[
            "process_analysis"
        ] += f"\n\n⚠️ {blocker_count} evento(s) de blocker registrado(s)."

    # Comparison with previous
    if prev_data:
        prev_total = prev_data.get("total_seconds", 0)
        curr_total = data.get("total_seconds", 0)
        if prev_total > 0:
            diff_pct = ((curr_total - prev_total) / prev_total) * 100
            if diff_pct < -10:
                insights["improvement_from_previous"] = (
                    f"Tempo total **reduziu {abs(diff_pct):.0f}%** em relação à feature anterior."
                )
            elif diff_pct > 10:
                insights["regression_from_previous"] = (
                    f"Tempo total **aumentou {diff_pct:.0f}%** em relação à feature anterior."
                )

    # Actionable recommendation
    recommendations = []
    for stage in ["PO", "DESIGN", "DEV", "QA"]:
        info = data["stage_times"].get(stage, {})
        cycles = info.get("cycles", 0)
        if cycles > 2:
            recommendations.append(
                f"- **{stage}**: {cycles} ciclos — revisar processo de review在这一 stage."
            )

    total_cycles = sum(data.get("gate_cycles", {}).values())
    if total_cycles > 3:
        recommendations.append(
            "- **Revisões em geral**: Muitas revisões podem indicar falta de alinhamento prévio. Considere adicionar gate de alinhamento antes de submeter para review."
        )

    open_bugs = len(data.get("open_bugs", []))
    if open_bugs > 0:
        recommendations.append(
            f"- **Bugs abertos**: {open_bugs} bug(s) aberto(s) na homologação. Idealmente bugs devem ser resolvidos antes de arquivar."
        )

    if recommendations:
        insights["actionable_recommendation_for_orchestrator"] = (
            "Ações recomendadas para o orchestrator:\n" + "\n".join(recommendations)
        )
    else:
        insights["actionable_recommendation_for_orchestrator"] = (
            "Fluxo dentro dos parâmetros esperados. Continuar monitoramento regular."
        )

    return insights


# ---------------------------------------------------------------------------
# Markdown generation
# ---------------------------------------------------------------------------


def build_retrospective_markdown(
    data: Dict[str, Any],
    insights: Dict[str, str],
    classification: str,
) -> str:
    """Build the full retrospective Markdown document from collected data."""
    badge = classification_badge(classification)
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    slug = data["change_id"]
    total_str = format_duration(data["total_seconds"])

    # Build feature history (list existing retrospectives)
    history_lines = _build_history_lines()

    md = f"""# 📋 Retrospective — {data['title']}

**Card:** #{data.get('card_number', '?')} | **Data:** {date_str} | **Classificação:** [{badge}]

---

## Resumo da Feature

| Campo | Valor |
|-------|-------|
| Nome | {data['title']} |
| Change ID | {data['change_id']} |
| Status | ✅ Homologada |
| Tempo Total | {total_str} |
| Homologada em | {data['homologated_at'][:10]} |

---

## Métricas de Processo

{_render_stage_table(data)}

**Tempo Total:** {total_str}

---

## 🔍 Análise de Processo (Para o Orchestrador)

### Onde o fluxo travou?
{insights.get('process_analysis', 'Sem travamentos significativos detectados.')}

### O que melhorou em relação à feature anterior?
{insights.get('improvement_from_previous', 'Sem dados anteriores para comparação.')}

### O que piorou em relação à feature anterior?
{insights.get('regression_from_previous', 'Sem dados anteriores para comparação.')}

---

## 🎯 Recomendação para o Orchestrador

{insights.get('actionable_recommendation_for_orchestrator', 'Continuar monitoramento regular.')}

---

## Classificação de Risco

{_render_risk_table(data, classification)}

---

## Blocker Events

{_render_blocker_events(data)}

---

## Histórico de Retrospectivas

{history_lines}

---

_Gerado automaticamente por auto-retrospective em {datetime.now(timezone.utc).isoformat()}_
"""
    return md


def _build_history_lines() -> str:
    """Build the historical retrospective table lines."""
    retros = sorted(
        RETRO_DIR.glob("*.md"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )[:10]

    if not retros:
        return "| Nenhuma retrospectiva anterior |"

    lines = [
        "| Data | Feature | Classificação |",
        "|------|---------|---------------|",
    ]
    for rp in retros:
        # Extract date from filename: YYYY-MM-DD-slug.md
        date_part = rp.stem[:10]
        slug_part = rp.stem[11:] if len(rp.stem) > 10 else rp.stem
        # Try to read badge from file
        badge = "🟢"
        try:
            content = rp.read_text(encoding="utf-8")
            if "🟡" in content:
                badge = "🟡"
            elif "🔴" in content:
                badge = "🔴"
        except Exception:
            pass
        lines.append(f"| {date_part} | {slug_part} | {badge} |")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# LLM-enhanced insights (optional, falls back to heuristic)
# ---------------------------------------------------------------------------


def generate_llm_insights(
    data: Dict[str, Any],
    prev_data: Optional[Dict[str, Any]] = None,
) -> Dict[str, str]:
    """Generate insights using acpx codex LLM (falls back to heuristic on failure)."""
    prompt = _build_llm_prompt(data, prev_data)

    try:
        result = subprocess.run(
            ["acpx", "codex", "exec", "--format=json", prompt],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=str(REPO_ROOT),
        )
        if result.returncode == 0 and result.stdout.strip():
            # Try to parse JSON from output
            output = result.stdout.strip()
            # Find JSON block if present
            json_match = re.search(r"\{.*\}", output, re.DOTALL)
            if json_match:
                parsed = json.loads(json_match.group())
                return {
                    "process_analysis": parsed.get("process_analysis", ""),
                    "improvement_from_previous": parsed.get("improvement_from_previous", ""),
                    "regression_from_previous": parsed.get("regression_from_previous", ""),
                    "actionable_recommendation_for_orchestrator": parsed.get(
                        "actionable_recommendation_for_orchestrator", ""
                    ),
                }
    except Exception:
        pass

    # Fallback to heuristic
    return _generate_heuristic_insights(data, prev_data)


def _build_llm_prompt(data: Dict[str, Any], prev_data: Optional[Dict[str, Any]]) -> str:
    """Build the LLM prompt for insight generation."""
    stage_times = data.get("stage_times", {})
    prev_block = ""
    if prev_data:
        prev_stage_times = prev_data.get("stage_times", {})
        prev_block = f"""
Retrospectiva Anterior:
- Tempo total: {format_duration(prev_data.get('total_seconds', 0))}
- Classification: {prev_data.get('classification', 'N/A')}
- Stage times: {{
  PO: {format_duration(prev_stage_times.get('PO', {}).get('duration_seconds', 0))} ({prev_stage_times.get('PO', {}).get('cycles', 0)} ciclos)
  DESIGN: {format_duration(prev_stage_times.get('DESIGN', {}).get('duration_seconds', 0))} ({prev_stage_times.get('DESIGN', {}).get('cycles', 0)} ciclos)
  DEV: {format_duration(prev_stage_times.get('DEV', {}).get('duration_seconds', 0))} ({prev_stage_times.get('DEV', {}).get('cycles', 0)} ciclos)
  QA: {format_duration(prev_stage_times.get('QA', {}).get('duration_seconds', 0))} ({prev_stage_times.get('QA', {}).get('cycles', 0)} ciclos)
}}
- Gate cycles: {prev_data.get('gate_cycles', {})}
- Open bugs: {len(prev_data.get('open_bugs', []))}
"""

    prompt = f"""Você é um Scrum Master que analiza retrospectivas de features.
O público-alvo é o ORQUESTRADOR (Alan), não o time de desenvolvimento.

Sua tarefa: gerar a seção "Análise de Processo" e "Recomendação para o Orchestrador" de uma retrospectiva.

Regras:
1. Foque em COMO o processo funcionou, não em O QUE foi construído
2. Identifique padrões que o orchestrador pode corrigir (ex: "PO review sem deadline", "QA descobrindo bugs tarde", "Design com múltiplos ciclos")
3. Compare com a retrospectiva anterior quando existir
4. Seja específico: "Design precisou de 4 ciclos" é melhor que "Design teve problemas"
5. A recomendação DEVE ser acionável pelo orchestrador (mudar processo, adicionar gate, ajustar expectativa)
6. Responda APENAS com JSON válido com os campos: process_analysis, improvement_from_previous, regression_from_previous, actionable_recommendation_for_orchestrator

Input - Dados da Feature Atual:
- Change ID: {data['change_id']}
- Título: {data['title']}
- Tempo total: {format_duration(data.get('total_seconds', 0))}
- Stage times: {{
  PO: {format_duration(stage_times.get('PO', {}).get('duration_seconds', 0))} ({stage_times.get('PO', {}).get('cycles', 0)} ciclos)
  DESIGN: {format_duration(stage_times.get('DESIGN', {}).get('duration_seconds', 0))} ({stage_times.get('DESIGN', {}).get('cycles', 0)} ciclos)
  DEV: {format_duration(stage_times.get('DEV', {}).get('duration_seconds', 0))} ({stage_times.get('DEV', {}).get('cycles', 0)} ciclos)
  QA: {format_duration(stage_times.get('QA', {}).get('duration_seconds', 0))} ({stage_times.get('QA', {}).get('cycles', 0)} ciclos)
}}
- Gate cycles: {data.get('gate_cycles', {})}
- Total ciclos de revisão: {sum(data.get('gate_cycles', {}).values())}
- Blocker events: {len(data.get('blocker_events', []))}
- Open bugs: {len(data.get('open_bugs', []))}
{prev_block}

Output: JSON apenas, sem markdown wrapper.
"""
    return prompt


# ---------------------------------------------------------------------------
# Persistence
# ---------------------------------------------------------------------------


def persist_retrospective(markdown: str, change_id: str) -> Path:
    """Write the retrospective markdown file to disk.

    Returns the Path of the created file.
    """
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    filename = f"{date_str}-{change_id}.md"
    filepath = RETRO_DIR / filename
    filepath.write_text(markdown, encoding="utf-8")
    return filepath


def retrospective_file_path(change_id: str) -> Optional[Path]:
    """Find the retrospective file for a given change_id (most recent match)."""
    matches = sorted(
        RETRO_DIR.glob(f"*-{change_id}.md"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    return matches[0] if matches else None


def list_retrospectives(
    page: int = 1,
    per_page: int = 10,
) -> Dict[str, Any]:
    """List all retrospectives with pagination."""
    all_files = sorted(
        RETRO_DIR.glob("*.md"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )

    total = len(all_files)
    start = (page - 1) * per_page
    end = start + per_page
    page_files = all_files[start:end]

    retrospectives = []
    for fp in page_files:
        # Extract info from filename: YYYY-MM-DD-slug.md
        parts = fp.stem.split("-", 3)
        date_str = parts[0] if parts else ""
        slug = "-".join(parts[3:]) if len(parts) > 3 else fp.stem

        # Try to read classification
        classification = "sem_problemas"
        card_number = None
        try:
            content = fp.read_text(encoding="utf-8")
            if "🟡" in content:
                classification = "com_ressalvas"
            elif "🔴" in content:
                classification = "problemática"
            # Extract card number
            card_match = re.search(r"Card: #(\d+)", content)
            if card_match:
                card_number = int(card_match.group(1))
        except Exception:
            pass

        retrospectives.append(
            {
                "slug": slug,
                "card_id": card_number,
                "feature_name": slug.replace("-", " ").replace("_", " ").title(),
                "date": date_str,
                "classification": classification,
                "filename": fp.name,
            }
        )

    return {
        "retrospectives": retrospectives,
        "total": total,
        "page": page,
        "per_page": per_page,
    }


# ---------------------------------------------------------------------------
# Trigger
# ---------------------------------------------------------------------------


def generate_retrospective_for_change(
    project_slug: str,
    change_id: str,
) -> Optional[Path]:
    """Main entry point: collect data, classify, generate, and persist.

    Returns the path to the created file, or None on failure.
    """
    db_gen = get_workflow_db()
    db = next(db_gen)
    try:
        from app.workflow_models import Project

        project = db.query(Project).filter(Project.slug == project_slug).first()
        if not project:
            return None

        change = (
            db.query(Change)
            .filter(Change.project_id == project.id, Change.change_id == change_id)
            .first()
        )
        if not change:
            return None

        # Collect data
        data = collect_retrospective_data(db, change)
        data["classification"] = classify_retrospective(data)

        # Try LLM insights, fallback to heuristic
        insights = generate_llm_insights(data)

        # Build and persist markdown
        markdown = build_retrospective_markdown(data, insights, data["classification"])
        filepath = persist_retrospective(markdown, change_id)

        return filepath
    except Exception as e:
        import logging

        logging.getLogger(__name__).error(f"Retrospective generation failed: {e}")
        return None
    finally:
        db.close()
