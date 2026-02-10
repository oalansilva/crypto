"""Strategy Lab endpoints (CP1 - minimal scaffolding).

CP1 goals:
- Create a lab run and return run_id (accepted)
- Poll run status
- No LangGraph yet

Persistence:
- Writes a small JSON file under backend/logs/lab_runs/<run_id>.json

Security:
- Single-tenant MVP; no auth.
"""

from __future__ import annotations

import json
import os
import re
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/lab", tags=["lab"])


def _runs_dir() -> Path:
    # backend/app/routes/lab.py -> backend/app/routes -> backend/app -> backend
    base = Path(__file__).resolve().parents[2]
    d = base / "logs" / "lab_runs"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _run_path(run_id: str) -> Path:
    return _runs_dir() / f"{run_id}.json"


def _trace_path(run_id: str) -> Path:
    return _runs_dir() / f"{run_id}.jsonl"


def _append_trace(run_id: str, event: Dict[str, Any]) -> None:
    """Append one JSONL trace event for this run."""

    p = _trace_path(run_id)
    line = json.dumps(event, ensure_ascii=False)
    # Atomic-ish append
    with p.open("a", encoding="utf-8") as f:
        f.write(line)
        f.write("\n")


def _read_trace_tail(run_id: str, limit: int = 200) -> List[Dict[str, Any]]:
    """Read up to `limit` events from the tail of the JSONL trace."""

    p = _trace_path(run_id)
    if not p.exists():
        return []

    try:
        lines = p.read_text(encoding="utf-8").splitlines()
    except Exception:
        return []

    out: List[Dict[str, Any]] = []
    for line in lines[-limit:]:
        line = (line or "").strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except Exception:
            continue

    return out


def _now_ms() -> int:
    return int(time.time() * 1000)


class LabRunCreateRequest(BaseModel):
    symbol: Optional[str] = Field(default=None, max_length=30)
    timeframe: Optional[str] = Field(default=None, max_length=10)

    # Dev-only: enable trace correlation metadata for Studio/LangSmith.
    debug_trace: bool = False

    direction: str = "long"
    constraints: Dict[str, Any] = Field(default_factory=dict)
    objective: Optional[str] = None
    thinking: str = "low"
    deep_backtest: bool = True

    # Use full available history by default (user preference). For Binance/ccxt
    # data, the true maximum depends on the loader, but we treat this as:
    # since = inception default (2017-01-01) unless explicitly overridden.
    full_history: bool = True
    since: Optional[str] = None
    until: Optional[str] = None

    # Autonomous search limits
    max_iterations: int = 3


class LabRunCreateResponse(BaseModel):
    run_id: str
    status: str
    trace: Dict[str, Any]


class LabRunNeedsUserInputResponse(BaseModel):
    status: str
    missing: List[str]
    question: str


def _inputs_preflight(req: LabRunCreateRequest) -> Optional[LabRunNeedsUserInputResponse]:
    from app.services.lab_graph import build_upstream_contract

    contract = build_upstream_contract(
        context={
            "input": req.model_dump(),
            "symbol": req.symbol,
            "timeframe": req.timeframe,
            "objective": req.objective,
        }
    )
    if bool(contract.get("approved")):
        return None

    return LabRunNeedsUserInputResponse(
        status="needs_user_input",
        missing=list(contract.get("missing") or []),
        question=str(contract.get("question") or ""),
    )


class LabRunTraceEvent(BaseModel):
    ts_ms: int
    type: str
    data: Dict[str, Any] = Field(default_factory=dict)


class LabRunBudget(BaseModel):
    turns_used: int = 0
    # Default budgets for Labs runs.
    # Set high to avoid frequent UI "Limite atingido" confirmations during long backtests.
    turns_max: int = 200
    tokens_total: int = 0
    tokens_max: int = 1_000_000
    on_limit: str = "ask_user"  # ask_user


class LabRunOutputs(BaseModel):
    coordinator_summary: Optional[str] = None
    dev_summary: Optional[str] = None
    validator_verdict: Optional[str] = None
    tests_done: Optional[Dict[str, Any]] = None
    final_decision: Optional[Dict[str, Any]] = None

    # CP10 selection gate summary
    selection: Optional[Dict[str, Any]] = None

    # CP8
    candidate_template_name: Optional[str] = None

    # CP5
    saved_template_name: Optional[str] = None
    saved_favorite_id: Optional[int] = None


class LabRunStatusResponse(BaseModel):
    run_id: str
    status: str
    step: Optional[str] = None
    created_at_ms: int
    updated_at_ms: int

    # Stable trace object used by the UI.
    # Back-compat: includes viewer_url + api_url.
    trace: Dict[str, Any]

    # Back-compat: keep trace_events, but also provide events as alias.
    trace_events: List[LabRunTraceEvent] = Field(default_factory=list)
    events: List[LabRunTraceEvent] = Field(default_factory=list)

    budget: LabRunBudget = Field(default_factory=LabRunBudget)
    outputs: LabRunOutputs = Field(default_factory=LabRunOutputs)

    # CP9: job pipeline info for backtest execution
    backtest_job: Optional[Dict[str, Any]] = None

    # CP3/CP6: backtest output (supports walk-forward split)
    backtest: Optional[Dict[str, Any]] = None

    # If we hit budget limits, the run waits for user confirmation.
    needs_user_confirm: bool = False

    # Two-phase graph persistence fields
    phase: Optional[str] = None
    upstream_contract: Optional[Dict[str, Any]] = None
    upstream: Optional[Dict[str, Any]] = None


class LabRunContinueRequest(BaseModel):
    message: Optional[str] = None
    symbol: Optional[str] = Field(default=None, max_length=30)
    timeframe: Optional[str] = Field(default=None, max_length=10)
    objective: Optional[str] = None


class LabRunUpstreamMessageRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)


class LabRunUpstreamMessageResponse(BaseModel):
    status: str
    run_id: str
    phase: str
    upstream_contract: Dict[str, Any]
    upstream: Dict[str, Any]


class LabRunUpstreamApproveResponse(BaseModel):
    status: str
    run_id: str
    phase: str


class LabRunUpstreamFeedbackRequest(BaseModel):
    message: str


class LabRunUpstreamFeedbackResponse(BaseModel):
    status: str
    run_id: str
    phase: str
    upstream_contract: Dict[str, Any]
    upstream: Dict[str, Any]


def _parse_symbol_timeframe_from_text(text: Optional[str]) -> Dict[str, str]:
    raw = str(text or "")

    # Accept explicit key/value (symbol=, timeframe=). Tolerate common typo: "sumbol".
    symbol_match = re.search(
        r"(?:^|\s)(?:symbol|sumbol)\s*[:=]\s*([A-Za-z0-9._-]+/[A-Za-z0-9._-]+)",
        raw,
        flags=re.IGNORECASE,
    )
    timeframe_match = re.search(r"(?:^|\s)timeframe\s*[:=]\s*([0-9]+[A-Za-z]+)", raw, flags=re.IGNORECASE)

    out: Dict[str, str] = {}

    # Also accept compact inputs like: "BTC/USDT 4H" (or "BTC/USDT 4h")
    compact_match = re.search(r"([A-Za-z0-9._-]+/[A-Za-z0-9._-]+)\s+([0-9]+[A-Za-z]+)", raw)

    # Also accept symbol-only or timeframe-only freeform.
    symbol_only_match = re.search(r"\b([A-Za-z0-9._-]+/[A-Za-z0-9._-]+)\b", raw)
    timeframe_only_match = re.search(r"\b([0-9]+\s*(?:m|h|d|w|minuto(?:s)?|hora(?:s)?|dia(?:s)?|semana(?:s)?))\b", raw, flags=re.IGNORECASE)

    if symbol_match:
        out["symbol"] = str(symbol_match.group(1) or "").strip()
    elif compact_match:
        out["symbol"] = str(compact_match.group(1) or "").strip()
    elif symbol_only_match:
        out["symbol"] = str(symbol_only_match.group(1) or "").strip()

    if timeframe_match:
        out["timeframe"] = str(timeframe_match.group(1) or "").strip()
    elif compact_match:
        out["timeframe"] = str(compact_match.group(2) or "").strip()
    elif timeframe_only_match:
        out["timeframe"] = str(timeframe_only_match.group(1) or "").strip()

    return out


def _sanitize_upstream_messages(raw: Any) -> List[Dict[str, Any]]:
    if not isinstance(raw, list):
        return []

    out: List[Dict[str, Any]] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        role = str(item.get("role") or "").strip().lower()
        if role == "validator":
            role = "trader"
        if role not in ("user", "trader"):
            continue
        text = str(item.get("text") or "").strip()
        if not text:
            continue
        ts_raw = item.get("ts_ms")
        try:
            ts_ms = int(ts_raw)
        except Exception:
            ts_ms = _now_ms()
        out.append({"role": role, "text": text, "ts_ms": ts_ms})
    return out


def _ensure_upstream_state(run: Dict[str, Any]) -> Dict[str, Any]:
    upstream = run.get("upstream")
    if not isinstance(upstream, dict):
        upstream = {}

    messages = _sanitize_upstream_messages(upstream.get("messages"))
    pending_question = str(upstream.get("pending_question") or "").strip()

    contract = run.get("upstream_contract") or {}
    if not pending_question and isinstance(contract, dict) and not bool(contract.get("approved")):
        pending_question = str(contract.get("question") or "").strip()

    strategy_draft = upstream.get("strategy_draft")
    if not isinstance(strategy_draft, dict):
        strategy_draft = None

    ready_for_user_review = bool(upstream.get("ready_for_user_review"))
    user_approved = bool(upstream.get("user_approved"))
    user_feedback = str(upstream.get("user_feedback") or "").strip()

    normalized = {
        "messages": messages,
        "pending_question": pending_question,
        "strategy_draft": strategy_draft,
        "ready_for_user_review": ready_for_user_review,
        "user_approved": user_approved,
        "user_feedback": user_feedback,
    }
    run["upstream"] = normalized
    return normalized


def _append_upstream_message(run_id: str, run: Dict[str, Any], *, role: str, text: str) -> Optional[Dict[str, Any]]:
    role_norm = str(role or "").strip().lower()
    if role_norm == "validator":
        role_norm = "trader"
    if role_norm not in ("user", "trader"):
        return None

    content = str(text or "").strip()
    if not content:
        return None

    upstream = _ensure_upstream_state(run)
    msg = {"role": role_norm, "text": content, "ts_ms": _now_ms()}
    upstream["messages"].append(msg)
    run["upstream"] = upstream

    _append_trace(
        run_id,
        {
            "ts_ms": msg["ts_ms"],
            "type": "upstream_message",
            "data": {"role": role_norm, "text": content[:2000]},
        },
    )
    return msg


