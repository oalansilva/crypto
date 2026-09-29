"""Closed-day Jev diagnosis and validated confidence apply (#1045).

The ruler stays read-only. This module persists one diagnosis per closed UTC
day, applies only the declared per-regime confidence outcome, and never writes
target, stop, horizon or size. Calibration is born paused.
"""

from __future__ import annotations

import hashlib
import statistics
import importlib.util
import json
import logging
import uuid
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any, Optional, Sequence

from sqlalchemy.orm import Session

from app.models import (
    ScalpCalibrationState,
    ScalpConfidenceVersion,
    ScalpJevDiagnosis,
    ScalpUserState,
)
from app.services.scalp_engine import (
    CONFIDENCE_POLICY_CLOSED,
    CONFIDENCE_POLICY_NUMERIC,
    CONFIDENCE_POLICY_OFF,
    REGIME_ACTIVE,
    REGIME_CALM,
    ConfidencePolicy,
    MarketRegime,
)
from app.services.scalp_jev_log import log_file_path


def bundle_version_policies(
    confidence: dict[str, dict[str, Any]],
    *,
    target_bp: str,
    stop_bp: str,
    horizon_s: int,
    regime_boundary_bp: Optional[str],
    slippage_cap_bp: str = "10",
    confidence_map: Optional[dict[str, str]] = None,
) -> dict[str, Any]:
    """One fingerprint payload: confidence + geometry + boundary (#1070)."""
    payload = dict(confidence)
    payload["geometry"] = {
        "target_bp": target_bp,
        "stop_bp": stop_bp,
        "horizon_s": horizon_s,
        "slippage_cap_bp": slippage_cap_bp,
    }
    if regime_boundary_bp is not None:
        payload["regime_boundary_bp"] = regime_boundary_bp
    if confidence_map:
        payload["confidence_map"] = confidence_map
    return payload


def compute_regime_boundary_bp(
    vol_bps: Sequence[Decimal], *, min_per_side: int = 200
) -> Optional[Decimal]:
    values = sorted(v for v in vol_bps if v is not None and v.is_finite())
    if len(values) < min_per_side * 2:
        return None
    return Decimal(str(statistics.median([float(v) for v in values])))


def _vol_bps_from_decisions(decisions: Sequence[Any]) -> list[Decimal]:
    vols: list[Decimal] = []
    for decision in decisions:
        vol = getattr(decision, "vol_bp", None)
        if vol is not None and vol.is_finite():
            vols.append(vol)
    return vols


def _maybe_measure_and_persist_regime_boundary(
    db: Session,
    summary: dict[str, Any],
    decisions: Sequence[Any],
    *,
    closed: date,
    now: datetime,
) -> None:
    """Measure σ boundary from real log decisions; persist version when needed (#1070)."""
    if summary.get("regime_boundary_bp") is not None:
        return
    measured = compute_regime_boundary_bp(_vol_bps_from_decisions(decisions))
    if measured is None:
        return
    summary["regime_boundary_bp"] = str(measured)
    summary["regime_boundary_status"] = "measured"

    current = active_version(db)
    if current is not None and regime_boundary_from_policies(policies_of(current)) is not None:
        return

    from app.services.scalp_service import _confidence_min

    in_use = _confidence_min()
    conf_value = str(in_use if in_use is not None else Decimal("0.7"))
    confidence = {
        REGIME_CALM: {"kind": CONFIDENCE_POLICY_NUMERIC, "value": conf_value},
        REGIME_ACTIVE: {"kind": CONFIDENCE_POLICY_NUMERIC, "value": conf_value},
    }
    policies = bundle_version_policies(
        confidence,
        target_bp="35",
        stop_bp="-28",
        horizon_s=900,
        regime_boundary_bp=str(measured),
        slippage_cap_bp="10",
    )
    _activate_version(
        db,
        policies=policies,
        closed=closed,
        reason=_BOUNDARY_MEASURED_ACTIVATE_REASON,
        source=SOURCE_MEASURED_BOUNDARY,
        previous=current,
        choice_until=None,
        validated_until=None,
        now=now,
    )


def _version_lacks_regime_boundary(db: Session) -> bool:
    current = active_version(db)
    if current is None:
        return True
    return regime_boundary_from_policies(policies_of(current)) is None


def _try_measure_regime_boundary_from_log(
    db: Session,
    summary: dict[str, Any],
    *,
    closed: date,
    now: datetime,
) -> None:
    log_path = log_file_path()
    if not log_path.exists():
        return
    ruler = _load_ruler()
    decisions, _refusals, _malformed = ruler.parse_log(log_path)
    _maybe_measure_and_persist_regime_boundary(
        db,
        summary,
        decisions,
        closed=closed,
        now=now,
    )


def confidence_only(policies: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        regime: dict(policies[regime])
        for regime in (REGIME_CALM, REGIME_ACTIVE)
        if regime in policies
    }


def geometry_from_policies(policies: dict[str, Any]) -> dict[str, Any]:
    geo = policies.get("geometry")
    if isinstance(geo, dict):
        return geo
    return {
        "target_bp": "35",
        "stop_bp": "-28",
        "horizon_s": 900,
        "slippage_cap_bp": "10",
    }


def regime_boundary_from_policies(policies: dict[str, Any]) -> Optional[str]:
    raw = policies.get("regime_boundary_bp")
    return None if raw is None else str(raw)


