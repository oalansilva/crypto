"""Backtest individual de ação e ETF da Binance (card #1119).

Reúne o que as rotas ``POST /api/combos/backtest`` e ``POST /api/combos/optimize``
compartilham para uma ação ou ETF:

* quem roda e em qual tempo gráfico (decisões 2 e 5);
* a coleta sob demanda, só do que a execução usa (decisão 4);
* a identidade do ativo e as convenções da execução, que vão na resposta (decisões 12 e 13).

A coleta chama ``HistoryService.ensure`` (decisão 5 do #1118). Seletor, filtro, busca e
análises recusadas nunca chegam aqui.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from typing import Any, Optional

import pandas as pd

from app.metrics.backtest_execution_costs import (
    fee_for_class,
    slippage_for_timeframe,
    stop_gap_enabled,
)

from app.services.market_data_providers import EQUITY_BACKTEST_TIMEFRAMES

logger = logging.getLogger(__name__)

# Tempos de estratégia de ação/ETF: 1d nativo; 15m, 1h e 4h montados do 5m no pregão regular.
ALL_HISTORY_START = "2000-01-01"
CODE_HISTORY_UNAVAILABLE = "history_unavailable"
CODE_TIMEFRAME_NOT_SUPPORTED = "timeframe_not_supported"
EQUITY_TIMEFRAME_MESSAGE = "Ação e ETF rodam em 15m, 1h, 4h ou 1d."
CURRENCY_BY_CLASS = {"stock": "USD", "etf": "USD"}

# Motivos curtos para o texto do 422 (o código cru da Binance nunca aparece).
_FAILURE_TEXT = {
    "binance_rate_limited": "limite de requisições da Binance",
    "binance_unavailable": "Binance indisponível",
    "binance_business_error": "a Binance recusou o pedido",
    "binance_format_changed": "formato da Binance mudou",
    "binance_circuit_open": "coleta em pausa por falhas seguidas da Binance",
    "internal_error": "erro interno na coleta",
}

_DATE_ONLY = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def is_equity_class(asset_class: str | None) -> bool:
    return str(asset_class or "").lower() in ("stock", "etf")


def inclusive_end(value: Any) -> Any:
    """Data sem hora no fim da janela vale até o fim desse dia (``2024-01-31`` inclui o pregão)."""

    if isinstance(value, str) and _DATE_ONLY.match(value.strip()):
        return (
            pd.Timestamp(value.strip(), tz="UTC")
            + pd.Timedelta(days=1)
            - pd.Timedelta(microseconds=1)
        )
    return value


class EquityRunError(Exception):
    """Falha que a rota devolve como 422 estruturado."""

    def __init__(self, code: str, message: str, **extra: Any) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.extra = extra

    def detail(self) -> dict[str, Any]:
        return {"code": self.code, "message": self.message, **self.extra}


def timeframe_refusal(timeframe: str) -> Optional[EquityRunError]:
    """1m, 5m (e 30m) não são tempo de estratégia de ação/ETF; o motivo vai antes de rodar."""

    tf = str(timeframe or "").strip().lower()
    if tf in EQUITY_BACKTEST_TIMEFRAMES:
        return None
    return EquityRunError(
        CODE_TIMEFRAME_NOT_SUPPORTED,
        f"{EQUITY_TIMEFRAME_MESSAGE} O tempo {tf or '(vazio)'} não roda para ação e ETF.",
        timeframe=tf,
    )


def failure_text(code: str | None) -> str:
    return _FAILURE_TEXT.get(code or "", "falha na coleta")


def history_unavailable_message(symbol: str, reason: str) -> str:
    return (
        f"Histórico de {symbol} indisponível agora: {reason}. " "Tente de novo em alguns minutos."
    )


# ---------------------------------------------------------------- identidade


def crypto_identity(symbol: str) -> dict[str, Any]:
    sym = str(symbol or "").strip().upper()
    base, _, quote = sym.partition("/")
    return {
        "symbol": sym,
        "asset_id": f"binance:spot:{sym}",
        "asset_class": "crypto",
        "name": base or sym,
        "currency": quote or "USDT",
    }


def asset_identity(symbol: str) -> dict[str, Any]:
    """``asset = {symbol, asset_id, asset_class, name, currency}`` da execução (decisão 12)."""

    sym = str(symbol or "").strip().upper()
    if "/" in sym:
        return crypto_identity(sym)
    from app.database import SessionLocal
    from app.models_asset_catalog import AssetCatalog

    db = SessionLocal()
    try:
        row = (
            db.query(AssetCatalog)
            .filter(AssetCatalog.symbol == sym, AssetCatalog.asset_class.in_(["stock", "etf"]))
            .order_by(AssetCatalog.removed_at.isnot(None), AssetCatalog.asset_id)
            .first()
        )
        if row is None:
            return {
                "symbol": sym,
                "asset_id": None,
                "asset_class": None,
                "name": sym,
                "currency": "USD",
            }
        return {
            "symbol": sym,
            "asset_id": row.asset_id,
            "asset_class": row.asset_class,
            "name": row.name or sym,
            "currency": CURRENCY_BY_CLASS.get(row.asset_class, "USD"),
        }
    finally:
        db.close()


def build_conventions(
    *,
    asset_class: str | None,
    timeframe: str,
    direction: str = "long",
    gap_stops: int = 0,
) -> dict[str, Any]:
    """``conventions`` da resposta: custos, calendário, fração e short."""

    cls = str(asset_class or "crypto").lower()
    equity = is_equity_class(cls)
    fee, confirmed = fee_for_class(cls)
    return {
        "fee": fee,
        "fee_confirmed": bool(confirmed),
        "slippage": slippage_for_timeframe(timeframe),
        "calendar": {
            "kind": "nyse_regular_session" if equity else "24x7",
            "timezone": "America/New_York" if equity else "UTC",
            "years": "calendar_days_365",
            "sessions_per_year": 252 if equity else None,
        },
        "fraction": ({"simulated": True, "confirms_account": False} if equity else None),
        "short": (
            {"simulated": True, "confirms_account": False}
            if str(direction or "long").lower() == "short"
            else None
        ),
        "gap_exit": {"enabled": stop_gap_enabled(), "stops_with_gap": int(gap_stops or 0)},
        "adjusted_prices": equity,
    }


def finalize_execution(
    execution: dict[str, Any] | None,
    *,
    asset: dict[str, Any],
    timeframe: str,
    direction: str,
    requested: dict[str, Any],
    frame: pd.DataFrame | None,
    collection: dict[str, Any] | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Completa ``execution`` (janelas, coleta) e devolve ``(execution, conventions)``."""

    out = dict(execution or {})
    out.setdefault("timeframe", timeframe)
    first = last = None
    if frame is not None and len(frame):
        idx = pd.DatetimeIndex(frame.index)
        first, last = idx.min(), idx.max()
    out["window"] = {
        "requested": {"start": requested.get("start"), "end": requested.get("end")},
        "covered": {
            "start": first.isoformat() if first is not None else None,
            "end": last.isoformat() if last is not None else None,
            "candles": int(len(frame)) if frame is not None else 0,
        },
    }
    out["collection"] = collection
    conventions = build_conventions(
        asset_class=asset.get("asset_class"),
        timeframe=timeframe,
        direction=direction,
        gap_stops=int(out.get("gap_stops") or 0),
    )
    return out, conventions