def _build_upstream_contract_from_input(inp: Dict[str, Any]) -> Dict[str, Any]:
    from app.services.lab_graph import build_upstream_contract

    return build_upstream_contract(
        context={
            "input": inp,
            "symbol": inp.get("symbol"),
            "timeframe": inp.get("timeframe"),
            "objective": inp.get("objective"),
        }
    )


def _contract_trace_data(contract: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "approved": bool(contract.get("approved")),
        "missing": list(contract.get("missing") or []),
        "question": str(contract.get("question") or ""),
        "inputs": dict(contract.get("inputs") or {}),
    }


async def _try_trader_upstream_turn(
    *,
    run_id: str,
    session_key: str,
    thinking: str,
    user_message: str,
    contract: Dict[str, Any],
    upstream_messages: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Best-effort Trader turn using validator persona id internally."""

    compact_history = []
    for msg in upstream_messages[-12:]:
        if not isinstance(msg, dict):
            continue
        role = str(msg.get("role") or "").strip().lower()
        text = str(msg.get("text") or "").strip()
        if role in ("user", "trader") and text:
            compact_history.append({"role": role, "text": text})

    system_prompt = (
        "Papel: Trader do upstream do Strategy Lab.\n"
        "Você conversa com um humano para fechar um contrato upstream e propor uma estratégia antes de executar.\n"
        "Objetivo: conversa fluida (estilo chat), entendendo respostas em formatos variados e extraindo inputs/constraints com segurança.\n"
        "Responda EXCLUSIVAMENTE com JSON válido no formato:\n"
        "{\n"
        '  "reply": "próxima pergunta curta (ou confirmação)",\n'
        '  "inputs": {"symbol": "BTC/USDT", "timeframe": "4h", "objective": "..."},\n'
        '  "constraints": {"max_drawdown": 0.2, "min_sharpe": 0.4},\n'
        '  "ready_for_user_review": true,\n'
        '  "strategy_draft": {\n'
        '    "version": 1,\n'
        '    "one_liner": "...",\n'
        '    "rationale": "...",\n'
        '    "indicators": [{"source":"pandas_ta","name":"rsi","params":{"length":14}}],\n'
        '    "entry_idea": "...",\n'
        '    "exit_idea": "...",\n'
        '    "risk_plan": "...",\n'
        '    "what_to_measure": ["sharpe_holdout","max_drawdown_holdout","min_trades"],\n'
        '    "open_questions": ["..."]\n'
        '  }\n'
        "}\n\n"
        "Regras:\n"
        "- NÃO invente symbol/timeframe.\n"
        "- Se o humano respondeu algo como 'BTC/USDT 4H', 'BTCUSDT 4h', 'btc usdt no 4 horas', extraia e preencha `inputs`.\n"
        "- Se um campo já existir no Contrato atual (JSON) ou já apareceu no histórico, NÃO pergunte por ele de novo. Pergunte pelo próximo campo faltante.\n"
        "- Se não souber algum campo, omita o campo e faça uma pergunta objetiva.\n"
        "- Quando já houver informação suficiente (symbol+timeframe+objetivo+constraints), preencha `strategy_draft` e marque `ready_for_user_review=true`.\n"
    )

    payload_message = (
        "Histórico upstream (JSON):\n"
        + json.dumps(compact_history, ensure_ascii=False, indent=2)
        + "\n\nContrato atual (JSON):\n"
        + json.dumps(contract, ensure_ascii=False, indent=2)
        + "\n\nÚltima mensagem do humano:\n"
        + str(user_message or "")
    )

    try:
        response = await _persona_call_async(
            run_id=run_id,
            session_key=session_key,
            persona="validator",
            system_prompt=system_prompt,
            message=payload_message,
            thinking=thinking or "low",
            timeout_s=60,
        )
    except Exception:
        return {}

    obj = _extract_json_object(response.get("text") or "")
    if not isinstance(obj, dict):
        return {}

    out: Dict[str, Any] = {}
    reply = str(obj.get("reply") or obj.get("question") or obj.get("message") or "").strip()
    if reply:
        out["reply"] = reply

    inputs = obj.get("inputs")
    if isinstance(inputs, dict):
        norm_inputs: Dict[str, Any] = {}
        for k in ("symbol", "timeframe", "objective"):
            v = inputs.get(k)
            if isinstance(v, str) and v.strip():
                norm_inputs[k] = v.strip()
        if norm_inputs:
            out["inputs"] = norm_inputs

    constraints = obj.get("constraints")
    if isinstance(constraints, dict):
        out["constraints"] = constraints

    if isinstance(obj.get("ready_for_user_review"), bool):
        out["ready_for_user_review"] = bool(obj.get("ready_for_user_review"))

    strategy_draft = obj.get("strategy_draft")
    if isinstance(strategy_draft, dict):
        out["strategy_draft"] = strategy_draft

    return out


async def _try_trader_generate_strategy_draft(*, run_id: str, session_key: str, thinking: str, contract: Dict[str, Any], upstream_messages: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Focused call to generate only the strategy draft once inputs are approved."""

    compact_history = []
    for msg in upstream_messages[-12:]:
        if not isinstance(msg, dict):
            continue
        role = str(msg.get("role") or "").strip().lower()
        text = str(msg.get("text") or "").strip()
        if role in ("user", "trader") and text:
            compact_history.append({"role": role, "text": text})

    system_prompt = (
        "Papel: Trader do upstream do Strategy Lab.\n"
        "Tarefa: gerar um Strategy Draft para o humano aprovar ANTES de iniciar execução.\n"
        "Responda EXCLUSIVAMENTE com JSON válido no formato:\n"
        "{\n"
        '  "ready_for_user_review": true,\n'
        '  "strategy_draft": {\n'
        '    "version": 1,\n'
        '    "one_liner": "...",\n'
        '    "rationale": "...",\n'
        '    "indicators": [{"source":"pandas_ta","name":"rsi","params":{"length":14}}],\n'
        '    "entry_idea": "...",\n'
        '    "exit_idea": "...",\n'
        '    "risk_plan": "...",\n'
        '    "what_to_measure": ["sharpe_holdout","max_drawdown_holdout","min_trades"],\n'
        '    "open_questions": []\n'
        '  }\n'
        "}\n\n"
        "Regras:\n"
        "- NÃO invente symbol/timeframe. Use os do Contrato atual.\n"
        "- Indicadores devem ser plausíveis e baseados em pandas_ta (nome + params).\n"
        "- Draft deve ser curto e testável (idéia + como entrar/sair + risco).\n"
    )

    payload_message = (
        "Histórico upstream (JSON):\n"
        + json.dumps(compact_history, ensure_ascii=False, indent=2)
        + "\n\nContrato atual (JSON):\n"
        + json.dumps(contract, ensure_ascii=False, indent=2)
    )

    try:
        response = await _persona_call_sync(
            run_id=run_id,
            session_key=session_key,
            persona="validator",
            system_prompt=system_prompt,
            message=payload_message,
            thinking=thinking or "low",
            timeout_s=60,
        )
    except Exception:
        return {}

    obj = _extract_json_object(response.get("text") or "")
    if not isinstance(obj, dict):
        return {}

    out: Dict[str, Any] = {}
    if isinstance(obj.get("ready_for_user_review"), bool):
        out["ready_for_user_review"] = bool(obj.get("ready_for_user_review"))
    sd = obj.get("strategy_draft")
    if isinstance(sd, dict) and bool(sd):
        out["strategy_draft"] = sd

    return out


def _next_trader_prompt(contract: Dict[str, Any]) -> str:
    if bool(contract.get("approved")):
        return "Contrato upstream aprovado. Revise o resumo e clique em Iniciar execução."

    missing = contract.get("missing")
    if isinstance(missing, list) and missing:
        m0 = str(missing[0] or "").strip().lower()
        if m0 in ("symbol", "ticker"):
            return "Qual é o symbol (ex: BTC/USDT)?"
        if m0 in ("timeframe", "tf"):
            return "Qual é o timeframe (ex: 1h, 4h, 1d)?"
        if m0 in ("objective", "goal"):
            return "Qual é o objetivo do backtest (o que você quer otimizar/validar)?"

    q = str(contract.get("question") or "").strip()
    if q:
        return q

    return "Antes de continuar, preciso de mais detalhes para fechar o contrato upstream."


async def _handle_upstream_user_message(run_id: str, run: Dict[str, Any], user_message: str) -> Dict[str, Any]:
    text = str(user_message or "").strip()
    if not text:
        raise HTTPException(status_code=400, detail="message is required")

    _ensure_upstream_state(run)
    _append_upstream_message(run_id, run, role="user", text=text)
    upstream = _ensure_upstream_state(run)

    inp = run.get("input") or {}
    if not isinstance(inp, dict):
        inp = {}

    parsed = _parse_symbol_timeframe_from_text(text)
    for k, v in parsed.items():
        inp[k] = v

    if not str(inp.get("objective") or "").strip():
        inp["objective"] = text

    prev_contract = run.get("upstream_contract") or {}
    prev_approved = bool(prev_contract.get("approved"))
    session_key = str(run.get("session_key") or f"lab-{run_id}")
    thinking = str((run.get("input") or {}).get("thinking") or "low")

    contract = _build_upstream_contract_from_input(inp)

    trader_turn = await _try_trader_upstream_turn(
        run_id=run_id,
        session_key=session_key,
        thinking=thinking,
        user_message=text,
        contract=contract,
        upstream_messages=upstream.get("messages") or [],
    )

    def _normalize_timeframe(tf: str) -> str:
        t = str(tf or "").strip().lower().replace(" ", "")
        # Portuguese words
        t = t.replace("horas", "h").replace("hora", "h")
        t = t.replace("minutos", "m").replace("minuto", "m")
        t = t.replace("dias", "d").replace("dia", "d")
        t = t.replace("semanas", "w").replace("semana", "w")
        m = re.match(r"^([0-9]+)([a-z]+)$", t)
        if not m:
            return str(tf or "").strip()
        n, u = m.group(1), m.group(2)
        if u not in ("m", "h", "d", "w"):
            return str(tf or "").strip()
        return f"{n}{u}"

    def _normalize_symbol(sym: str) -> str:
        s = str(sym or "").strip().upper().replace("-", "/").replace("_", "/")
        if "/" in s:
            return s
        # Common compact forms: BTCUSDT
        for quote in ("USDT", "USD", "USDC"):
            if s.endswith(quote) and len(s) > len(quote):
                base = s[: -len(quote)]
                return f"{base}/{quote}"
        return s

    trader_inputs = trader_turn.get("inputs") if isinstance(trader_turn.get("inputs"), dict) else {}
    for k in ("symbol", "timeframe", "objective"):
        v = trader_inputs.get(k)
        if isinstance(v, str) and v.strip():
            if k == "symbol":
                inp[k] = _normalize_symbol(v)
            elif k == "timeframe":
                inp[k] = _normalize_timeframe(v)
            else:
                inp[k] = v.strip()

    trader_constraints = trader_turn.get("constraints")
    if isinstance(trader_constraints, dict):
        constraints = inp.get("constraints") if isinstance(inp.get("constraints"), dict) else {}
        constraints.update(trader_constraints)
        inp["constraints"] = constraints

    contract = _build_upstream_contract_from_input(inp)

    # Strategy draft + review gate
    if bool(contract.get("approved")):
        upstream["ready_for_user_review"] = bool(trader_turn.get("ready_for_user_review"))
        sd = trader_turn.get("strategy_draft")
        if isinstance(sd, dict) and bool(sd):
            upstream["strategy_draft"] = sd

        # If contract is approved but the Trader didn't provide a draft yet, force a focused draft generation call.
        if not bool(upstream.get("ready_for_user_review")) or not isinstance(upstream.get("strategy_draft"), dict):
            draft_turn = await _try_trader_generate_strategy_draft(
                run_id=run_id,
                session_key=session_key,
                thinking=thinking,
                contract=contract,
                upstream_messages=upstream.get("messages") or [],
            )
            if bool(draft_turn.get("ready_for_user_review")) and isinstance(draft_turn.get("strategy_draft"), dict):
                upstream["ready_for_user_review"] = True
                upstream["strategy_draft"] = draft_turn.get("strategy_draft")
    else:
        upstream["ready_for_user_review"] = False
        upstream["strategy_draft"] = None

    trader_reply = str(trader_turn.get("reply") or "").strip() or _next_trader_prompt(contract)
    if bool(contract.get("approved")):
        contract["question"] = ""
        upstream["pending_question"] = ""
    else:
        contract["question"] = trader_reply
        upstream["pending_question"] = trader_reply

    run["input"] = inp
    run["upstream"] = upstream
    run["upstream_contract"] = contract

    _append_upstream_message(run_id, run, role="trader", text=trader_reply)
    upstream = _ensure_upstream_state(run)

    run["upstream"] = upstream

    _append_trace(
        run_id,
        {
            "ts_ms": _now_ms(),
            "type": "upstream_contract_updated",
            "data": _contract_trace_data(contract),
        },
    )
    if bool(contract.get("approved")) and not prev_approved:
        _append_trace(
            run_id,
            {
                "ts_ms": _now_ms(),
                "type": "upstream_approved",
                "data": {"inputs": dict(contract.get("inputs") or {})},
            },
        )

    status = "ready_for_review" if (bool(contract.get("approved")) and bool(upstream.get("ready_for_user_review"))) else ("ready_for_execution" if bool(contract.get("approved")) else "needs_user_input")
    if bool(upstream.get("ready_for_user_review")):
        _append_trace(run_id, {"ts_ms": _now_ms(), "type": "upstream_strategy_draft_ready", "data": {"has_draft": bool(upstream.get("strategy_draft"))}})

    return {
        "input": inp,
        "upstream": upstream,
        "upstream_contract": contract,
        "status": status,
        "step": "upstream",
        "phase": "upstream",
        "needs_user_confirm": False,
    }


def _load_run_json(run_id: str) -> Dict[str, Any]:
    p = _run_path(run_id)
    if not p.exists():
        return {}
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {}
    if not isinstance(data, dict):
        return {}
    _ensure_upstream_state(data)
    return data


def _update_run_json(run_id: str, patch: Dict[str, Any]) -> None:
    p = _run_path(run_id)
    if not p.exists():
        return
    cur = _load_run_json(run_id)
    cur.update(patch)
    _ensure_upstream_state(cur)
    cur["updated_at_ms"] = _now_ms()
    p.write_text(json.dumps(cur, ensure_ascii=False, indent=2), encoding="utf-8")


def _cp3_default_since(timeframe: str, full_history: bool = True) -> str:
    """Default since.

    If full_history=True, we always start from a conservative "inception" date.
    """

    if full_history:
        return "2017-01-01 00:00:00"

    # Legacy bounded windows (kept for optional override)
    tf = (timeframe or "").lower()
    if tf.endswith("h") or tf.endswith("m"):
        # Intraday: 6 months
        return "2025-08-01 00:00:00"
    # Daily+: 2 years
    return "2024-01-01 00:00:00"


def _extract_tokens_from_gateway_payload(payload: Dict[str, Any]) -> int:
    """Best-effort token extraction from OpenClaw gateway agent payload."""

    # payload: {runId,status,result:{...}}
    res = (payload or {}).get("result") or {}

    # Newer gateway shape: result.meta.agentMeta.usage
    agent_meta = (res.get("meta") or {}).get("agentMeta") or {}
    usage = agent_meta.get("usage") or {}

    # Common keys
    for k in ("totalTokens", "total_tokens", "tokens_total", "total"):
        v = usage.get(k)
        if isinstance(v, int):
            return v

    # Some providers split in/out
    if isinstance(usage.get("input"), int) and isinstance(usage.get("output"), int):
        return int(usage.get("input")) + int(usage.get("output"))
    if isinstance(usage.get("inputTokens"), int) and isinstance(usage.get("outputTokens"), int):
        return int(usage.get("inputTokens")) + int(usage.get("outputTokens"))

    return 0


def _extract_text_from_gateway_payload(payload: Dict[str, Any]) -> str:
    """Best-effort extraction of assistant text from gateway payload."""

    res = (payload or {}).get("result") or {}

    # Preferred: payloads[0].text
    payloads = res.get("payloads")
    if isinstance(payloads, list) and payloads:
        p0 = payloads[0]
        if isinstance(p0, dict):
            t = p0.get("text") or p0.get("content")
            if isinstance(t, str) and t.strip():
                return t.strip()
        if isinstance(p0, str) and p0.strip():
            return p0.strip()

    # Fallback: meta/message fields
    for k in ("text", "message", "output"):
        t = res.get(k)
        if isinstance(t, str) and t.strip():
            return t.strip()

    # Last resort: stringify compactly
    return json.dumps(res, ensure_ascii=False)[:4000]


async def _persona_call_async(*,
                       run_id: str,
                       session_key: str,
                       persona: str,
                       system_prompt: str,
                       message: str,
                       thinking: str,
                       timeout_s: int = 180) -> Dict[str, Any]:
    """Run one persona through OpenClaw gateway and trace it."""

    from app.services.openclaw_gateway_client import run_agent_via_gateway

    start = _now_ms()
    _append_trace(run_id, {"ts_ms": start, "type": "persona_started", "data": {"persona": persona}})

    payload = await run_agent_via_gateway(
        message=message,
        session_key=session_key,
        agent_id="main",
        thinking=thinking,
        timeout_s=timeout_s,
        extra_system_prompt=system_prompt,
    )

    tokens = _extract_tokens_from_gateway_payload(payload)
    end = _now_ms()

    text = _extract_text_from_gateway_payload(payload)

    _append_trace(
        run_id,
        {
            "ts_ms": end,
            "type": "persona_done",
            "data": {"persona": persona, "duration_ms": end - start, "tokens": tokens, "text": text[:2000]},
        },
    )

    return {"text": text, "tokens": tokens, "raw": payload}


def _persona_call_sync(*,
                       run_id: str,
                       session_key: str,
                       persona: str,
                       system_prompt: str,
                       message: str,
                       thinking: str,
                       timeout_s: int = 180) -> Dict[str, Any]:
    """Sync wrapper for async persona call (safe for non-async contexts)."""

    import asyncio

    return asyncio.run(
        _persona_call_async(
            run_id=run_id,
            session_key=session_key,
            persona=persona,
            system_prompt=system_prompt,
            message=message,
            thinking=thinking,
            timeout_s=timeout_s,
        )
    )


def _budget_ok(budget: Dict[str, Any]) -> bool:
    return int(budget.get("turns_used", 0)) < int(budget.get("turns_max", 0)) and int(budget.get("tokens_total", 0)) < int(
        budget.get("tokens_max", 0)
    )


def _inc_budget(budget: Dict[str, Any], *, turns: int = 0, tokens: int = 0) -> Dict[str, Any]:
    b = dict(budget or {})
    b["turns_used"] = int(b.get("turns_used", 0)) + int(turns)
    b["tokens_total"] = int(b.get("tokens_total", 0)) + int(tokens)
    return b


def _verdict_label(text: Optional[str]) -> str:
    """Extract approval label from the validator output.

    Important: do NOT treat mentions like "para virar approved" as approval.
    Prefer explicit leading verdict markers.
    """

    raw = (text or "").strip()
    t = raw.lower()
    if not t:
        return "unknown"

    # JSON-only validator support
    if raw.startswith("{"):
        try:
            obj = json.loads(raw)
            v = str(obj.get("verdict") or "").strip().lower()
            if v in ("approved", "rejected", "metrics_invalid"):
                return v
        except Exception:
            pass

    # Strong signals first (explicit markers)
    for pat in (
        "veredito: rejected",
        "veredito: reprovado",
        "veredito: aprovado",  # pt-BR
        "veredito: approved",
    ):
        if pat in t:
            if "rejected" in pat or "reprovado" in pat:
                return "rejected"
            if "approved" in pat or "aprovado" in pat:
                return "approved"

    # Next: heading-ish patterns at start
    if t.startswith("**veredito: rejected") or t.startswith("veredito: rejected"):
        return "rejected"
    if t.startswith("**veredito: approved") or t.startswith("veredito: approved"):
        return "approved"
    if t.startswith("rejected") or t.startswith("**rejected"):
        return "rejected"
    if t.startswith("approved") or t.startswith("**approved"):
        return "approved"

    # Fallback: if both words appear, prefer rejected (safer)
    has_app = "approved" in t or "aprovado" in t
    has_rej = "rejected" in t or "reprovado" in t
    if has_app and has_rej:
        return "rejected"
    if has_rej:
        return "rejected"
    if has_app:
        return "approved"

    return "unknown"


def _make_autosave_name(*, run_id: str, base_template: str, symbol: str, timeframe: str) -> str:
    safe_symbol = (symbol or "").replace("/", "_")
    rid = (run_id or "")[:8]
    return f"lab_{rid}_{base_template}_{safe_symbol}_{timeframe}".strip("_")


def _ensure_unique_template_name(combo, name: str) -> str:
    # combo: ComboService
    base = name
    if not combo.get_template_metadata(base):
        return base
    for i in range(2, 200):
        cand = f"{base}_{i}"
        if not combo.get_template_metadata(cand):
            return cand
    # last resort
    return f"{base}_{uuid.uuid4().hex[:6]}"


def _extract_json_object(text: str) -> Optional[Dict[str, Any]]:
    if not isinstance(text, str):
        return None
    s = text.strip()
    if not s:
        return None
    # try direct parse
    try:
        obj = json.loads(s)
        if isinstance(obj, dict):
            return obj
    except Exception:
        pass
    # try substring between first { and last }
    a = s.find("{")
    b = s.rfind("}")
    if a >= 0 and b > a:
        try:
            obj = json.loads(s[a : b + 1])
            if isinstance(obj, dict):
                return obj
        except Exception:
            return None
    return None


def _make_candidate_name(*, run_id: str, base_template: str, symbol: str, timeframe: str, n: int) -> str:
    safe_symbol = (symbol or "").replace("/", "_")
    rid = (run_id or "")[:8]
    return f"lab_{rid}_candidate_{n}_{base_template}_{safe_symbol}_{timeframe}".strip("_")


def _cp8_save_candidate_template(run_id: str, run: Dict[str, Any], outputs: Dict[str, Any]) -> Dict[str, Any]:
    """CP8: save a real candidate template based on dev output JSON."""

    if outputs.get("candidate_template_name"):
        return outputs

    dev_text = outputs.get("dev_summary")
    blob = _extract_json_object(dev_text or "")
    if not blob:
        _append_trace(run_id, {"ts_ms": _now_ms(), "type": "candidate_error", "data": {"error": "dev_summary is not valid JSON"}})
        return outputs

    candidate_data = blob.get("candidate_template_data")
    if not isinstance(candidate_data, dict):
        _append_trace(run_id, {"ts_ms": _now_ms(), "type": "candidate_error", "data": {"error": "missing candidate_template_data"}})
        return outputs

    inds = candidate_data.get("indicators") or []
    if not isinstance(inds, list):
        _append_trace(run_id, {"ts_ms": _now_ms(), "type": "candidate_error", "data": {"error": "indicators must be a list"}})
        return outputs

    if len(inds) > 4:
        _append_trace(run_id, {"ts_ms": _now_ms(), "type": "candidate_error", "data": {"error": f"too many indicators: {len(inds)}"}})
        return outputs

    # Validate indicator schema (must match ComboStrategy expectation)
    for idx, ind in enumerate(inds):
        if not isinstance(ind, dict):
            _append_trace(
                run_id,
                {
                    "ts_ms": _now_ms(),
                    "type": "candidate_error",
                    "data": {"error": f"indicator[{idx}] must be an object with type/alias/params"},
                },
            )
            return outputs
        if not isinstance(ind.get("type"), str) or not ind.get("type"):
            _append_trace(run_id, {"ts_ms": _now_ms(), "type": "candidate_error", "data": {"error": f"indicator[{idx}].type missing"}})
            return outputs
        if not isinstance(ind.get("alias"), str) or not ind.get("alias"):
            _append_trace(run_id, {"ts_ms": _now_ms(), "type": "candidate_error", "data": {"error": f"indicator[{idx}].alias missing"}})
            return outputs
        if not isinstance(ind.get("params"), dict):
            _append_trace(run_id, {"ts_ms": _now_ms(), "type": "candidate_error", "data": {"error": f"indicator[{idx}].params must be object"}})
            return outputs

    try:
        from app.services.combo_service import ComboService

        inp = run.get("input") or {}
        backtest = run.get("backtest") or {}
        base_template = str(inp.get("base_template") or backtest.get("template") or "")
        symbol = str(backtest.get("symbol") or inp.get("symbol") or "")
        timeframe = str(backtest.get("timeframe") or inp.get("timeframe") or "")

        combo = ComboService()

        # find next available candidate name
        n = 1
        while True:
            name = _make_candidate_name(run_id=run_id, base_template=base_template, symbol=symbol, timeframe=timeframe, n=n)
            if not combo.get_template_metadata(name):
                break
            n += 1
            if n > 50:
                raise RuntimeError("too many candidates")

        # clone base, then overwrite template_data
        combo.clone_template(template_name=base_template, new_name=name)
        desc = blob.get("description")
        if not isinstance(desc, str):
            desc = f"Lab candidate from {run_id}"

        combo.update_template(template_name=name, description=desc, template_data=candidate_data)

        outputs["candidate_template_name"] = name
        _append_trace(run_id, {"ts_ms": _now_ms(), "type": "candidate_saved", "data": {"template": name}})
        return outputs

    except Exception as e:
        _append_trace(run_id, {"ts_ms": _now_ms(), "type": "candidate_error", "data": {"error": str(e)}})
        return outputs


def _cp10_selection_gate(run: Dict[str, Any]) -> Dict[str, Any]:
    """CP10: deterministic approval gate based on holdout metrics.

    This gate is evaluated before autosave.
    """

    inp = run.get("input") or {}
    constraints = inp.get("constraints") or {}
    max_dd = constraints.get("max_drawdown")
    min_sharpe = constraints.get("min_sharpe")

    backtest = run.get("backtest") or {}
    wf = backtest.get("walk_forward") or {}
    hold = (wf.get("holdout") or {}).get("metrics") or {}

    total_trades = hold.get("total_trades")
    sharpe = hold.get("sharpe_ratio")
    dd = hold.get("max_drawdown")
    # Some parts store pct; accept both
    dd_pct = hold.get("max_drawdown_pct")

    reasons: list[str] = []

    # Minimum trades on holdout (default 10)
    min_holdout_trades = int(constraints.get("min_holdout_trades") or 10)
    if not isinstance(total_trades, (int, float)) or int(total_trades) < min_holdout_trades:
        reasons.append(f"holdout_total_trades<{min_holdout_trades} ({total_trades})")

    if min_sharpe is not None:
        try:
            if sharpe is None or float(sharpe) < float(min_sharpe):
                reasons.append(f"holdout_sharpe<{min_sharpe} ({sharpe})")
        except Exception:
            reasons.append("holdout_sharpe_invalid")

    if max_dd is not None:
        # compare against decimal dd if available else pct
        try:
            if dd is not None:
                if float(dd) > float(max_dd):
                    reasons.append(f"holdout_max_drawdown>{max_dd} ({dd})")
            elif dd_pct is not None:
                if float(dd_pct) / 100.0 > float(max_dd):
                    reasons.append(f"holdout_max_drawdown_pct>{max_dd} ({dd_pct})")
        except Exception:
            reasons.append("holdout_max_drawdown_invalid")

    return {
        "approved": len(reasons) == 0,
        "reasons": reasons,
        "min_holdout_trades": min_holdout_trades,
        "holdout": {"total_trades": total_trades, "sharpe_ratio": sharpe, "max_drawdown": dd, "max_drawdown_pct": dd_pct},
    }


def _metrics_preflight(*, run: Dict[str, Any]) -> Dict[str, Any]:
    """Deterministic preflight for metrics integrity.

    Goal: detect instrumentação/métricas inválidas cedo e evitar gastar tokens no validator.
    """

    backtest = run.get("backtest") or {}
    wf = backtest.get("walk_forward") or {}
    hold = (wf.get("holdout") or {}).get("metrics") or {}

    errors: list[str] = []
    warnings: list[str] = []

    def _finite(x) -> bool:
        try:
            xf = float(x)
            return (xf == xf) and (xf not in (float("inf"), float("-inf")))
        except Exception:
            return False

    sortino = hold.get("sortino_ratio")
    sortino_status = hold.get("sortino_status")
    dd = hold.get("max_drawdown")
    dd_pct = hold.get("max_drawdown_pct")

    # Sortino sanity
    if sortino is not None:
        if not _finite(sortino):
            errors.append("sortino_invalid")
        else:
            try:
                if abs(float(sortino)) > 1e6:
                    errors.append(f"sortino_implausible ({sortino})")
            except Exception:
                errors.append("sortino_invalid")
    else:
        # None is OK when degenerate, but we want an explicit status
        if sortino_status not in ("degenerate", "ok", "invalid"):
            warnings.append("sortino_missing_status")

    # Drawdown sanity
    if dd is not None:
        if not _finite(dd) or float(dd) < 0 or float(dd) > 1.0:
            errors.append(f"max_drawdown_invalid ({dd})")
    elif dd_pct is not None:
        if not _finite(dd_pct) or float(dd_pct) < 0 or float(dd_pct) > 100.0:
            errors.append(f"max_drawdown_pct_invalid ({dd_pct})")
    else:
        warnings.append("max_drawdown_missing")

    # Trades count sanity
    tt = hold.get("total_trades")
    if tt is None:
        warnings.append("holdout_total_trades_missing")

    ok = len(errors) == 0
    return {
        "ok": ok,
        "errors": errors,
        "warnings": warnings,
        "metrics_checks": {
            "sortino_present": sortino is not None,
            "sortino_status": sortino_status,
            "max_drawdown": dd,
            "max_drawdown_pct": dd_pct,
            "total_trades": tt,
        },
    }


def _gate_decision(*, outputs: Dict[str, Any], selection: Dict[str, Any], preflight: Dict[str, Any]) -> Dict[str, Any]:
    """Consolidate final verdict into a single, consistent decision object."""

    verdict = _verdict_label(outputs.get("validator_verdict"))

    reasons: list[str] = []
    if isinstance(preflight, dict) and preflight.get("ok") is False:
        reasons.append("metrics_preflight_failed")

    if isinstance(selection, dict) and not selection.get("approved"):
        reasons.extend(selection.get("reasons") or [])

    if verdict in ("unknown", "metrics_invalid"):
        if verdict == "metrics_invalid":
            reasons.append("validator_metrics_invalid")
        else:
            reasons.append("validator_unknown")

    approved = (verdict == "approved") and bool(selection.get("approved")) and not (isinstance(preflight, dict) and preflight.get("ok") is False)

    final = {
        "verdict": "approved" if approved else ("metrics_invalid" if (verdict == "metrics_invalid" or (isinstance(preflight, dict) and preflight.get("ok") is False)) else "rejected"),
        "approved": bool(approved),
        "reasons": reasons,
        "validator_verdict": verdict,
        "selection_gate": selection,
        "metrics_preflight": preflight,
    }
    return final


def _cp5_autosave_if_approved(run_id: str, run: Dict[str, Any], outputs: Dict[str, Any]) -> Dict[str, Any]:
    """CP5/CP10: autosave (template + favorite) only when validator says approved AND selection gate passes."""

    # Prefer consolidated gate decision when available
    gate = outputs.get("gate_decision") if isinstance(outputs, dict) else None
    if isinstance(gate, dict):
        if not gate.get("approved"):
            _append_trace(run_id, {"ts_ms": _now_ms(), "type": "autosave_blocked", "data": {"reason": "gate_decision", "gate_decision": gate}})
            return outputs
        selection = (gate.get("selection_gate") or {}) if isinstance(gate.get("selection_gate"), dict) else (outputs.get("selection") or {})
    else:
        verdict = _verdict_label(outputs.get("validator_verdict"))
        selection = outputs.get("selection") or {}
        if verdict != "approved":
            return outputs
        if not selection or not selection.get("approved"):
            _append_trace(run_id, {"ts_ms": _now_ms(), "type": "autosave_blocked", "data": {"reason": "selection_gate", "selection": selection}})
            return outputs

    try:
        from app.services.combo_service import ComboService
        from app.database import SessionLocal
        from app.models import FavoriteStrategy

        inp = run.get("input") or {}
        backtest = run.get("backtest") or {}
        base_template = str(inp.get("base_template") or backtest.get("template") or "")
        # CP10: if we have a candidate template, autosave should be based on it.
        candidate_template = outputs.get("candidate_template_name")
        template_to_save = str(candidate_template or base_template)

        symbol = str(backtest.get("symbol") or inp.get("symbol") or "")
        timeframe = str(backtest.get("timeframe") or inp.get("timeframe") or "")

        combo = ComboService()

        # Guardrail: max 4 indicators
        base_meta = combo.get_template_metadata(template_to_save)
        inds = (base_meta or {}).get("indicators") or []
        if len(inds) > 4:
            raise RuntimeError(f"template has too many indicators (max 4): {len(inds)}")

        new_name = _make_autosave_name(run_id=run_id, base_template=template_to_save, symbol=symbol, timeframe=timeframe)
        new_name = _ensure_unique_template_name(combo, new_name)

        # Clone template
        cloned = combo.clone_template(template_name=template_to_save, new_name=new_name)
        if not cloned:
            raise RuntimeError("failed to clone template")

        # Create favorite pointing to the cloned template
        params = backtest.get("params") or {}
        metrics = backtest.get("metrics")
        since = backtest.get("since")
        until = backtest.get("until")

        period_type = "2y" if str(timeframe).endswith("d") else "6m"

        fav_name = f"{new_name} - {symbol} {timeframe} (lab)"
        notes = f"lab_run_id={run_id}; verdict=approved"

        db = SessionLocal()
        try:
            fav = FavoriteStrategy(
                name=fav_name,
                symbol=symbol,
                timeframe=timeframe,
                strategy_name=new_name,
                parameters=params,
                metrics=metrics,
                notes=notes,
                tier=None,
                start_date=since,
                end_date=until,
                period_type=period_type,
            )
            db.add(fav)
            db.commit()
            db.refresh(fav)
            outputs["saved_template_name"] = new_name
            outputs["saved_favorite_id"] = int(fav.id)
        finally:
            db.close()

        _append_trace(run_id, {"ts_ms": _now_ms(), "type": "autosave_done", "data": {"template": new_name, "favorite_id": outputs.get("saved_favorite_id")}})
        return outputs

    except Exception as e:
        _append_trace(run_id, {"ts_ms": _now_ms(), "type": "autosave_error", "data": {"error": str(e)}})
        return outputs


def _cp4_run_personas_if_possible(run_id: str) -> None:
    """Run two-phase Lab graph, persisting upstream contract + phase."""

    run = _load_run_json(run_id)
    budget = run.get("budget") or {}
    outputs = run.get("outputs") or {}
    upstream_contract = run.get("upstream_contract") or {}
    phase = str(run.get("phase") or "upstream")

    # If already waiting budget confirmation, do nothing.
    if run.get("needs_user_confirm"):
        return

    if not _budget_ok(budget):
        _update_run_json(
            run_id,
            {
                "status": "needs_user_confirm",
                "step": "budget",
                "needs_user_confirm": True,
                "phase": phase,
                "upstream_contract": upstream_contract,
            },
        )
        _append_trace(run_id, {"ts_ms": _now_ms(), "type": "budget_limit", "data": budget})
        return

    session_key = run.get("session_key") or f"lab-{run_id}"
    inp = run.get("input") or {}
    thinking = inp.get("thinking") or "low"
    backtest = run.get("backtest") or {}
    objective = inp.get("objective")

    wf = backtest.get("walk_forward") or {}
    context = {
        "input": inp,
        "objective": objective,
        "symbol": (backtest.get("symbol") or inp.get("symbol")),
        "timeframe": (backtest.get("timeframe") or inp.get("timeframe")),
        "template": backtest.get("template"),
        "walk_forward": {
            "split": (wf.get("split") or "70/30"),
            "metrics_all": (backtest.get("metrics") or {}),
            "metrics_in_sample": ((wf.get("in_sample") or {}).get("metrics") or {}),
            "metrics_holdout": ((wf.get("holdout") or {}).get("metrics") or {}),
        },
        "metrics_preflight": _metrics_preflight(run=run),
    }

    try:
        _append_trace(run_id, {"ts_ms": _now_ms(), "type": "metrics_preflight", "data": context.get("metrics_preflight") or {}})
    except Exception:
        pass

    graph_status = ""
    try:
        from app.services.lab_graph import LabGraphDeps, build_cp7_graph

        graph = build_cp7_graph()
        deps = LabGraphDeps(
            persona_call=_persona_call_sync,
            append_trace=_append_trace,
            now_ms=_now_ms,
            inc_budget=_inc_budget,
            budget_ok=_budget_ok,
        )

        state_in = {
            "run_id": run_id,
            "session_key": session_key,
            "thinking": thinking,
            "context": context,
            "deps": deps,
            "budget": budget,
            "outputs": outputs,
            "upstream_contract": upstream_contract,
            "phase": phase,
        }

        state_out = graph.invoke(state_in)
        budget = state_out.get("budget") or budget
        outputs = state_out.get("outputs") or outputs
        upstream_contract = state_out.get("upstream_contract") or upstream_contract
        phase = str(state_out.get("phase") or phase)
        graph_status = str(state_out.get("status") or "").strip()

        _update_run_json(
            run_id,
            {
                "budget": budget,
                "outputs": outputs,
                "upstream_contract": upstream_contract,
                "phase": phase,
            },
        )
    except Exception as e:
        _append_trace(run_id, {"ts_ms": _now_ms(), "type": "langgraph_error", "data": {"error": str(e)}})

    if isinstance(upstream_contract, dict) and not bool(upstream_contract.get("approved")):
        _update_run_json(
            run_id,
            {
                "status": "needs_user_input",
                "step": "upstream",
                "phase": "upstream",
                "upstream_contract": upstream_contract,
                "budget": budget,
                "outputs": outputs,
                "session_key": session_key,
                "needs_user_confirm": False,
            },
        )
        return

    # CP8: persist candidate template after Dev output exists
    if outputs.get("coordinator_summary") and outputs.get("dev_summary"):
        outputs = _cp8_save_candidate_template(run_id, _load_run_json(run_id) or run, outputs)

    # CP10: deterministic selection gate (holdout-based)
    if outputs.get("coordinator_summary") and outputs.get("validator_verdict"):
        sel = _cp10_selection_gate(_load_run_json(run_id) or run)
        outputs["selection"] = sel
        _append_trace(run_id, {"ts_ms": _now_ms(), "type": "selection_gate", "data": sel})

        pre = (context.get("metrics_preflight") or {}) if isinstance(context, dict) else {}
        gate = _gate_decision(outputs=outputs, selection=sel, preflight=pre)
        outputs["gate_decision"] = gate
        _append_trace(run_id, {"ts_ms": _now_ms(), "type": "gate_decision", "data": gate})
        _update_run_json(run_id, {"outputs": outputs})

    # CP5/CP10: autosave only if approved
    if outputs.get("coordinator_summary") and outputs.get("dev_summary") and outputs.get("validator_verdict"):
        outputs = _cp5_autosave_if_approved(run_id, _load_run_json(run_id) or run, outputs)

    needs_confirm = not _budget_ok(budget) and graph_status not in ("done", "failed")
    patch: Dict[str, Any] = {
        "budget": budget,
        "outputs": outputs,
        "session_key": session_key,
        "needs_user_confirm": bool(needs_confirm),
        "phase": phase,
        "upstream_contract": upstream_contract,
    }

    if graph_status == "done":
        patch.update({"status": "done", "step": "done", "needs_user_confirm": False, "phase": "done"})
    elif graph_status == "failed":
        patch.update({"status": "failed", "step": "tests", "needs_user_confirm": False, "phase": "done"})
    elif needs_confirm:
        patch.update({"status": "needs_user_confirm", "step": "budget"})
        _append_trace(run_id, {"ts_ms": _now_ms(), "type": "budget_limit", "data": budget})
    else:
        patch.update({"status": "running", "step": "implementation", "phase": phase or "implementation"})

    _update_run_json(run_id, patch)


def _choose_seed_template(*, combo: Any, preferred: Optional[str] = None) -> str:
    """Pick a seed template when the UI is in autonomous mode."""

    if isinstance(preferred, str) and preferred.strip():
        return preferred.strip()

    try:
        templates = combo.list_templates() or {}
        # Prefer prebuilt/examples first
        candidates = []
        for k in ("prebuilt", "examples", "custom"):
            for t in (templates.get(k) or []):
                name = (t or {}).get("name")
                if not name:
                    continue
                # avoid known short-only seed
                if name == "short_ema200_pullback":
                    continue
                candidates.append(str(name))
        if candidates:
            # deterministic default: pick first alphabetical
            return sorted(set(candidates))[0]
    except Exception:
        pass

    return "multi_ma_crossover"


def _run_lab_autonomous(run_id: str, req_dict: Dict[str, Any]) -> None:
    """Autonomous Lab loop.

    Implements:
    1) Backtest candidate inside the same run (not just propose it).
    2) Iterate multiple attempts (bounded) until an interesting result or limits hit.
    3) Quick parameter tuning (tool-based) on the candidate before re-testing.

    Uses the CP9 job pipeline (JobManager state) for each backtest.
    """

    import copy
    import itertools
    import random

    from app.services.job_manager import JobManager
    from app.services.combo_service import ComboService
    from src.data.incremental_loader import IncrementalLoader
    from app.services.combo_optimizer import _run_backtest_logic
    from app.services.lab_graph import build_upstream_contract

    run = _load_run_json(run_id) or {}
    inp = run.get("input") or {}
    upstream_contract = run.get("upstream_contract") or {}

    if not bool(upstream_contract.get("approved")):
        upstream_contract = build_upstream_contract(
            context={
                "input": req_dict,
                "symbol": req_dict.get("symbol"),
                "timeframe": req_dict.get("timeframe"),
                "objective": req_dict.get("objective"),
            }
        )
        _append_trace(run_id, {"ts_ms": _now_ms(), "type": "upstream_started", "data": {}})
        _append_trace(
            run_id,
            {
                "ts_ms": _now_ms(),
                "type": "upstream_done",
                "data": {
                    "approved": bool(upstream_contract.get("approved")),
                    "missing": upstream_contract.get("missing") or [],
                    "question": upstream_contract.get("question") or "",
                },
            },
        )
        _append_trace(
            run_id,
            {
                "ts_ms": _now_ms(),
                "type": "upstream_contract_updated",
                "data": _contract_trace_data(upstream_contract),
            },
        )
        _update_run_json(run_id, {"phase": "upstream", "upstream_contract": upstream_contract, "status": "running", "step": "upstream"})
        if not bool(upstream_contract.get("approved")):
            _append_trace(
                run_id,
                {
                    "ts_ms": _now_ms(),
                    "type": "final_decision",
                    "data": {"status": "needs_user_input", "reason": "upstream_not_approved", "missing": upstream_contract.get("missing") or []},
                },
            )
            _update_run_json(run_id, {"status": "needs_user_input", "step": "upstream", "phase": "upstream", "upstream_contract": upstream_contract})
            return
        _append_trace(
            run_id,
            {
                "ts_ms": _now_ms(),
                "type": "upstream_approved",
                "data": {"inputs": dict(upstream_contract.get("inputs") or {})},
            },
        )

    _update_run_json(run_id, {"phase": "execution", "upstream_contract": upstream_contract, "status": "running", "step": "execution"})

    inputs = upstream_contract.get("inputs") or {}
    symbol = str(inputs.get("symbol") or "").strip()
    timeframe = str(inputs.get("timeframe") or "").strip()
    deep_backtest = bool(req_dict.get("deep_backtest", True))
    direction = str(req_dict.get("direction") or "long")
    if direction not in ("long", "short"):
        direction = "long"
    full_history = bool(inp.get("full_history", True))
    since_str = str(inp.get("since") or "").strip() or _cp3_default_since(timeframe, full_history=full_history)
    until_str = str(inp.get("until") or "").strip() or None

    max_iterations = int(inp.get("max_iterations") or 3)
    max_iterations = max(1, min(10, max_iterations))

    jm = JobManager()
    combo = ComboService()

    # Load candles ONCE for the run (full history by default)
    loader = IncrementalLoader()
    df = loader.fetch_data(symbol=symbol, timeframe=timeframe, since_str=since_str, until_str=until_str)
    if getattr(df, "empty", False) or len(df) == 0:
        _update_run_json(run_id, {"status": "error", "step": "error", "error": "no candles loaded"})
        return
    try:
        df = df.sort_index()
    except Exception:
        pass

    n = len(df)
    split_idx = int(n * 0.7)
    split_idx = max(1, min(n - 1, split_idx))
    df_is = df.iloc[:split_idx]
    df_oos = df.iloc[split_idx:]

    def _df_bounds(dfx):
        if len(dfx) == 0:
            return None, None
        try:
            s = dfx.index[0]
            e = dfx.index[-1]
            return (s.isoformat() if hasattr(s, "isoformat") else str(s)), (e.isoformat() if hasattr(e, "isoformat") else str(e))
        except Exception:
            return None, None

    is_since, is_until = _df_bounds(df_is)
    oos_since, oos_until = _df_bounds(df_oos)

    def _context_for_backtest(bt: Dict[str, Any]) -> Dict[str, Any]:
        wf = (bt.get("walk_forward") or {})
        return {
            "input": inp,
            "objective": (inp.get("objective") or None),
            "symbol": bt.get("symbol"),
            "timeframe": bt.get("timeframe"),
            "template": bt.get("template"),
            "walk_forward": {
                "split": (wf.get("split") or "70/30"),
                "metrics_all": (bt.get("metrics") or {}),
                "metrics_in_sample": ((wf.get("in_sample") or {}).get("metrics") or {}),
                "metrics_holdout": ((wf.get("holdout") or {}).get("metrics") or {}),
            },
        }

    def _run_backtest_job(*, template_name: str, label: str, iteration: int) -> Dict[str, Any]:
        meta = combo.get_template_metadata(template_name)
        if not meta:
            raise RuntimeError(f"template not found: {template_name}")

        template_data = {
            "indicators": meta.get("indicators"),
            "entry_logic": meta.get("entry_logic"),
            "exit_logic": meta.get("exit_logic"),
            "stop_loss": meta.get("stop_loss"),
        }

        job_id = jm.create_job({"kind": "lab_backtest", "run_id": run_id, "iteration": iteration, "label": label, "template": template_name})
        _update_run_json(
            run_id,
            {
                "status": "running",
                "step": "backtest_job",
                "backtest_job": {"job_id": job_id, "status": "RUNNING", "progress": {"step": "init", "pct": 0}},
            },
        )
        _append_trace(run_id, {"ts_ms": _now_ms(), "type": "job_created", "data": {"job_id": job_id, "label": label, "template": template_name, "iteration": iteration}})

        # ALL / IS / HOLDOUT metrics
        state = jm.load_state(job_id) or {}
        state.update({"status": "RUNNING", "progress": {"step": "backtest_all", "pct": 35}})
        jm.save_state(job_id, state)
        metrics_all, full_params = _run_backtest_logic(
            template_data=template_data,
            params={"direction": direction},
            df=df,
            deep_backtest=deep_backtest,
            symbol=symbol,
            since_str=since_str,
            until_str=until_str,
        )

        state = jm.load_state(job_id) or {}
        state.update({"status": "RUNNING", "progress": {"step": "backtest_in_sample", "pct": 60}})
        jm.save_state(job_id, state)
        metrics_is, _ = _run_backtest_logic(
            template_data=template_data,
            params={"direction": direction},
            df=df_is,
            deep_backtest=deep_backtest,
            symbol=symbol,
            since_str=is_since or since_str,
            until_str=is_until,
        )

        state = jm.load_state(job_id) or {}
        state.update({"status": "RUNNING", "progress": {"step": "backtest_holdout", "pct": 85}})
        jm.save_state(job_id, state)
        metrics_oos, _ = _run_backtest_logic(
            template_data=template_data,
            params={"direction": direction},
            df=df_oos,
            deep_backtest=deep_backtest,
            symbol=symbol,
            since_str=oos_since or since_str,
            until_str=oos_until,
        )

        out = {
            "symbol": symbol,
            "timeframe": timeframe,
            "template": template_name,
            "since": since_str,
            "until": until_str,
            "deep_backtest": deep_backtest,
            "direction": direction,
            "params": full_params,
            "walk_forward": {
                "split": "70/30",
                "split_idx": split_idx,
                "candles_all": n,
                "candles_in_sample": len(df_is),
                "candles_holdout": len(df_oos),
                "in_sample": {"since": is_since, "until": is_until, "metrics": metrics_is},
                "holdout": {"since": oos_since, "until": oos_until, "metrics": metrics_oos},
            },
            "metrics": metrics_all,
            "candles": n,
            "label": label,
            "iteration": iteration,
        }

        _append_trace(
            run_id,
            {
                "ts_ms": _now_ms(),
                "type": "backtest_done",
                "data": {"label": label, "template": template_name, "metrics_all": metrics_all, "metrics_in_sample": metrics_is, "metrics_holdout": metrics_oos},
            },
        )

        state = jm.load_state(job_id) or {}
        state.update({"status": "COMPLETED", "progress": {"step": "done", "pct": 100}, "final_results": out})
        jm.save_state(job_id, state)

        _update_run_json(
            run_id,
            {
                "status": "running",
                "step": "personas",
                "backtest": out,
                "backtest_job": {"job_id": job_id, "status": "COMPLETED", "progress": {"step": "done", "pct": 100}},
            },
        )
        return out

    def _quick_tune_candidate_params(template_name: str, iteration: int) -> None:
        """Lightweight parameter tuning on IN-SAMPLE using tool backtests.

        We keep it intentionally small/fast: sample a handful of variations.
        """

        try:
            meta = combo.get_template_metadata(template_name)
            if not meta:
                return
            inds = meta.get("indicators") or []
            if not isinstance(inds, list) or not inds:
                return

            # Build candidate value options for numeric params
            per_ind_options: list[list[Dict[str, Any]]] = []
            for ind in inds:
                if not isinstance(ind, dict):
                    continue
                params0 = ind.get("params") or {}
                if not isinstance(params0, dict):
                    params0 = {}

                # For common length/period keys, try +/- 20% and +/- 5
                options = []
                for delta_mul in (0.8, 1.0, 1.2):
                    ind2 = copy.deepcopy(ind)
                    for k in list(params0.keys()):
                        v = params0.get(k)
                        if isinstance(v, (int, float)) and k in ("length", "period"):
                            nv = int(max(2, round(float(v) * delta_mul)))
                            ind2.setdefault("params", {})[k] = nv
                    options.append(ind2)
                per_ind_options.append(options[:3])

            if not per_ind_options:
                return

            # Sample up to 12 combinations
            combos = list(itertools.product(*per_ind_options))
            random.shuffle(combos)
            combos = combos[:12]

            base_template_data = {
                "indicators": meta.get("indicators"),
                "entry_logic": meta.get("entry_logic"),
                "exit_logic": meta.get("exit_logic"),
                "stop_loss": meta.get("stop_loss"),
            }

            best = None
            best_metrics = None

            for c in combos:
                td = copy.deepcopy(base_template_data)
                td["indicators"] = list(c)
                # Tune stop_loss lightly
                sl = td.get("stop_loss")
                if isinstance(sl, dict):
                    sl = sl.get("default")
                if not isinstance(sl, (int, float)):
                    sl = 0.03
                td["stop_loss"] = float(min(0.08, max(0.005, sl)))

                metrics, _ = _run_backtest_logic(
                    template_data=td,
                    params={"direction": direction},
                    df=df_is,
                    deep_backtest=False,
                    symbol=symbol,
                    since_str=is_since or since_str,
                    until_str=is_until,
                )
                sharpe = (metrics or {}).get("sharpe_ratio")
                if best is None or (isinstance(sharpe, (int, float)) and isinstance((best_metrics or {}).get("sharpe_ratio"), (int, float)) and sharpe > (best_metrics or {}).get("sharpe_ratio")):
                    best = td
                    best_metrics = metrics

            if best is not None and best_metrics is not None:
                combo.update_template(template_name=template_name, template_data=best)
                _append_trace(run_id, {"ts_ms": _now_ms(), "type": "param_tuned", "data": {"template": template_name, "iteration": iteration, "best_in_sample": best_metrics}})
        except Exception as e:
            _append_trace(run_id, {"ts_ms": _now_ms(), "type": "param_tune_error", "data": {"template": template_name, "iteration": iteration, "error": str(e)}})

    # Loop: propose → backtest candidate → validate → repeat
    current_template = _choose_seed_template(combo=combo, preferred=req_dict.get("base_template"))
    _append_trace(run_id, {"ts_ms": _now_ms(), "type": "seed_chosen", "data": {"template": current_template}})

    for it in range(1, max_iterations + 1):
        _append_trace(run_id, {"ts_ms": _now_ms(), "type": "iteration_started", "data": {"iteration": it, "template": current_template}})

        # Backtest current template
        bt = _run_backtest_job(template_name=current_template, label=f"iter{it}_current", iteration=it)

        # Run CP7 personas (coordinator+dev+validator) on current results to get a candidate
        try:
            from app.services.lab_graph import LabGraphDeps, build_cp7_graph

            run = _load_run_json(run_id) or {}
            budget = run.get("budget") or {}
            outputs = run.get("outputs") or {}

            deps = LabGraphDeps(
                persona_call=_persona_call_sync,
                append_trace=_append_trace,
                now_ms=_now_ms,
                inc_budget=_inc_budget,
                budget_ok=_budget_ok,
            )

            graph = build_cp7_graph()
            state = {
                "run_id": run_id,
                "session_key": run.get("session_key") or f"lab-{run_id}",
                "thinking": inp.get("thinking") or "low",
                "context": _context_for_backtest(bt),
                "deps": deps,
                "budget": budget,
                "outputs": outputs,
                "upstream_contract": run.get("upstream_contract") or {},
                "phase": run.get("phase") or "upstream",
            }
            final = graph.invoke(state)
            budget = final.get("budget") or budget
            outputs = final.get("outputs") or outputs
            phase = final.get("phase") or run.get("phase") or "upstream"
            upstream_contract = final.get("upstream_contract") or run.get("upstream_contract") or {}
            graph_status = str(final.get("status") or "").strip()

            _update_run_json(
                run_id,
                {
                    "budget": budget,
                    "outputs": outputs,
                    "phase": phase,
                    "upstream_contract": upstream_contract,
                },
            )

            if isinstance(upstream_contract, dict) and not bool(upstream_contract.get("approved")):
                _update_run_json(run_id, {"status": "needs_user_input", "step": "upstream", "phase": "upstream"})
                return

            if graph_status == "failed":
                _update_run_json(run_id, {"status": "failed", "step": "tests", "phase": "done"})
                return

            if not _budget_ok(budget):
                _update_run_json(run_id, {"status": "needs_user_confirm", "step": "budget", "needs_user_confirm": True})
                return

            # CP8 save candidate
            outputs = _cp8_save_candidate_template(run_id, _load_run_json(run_id) or {}, outputs)
            _update_run_json(run_id, {"outputs": outputs})

        except Exception as e:
            _append_trace(run_id, {"ts_ms": _now_ms(), "type": "personas_error", "data": {"error": str(e), "iteration": it}})
            _update_run_json(run_id, {"status": "error", "step": "error", "error": str(e)})
            return

        run = _load_run_json(run_id) or {}
        outputs = run.get("outputs") or {}
        cand = outputs.get("candidate_template_name")
        if not cand:
            _update_run_json(run_id, {"status": "error", "step": "error", "error": "candidate not created"})
            return

        # Tool-based quick parameter tuning on candidate (IN-SAMPLE)
        _quick_tune_candidate_params(str(cand), it)

        # Backtest candidate and overwrite run.backtest
        bt2 = _run_backtest_job(template_name=str(cand), label=f"iter{it}_candidate", iteration=it)

        # Re-run validator on the candidate results (so verdict matches the tested candidate)
        try:
            run = _load_run_json(run_id) or {}
            budget = run.get("budget") or {}
            outputs = run.get("outputs") or {}
            if _budget_ok(budget):
                # Deterministic preflight: block validator call if metrics are invalid
                pre = _metrics_preflight(run=run)
                _append_trace(run_id, {"ts_ms": _now_ms(), "type": "metrics_preflight", "data": pre})
                if pre.get("ok") is False:
                    outputs["validator_verdict"] = json.dumps(
                        {
                            "verdict": "metrics_invalid",
                            "reasons": ["metrics_preflight_failed"],
                            "required_fixes": (pre.get("errors") or [])[:8],
                            "notes": "Preflight determinístico falhou; bloqueando validator LLM.",
                        },
                        ensure_ascii=False,
                    )
                    _update_run_json(run_id, {"budget": budget, "outputs": outputs})
                else:
                    msg = "Contexto do run (JSON):\n" + json.dumps(_context_for_backtest(bt2), ensure_ascii=False, indent=2) + "\n"
                    r = _persona_call_sync(
                        run_id=run_id,
                        session_key=run.get("session_key") or f"lab-{run_id}",
                        persona="validator",
                        system_prompt=(
                            "Papel: Validator (Trader + Product Owner). "
                            "Você é o gate final de decisão do Strategy Lab. "
                            "Responda EXCLUSIVAMENTE com JSON válido (sem markdown/texto fora do JSON) no formato: "
                            "{\"verdict\":\"approved\"|\"rejected\"|\"metrics_invalid\",\"reasons\":[...],\"required_fixes\":[...],\"notes\":\"...\"}. "
                            "Baseie o veredito principalmente no HOLDOUT (30% mais recente). "
                            "Se houver 0 trades, colunas inválidas ou métricas suspeitas/degeneradas, use verdict=metrics_invalid ou rejected (conforme o caso). "
                            "Idioma: pt-BR. Seja curto e decisório."
                        ),
                        message=msg,
                        thinking=inp.get("thinking") or "low",
                    )
                    outputs["validator_verdict"] = r.get("text")
                    budget = _inc_budget(budget, turns=1, tokens=r.get("tokens", 0) or 0)
                    _update_run_json(run_id, {"budget": budget, "outputs": outputs})
        except Exception as e:
            _append_trace(run_id, {"ts_ms": _now_ms(), "type": "validator_error", "data": {"error": str(e), "iteration": it}})

        # Gate + autosave (based on candidate backtest)
        run = _load_run_json(run_id) or {}
        outputs = run.get("outputs") or {}
        sel = _cp10_selection_gate(run)
        outputs["selection"] = sel
        _append_trace(run_id, {"ts_ms": _now_ms(), "type": "selection_gate", "data": sel})

        # Consolidated gate decision
        pre = _metrics_preflight(run=run)
        gate = _gate_decision(outputs=outputs, selection=sel, preflight=pre)
        outputs["gate_decision"] = gate
        _append_trace(run_id, {"ts_ms": _now_ms(), "type": "gate_decision", "data": gate})

        _update_run_json(run_id, {"outputs": outputs})

        outputs = _cp5_autosave_if_approved(run_id, run, outputs)
        _update_run_json(run_id, {"outputs": outputs})

        if outputs.get("saved_favorite_id"):
            _update_run_json(run_id, {"status": "done", "step": "done", "phase": "done", "needs_user_confirm": False})
            _append_trace(run_id, {"ts_ms": _now_ms(), "type": "iteration_done", "data": {"iteration": it, "result": "approved_and_saved"}})
            return

        gd = (outputs.get("gate_decision") or {}) if isinstance(outputs, dict) else {}
        res = str(gd.get("verdict") or "rejected")
        _append_trace(run_id, {"ts_ms": _now_ms(), "type": "iteration_done", "data": {"iteration": it, "result": res}})
        current_template = str(cand)

    # If we exit the loop, we're done (rejected after max iterations)
    _update_run_json(run_id, {"status": "done", "step": "done", "phase": "done"})


@router.post("/run", response_model=Union[LabRunCreateResponse, LabRunNeedsUserInputResponse])
async def create_run(
    req: LabRunCreateRequest,
    background_tasks: BackgroundTasks,
) -> Union[LabRunCreateResponse, LabRunNeedsUserInputResponse]:
    run_id = uuid.uuid4().hex
    now = _now_ms()
    # Trace provider selection (dev-only).
    # If LangSmith tracing is enabled in the environment, prefer it.
    langsmith_on = str(os.environ.get("LANGSMITH_TRACING") or "").lower() in ("1", "true", "yes", "on")
    trace_provider = "langsmith" if (bool(req.debug_trace) and langsmith_on) else ("langgraph_studio" if bool(req.debug_trace) else "none")
    trace_enabled = bool(req.debug_trace)
    trace_thread_id = f"lab-{run_id}"  # stable correlation key for dev tools
    trace_id = run_id

    # Optional: if configured, return a URL that the frontend can open.
    # For Studio this is usually local/dev-only; for hosted tracing (LangSmith)
    # this could be a real URL.
    trace_public_base = (os.environ.get("LAB_TRACE_PUBLIC_URL") or os.environ.get("TRACE_PUBLIC_URL") or "").strip()

    def _make_trace_url(base: str, thread_id: str) -> str:
        base = (base or "").strip()
        if not base:
            return ""
        # If base already has a query string, append as a query param so we don't
        # break the URL structure.
        if "?" in base:
            sep = "&" if not base.endswith("?") else ""
            return f"{base}{sep}q={thread_id}"
        return base.rstrip("/") + "/" + thread_id

    trace_url = _make_trace_url(trace_public_base, trace_thread_id) if (trace_public_base and trace_enabled) else None
    run_input = req.model_dump()
    upstream_contract = _build_upstream_contract_from_input(run_input)
    initial_status = "ready_for_execution" if bool(upstream_contract.get("approved")) else "needs_user_input"
    initial_question = _next_trader_prompt(upstream_contract)
    initial_strategy_draft = None
    initial_ready_for_review = False

    trader_turn = None
    if not bool(upstream_contract.get("approved")):
        trader_turn = await _try_trader_upstream_turn(
            run_id=run_id,
            session_key=trace_thread_id,
            thinking=str(run_input.get("thinking") or "low"),
            user_message=str(run_input.get("objective") or ""),
            contract=upstream_contract,
            upstream_messages=[],
        )
        initial_question = str((trader_turn or {}).get("reply") or "").strip() or initial_question
        upstream_contract["question"] = initial_question
    else:
        # If already approved at creation time, Trader may still provide a draft for review.
        trader_turn = await _try_trader_upstream_turn(
            run_id=run_id,
            session_key=trace_thread_id,
            thinking=str(run_input.get("thinking") or "low"),
            user_message=str(run_input.get("objective") or ""),
            contract=upstream_contract,
            upstream_messages=[],
        )
        initial_ready_for_review = bool((trader_turn or {}).get("ready_for_user_review"))
        sd = (trader_turn or {}).get("strategy_draft")
        if isinstance(sd, dict) and bool(sd):
            initial_strategy_draft = sd
        if initial_ready_for_review:
            initial_status = "ready_for_review"

    payload = {
        "run_id": run_id,
        "status": initial_status,
        "step": "upstream",
        "phase": "upstream",
        "created_at_ms": now,
        "updated_at_ms": now,
        "input": run_input,
        "upstream_contract": upstream_contract,
        "upstream": {
            "messages": (
                [{"role": "trader", "text": initial_question, "ts_ms": now}]
                if not bool(upstream_contract.get("approved"))
                else []
            ),
            "pending_question": (initial_question if not bool(upstream_contract.get("approved")) else ""),
            "strategy_draft": initial_strategy_draft,
            "ready_for_user_review": initial_ready_for_review,
            "user_approved": False,
            "user_feedback": "",
        },
        "trace": [],
        "trace_meta": {
            "enabled": trace_enabled,
            "provider": trace_provider,
            "thread_id": trace_thread_id,
            "trace_id": trace_id,
            "trace_url": trace_url,
        },
        "session_key": trace_thread_id,
        "budget": {
            "turns_used": 0,
            "turns_max": 200,
            "tokens_total": 0,
            "tokens_max": 1000000,
            "on_limit": "ask_user",
            "continue_turns": 3,
            "continue_tokens": 15000,
        },
        "outputs": {
            "coordinator_summary": None,
            "dev_summary": None,
            "validator_verdict": None,
            "tests_done": None,
            "final_decision": None,
            "selection": None,
            "candidate_template_name": None,
            "saved_template_name": None,
            "saved_favorite_id": None,
        },
        "backtest_job": None,
        "needs_user_confirm": False,
    }

    try:
        _run_path(run_id).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        _append_trace(
            run_id,
            {
                "ts_ms": now,
                "type": "upstream_contract_updated",
                "data": _contract_trace_data(upstream_contract),
            },
        )
        if bool(upstream_contract.get("approved")):
            _append_trace(
                run_id,
                {
                    "ts_ms": now,
                    "type": "upstream_approved",
                    "data": {"inputs": dict(upstream_contract.get("inputs") or {})},
                },
            )
        else:
            _append_trace(
                run_id,
                {
                    "ts_ms": now,
                    "type": "upstream_message",
                    "data": {"role": "trader", "text": initial_question[:2000]},
                },
            )
        _append_trace(
            run_id,
            {
                "ts_ms": now,
                "type": "run_created",
                "data": {"input": run_input},
            },
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"failed to persist run: {e}")

    return LabRunCreateResponse(
        run_id=run_id,
        status=initial_status,
        trace={
            "viewer_url": f"http://31.97.92.212:5173/lab/runs/{run_id}",
            "api_url": f"/api/lab/runs/{run_id}",
            "enabled": trace_enabled,
            "provider": trace_provider,
            "thread_id": trace_thread_id,
            "trace_id": trace_id,
            "trace_url": trace_url,
        },
    )


@router.get("/runs/{run_id}", response_model=LabRunStatusResponse)
async def get_run(run_id: str) -> LabRunStatusResponse:
    p = _run_path(run_id)
    if not p.exists():
        raise HTTPException(status_code=404, detail="run not found")

    data = _load_run_json(run_id)
    if not data:
        raise HTTPException(status_code=500, detail="failed to read run")

    trace_events = _read_trace_tail(run_id, limit=200)

    trace_meta = data.get("trace_meta") or {}
    enabled = bool(trace_meta.get("enabled"))
    provider = str(trace_meta.get("provider") or ("langgraph_studio" if enabled else "none"))
    thread_id = trace_meta.get("thread_id")
    trace_id = trace_meta.get("trace_id")
    trace_url = trace_meta.get("trace_url")

    return LabRunStatusResponse(
        run_id=data.get("run_id") or run_id,
        status=data.get("status") or "unknown",
        step=data.get("step"),
        created_at_ms=int(data.get("created_at_ms") or 0),
        updated_at_ms=int(data.get("updated_at_ms") or 0),
        trace={
            "viewer_url": f"http://31.97.92.212:5173/lab/runs/{run_id}",
            "api_url": f"/api/lab/runs/{run_id}",
            "enabled": enabled,
            "provider": provider,
            "thread_id": thread_id,
            "trace_id": trace_id,
            "trace_url": trace_url,
        },
        trace_events=trace_events,
        events=trace_events,
        budget=data.get("budget") or {},
        outputs=data.get("outputs") or {},
        backtest_job=data.get("backtest_job"),
        backtest=data.get("backtest"),
        needs_user_confirm=bool(data.get("needs_user_confirm")),
        phase=data.get("phase"),
        upstream_contract=data.get("upstream_contract"),
        upstream=data.get("upstream") or {"messages": [], "pending_question": ""},
    )


@router.get("/jobs/{job_id}")
async def get_job(job_id: str) -> Dict[str, Any]:
    """CP9: fetch job state for a backtest job."""

    from app.services.job_manager import JobManager

    jm = JobManager()
    state = jm.load_state(job_id)
    if not state:
        raise HTTPException(status_code=404, detail="job not found")
    return state


@router.post("/runs/{run_id}/upstream/message", response_model=LabRunUpstreamMessageResponse)
async def post_upstream_message(run_id: str, req: LabRunUpstreamMessageRequest) -> LabRunUpstreamMessageResponse:
    p = _run_path(run_id)
    if not p.exists():
        raise HTTPException(status_code=404, detail="run not found")

    run = _load_run_json(run_id)
    phase = str(run.get("phase") or "upstream")
    if phase != "upstream":
        raise HTTPException(status_code=409, detail="upstream chat is available only during phase=upstream")

    patch = await _handle_upstream_user_message(run_id, run, req.message)
    _update_run_json(run_id, patch)
    updated = _load_run_json(run_id)

    return LabRunUpstreamMessageResponse(
        status=str(updated.get("status") or patch.get("status") or "needs_user_input"),
        run_id=run_id,
        phase=str(updated.get("phase") or "upstream"),
        upstream_contract=dict(updated.get("upstream_contract") or {}),
        upstream=dict(updated.get("upstream") or {"messages": [], "pending_question": ""}),
    )


@router.post("/runs/{run_id}/upstream/feedback", response_model=LabRunUpstreamFeedbackResponse)
async def post_upstream_feedback(run_id: str, req: LabRunUpstreamFeedbackRequest) -> LabRunUpstreamFeedbackResponse:
    p = _run_path(run_id)
    if not p.exists():
        raise HTTPException(status_code=404, detail="run not found")

    run = _load_run_json(run_id)
    phase = str(run.get("phase") or "upstream")
    if phase != "upstream":
        raise HTTPException(status_code=409, detail="upstream feedback is available only during phase=upstream")

    upstream = _ensure_upstream_state(run)
    feedback = str(req.message or "").strip()
    if not feedback:
        raise HTTPException(status_code=400, detail="message is required")

    upstream["user_feedback"] = feedback
    upstream["ready_for_user_review"] = False
    upstream["user_approved"] = False

    _append_trace(run_id, {"ts_ms": _now_ms(), "type": "upstream_user_feedback", "data": {"text": feedback[:2000]}})

    # Treat feedback as the next user message to revise the draft.
    patch = _handle_upstream_user_message(run_id, run, feedback)
    patch["upstream"] = upstream

    _update_run_json(run_id, patch)
    updated = _load_run_json(run_id)

    return LabRunUpstreamFeedbackResponse(
        status=str(updated.get("status") or patch.get("status") or "needs_user_input"),
        run_id=run_id,
        phase=str(updated.get("phase") or "upstream"),
        upstream_contract=dict(updated.get("upstream_contract") or {}),
        upstream=dict(updated.get("upstream") or {"messages": [], "pending_question": ""}),
    )


@router.post("/runs/{run_id}/upstream/approve", response_model=LabRunUpstreamApproveResponse)
async def post_upstream_approve(run_id: str, background_tasks: BackgroundTasks) -> LabRunUpstreamApproveResponse:
    p = _run_path(run_id)
    if not p.exists():
        raise HTTPException(status_code=404, detail="run not found")

    run = _load_run_json(run_id)
    phase = str(run.get("phase") or "upstream")
    if phase != "upstream":
        raise HTTPException(status_code=409, detail="upstream approve is available only during phase=upstream")

    upstream_contract = run.get("upstream_contract") or {}
    if not bool(upstream_contract.get("approved")):
        raise HTTPException(status_code=409, detail="upstream contract not approved")

    upstream = _ensure_upstream_state(run)
    if not bool(upstream.get("ready_for_user_review")):
        raise HTTPException(status_code=409, detail="strategy draft not ready for review")

    upstream["user_approved"] = True
    run["upstream"] = upstream

    _append_trace(run_id, {"ts_ms": _now_ms(), "type": "upstream_user_approved", "data": {}})

    _update_run_json(run_id, {"upstream": upstream})

    # Start execution (same behavior as /continue when upstream is approved)
    inp = run.get("input") or {}
    _update_run_json(
        run_id,
        {
            "status": "running",
            "step": "execution",
            "phase": "execution",
            "needs_user_confirm": False,
        },
    )
    _append_trace(run_id, {"ts_ms": _now_ms(), "type": "execution_started_by_user", "data": {"via": "upstream_approve"}})
    background_tasks.add_task(_run_lab_autonomous, run_id, inp)

    return LabRunUpstreamApproveResponse(status="ok", run_id=run_id, phase="execution")


@router.post("/runs/{run_id}/continue")
async def continue_run(
    run_id: str,
    background_tasks: BackgroundTasks,
    req: Optional[LabRunContinueRequest] = None,
) -> Dict[str, Any]:
    """Resume from upstream, optionally with updated user inputs."""

    p = _run_path(run_id)
    if not p.exists():
        raise HTTPException(status_code=404, detail="run not found")

    run = _load_run_json(run_id)
    phase = str(run.get("phase") or "upstream")
    upstream_contract = run.get("upstream_contract") or {}

    if phase == "upstream":
        if not bool(upstream_contract.get("approved")):
            raise HTTPException(status_code=409, detail="upstream contract not approved")

        if str(run.get("status") or "").strip() in ("running", "done"):
            return {"status": "ok", "run_id": run_id, "phase": "execution"}

        inp = run.get("input") or {}
        _update_run_json(
            run_id,
            {
                "status": "running",
                "step": "execution",
                "phase": "execution",
                "needs_user_confirm": False,
            },
        )
        _append_trace(run_id, {"ts_ms": _now_ms(), "type": "execution_started_by_user", "data": {}})
        background_tasks.add_task(_run_lab_autonomous, run_id, inp)
        return {"status": "ok", "run_id": run_id, "phase": "execution"}

    inp = run.get("input") or {}

    payload_updates: Dict[str, Any] = {}
    parsed_from_message = _parse_symbol_timeframe_from_text((req.message if req else None))
    if req is not None:
        if req.symbol:
            payload_updates["symbol"] = str(req.symbol).strip()
        if req.timeframe:
            payload_updates["timeframe"] = str(req.timeframe).strip()
        if req.objective is not None:
            payload_updates["objective"] = str(req.objective)
        if req.message:
            payload_updates["objective"] = str(req.message)
    for k, v in parsed_from_message.items():
        payload_updates[k] = v
    if payload_updates:
        inp.update(payload_updates)

    budget = run.get("budget") or {}
    inc_turns = int(budget.get("continue_turns", 3))
    inc_tokens = int(budget.get("continue_tokens", 15000))

    budget["turns_max"] = int(budget.get("turns_max", 0)) + inc_turns
    budget["tokens_max"] = int(budget.get("tokens_max", 0)) + inc_tokens

    _append_trace(
        run_id,
        {
            "ts_ms": _now_ms(),
            "type": "user_continue",
            "data": {"inc_turns": inc_turns, "inc_tokens": inc_tokens, "budget": budget, "input_updates": payload_updates},
        },
    )

    _update_run_json(
        run_id,
        {
            "input": inp,
            "budget": budget,
            "needs_user_confirm": False,
            "status": "running",
            "step": ("upstream" if phase == "upstream" else str(run.get("step") or "execution")),
            "phase": phase,
        },
    )

    if phase == "upstream":
        # Legacy path for pre-CTA upstream resumes.
        try:
            _cp4_run_personas_if_possible(run_id)
        except Exception as e:
            _append_trace(run_id, {"ts_ms": _now_ms(), "type": "personas_error", "data": {"error": str(e)}})

    return {"status": "ok", "run_id": run_id, "budget": budget, "input": inp, "phase": phase}