def bundle_from_summary(
    confidence: dict[str, dict[str, Any]],
    summary: dict[str, Any],
    *,
    backtest: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    geo = summary.get("geometry_proposal") or summary.get("geometry_in_use") or {}
    boundary = None
    if summary.get("regime_boundary_bp") is not None:
        boundary = str(summary["regime_boundary_bp"])
    elif backtest and backtest.get("regime_boundary_bp"):
        boundary = str(backtest["regime_boundary_bp"])
    return bundle_version_policies(
        confidence,
        target_bp=str(geo.get("target_bp") or "35"),
        stop_bp=str(geo.get("stop_bp") or "-28"),
        horizon_s=int(geo.get("horizon_s") or 900),
        regime_boundary_bp=boundary,
        slippage_cap_bp=str(geo.get("slippage_cap_bp") or "10"),
    )


def backtest_promotion_ready(summary: dict[str, Any]) -> bool:
    backtest = summary.get("backtest") or {}
    if backtest.get("promotable") is True:
        return True
    regimes = backtest.get("regimes") or {}
    if not regimes:
        return False
    return all(bool(row.get("promotable")) for row in regimes.values())


def _backtest_sample_phrase(summary: dict[str, Any]) -> str:
    backtest = summary.get("backtest") or {}
    regimes = backtest.get("regimes") or {}
    if not regimes:
        return (
            "O backtest offline ainda não fechou 200 janelas independentes por regime; "
            "a geometria em uso continua enquanto a grelha varia."
        )
    parts = []
    for name, row in regimes.items():
        label = "calmo" if name == REGIME_CALM else "agitado"
        n = int(row.get("n") or 0)
        lower = row.get("ci95_lower_bp")
        parts.append(f"{label}: {n} janelas, IC 95% inferior {lower} bp")
    promotable = backtest_promotion_ready(summary)
    tail = (
        "O conjunto pode ser promovido: lucro líquido médio com IC acima de zero."
        if promotable
        else "Ainda não há prova de lucro líquido com IC acima de zero; alvo, stop e prazo continuam a variar."
    )
    return "Backtest: " + "; ".join(parts) + ". " + tail


def _geometry_bundle_phrase(
    policies: dict[str, Any], version: Optional[ScalpConfidenceVersion]
) -> str:
    geo = geometry_from_policies(policies)
    boundary = regime_boundary_from_policies(policies)
    mins = int(int(geo.get("horizon_s") or 900) // 60)
    version_bit = f"Versão {version.version_n}." if version is not None else "Sem versão promovida."
    boundary_bit = (
        f"Recorte de regime em {boundary} bp."
        if boundary is not None
        else "Recorte de regime ainda ausente."
    )
    return (
        f"Conjunto aplicado: alvo {geo.get('target_bp')} bp, stop {geo.get('stop_bp')} bp, "
        f"prazo {mins} min. {boundary_bit} {version_bit}"
    )


logger = logging.getLogger(__name__)

POSTERIOR_MIN = 200
RUN_AFTER_MINUTE = 15
CALIBRATION_ROW_ID = 1
SOURCE_AUTOMATIC = "automatic"
SOURCE_MEASURED_BOUNDARY = "measured_boundary"
SOURCE_REVERT_AUTO = "auto_revert"
SOURCE_REVERT_MANUAL = "manual_revert"

_BOUNDARY_MEASURED_ACTIVATE_REASON = (
    "Fronteira medida no vol_bp real do log de diagnóstico; "
    "a confiança mantém o valor em uso; alvo, stop e prazo não mudam."
)

VERB_APPLY = "aplicar"
VERB_KEEP = "manter"
VERB_BLOCK = "bloquear"
VERB_REVERT = "reverter"

_MONTHS_PT = (
    "jan",
    "fev",
    "mar",
    "abr",
    "mai",
    "jun",
    "jul",
    "ago",
    "set",
    "out",
    "nov",
    "dez",
)
_MONTHS_LONG = (
    "janeiro",
    "fevereiro",
    "março",
    "abril",
    "maio",
    "junho",
    "julho",
    "agosto",
    "setembro",
    "outubro",
    "novembro",
    "dezembro",
)

_ruler_module = None
_backtest_module = None


def _utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _load_ruler():
    global _ruler_module
    if _ruler_module is not None:
        return _ruler_module
    path = Path(__file__).resolve().parents[3] / "scripts" / "scalp_jev_eval.py"
    spec = importlib.util.spec_from_file_location("scalp_jev_eval", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    import sys

    sys.modules["scalp_jev_eval"] = module
    spec.loader.exec_module(module)
    _ruler_module = module
    return module


def _load_backtest():
    global _backtest_module
    if _backtest_module is not None:
        return _backtest_module
    path = Path(__file__).resolve().parents[3] / "scripts" / "scalp_jev_backtest.py"
    spec = importlib.util.spec_from_file_location("scalp_jev_backtest", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    import sys

    sys.modules["scalp_jev_backtest"] = module
    spec.loader.exec_module(module)
    _backtest_module = module
    return module


def _attach_offline_backtest(summary: dict[str, Any], *, fee_bp: Decimal) -> None:
    """Fill ``summary[\"backtest\"]`` from ``scripts/scalp_jev_backtest.py`` (#1070)."""
    backtest = _load_backtest()
    geo = summary.get("geometry_proposal") or summary.get("geometry_in_use") or {}
    try:
        target_bp = Decimal(str(geo.get("target_bp") or "35"))
        stop_bp = Decimal(str(geo.get("stop_bp") or "-28"))
        horizon_s = int(geo.get("horizon_s") or 900)
    except Exception:
        target_bp, stop_bp, horizon_s = Decimal("35"), Decimal("-28"), 900
    tape = backtest.synthetic_trade_tape(n_windows=500, horizon_s=horizon_s)
    result = backtest.run_offline_backtest(
        trades=tape,
        fee_bp=fee_bp,
        horizon_s=horizon_s,
        target_bp=target_bp,
        stop_bp=stop_bp,
    )
    summary["backtest"] = {
        "promotable": result.get("promotable"),
        "regimes": result.get("regimes") or {},
        "benchmark": result.get("benchmark"),
        "returns_by_geometry": result.get("returns_by_geometry"),
        "regime_boundary_bp": result.get("regime_boundary_bp"),
    }


def _json_load(raw: Optional[str]) -> Any:
    if not raw:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return None


def _json_dump(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, default=str)


def _fmt_day(value: date) -> str:
    return f"{value.day} {_MONTHS_PT[value.month - 1]} {value.year}"


def _fmt_long_day(value: date) -> str:
    return f"{value.day} de {_MONTHS_LONG[value.month - 1]} de {value.year}"


def _em_100(rate: Optional[Decimal]) -> Optional[int]:
    if rate is None:
        return None
    return int((rate * Decimal("100")).quantize(Decimal("1")))


def _usd_per_100(bp: Optional[Decimal]) -> str:
    if bp is None:
        return "nada"
    cents = (bp / Decimal("100")).quantize(Decimal("0.01"))
    text = f"{cents:.2f}".replace(".", ",")
    if cents < 0:
        return f"cerca de US$ {text[1:]} a menos"
    if cents == 0:
        return "nada"
    return f"cerca de US$ {text} a mais"


def fingerprint_of(policies: dict[str, Any]) -> str:
    canonical = json.dumps(policies, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def closed_day_for(now: datetime) -> date:
    return now.date() - timedelta(days=1)


def day_end(closed: date) -> datetime:
    return datetime(closed.year, closed.month, closed.day) + timedelta(days=1)


def seed_for_day(closed: date) -> int:
    digest = hashlib.sha256(closed.isoformat().encode("utf-8")).hexdigest()
    return int(digest[:8], 16)


def get_calibration_state(db: Session) -> ScalpCalibrationState:
    row = (
        db.query(ScalpCalibrationState)
        .filter(ScalpCalibrationState.id == CALIBRATION_ROW_ID)
        .first()
    )
    if row is None:
        row = ScalpCalibrationState(id=CALIBRATION_ROW_ID, paused=True, updated_at=_utcnow())
        db.add(row)
        db.commit()
        db.refresh(row)
    return row


def set_calibration_paused(db: Session, *, paused: bool) -> ScalpCalibrationState:
    """Pause or enable calibration. Does not touch the per-user switch or kill."""
    row = get_calibration_state(db)
    row.paused = bool(paused)
    row.updated_at = _utcnow()
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def active_version(db: Session) -> Optional[ScalpConfidenceVersion]:
    return (
        db.query(ScalpConfidenceVersion)
        .filter(ScalpConfidenceVersion.active.is_(True))
        .order_by(ScalpConfidenceVersion.version_n.desc())
        .first()
    )


def version_by_id(db: Session, version_id: Optional[str]) -> Optional[ScalpConfidenceVersion]:
    if not version_id:
        return None
    return db.query(ScalpConfidenceVersion).filter(ScalpConfidenceVersion.id == version_id).first()


def diagnosis_for(db: Session, closed: date) -> Optional[ScalpJevDiagnosis]:
    return db.query(ScalpJevDiagnosis).filter(ScalpJevDiagnosis.closed_day == closed).first()


def env_policies() -> dict[str, dict[str, Any]]:
    """#1030 env fallback used while no applied version exists."""
    from app.services.scalp_service import _confidence_policy_for, _regime_boundary_bp

    boundary = _regime_boundary_bp()
    out: dict[str, dict[str, Any]] = {}
    for regime in (REGIME_CALM, REGIME_ACTIVE):
        policy = _confidence_policy_for(regime=regime, boundary_bp=boundary, db=None)
        out[regime] = {
            "kind": policy.kind,
            "value": None if policy.value is None else str(policy.value),
        }
    return out


def policies_of(version: Optional[ScalpConfidenceVersion]) -> dict[str, dict[str, Any]]:
    if version is None:
        return env_policies()
    loaded = _json_load(version.policies_json)
    return loaded if isinstance(loaded, dict) else env_policies()


def policy_from_map(policies: dict[str, Any], *, regime: MarketRegime) -> ConfidencePolicy:
    row = policies.get(regime) or {}
    kind = str(row.get("kind") or CONFIDENCE_POLICY_CLOSED)
    raw = row.get("value")
    value = None
    if kind == CONFIDENCE_POLICY_NUMERIC and raw is not None:
        try:
            value = Decimal(str(raw))
        except Exception:
            kind = CONFIDENCE_POLICY_CLOSED
            value = None
        if value is not None and (not value.is_finite() or value < 0 or value > 1):
            kind = CONFIDENCE_POLICY_CLOSED
            value = None
    if kind not in {CONFIDENCE_POLICY_NUMERIC, CONFIDENCE_POLICY_OFF, CONFIDENCE_POLICY_CLOSED}:
        kind = CONFIDENCE_POLICY_CLOSED
        value = None
    if kind != CONFIDENCE_POLICY_NUMERIC:
        value = None
    return ConfidencePolicy(kind=kind, value=value, regime=regime)


def consumed_policy_for(
    db: Optional[Session], *, regime: MarketRegime, boundary_bp: Optional[Decimal]
) -> ConfidencePolicy:
    """Applied version if one exists, otherwise the #1030 env (fail closed)."""
    from app.services.scalp_service import _confidence_policy_for as env_policy

    if db is None:
        return env_policy(regime=regime, boundary_bp=boundary_bp, db=None)
    version = active_version(db)
    if version is None:
        return env_policy(regime=regime, boundary_bp=boundary_bp, db=None)
    return policy_from_map(policies_of(version), regime=regime)


def declared_policies(summary: dict[str, Any]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    regimes = summary.get("regimes") or {}
    for regime in (REGIME_CALM, REGIME_ACTIVE):
        row = regimes.get(regime) or {}
        kind = str(row.get("policy") or CONFIDENCE_POLICY_CLOSED)
        value = None
        chosen = row.get("chosen") or {}
        if kind == CONFIDENCE_POLICY_NUMERIC and chosen.get("threshold") is not None:
            value = str(chosen["threshold"])
        out[regime] = {"kind": kind, "value": value}
    return out


def _policies_from_windows(
    rows: list[Any],
    *,
    fee_bp: Decimal,
    boundary_bp: Optional[Decimal],
    ruler: Any,
) -> dict[str, dict[str, Any]]:
    """Per-regime policy of ``rows`` only — posterior windows stay out of the choice."""
    eligible, _sources = ruler.eligible_population(rows, fee_bp=fee_bp)
    out: dict[str, dict[str, Any]] = {}
    for regime in (REGIME_CALM, REGIME_ACTIVE):
        subset = [
            (decision, realized)
            for decision, realized in eligible
            if ruler.market_regime(decision, boundary_bp) == regime
        ]
        analysis = ruler.regime_analysis(
            subset,
            fee_bp=fee_bp,
            boundary_bp=boundary_bp,
            labels={"regime": regime},
        )
        kind = str(analysis.get("policy") or CONFIDENCE_POLICY_CLOSED)
        value = None
        chosen = analysis.get("chosen") or {}
        if kind == CONFIDENCE_POLICY_NUMERIC and chosen.get("threshold") is not None:
            value = str(chosen["threshold"])
        out[regime] = {"kind": kind, "value": value}
    return out


def _account_maker_fee(db: Session) -> tuple[Decimal, str]:
    """Real maker fee when a signed account read succeeds; otherwise fallback."""
    from app.models import UserExchangeCredential
    from app.services.scalp_service import FALLBACK_FEE_BP, _live_fee_terms
    from app.services.user_exchange_credentials import BINANCE_PROVIDER

    rows = (
        db.query(UserExchangeCredential)
        .filter(UserExchangeCredential.provider == BINANCE_PROVIDER)
        .all()
    )
    for cred in rows:
        if not str(cred.api_key or "").strip() or not str(cred.api_secret or "").strip():
            continue
        try:
            live = _live_fee_terms(str(cred.api_key), str(cred.api_secret))
            fee_bp = live[0]
            fee_bp = Decimal(str(fee_bp))
            if fee_bp > 0:
                return fee_bp, "account"
        except Exception as exc:
            logger.warning(
                "diagnosis maker fee fallback cred=%s err=%s",
                cred.user_id,
                type(exc).__name__,
            )
            continue
    return FALLBACK_FEE_BP, "fallback"


def _policy_net_bp(
    rows: list[Any],
    policies: dict[str, Any],
    *,
    fee_bp: Decimal,
    boundary_bp: Optional[Decimal],
    ruler: Any,
) -> Optional[Decimal]:
    round_trip = Decimal("2") * fee_bp
    pnls: list[Decimal] = []
    for decision, realized in rows:
        if realized.signed_bp is None:
            continue
        regime = ruler.market_regime(decision, boundary_bp)
        policy = policy_from_map(policies, regime=regime or REGIME_CALM)
        if policy.kind == CONFIDENCE_POLICY_CLOSED:
            pnls.append(Decimal("0"))
        elif policy.kind == CONFIDENCE_POLICY_OFF:
            pnls.append(realized.signed_bp - round_trip)
        elif policy.value is not None and decision.confidence >= policy.value:
            pnls.append(realized.signed_bp - round_trip)
        else:
            pnls.append(Decimal("0"))
    if not pnls:
        return None
    return sum(pnls, Decimal("0")) / Decimal(len(pnls))


def _quality_block(
    summary: dict[str, Any],
    *,
    newest_candle: Optional[datetime],
    last_window_end: Optional[datetime],
) -> Optional[tuple[str, str]]:
    if summary.get("regime_boundary_bp") is None:
        return (
            "regime_boundary",
            "A fronteira entre mercado calmo e agitado está ausente. Os dois regimes continuam fechados e nenhum ajuste pode ser promovido.",
        )
    measurement = (summary.get("measurement") or {}).get("status")
    if measurement == "não medido":
        return (
            "measurement",
            "A leitura dos preços falhou. Isto não é um resultado do scalp. A confiança fica.",
        )
    if (
        newest_candle is not None
        and last_window_end is not None
        and newest_candle < last_window_end
    ):
        return (
            "stale",
            "Os dados desta leitura já tinham expirado. Isto não é um resultado do scalp. A confiança fica.",
        )
    if measurement == "medição parcial":
        missing = (summary.get("measurement") or {}).get("windows_without_price_coverage") or 0
        if int(missing) > 0:
            return (
                "coverage",
                "Faltam preços para fechar o dia. Isto não é um resultado do scalp. A confiança fica.",
            )
    homo = summary.get("homogeneity") or {}
    if homo.get("status") != "homogénea":
        return (
            "unverified",
            f"A comparação foi bloqueada: {_homogeneity_reason(summary)}. "
            "Isto não é um resultado do scalp. A confiança fica.",
        )
    if summary.get("fee_source") != "account":
        return (
            "cost",
            "A taxa desta leitura não veio da consulta de comissão da conta. Isto não é um resultado do scalp. A confiança fica.",
        )
    bench = (summary.get("benchmark") or {}).get("overall") or {}
    if not bench.get("computable"):
        return (
            "benchmark",
            "Não deu para comparar o sinal com o acaso. Isto não é um resultado do scalp. A confiança fica.",
        )
    viability = _viability_status(summary)
    if viability == "insufficient_sample":
        return (
            "sample",
            "A amostra ainda não tem 200 janelas históricas independentes com preço. Isto não é um resultado do scalp. A confiança fica.",
        )
    if viability == "indeterminate":
        return ("barriers", _barrier_evidence_reason(summary))
    if viability == "not_operable" and not summary.get("geometry_search_active"):
        return (
            "not_operable",
            "As barreiras foram medidas e nenhuma alternativa de alvo ou prazo supera o necessário depois da taxa. Não mudei parâmetro nenhum.",
        )
    return None


def _viability_status(summary: dict[str, Any]) -> str:
    status = summary.get("viability_status")
    if status in {"viable", "not_operable", "indeterminate", "insufficient_sample"}:
        return status
    # Older stored diagnoses only had a boolean. Treat its negative value as
    # unknown: it may have come from missing or indeterminate barrier data.
    return "viable" if summary.get("operable") is True else "indeterminate"


def _barrier_evidence_reason(summary: dict[str, Any]) -> str:
    measurement = summary.get("barrier_measurement") or {}
    candidate_count = int(measurement.get("candidate_count") or 0)
    indeterminate = int(measurement.get("indeterminate_candidates") or 0)
    no_hits = int(measurement.get("no_hit_candidates") or 0)
    in_use = summary.get("geometry_in_use") or {}
    if indeterminate:
        detail = (
            f"as barreiras ficaram sem resolução em {indeterminate} de {candidate_count} "
            "alternativas de alvo e prazo"
        )
    elif no_hits:
        detail = (
            f"em {no_hits} de {candidate_count} alternativas de alvo e prazo, nenhuma janela "
            "tocou o alvo ou o stop"
        )
    elif int(in_use.get("n_indeterminate") or 0):
        detail = (
            f"as barreiras atuais ficaram sem resolução em {int(in_use['n_indeterminate'])} "
            "janelas históricas"
        )
    elif not int(in_use.get("n_target") or 0) + int(in_use.get("n_stop") or 0):
        detail = "não houve alvo nem stop medidos em janelas históricas comparáveis"
    else:
        detail = "a medição das barreiras e dos prazos candidatos não ficou completa"
    return (
        f"{detail}; ainda não dá para afirmar que o scalp não se paga. "
        "A confiança fica e nenhum parâmetro é promovido."
    )


def _has_incomplete_barrier_evidence(summary: dict[str, Any]) -> bool:
    measurement = summary.get("barrier_measurement") or {}
    in_use = summary.get("geometry_in_use") or {}
    return bool(
        int(measurement.get("indeterminate_candidates") or 0)
        or int(measurement.get("no_hit_candidates") or 0)
        or int(in_use.get("n_indeterminate") or 0)
        or not (int(in_use.get("n_target") or 0) + int(in_use.get("n_stop") or 0))
    )


def _confidence_phrase(policies: dict[str, Any], version: Optional[ScalpConfidenceVersion]) -> str:
    parts: list[str] = []
    calm = policy_from_map(policies, regime=REGIME_CALM)
    active = policy_from_map(policies, regime=REGIME_ACTIVE)
    if calm.kind == CONFIDENCE_POLICY_NUMERIC and calm.value is not None:
        pct = int((calm.value * Decimal("100")).quantize(Decimal("1")))
        parts.append(f"mercado calmo só entra acima de {pct}%")
    elif calm.kind == CONFIDENCE_POLICY_OFF:
        parts.append("mercado calmo entra sem filtro de confiança")
    else:
        parts.append("mercado calmo não entra")
    if active.kind == CONFIDENCE_POLICY_NUMERIC and active.value is not None:
        pct = int((active.value * Decimal("100")).quantize(Decimal("1")))
        parts.append(f"mercado agitado só entra acima de {pct}%")
    elif active.kind == CONFIDENCE_POLICY_OFF:
        parts.append("mercado agitado entra sem filtro de confiança")
    else:
        parts.append("mercado agitado não entra")
    text = ". ".join(parts) + "."
    if version is not None:
        text += f" Versão {version.version_n}."
    return text[0].upper() + text[1:] if text else text


def _decision_label(verb: str) -> str:
    return {
        VERB_APPLY: "mudei a confiança",
        VERB_KEEP: "mantive a confiança",
        VERB_BLOCK: "não mudei a confiança",
        VERB_REVERT: "voltei à versão anterior",
    }.get(verb, "não mudei a confiança")


def _homogeneity_reason(summary: dict[str, Any]) -> str:
    homo = summary.get("homogeneity") or {}
    eligible = int((summary.get("eligible_population") or {}).get("n") or 0)
    affected = int(homo.get("affected_windows", homo.get("excluded_windows", 0)) or 0)
    if eligible == 0:
        return "nenhuma janela ficou elegível para conferir o modelo e a origem da confiança"
    if homo.get("status") == "não homogénea":
        return (
            f"o modelo ou a origem da confiança varia em {affected} de {eligible} "
            "janelas elegíveis"
        )
    unknown: list[str] = []
    if any(
        str(value).strip().lower() in {"", "unknown", "desconhecido", "none"}
        for value in homo.get("models", [])
    ):
        unknown.append("o modelo não foi identificado")
    if any(
        str(value).strip().lower() in {"", "unknown", "desconhecido", "none"}
        for value in homo.get("origins", [])
    ):
        unknown.append("a origem da confiança não foi identificada")
    if not unknown:
        unknown.append("a identidade da amostra não pôde ser confirmada")
    return f"{' e '.join(unknown)} em {affected} de {eligible} janelas elegíveis"


def _format_period(period: Optional[tuple[datetime, datetime]]) -> Optional[str]:
    if period is None:
        return None
    start, end = period
    start_label = f"{start.day} {_MONTHS_LONG[start.month - 1]} {start.year} {start:%H:%M}"
    end_label = f"{end.day} {_MONTHS_LONG[end.month - 1]} {end.year} {end:%H:%M}"
    return f"{start_label} a {end_label} UTC"


def _sample_is_comparable(summary: dict[str, Any], block_kind: Optional[str] = None) -> bool:
    measurement = summary.get("measurement") or {}
    homogeneity = summary.get("homogeneity") or {}
    benchmark = (summary.get("benchmark") or {}).get("overall") or {}
    return block_kind not in {
        "measurement",
        "stale",
        "coverage",
        "unverified",
        "cost",
        "benchmark",
        "regime_boundary",
        "barriers",
        "sample",
        "not_operable",
        "posterior",
    } and (
        measurement.get("status") == "medido"
        and homogeneity.get("status") == "homogénea"
        and summary.get("fee_source") == "account"
        and summary.get("regime_boundary_bp") is not None
        and bool(benchmark.get("computable"))
        and _viability_status(summary) == "viable"
    )


def _data_quality_phrase(
    summary: dict[str, Any],
    period: Optional[tuple[datetime, datetime]],
    block_kind: Optional[str] = None,
    posterior_n: Optional[int] = None,
) -> str:
    measurement = summary.get("measurement") or {}
    homogeneity = summary.get("homogeneity") or {}
    stats = summary.get("stats") or {}
    total = int(measurement.get("n_windows", stats.get("n", 0)) or 0)
    priced = int(measurement.get("n_priced", stats.get("n_priced", 0)) or 0)
    period_label = _format_period(period)
    period_part = f" entre {period_label}" if period_label else ""
    quality: list[str] = []
    if summary.get("regime_boundary_bp") is None:
        quality.append(
            "a fronteira entre mercado calmo e agitado está ausente; os dois regimes continuam bloqueados"
        )
    if block_kind == "stale":
        quality.append("os preços guardados estavam atrasados para o fim da janela")
    if measurement.get("status") == "não medido":
        quality.append("os preços não puderam ser medidos")
    elif measurement.get("status") == "medição parcial":
        missing = int(measurement.get("windows_without_price_coverage", 0) or 0)
        quality.append(f"faltam preços em {missing} janelas")
    if homogeneity.get("status") != "homogénea":
        quality.append(f"comparação bloqueada: {_homogeneity_reason(summary)}")
    if summary.get("fee_source") != "account":
        quality.append("o custo usa a taxa conservadora, não a taxa consultada da conta")
    benchmark = (summary.get("benchmark") or {}).get("overall") or {}
    if not benchmark.get("computable"):
        quality.append("não foi possível comparar o sinal com uma escolha aleatória")
    viability = _viability_status(summary)
    if viability == "not_operable":
        quality.append(
            "as barreiras foram medidas e nenhuma alternativa supera o necessário depois da taxa"
        )
    elif viability == "indeterminate":
        quality.append(_barrier_evidence_reason(summary).rstrip("."))
    elif viability == "insufficient_sample":
        quality.append("a amostra ainda não é suficiente para avaliar a viabilidade")
        if _has_incomplete_barrier_evidence(summary):
            quality.append(_barrier_evidence_reason(summary).rstrip("."))
    if block_kind == "posterior":
        count = 0 if posterior_n is None else posterior_n
        noun = "janela passou" if count == 1 else "janelas passaram"
        quality.append(f"só {count} {noun} pelos filtros da posterior")
    period_text = f"{priced} de {total} janelas históricas têm preço{period_part}"
    if quality:
        return (
            f"{period_text}. "
            + "; ".join(quality)
            + ". São janelas históricas avaliadas, não trades executados."
        )
    return (
        f"{period_text}. Os filtros desta leitura passaram. São janelas históricas avaliadas, "
        "não trades executados."
    )


def _sample_phrase(
    posterior_n: int,
    comparable: bool,
    summary: dict[str, Any],
    block_kind: Optional[str] = None,
) -> str:
    noun = (
        "janela histórica independente com preço"
        if posterior_n == 1
        else "janelas históricas independentes com preço"
    )
    subject = f"{posterior_n} {noun}"
    if comparable:
        return (
            f"{subject} foram medidas depois da escolha; a comparação está verificada. "
            "Não são trades executados. Para mudar a confiança são necessárias 200."
        )
    reasons: list[str] = []
    if (summary.get("homogeneity") or {}).get("status") != "homogénea":
        reasons.append(_homogeneity_reason(summary))
    if (summary.get("measurement") or {}).get("status") != "medido":
        reasons.append("a medição não está completa")
    if summary.get("fee_source") != "account":
        reasons.append("a taxa da conta não foi confirmada")
    if not ((summary.get("benchmark") or {}).get("overall") or {}).get("computable"):
        reasons.append("o sinal não pôde ser comparado com uma escolha aleatória")
    if block_kind == "stale":
        reasons.append("os preços estavam atrasados")
    if summary.get("regime_boundary_bp") is None:
        reasons.append("a fronteira entre mercado calmo e agitado está ausente")
    viability = _viability_status(summary)
    if viability == "not_operable":
        reasons.append(
            "as barreiras foram medidas e nenhuma alternativa supera o necessário depois da taxa"
        )
    elif viability == "indeterminate":
        reasons.append(_barrier_evidence_reason(summary).rstrip("."))
    elif viability == "insufficient_sample":
        reasons.append("a amostra ainda não é suficiente para avaliar a viabilidade")
        if _has_incomplete_barrier_evidence(summary):
            reasons.append(_barrier_evidence_reason(summary).rstrip("."))
    reason = "; ".join(dict.fromkeys(reasons)) or "os filtros da comparação não passaram"
    if posterior_n < POSTERIOR_MIN:
        passed = "passou" if posterior_n == 1 else "passaram"
        return (
            f"{subject} {passed} pelos filtros depois da escolha; ainda não chegam às 200 necessárias. "
            f"Motivo: {reason}. "
            "São janelas avaliadas, não trades executados."
        )
    return (
        f"{subject} foram medidas depois da escolha, mas não podem ser comparadas: {reason}. "
        "São janelas avaliadas, não trades executados."
    )


def _target_stop_phrase(summary: dict[str, Any]) -> str:
    in_use = summary.get("geometry_in_use") or {}
    try:
        with_cost = Decimal(in_use["break_even_with_cost"])
        without = Decimal(in_use["break_even_without_cost"])
    except Exception:
        return "alvo e stop ficam como estão."
    n_target = int(in_use.get("n_target") or 0)
    n_stop = int(in_use.get("n_stop") or 0)
    resolved = n_target + n_stop
    hit = Decimal(n_target) / Decimal(resolved) if resolved else None
    with_n = _em_100(with_cost)
    without_n = _em_100(without)
    hit_n = _em_100(hit)
    n_time_exit = int(in_use.get("n_time_exit") or 0)
    n_indeterminate = int(in_use.get("n_indeterminate") or 0)
    n_unknown = int(in_use.get("n_unknown") or 0)
    hit_bit = (
        f" O alvo foi atingido em cerca de {hit_n} em 100 das janelas em que o preço chegou ao alvo ou stop."
        if hit_n is not None
        else ""
    )
    if _viability_status(summary) in {"indeterminate", "insufficient_sample"}:
        observations = f" No alvo e stop atuais: {n_target} alvos, {n_stop} stops e {n_time_exit} saídas pelo prazo."
        if n_indeterminate:
            observations += f" Em {n_indeterminate} janelas históricas as barreiras não tiveram resolução suficiente."
        if n_unknown:
            observations += f" Em {n_unknown} janelas faltou uma direção reconhecida."
        if hit_n is None and not n_indeterminate and not n_unknown:
            observations += " Nenhuma barreira foi atingida, então não há acerto comparável."
        if _viability_status(summary) == "insufficient_sample":
            observations += " A amostra ainda é curta para concluir se a estratégia se paga."
        else:
            observations += " Ainda não dá para concluir se a estratégia se paga."
        return (
            f"Com a taxa, o alvo precisaria ser atingido em cerca de {with_n} de cada 100 janelas; "
            f"sem a taxa, em cerca de {without_n}.{hit_bit}{observations}"
        )
    return (
        f"para não perder com a taxa, teria de acertar cerca de {with_n} em 100. "
        f"Sem a taxa, cerca de {without_n} em 100.{hit_bit}"
    )


def _signal_phrase(summary: dict[str, Any]) -> str:
    bench = (summary.get("benchmark") or {}).get("overall") or {}
    contrib = bench.get("predictive_contribution_bp")
    try:
        value = Decimal(contrib) if contrib is not None else None
    except Exception:
        value = None
    if value is None:
        return (
            "não deu para comparar o sinal com uma escolha aleatória na mesma proporção de compras."
        )
    if value <= 0:
        return "não ganhou da escolha aleatória na mesma proporção de compras."
    return "ganhou da escolha aleatória na mesma proporção de compras."


def _side_phrase(summary: dict[str, Any]) -> str:
    bench = (summary.get("benchmark") or {}).get("overall") or {}
    buy = bench.get("buy_fraction")
    sig = bench.get("signal_accuracy")
    hold = bench.get("buy_and_hold_accuracy")
    buy_n = _em_100(Decimal(buy) if buy is not None else None)
    sig_n = _em_100(Decimal(sig) if sig is not None else None)
    hold_n = _em_100(Decimal(hold) if hold is not None else None)
    if buy_n is None or sig_n is None or hold_n is None:
        return "não deu para ler o lado das operações."
    return (
        f"Em {buy_n} de 100 janelas o sinal indicou compra. Acertar o lado ficou em {sig_n} em 100, "
        f"igual a comprar e segurar ({hold_n} em 100)."
        if sig_n == hold_n
        else (
            f"Em {buy_n} de 100 janelas o sinal indicou compra. Acertar o lado ficou em {sig_n} em 100; "
            f"comprar e segurar ficou em {hold_n} em 100."
        )
    )


def build_panel(
    *,
    closed: date,
    shown_on: date,
    verb: str,
    reason: str,
    posterior_n: int,
    comparable: bool,
    summary: dict[str, Any],
    policies: dict[str, Any],
    version: Optional[ScalpConfidenceVersion],
    period: Optional[tuple[datetime, datetime]],
    block_kind: Optional[str] = None,
) -> dict[str, Any]:
    lead = (
        f"Um aviso por dia, só depois que o dia fecha. Este é o de {_fmt_long_day(shown_on)}. "
        "Hoje não há outro."
    )
    return {
        "closed_day": closed.isoformat(),
        "shown_on": shown_on.isoformat(),
        "lead": lead,
        "when": f"{_fmt_day(shown_on)}, sobre o dia {closed.day} que já fechou",
        "data_ok": _data_quality_phrase(summary, period, block_kind, posterior_n),
        "until": "só as janelas que já tinham terminado à meia-noite UTC",
        "period": _format_period(period),
        "confidence_now": _confidence_phrase(policies, version),
        "regime_boundary_bp": summary.get("regime_boundary_bp"),
        "regime_boundary_status": summary.get("regime_boundary_status")
        or ("configured" if summary.get("regime_boundary_bp") is not None else "absent"),
        "viability_status": _viability_status(summary),
        "barrier_measurement": summary.get("barrier_measurement"),
        "decision": _decision_label(verb),
        "verb": verb,
        "sample": _sample_phrase(
            posterior_n,
            comparable and _sample_is_comparable(summary, block_kind),
            summary,
            block_kind,
        ),
        "target_stop": _target_stop_phrase(summary),
        "signal": _signal_phrase(summary),
        "side": _side_phrase(summary),
        "backtest_sample": _backtest_sample_phrase(summary),
        "geometry_bundle": _geometry_bundle_phrase(policies, version),
        "reason": reason,
    }


def _history_line(diagnosis: ScalpJevDiagnosis) -> dict[str, Any]:
    panel = _json_load(diagnosis.panel_json) or {}
    return {
        "date": diagnosis.closed_day.isoformat(),
        "label": _fmt_day(diagnosis.closed_day + timedelta(days=1)),
        "verb": diagnosis.verb,
        "text": diagnosis.operator_reason,
        "decision": panel.get("decision") or _decision_label(diagnosis.verb),
    }


def history_payload(db: Session) -> list[dict[str, Any]]:
    rows = db.query(ScalpJevDiagnosis).order_by(ScalpJevDiagnosis.closed_day.desc()).limit(12).all()
    items = [_history_line(row) for row in rows]
    manuals = (
        db.query(ScalpConfidenceVersion)
        .filter(ScalpConfidenceVersion.source == SOURCE_REVERT_MANUAL)
        .order_by(ScalpConfidenceVersion.applied_at.desc())
        .limit(6)
        .all()
    )
    for version in manuals:
        day = version.applied_at.date()
        items.append(
            {
                "date": day.isoformat(),
                "label": _fmt_day(day),
                "verb": VERB_REVERT,
                "text": (
                    f"Voltei atrás. A versão {version.version_n} voltou a valer. "
                    "A posição que já estava aberta sai como estava."
                ),
                "decision": _decision_label(VERB_REVERT),
            }
        )
    items.sort(key=lambda row: row["date"], reverse=True)
    return items[:12]


def _next_version_n(db: Session) -> int:
    current = (
        db.query(ScalpConfidenceVersion).order_by(ScalpConfidenceVersion.version_n.desc()).first()
    )
    return 1 if current is None else int(current.version_n) + 1


def _deactivate_all(db: Session) -> None:
    for row in db.query(ScalpConfidenceVersion).filter(ScalpConfidenceVersion.active.is_(True)):
        row.active = False
        db.add(row)


def _activate_version(
    db: Session,
    *,
    policies: dict[str, Any],
    closed: date,
    reason: str,
    source: str,
    previous: Optional[ScalpConfidenceVersion],
    choice_until: Optional[datetime],
    validated_until: Optional[datetime],
    fingerprint: Optional[str] = None,
    now: Optional[datetime] = None,
    reuse: Optional[ScalpConfidenceVersion] = None,
) -> ScalpConfidenceVersion:
    stamp = now or _utcnow()
    fp = fingerprint or fingerprint_of(policies)
    existing = reuse or (
        db.query(ScalpConfidenceVersion).filter(ScalpConfidenceVersion.fingerprint == fp).first()
    )
    _deactivate_all(db)
    if existing is not None:
        existing.active = True
        existing.applied_at = stamp
        existing.applied_for_day = closed
        existing.reason = reason
        existing.source = source
        if source not in {SOURCE_REVERT_AUTO, SOURCE_REVERT_MANUAL}:
            existing.previous_id = None if previous is None else previous.id
        # A reverted fingerprint keeps the posterior cutoff that rejected it.
        # Otherwise reactivating an older row makes already-used windows appear
        # new to the next automatic validation.
        existing.choice_until = choice_until
        existing.validated_until = validated_until
        db.add(existing)
        db.flush()
        return existing
    version = ScalpConfidenceVersion(
        id=str(uuid.uuid4()),
        version_n=_next_version_n(db),
        fingerprint=fp,
        policies_json=_json_dump(policies),
        previous_id=None if previous is None else previous.id,
        applied_at=stamp,
        applied_for_day=closed,
        reason=reason,
        source=source,
        active=True,
        choice_until=choice_until,
        validated_until=validated_until,
        created_at=stamp,
    )
    db.add(version)
    db.flush()
    return version


def _split_posterior(
    windows: list[Any],
    current: Optional[ScalpConfidenceVersion],
) -> tuple[list[Any], list[Any]]:
    ordered = sorted(windows, key=lambda item: item[0].at)
    if current is not None:
        cutoff = current.validated_until or current.choice_until
        if cutoff is not None:
            ordered = [item for item in ordered if item[0].at > cutoff]
    if len(ordered) <= POSTERIOR_MIN:
        return [], ordered
    cut = len(ordered) - POSTERIOR_MIN
    return ordered[:cut], ordered[cut:]


def _refresh_existing_diagnosis_after_boundary_measure(
    db: Session,
    existing: ScalpJevDiagnosis,
    summary: dict[str, Any],
    *,
    closed: date,
    stamp: datetime,
) -> None:
    """Reconcile stored panel/summary after log bootstrap measured regime_boundary_bp."""
    if summary.get("regime_boundary_bp") is None:
        return
    period = None
    if existing.period_start is not None and existing.period_end is not None:
        period = (existing.period_start, existing.period_end)
    newest = existing.period_end
    last_end = existing.period_end
    current = active_version(db)
    policies = policies_of(current)
    block_kind = existing.block_kind
    blocked = existing.blocked
    verb = existing.verb
    reason = existing.operator_reason or existing.reason or ""
    if existing.block_kind == "regime_boundary":
        quality = _quality_block(
            summary,
            newest_candle=newest,
            last_window_end=last_end,
        )
        if quality is not None:
            block_kind, reason = quality[0], quality[1]
            blocked = True
            verb = VERB_BLOCK
        else:
            block_kind = None
            blocked = False
    comparable_flag = existing.posterior_n >= POSTERIOR_MIN and _sample_is_comparable(
        summary, block_kind
    )
    panel = build_panel(
        closed=closed,
        shown_on=stamp.date(),
        verb=verb,
        reason=reason,
        posterior_n=existing.posterior_n,
        comparable=comparable_flag,
        summary=summary,
        policies=policies,
        version=current,
        period=period,
        block_kind=block_kind,
    )
    existing.summary_json = _json_dump(summary)
    existing.panel_json = _json_dump(panel)
    existing.block_kind = block_kind
    existing.blocked = blocked
    existing.verb = verb
    existing.reason = reason
    existing.operator_reason = reason
    if current is not None:
        existing.applied_version_id = current.id
    db.add(existing)


def _store_diagnosis(
    db: Session,
    *,
    closed: date,
    now: datetime,
    summary: dict[str, Any],
    verb: str,
    reason: str,
    operator_reason: str,
    blocked: bool,
    block_kind: Optional[str],
    posterior_n: int,
    operable: bool,
    fingerprint: Optional[str],
    applied: Optional[ScalpConfidenceVersion],
    panel: dict[str, Any],
    period: Optional[tuple[datetime, datetime]],
) -> ScalpJevDiagnosis:
    existing = diagnosis_for(db, closed)
    if existing is not None:
        return existing
    row = ScalpJevDiagnosis(
        closed_day=closed,
        run_at=now,
        period_start=None if period is None else period[0],
        period_end=None if period is None else period[1],
        measurement_status=str((summary.get("measurement") or {}).get("status") or "não aplicável"),
        verb=verb,
        reason=reason,
        operator_reason=operator_reason,
        blocked=blocked,
        block_kind=block_kind,
        posterior_n=posterior_n,
        operable=operable,
        fingerprint=fingerprint,
        applied_version_id=None if applied is None else applied.id,
        panel_json=_json_dump(panel),
        summary_json=_json_dump(summary),
        created_at=now,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def run_closed_day_diagnosis(
    db: Session,
    *,
    now: Optional[datetime] = None,
    summary: Optional[dict[str, Any]] = None,
    realized_windows: Optional[list[Any]] = None,
    newest_candle: Optional[datetime] = None,
    last_window_end: Optional[datetime] = None,
    fee_bp: Decimal = Decimal("10"),
    closed: Optional[date] = None,
) -> ScalpJevDiagnosis:
    """Persist one diagnosis for the closed UTC day and maybe apply confidence."""
    stamp = now or _utcnow()
    closed = closed or closed_day_for(stamp)
    existing = diagnosis_for(db, closed)
    if existing is not None:
        if _version_lacks_regime_boundary(db):
            summary_payload = _json_load(existing.summary_json)
            if not isinstance(summary_payload, dict):
                summary_payload = {}
            _try_measure_regime_boundary_from_log(
                db,
                summary_payload,
                closed=closed,
                now=stamp,
            )
            _refresh_existing_diagnosis_after_boundary_measure(
                db,
                existing,
                summary_payload,
                closed=closed,
                stamp=stamp,
            )
            db.commit()
            db.refresh(existing)
        return existing
    ruler = _load_ruler()
    log_decisions: list[Any] = []
    if summary is None:
        from app.services.scalp_service import _regime_boundary_bp

        fee_bp, fee_source = _account_maker_fee(db)
        log_path = log_file_path()
        if not log_path.exists():
            decisions, refusals, malformed = [], {}, 0
        else:
            decisions, refusals, malformed = ruler.parse_log(log_path)
        log_decisions = list(decisions)
        until = day_end(closed)
        if decisions:
            need_from = min(d.at for d in decisions)
            need_to = until + timedelta(hours=24)
        else:
            need_from = need_to = until
        series, ohlcv_read = ruler.load_candles(need_from=need_from, need_to=need_to)
        _report, summary = ruler.build_report(
            log_path=log_path,
            decisions=decisions,
            refusals=refusals,
            malformed=malformed,
            series=series,
            ohlcv_note=ohlcv_read.reason,
            ohlcv_read=ohlcv_read,
            fee_bp=fee_bp,
            fee_source=fee_source,
            regime_boundary_bp=_regime_boundary_bp(db),
            rng_seed=seed_for_day(closed),
            until=until,
        )
        _attach_offline_backtest(summary, fee_bp=fee_bp)
        windows = ruler.non_overlapping(decisions)
        windows = [d for d in windows if d.at + timedelta(seconds=ruler.HORIZON_S) <= until]
        realized_windows = [(d, ruler.realized_for(d, series)) for d in windows]
        if series.candles:
            last_stamp, _o, _h, _l, _c = series.candles[-1]
            newest_candle = last_stamp + series.step
        last_window_end = None
        if windows:
            last_window_end = max(d.at + timedelta(seconds=ruler.HORIZON_S) for d in windows)

    assert summary is not None
    rows = list(realized_windows or [])
    boundary_decisions = log_decisions or [decision for decision, _realized in rows]
    _maybe_measure_and_persist_regime_boundary(
        db,
        summary,
        boundary_decisions,
        closed=closed,
        now=stamp,
    )
    current = active_version(db)
    current_policies = policies_of(current)
    state = get_calibration_state(db)
    shown_on = stamp.date()
    # Only windows with a realized price can be evidence for choosing or
    # validating confidence. Unpriced/indeterminate windows do not count
    # toward the independent 200-window posterior floor.
    measured_rows = [
        (decision, realized) for decision, realized in rows if realized.signed_bp is not None
    ]
    period = (
        (
            min(decision.at for decision, _realized in measured_rows),
            max(decision.at for decision, _realized in measured_rows)
            + timedelta(seconds=ruler.HORIZON_S),
        )
        if measured_rows
        else None
    )
    eligible_rows, _verdict_sources = ruler.eligible_population(measured_rows, fee_bp=fee_bp)
    # Apply and reversal use only independent priced windows that pass every
    # non-confidence entry gate. Raw log rows and unpriced windows cannot
    # inflate the posterior floor.
    choice_rows, posterior_rows = _split_posterior(eligible_rows, current)
    boundary_raw = summary.get("regime_boundary_bp")
    boundary_bp = Decimal(boundary_raw) if boundary_raw is not None else None
    if choice_rows:
        declared_conf = _policies_from_windows(
            choice_rows, fee_bp=fee_bp, boundary_bp=boundary_bp, ruler=ruler
        )
    else:
        declared_conf = confidence_only(current_policies)
    declared = bundle_from_summary(
        declared_conf,
        summary,
        backtest=summary.get("backtest"),
    )
    declared_fp = fingerprint_of(declared)
    posterior_n = len(posterior_rows)
    comparable = posterior_n >= POSTERIOR_MIN
    quality = _quality_block(summary, newest_candle=newest_candle, last_window_end=last_window_end)

    def _finish(
        *,
        verb: str,
        reason: str,
        blocked: bool,
        block_kind: Optional[str],
        applied: Optional[ScalpConfidenceVersion] = None,
        policies: Optional[dict[str, Any]] = None,
        comparable_flag: bool = comparable,
    ) -> ScalpJevDiagnosis:
        used_policies = policies if policies is not None else policies_of(applied or current)
        panel = build_panel(
            closed=closed,
            shown_on=shown_on,
            verb=verb,
            reason=reason,
            posterior_n=posterior_n,
            comparable=comparable_flag,
            summary=summary,
            policies=used_policies,
            version=applied or current,
            period=period,
            block_kind=block_kind,
        )
        return _store_diagnosis(
            db,
            closed=closed,
            now=stamp,
            summary=summary,
            verb=verb,
            reason=reason,
            operator_reason=reason,
            blocked=blocked,
            block_kind=block_kind,
            posterior_n=posterior_n,
            operable=bool(summary.get("operable")),
            fingerprint=declared_fp,
            applied=applied,
            panel=panel,
            period=period,
        )

    if quality is not None:
        kind, phrase = quality
        return _finish(verb=VERB_BLOCK, reason=phrase, blocked=True, block_kind=kind)

    if state.paused:
        return _finish(
            verb=VERB_BLOCK,
            reason=(
                "O ajuste automático está em pausa. O aviso ficou. "
                "A confiança não mudou. Ligar o ajuste não liga o scalp."
            ),
            blocked=True,
            block_kind="paused",
        )

    if not comparable:
        return _finish(
            verb=VERB_BLOCK,
            reason=(
                f"Não mudei nada. Só há {posterior_n} janelas históricas com preço que passaram pelos filtros, "
                "abaixo de 200. Com este alvo e este stop "
                "o scalp não se paga. A confiança fica como está. Alvo, stop e o prazo "
                "do scalp não mudam."
            ),
            blocked=True,
            block_kind="posterior",
            comparable_flag=False,
        )

    if (
        state.suppressed_fingerprint
        and state.suppressed_day == stamp.date()
        and state.suppressed_fingerprint == declared_fp
    ):
        return _finish(
            verb=VERB_BLOCK,
            reason="Hoje já voltei atrás nesta versão. O automático não a volta a aplicar no mesmo dia.",
            blocked=True,
            block_kind="suppressed",
        )

    same_day_apply = (
        db.query(ScalpConfidenceVersion)
        .filter(ScalpConfidenceVersion.applied_for_day == closed)
        .first()
    )
    if same_day_apply is not None:
        return _finish(
            verb=VERB_KEEP,
            reason="Neste dia fechado a confiança já tinha mudado uma vez. Não muda duas vezes.",
            blocked=True,
            block_kind="once_per_day",
        )

    if choice_rows and current is not None and current.fingerprint == declared_fp:
        return _finish(
            verb=VERB_KEEP,
            reason="A confiança já é esta. Não apliquei a mesma versão outra vez.",
            blocked=False,
            block_kind=None,
        )

    declared_net = _policy_net_bp(
        posterior_rows,
        confidence_only(declared),
        fee_bp=fee_bp,
        boundary_bp=boundary_bp,
        ruler=ruler,
    )
    current_net = _policy_net_bp(
        posterior_rows,
        confidence_only(current_policies),
        fee_bp=fee_bp,
        boundary_bp=boundary_bp,
        ruler=ruler,
    )

    posterior_policies = (
        _policies_from_windows(
            posterior_rows,
            fee_bp=fee_bp,
            boundary_bp=boundary_bp,
            ruler=ruler,
        )
        if posterior_rows
        else current_policies
    )
    reopen = False
    for regime in (REGIME_CALM, REGIME_ACTIVE):
        was = policy_from_map(confidence_only(current_policies), regime=regime)
        now_kind = confidence_only(declared).get(regime, {}).get("kind")
        posterior_kind = posterior_policies.get(regime, {}).get("kind")
        if (
            was.kind == CONFIDENCE_POLICY_CLOSED
            and now_kind
            in {
                CONFIDENCE_POLICY_NUMERIC,
                CONFIDENCE_POLICY_OFF,
            }
            and posterior_kind in {CONFIDENCE_POLICY_NUMERIC, CONFIDENCE_POLICY_OFF}
        ):
            # An open posterior policy confirms the regime can reopen. OFF may
            # still have negative net return; positive return is not required.
            reopen = True

    improves = declared_net is not None and current_net is not None and declared_net > current_net
    bundle_ready = backtest_promotion_ready(summary)

    if current is not None and current.previous_id and current.applied_for_day < closed:
        previous = version_by_id(db, current.previous_id)
        if previous is not None:
            previous_net = _policy_net_bp(
                posterior_rows,
                policies_of(previous),
                fee_bp=fee_bp,
                boundary_bp=boundary_bp,
                ruler=ruler,
            )
            if (
                current_net is not None
                and previous_net is not None
                and current_net < previous_net
                and not improves
            ):
                restored = _activate_version(
                    db,
                    policies=policies_of(previous),
                    closed=closed,
                    reason="A versão aplicada passou a perder mais do que a anterior.",
                    source=SOURCE_REVERT_AUTO,
                    previous=current,
                    choice_until=posterior_rows[-1][0].at if posterior_rows else None,
                    validated_until=posterior_rows[-1][0].at if posterior_rows else None,
                    fingerprint=previous.fingerprint,
                    now=stamp,
                    reuse=previous,
                )
                phrase = (
                    f"Voltei atrás. A versão {restored.version_n} voltou a valer. "
                    "A posição que já estava aberta sai como estava."
                )
                return _finish(
                    verb=VERB_REVERT,
                    reason=phrase,
                    blocked=False,
                    block_kind=None,
                    applied=restored,
                    policies=policies_of(restored),
                )

    if not bundle_ready and not reopen and not improves:
        return _finish(
            verb=VERB_KEEP,
            reason=(
                "Mantive. A nova não perdia menos do que a que já valia, "
                "mesmo ainda no prejuízo. A confiança fica."
            ),
            blocked=False,
            block_kind="no_improvement",
        )

    applied = _activate_version(
        db,
        policies=declared,
        closed=closed,
        reason=(
            "Apliquei alvo, stop, prazo, recorte e confiança juntos; o backtest provou lucro líquido."
            if bundle_ready
            else (
                "A posterior confirmou que o regime pode voltar a operar; o retorno ainda pode ser negativo."
                if reopen and not improves
                else "A nova perdia menos, já com a taxa."
            )
        ),
        source=SOURCE_AUTOMATIC,
        previous=current,
        choice_until=choice_rows[-1][0].at if choice_rows else None,
        validated_until=posterior_rows[-1][0].at if posterior_rows else None,
        fingerprint=declared_fp,
        now=stamp,
    )
    phrase = (
        "Apliquei. A entrada seguinte já usa esta confiança. "
        "Alvo, stop e o prazo do scalp não mudam. O interruptor não foi desligado."
    )
    return _finish(
        verb=VERB_APPLY,
        reason=phrase,
        blocked=False,
        block_kind=None,
        applied=applied,
        policies=declared,
    )


def maybe_run_daily(db: Session, *, now: Optional[datetime] = None) -> Optional[ScalpJevDiagnosis]:
    stamp = now or _utcnow()
    if stamp.hour == 0 and stamp.minute < RUN_AFTER_MINUTE:
        return None
    return run_closed_day_diagnosis(db, now=stamp)


def revert_to_previous(
    db: Session, *, now: Optional[datetime] = None
) -> Optional[ScalpConfidenceVersion]:
    """Manual revert to the registered previous version. No 200 wait. Next entry."""
    stamp = now or _utcnow()
    current = active_version(db)
    if current is None or not current.previous_id:
        return None
    previous = version_by_id(db, current.previous_id)
    if previous is None:
        return None
    cutoffs = [
        value
        for value in (
            current.choice_until,
            current.validated_until,
            previous.choice_until,
            previous.validated_until,
        )
        if value is not None
    ]
    cutoff = max(cutoffs) if cutoffs else None
    restored = _activate_version(
        db,
        policies=policies_of(previous),
        closed=stamp.date(),
        reason="Reversão manual para a versão anterior registada.",
        source=SOURCE_REVERT_MANUAL,
        previous=current,
        choice_until=cutoff,
        validated_until=cutoff,
        fingerprint=previous.fingerprint,
        now=stamp,
        reuse=previous,
    )
    state = get_calibration_state(db)
    state.suppressed_fingerprint = current.fingerprint
    state.suppressed_day = stamp.date()
    state.updated_at = stamp
    db.add(state)
    db.commit()
    db.refresh(restored)
    return restored


def status_fields(db: Session) -> dict[str, Any]:
    state = get_calibration_state(db)
    version = active_version(db)
    previous = version_by_id(db, version.previous_id) if version is not None else None
    latest = db.query(ScalpJevDiagnosis).order_by(ScalpJevDiagnosis.closed_day.desc()).first()
    policies = policies_of(version)
    panel = _json_load(latest.panel_json) if latest is not None else None
    if latest is not None and isinstance(panel, dict):
        # Keep the closed-day record immutable, while projecting its facts
        # through the current policy and the corrected trader-facing copy.
        panel = dict(panel)
        summary = _json_load(latest.summary_json) or {}
        period = (
            (latest.period_start, latest.period_end)
            if latest.period_start is not None and latest.period_end is not None
            else None
        )
        panel["period"] = _format_period(period)
        panel["regime_boundary_bp"] = summary.get("regime_boundary_bp")
        panel["regime_boundary_status"] = summary.get("regime_boundary_status") or (
            "configured" if summary.get("regime_boundary_bp") is not None else "absent"
        )
        panel["viability_status"] = _viability_status(summary)
        panel["barrier_measurement"] = summary.get("barrier_measurement")
        priced_total = int(
            (
                (summary.get("measurement") or {}).get(
                    "n_priced", (summary.get("stats") or {}).get("n_priced", 0)
                )
            )
            or 0
        )
        posterior_n = int(latest.posterior_n or 0)
        if priced_total:
            posterior_n = min(posterior_n, priced_total)
        eligible_total = int((summary.get("eligible_population") or {}).get("n") or 0)
        posterior_n = min(posterior_n, eligible_total)
        panel["data_ok"] = _data_quality_phrase(summary, period, latest.block_kind, posterior_n)
        panel["target_stop"] = _target_stop_phrase(summary)
        panel["sample"] = _sample_phrase(
            posterior_n,
            posterior_n >= POSTERIOR_MIN and _sample_is_comparable(summary, latest.block_kind),
            summary,
            latest.block_kind,
        )
        panel["backtest_sample"] = _backtest_sample_phrase(summary)
        panel["geometry_bundle"] = _geometry_bundle_phrase(policies, version)
        panel["confidence_now"] = _confidence_phrase(policies, version)
        closed_regimes = [
            "calmo" if regime == REGIME_CALM else "agitado"
            for regime in (REGIME_CALM, REGIME_ACTIVE)
            if policy_from_map(policies, regime=regime).kind == CONFIDENCE_POLICY_CLOSED
        ]
        if state.paused:
            panel["calibration_note"] = (
                "O ajuste automático está pausado. Isso não liga nem desliga o scalp."
            )
        elif closed_regimes:
            panel["calibration_note"] = (
                "O ajuste automático está ligado ao processamento dos diagnósticos, mas as "
                f"entradas continuam bloqueadas no regime {' e '.join(closed_regimes)}. "
                "Isso não liga o scalp nem envia ordens."
            )
        else:
            panel["calibration_note"] = (
                "O ajuste automático processa diagnósticos e não liga o scalp nem envia ordens."
            )
    return {
        "calibration_paused": bool(state.paused),
        "calibration_enabled": not bool(state.paused),
        "confidence_version": (
            None
            if version is None
            else {
                "id": version.id,
                "version_n": version.version_n,
                "fingerprint": version.fingerprint,
                "previous": (
                    None
                    if previous is None
                    else {
                        "id": previous.id,
                        "version_n": previous.version_n,
                        "policies": policies_of(previous),
                    }
                ),
                "current": policies,
                "reason": version.reason,
                "source": version.source,
            }
        ),
        "jev_diagnosis": (
            None
            if latest is None or not isinstance(panel, dict)
            else {
                **panel,
                "history": history_payload(db),
                "can_revert": bool(version is not None and version.previous_id),
            }
        ),
    }


def switches_untouched(db: Session, user_id: str) -> dict[str, Any]:
    row = db.query(ScalpUserState).filter(ScalpUserState.user_id == str(user_id)).first()
    return {
        "enabled": bool(row.enabled) if row is not None else False,
        "killed": bool(row.killed) if row is not None else False,
    }