# ---------------------------------------------------------------- coleta


@dataclass
class EquityPreparation:
    asset: dict[str, Any]
    collection: dict[str, Any] | None = None
    ensured: list[str] = field(default_factory=list)


def _spec_for(symbol: str, timeframe: str):
    from app.services.market_history.facade import spec_for_request

    return spec_for_request(symbol=symbol, timeframe=timeframe)


def prepare_equity_history(
    symbol: str,
    timeframe: str,
    start: Any,
    end: Any,
    *,
    intrabar: bool,
    service: Any = None,
) -> EquityPreparation:
    """Coleta sob demanda só o que o backtest de 1 ativo usa (decisão 4).

    * a série do tempo gráfico (1d nativo, ou o 5m de onde saem 15m/1h/4h);
    * com intrabar pedido, o 5m que monta o 15m (mesma série física nos tempos intradiários).

    Falha sem nada gravado na janela levanta ``EquityRunError`` (422 ``history_unavailable``);
    falha com parte gravada segue e devolve a nota "janela coberta menor que a pedida".
    """

    from app.services.market_history.facade import get_history_service
    from app.services.market_history.model import HistoryError

    tf = str(timeframe).strip().lower()
    refusal = timeframe_refusal(tf)
    if refusal is not None:
        raise refusal
    svc = service or get_history_service()
    start = start or ALL_HISTORY_START  # "todo o histórico": onde a Binance começa
    end_ts = inclusive_end(end)
    asset = asset_identity(symbol)
    try:
        chart = svc.resolve(_spec_for(symbol, tf))
        wanted = [("candles", chart)]
        if intrabar:
            wanted.append(("intraday", svc.resolve(_spec_for(symbol, "15m"))))
    except HistoryError as exc:
        raise EquityRunError(exc.code, str(exc)) from exc

    prep = EquityPreparation(asset=asset)
    seen: set[int] = set()
    outcomes: list[tuple[str, Any]] = []
    for role, series in wanted:
        if series.series_id in seen:
            continue
        seen.add(series.series_id)
        outcome = svc.ensure(series, start, end_ts)
        outcomes.append((role, outcome))
        prep.ensured.append(series.physical_timeframe)

    result = svc.read(chart, start, end_ts)
    problem = next((o for _, o in outcomes if o.status in ("failed", "paused", "waiting")), None)
    if result.candles is None or result.candles.empty:
        if problem is not None and problem.status == "failed":
            reason = failure_text(problem.error_code)
            raise EquityRunError(
                CODE_HISTORY_UNAVAILABLE,
                history_unavailable_message(asset["symbol"], reason),
                symbol=asset["symbol"],
                reason=reason,
                error_code=problem.error_code,
            )
        if problem is not None:  # coleta em pausa ou outra rodando sem resultado
            reason = "coleta em andamento"
        else:
            reason = f"a Binance não tem candles de {tf} de {asset['symbol']} nessa janela"
        raise EquityRunError(
            CODE_HISTORY_UNAVAILABLE,
            history_unavailable_message(asset["symbol"], reason),
            symbol=asset["symbol"],
            reason=reason,
        )

    if problem is not None:
        prep.collection = _partial_note(asset["symbol"], chart, result, problem, end_ts)
    return prep


