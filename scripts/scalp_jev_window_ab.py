#!/usr/bin/env python3
"""A/B read-only da janela de estado do scalp Jev — Card #1029.

Lê o log de diagnóstico do #1015 (``SCALP_JEV_LOG_FILE`` /
``backend/scalp_jev_diagnostic.log``) e compara a **confiança média** obtida
com a **janela de estado actual** e com a **janela maior**. É **read-only**:
não escreve produto, estado do scalp nem base de dados nova, e não precisa do
loop do scalp a correr.

O braço de cada observação é **derivado da janela de estado efectiva** que o
registo de retorno passou a declarar (``state_window_s=``): ``larger`` se e só
se a janela for maior do que a actual (900 s), ``current`` caso contrário. O
rótulo ``ab_arm=`` continua a ser lido, mas deixa de ser autoridade — um rótulo
``larger`` com a janela de 900 s é contado como incoerência e não move a
amostra. O braço **não** altera o gate, o limiar, a pergunta nem a decisão.

Regras do contrato (decisão 7 do Design):

* só observações com a **mesma versão fixa de modelo** (o pin do #1028) entram
  na amostra; a versão é declarada com o resultado;
* a amostra é agrupada em **janelas de 900 s não sobrepostas** — observações na
  mesma janela contam **uma vez**;
* conclui **apenas** com **≥ 30 janelas de 900 s não sobrepostas em cada
  braço**; abaixo disso **não conclui** e escreve **``amostra insuficiente``**;
* o **tamanho da amostra** (janelas e observações por braço) é sempre declarado.

Uso (do worktree do card, venv do source)::

    /srv/apps/dev/criptofarol/source/backend/.venv/bin/python \
        scripts/scalp_jev_window_ab.py --out <relatorio.md>
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import sys
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Any, Optional, Sequence

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.services.scalp_state_window import CURRENT_STATE_WINDOW_S  # noqa: E402

DEFAULT_LOG_PATH = BACKEND / "scalp_jev_diagnostic.log"

# The window that decides the A/B arm is the product single source (card #1029):
# imported, never re-declared here, so label and window cannot drift apart.
HORIZON_S = CURRENT_STATE_WINDOW_S
MIN_NON_OVERLAPPING_WINDOWS = 30
ARM_CURRENT = "current"
ARM_LARGER = "larger"
ARMS = (ARM_CURRENT, ARM_LARGER)
DEFAULT_PINNED_MODEL = "jev-1.13.0"

ReturnRe = re.compile(r"\sscalp jev call return id=(\S+) (.*)$")
KVRe = re.compile(r"([A-Za-z_][A-Za-z0-9_]*)=(\S+)")
TimestampRe = re.compile(r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) ")


def _dec(value: Any, default: str = "0") -> Decimal:
    try:
        if value is None:
            return Decimal(default)
        return Decimal(str(value))
    except Exception:
        return Decimal(default)


def _parse_stamp(raw: str) -> Optional[datetime]:
    try:
        return datetime.strptime(raw, "%Y-%m-%d %H:%M:%S,%f")
    except ValueError:
        return None


def _window_s(value: Any) -> Optional[int]:
    """Effective state window declared by the record; ``None`` when absent/invalid."""
    if value is None:
        return None
    try:
        parsed = float(str(value))
    except (TypeError, ValueError):
        return None
    # ``inf``/``1e400``/``nan`` are invalid, never a raise (``parse_returns``
    # promises "Never raises") and never a value that compares true by accident.
    if not math.isfinite(parsed):
        return None
    return int(parsed)


def _pinned_model() -> str:
    """Fixed model version of the sample (pin of the prerequisite of this card)."""
    try:
        if str(BACKEND) not in sys.path:
            sys.path.insert(0, str(BACKEND))
        from app.services.scalp_jev import jev_model

        return jev_model()
    except Exception:
        raw = (os.getenv("SCALP_JEV_MODEL") or "").strip()
        if not raw or raw.lower() == "jev-latest":
            return DEFAULT_PINNED_MODEL
        return raw


@dataclass(frozen=True)
class Observation:
    """One ``call return`` record: confidence, derived arm, model and window."""

    call_id: str
    at: datetime
    arm: str
    confidence: Decimal
    model: str
    # Effective state window declared by the record (card #1029) and the raw
    # label it carried; ``None`` on records that predate the effective window.
    state_window_s: Optional[int] = None
    recorded_arm: Optional[str] = None


def parse_returns(path: Path) -> tuple[list[Observation], int]:
    """Read every ``call return`` record with confidence + arm. Never raises."""
    observations: list[Observation] = []
    malformed = 0
    text = path.read_text(encoding="utf-8", errors="replace")
    for line in text.splitlines():
        returned = ReturnRe.search(line)
        if returned is None:
            continue
        stamp_match = TimestampRe.match(line)
        stamp = _parse_stamp(stamp_match.group(1)) if stamp_match else None
        if stamp is None:
            malformed += 1
            continue
        fields = dict(KVRe.findall(returned.group(2)))
        recorded = str(fields.get("ab_arm") or "").strip().lower()
        effective = _window_s(fields.get("state_window_s"))
        if effective is not None:
            # The record declares the effective window: derive the arm from it,
            # so a ``larger`` label with the 900 s window is not trusted.
            arm = ARM_LARGER if effective > HORIZON_S else ARM_CURRENT
        elif recorded in ARMS:
            arm = recorded
        else:
            malformed += 1
            continue
        if "confidence" not in fields:
            malformed += 1
            continue
        observations.append(
            Observation(
                call_id=returned.group(1),
                at=stamp,
                arm=arm,
                confidence=_dec(fields.get("confidence")),
                model=str(fields.get("model") or "unknown"),
                state_window_s=effective,
                recorded_arm=recorded if recorded in ARMS else None,
            )
        )
    return observations, malformed


def non_overlapping(observations: Sequence[Observation]) -> list[Observation]:
    """Greedy non-overlapping 900 s windows (first observation per window wins)."""
    accepted: list[Observation] = []
    last_at: Optional[datetime] = None
    for observation in sorted(observations, key=lambda item: item.at):
        if last_at is None or (observation.at - last_at).total_seconds() >= HORIZON_S:
            accepted.append(observation)
            last_at = observation.at
    return accepted


def _mean(values: Sequence[Decimal]) -> Optional[Decimal]:
    if not values:
        return None
    return sum(values, Decimal("0")) / Decimal(len(values))


def _fmt(value: Optional[Decimal], places: str = "0.001") -> str:
    if value is None:
        return "—"
    return str(Decimal(value).quantize(Decimal(places)))


def build_report(
    *,
    log_path: Path,
    observations: list[Observation],
    malformed: int,
    model: str,
) -> tuple[str, dict[str, Any]]:
    by_arm: dict[str, list[Observation]] = {arm: [] for arm in ARMS}
    excluded_other_model = 0
    for observation in observations:
        if observation.model != model:
            excluded_other_model += 1
            continue
        by_arm[observation.arm].append(observation)

    windows = {arm: non_overlapping(by_arm[arm]) for arm in ARMS}
    mean_confidence = {arm: _mean([obs.confidence for obs in windows[arm]]) for arm in ARMS}
    window_counts = {arm: len(windows[arm]) for arm in ARMS}
    observation_counts = {arm: len(by_arm[arm]) for arm in ARMS}
    enough = all(window_counts[arm] >= MIN_NON_OVERLAPPING_WINDOWS for arm in ARMS)
    # A record that declares an effective window but carries no label, or a
    # label that disagrees with the window, is a coherence finding — never a
    # reason to move the observation between arms.
    window_arm_mismatches = sum(
        1
        for observation in observations
        if observation.state_window_s is not None
        and observation.recorded_arm in ARMS
        and observation.recorded_arm != observation.arm
    )
    effective_windows = {
        arm: sorted({obs.state_window_s for obs in by_arm[arm] if obs.state_window_s is not None})
        for arm in ARMS
    }

    summary: dict[str, Any] = {
        "log": str(log_path),
        "model": model,
        "horizon_s": HORIZON_S,
        "min_non_overlapping_windows": MIN_NON_OVERLAPPING_WINDOWS,
        "malformed_records": malformed,
        "excluded_other_model": excluded_other_model,
        "windows": window_counts,
        "observations": observation_counts,
        "effective_windows_s": effective_windows,
        "window_arm_mismatches": window_arm_mismatches,
        "mean_confidence": {
            arm: (None if mean_confidence[arm] is None else str(mean_confidence[arm]))
            for arm in ARMS
        },
        "concludes": enough,
        "declaration": None if enough else "amostra insuficiente",
    }

    lines: list[str] = []
    lines.append("# Card #1029 — A/B read-only da janela de estado")
    lines.append("")
    lines.append(f"- log: `{log_path}`")
    lines.append(f"- versão de modelo fixa: `{model}`")
    lines.append(
        f"- amostra: janelas não sobrepostas de {HORIZON_S} s; mínimo "
        f"{MIN_NON_OVERLAPPING_WINDOWS} por braço"
    )
    lines.append(f"- registos malformados ignorados: {malformed}")
    lines.append(f"- observações de outra versão de modelo excluídas: {excluded_other_model}")
    lines.append(
        "- janela de estado efectiva declarada: "
        f"`current`={effective_windows[ARM_CURRENT] or '—'} s; "
        f"`larger`={effective_windows[ARM_LARGER] or '—'} s"
    )
    lines.append(f"- rótulos de braço incoerentes com a janela efectiva: {window_arm_mismatches}")
    lines.append("")
    lines.append("## Confiança média por braço (janela de estado)")
    lines.append("")
    lines.append("| braço | observações | janelas não sobrepostas | confiança média |")
    lines.append("| --- | --- | --- | --- |")
    for arm in ARMS:
        lines.append(
            f"| {arm} | {observation_counts[arm]} | {window_counts[arm]} | "
            f"{_fmt(mean_confidence[arm])} |"
        )
    lines.append("")
    lines.append("## Declaração / gate")
    lines.append("")
    if enough:
        lines.append("Amostra suficiente: o A/B conclui.")
        lines.append(
            f"- confiança média com a janela actual: {_fmt(mean_confidence[ARM_CURRENT])} "
            f"({window_counts[ARM_CURRENT]} janelas de {HORIZON_S} s não sobrepostas)"
        )
        lines.append(
            f"- confiança média com a janela maior: {_fmt(mean_confidence[ARM_LARGER])} "
            f"({window_counts[ARM_LARGER]} janelas de {HORIZON_S} s não sobrepostas)"
        )
        lines.append(f"- versão de modelo fixa: `{model}`")
    else:
        lines.append("**amostra insuficiente** — o A/B não conclui:")
        lines.append("")
        for arm in ARMS:
            if window_counts[arm] < MIN_NON_OVERLAPPING_WINDOWS:
                lines.append(
                    f"- braço `{arm}`: {window_counts[arm]} janela(s) não sobreposta(s) "
                    f"de {HORIZON_S} s < mínimo de {MIN_NON_OVERLAPPING_WINDOWS}"
                )
        if not (window_counts[ARM_CURRENT] and window_counts[ARM_LARGER]):
            lines.append("- as duas janelas de estado têm de ter amostra")
        lines.append("")
        lines.append(
            "Consequência: nenhuma conclusão sobre a janela de estado é retirada "
            "desta amostra; a decisão, os gates e a pergunta ficam inalterados."
        )
    lines.append("")
    return "\n".join(lines), summary


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--log",
        default=None,
        help=(
            "log de diagnóstico do #1015 (default: SCALP_JEV_LOG_FILE ou "
            "backend/scalp_jev_diagnostic.log)"
        ),
    )
    parser.add_argument("--json", action="store_true", help="imprime também o sumário JSON")
    parser.add_argument("--out", default=None, help="grava o relatório markdown neste caminho")
    args = parser.parse_args(argv)

    log_path = Path(args.log or os.getenv("SCALP_JEV_LOG_FILE") or DEFAULT_LOG_PATH)
    model = _pinned_model()
    observations: list[Observation] = []
    malformed = 0
    if log_path.exists():
        observations, malformed = parse_returns(log_path)
    report, summary = build_report(
        log_path=log_path,
        observations=observations,
        malformed=malformed,
        model=model,
    )
    if not log_path.exists():
        report = f"> **Log ausente**: `{log_path}` não existe.\n\n" + report
    print(report)
    if args.json:
        print("```json")
        print(json.dumps(summary, indent=2, ensure_ascii=False, default=str))
        print("```")
    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(report + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