def _partial_note(symbol, chart, result, problem, end_ts) -> dict[str, Any] | None:
    """Nota "Janela coberta menor que a pedida" (decisão 4): a coleta parou com parte guardada.

    Dois cortes possíveis: o fim (a atualização da cauda parou) e o começo (o preenchimento para trás
    parou antes de chegar ao início pedido). Fim de semana e feriado não contam como corte.
    """

    cov = result.coverage
    covered_start = cov["covered"]["start"]
    covered_end = cov["covered"]["end"]
    if covered_end is None or covered_start is None:
        return None
    requested_start = cov["requested"]["start"]
    requested_end = cov["requested"]["end"] or (
        pd.Timestamp(end_ts).tz_convert("UTC").strftime("%Y-%m-%dT%H:%M:%SZ")
        if end_ts is not None
        else pd.Timestamp.now(tz="UTC").strftime("%Y-%m-%dT%H:%M:%SZ")
    )
    first, last = pd.Timestamp(covered_start), pd.Timestamp(covered_end)
    tolerance = pd.Timedelta(days=4)
    left_out: list[dict[str, str]] = []
    stops: list[str] = []
    if requested_start is not None and not cov.get("reached_start"):
        wanted_start = pd.Timestamp(requested_start)
        if first - wanted_start > tolerance:
            left_out.append(
                {
                    "from": wanted_start.strftime("%Y-%m-%d"),
                    "to": (first - pd.Timedelta(days=1)).strftime("%Y-%m-%d"),
                }
            )
            stops.append("head")
    wanted_end = pd.Timestamp(requested_end)
    if wanted_end - last > tolerance:
        left_out.append(
            {
                "from": (last + pd.Timedelta(days=1)).strftime("%Y-%m-%d"),
                "to": wanted_end.strftime("%Y-%m-%d"),
            }
        )
        stops.append("tail")
    if not left_out:
        return None
    reason = (
        failure_text(problem.error_code) if problem.status == "failed" else "coleta interrompida"
    )
    return {
        "status": "partial",
        "kind": "both" if len(stops) == 2 else stops[0],
        "series": chart.physical_timeframe,
        "symbol": symbol,
        "reason": reason,
        "stopped_after": covered_end,
        "covered": cov["covered"],
        "requested": cov["requested"],
        "left_out": left_out,
    }
