"""Comparação da estratégia com uma referência escolhida (card #1123, decisões 4 a 6 e 10).

* ``compute``: função pura. Período comum encaixado nos fechamentos diários da referência,
  retorno da referência (último ÷ primeiro fechamento − 1), retorno da estratégia (composto dos
  trades fechados de dentro), CAGR dos dois lados com dias corridos ÷ 365,25, diferença em p.p.,
  o que ficou de fora, aviso de moeda e motivos sem número (``no_history | no_overlap |
  short_overlap``). Nunca devolve zero no lugar de "sem comparação": o caminho novo não usa o 0,0
  de ``metrics.benchmark.calculate_buy_and_hold`` (Descoberta e holdout seguem com ele).
* ``ReferenceSource``: coleta (``prepare_equity_history`` para ação/ETF, ``HistoryService`` para
  cripto) com teto de tempo, leitura da série 1d e congelamento da amostra (papel ``benchmark``).
* ``create_comparison``: carrega, calcula, congela e grava uma ``BenchmarkComparison``. Falha na
  coleta sem nada guardado não grava nada (``BenchmarkCollectionError``).
* ``get_comparison``/``summary``: leitura do que foi gravado, sem cálculo.
"""

from __future__ import annotations

import concurrent.futures
import logging
import math
import os
import uuid
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from typing import Any, Iterable, Optional

import pandas as pd

logger = logging.getLogger(__name__)

MIN_COMMON_DAYS = 30
DAYS_PER_YEAR = 365.25
EQUITY_CLASSES = ("stock", "etf")
NY_TZ = "America/New_York"
CURRENCY_NOTE_TEXT = "USDT tratado como USD, sem conversão. A comparação é só em percentual."
CLASS_LABEL = {"crypto": "Cripto", "stock": "Ação", "etf": "ETF"}
DEFAULT_COLLECT_TIMEOUT_SECONDS = 90.0
SAMPLE_EXPIRED = "sample_expired"


def auto_record_enabled() -> bool:
    """Gravação automática (rodada nova e refresh do favorito). Os testes antigos a desligam."""

    return os.getenv("BENCHMARK_AUTO_RECORD", "1").strip().lower() not in {
        "0",
        "false",
        "no",
        "off",
    }


class BenchmarkError(Exception):
    """Pedido de comparação que não pode ser atendido (422)."""

    code = "benchmark_error"

    def __init__(self, message: str, *, code: str | None = None, **extra: Any) -> None:
        super().__init__(message)
        if code:
            self.code = code
        self.message = message
        self.extra = extra

    def detail(self) -> dict[str, Any]:
        return {"code": self.code, "message": self.message, **self.extra}


class BenchmarkCollectionError(BenchmarkError):
    """A coleta da referência falhou sem nada guardado: nada é gravado (decisão 6)."""

    code = "reference_collection_failed"


# --------------------------------------------------------------------------- datas e textos


def _is_equity(asset_class: Optional[str]) -> bool:
    return str(asset_class or "").lower() in EQUITY_CLASSES


def to_day(value: Any, asset_class: Optional[str] = None) -> Optional[date]:
    """Data do calendário do lado: UTC na cripto, Nova York em ação/ETF. Data pura fica como está."""

    if value is None or value == "":
        return None
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    text = str(value).strip()
    if len(text) == 10 and text[4] == "-" and text[7] == "-":
        return date.fromisoformat(text)
    try:
        ts = pd.Timestamp(value)
    except (TypeError, ValueError):
        return None
    if pd.isna(ts):
        return None
    if ts.tzinfo is None:
        ts = ts.tz_localize("UTC")
    if _is_equity(asset_class):
        return ts.tz_convert(NY_TZ).date()
    return ts.tz_convert("UTC").date()


def br_date(value: Optional[date]) -> str:
    return value.strftime("%d/%m/%Y") if value else ""


def iso_day(value: Optional[date]) -> Optional[str]:
    return value.isoformat() if value else None


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _finite(value: Any) -> Optional[float]:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


# --------------------------------------------------------------------------- identidades


def reference_identity(symbol: str) -> dict[str, Any]:
    """``{symbol, asset_id, asset_class, name, currency}`` pelo símbolo (cripto) ou catálogo (ação/ETF)."""

    from app.services.equity_backtest import asset_identity

    return asset_identity(symbol)


def return_kind_of(asset_class: Optional[str]) -> str:
    return "price_no_dividends" if _is_equity(asset_class) else "price"


def return_kind_text(kind: Optional[str]) -> str:
    return (
        "Retorno de preço, sem dividendos" if kind == "price_no_dividends" else "Retorno de preço"
    )


def currency_note_of(
    strategy_currency: Optional[str], reference_currency: Optional[str]
) -> Optional[str]:
    a = str(strategy_currency or "").upper()
    b = str(reference_currency or "").upper()
    if not a or not b or a == b:
        return None
    return "usdt_as_usd"


# --------------------------------------------------------------------------- lado da estratégia


@dataclass
class StrategySide:
    symbol: str
    asset_class: Optional[str]
    currency: Optional[str]
    window_start: Optional[date]
    window_end: Optional[date]
    trades: list[dict[str, Any]] = field(default_factory=list)
    direction: str = "long"
    window_state: str = "registrado"  # registrado | deduzido
    snapshot_id: Optional[str] = None
    version_label: Optional[str] = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "symbol": self.symbol,
            "asset_class": self.asset_class,
            "currency": self.currency,
            "window": {
                "start": iso_day(self.window_start),
                "end": iso_day(self.window_end),
                "state": self.window_state,
            },
            "direction": self.direction,
        }


def closed_trades(trades: Iterable[dict[str, Any]] | None) -> list[dict[str, Any]]:
    out = []
    for trade in trades or []:
        if not isinstance(trade, dict):
            continue
        if not trade.get("exit_time") or not trade.get("entry_time"):
            continue
        if trade.get("exit_price") in (None, "", 0) and trade.get("profit") is None:
            continue
        out.append(trade)
    out.sort(key=lambda t: str(t.get("entry_time")))
    return out


def strategy_side(
    *,
    symbol: str,
    asset: Optional[dict[str, Any]],
    window: Optional[dict[str, Any]],
    requested: Optional[dict[str, Any]] = None,
    trades: Iterable[dict[str, Any]] | None = None,
    direction: Optional[str] = None,
    snapshot_id: Optional[str] = None,
    version_label: Optional[str] = None,
) -> StrategySide:
    """Janela da estratégia: a coberta gravada; sem ela, o período pedido marcado ``deduzido``."""

    ident = dict(asset or {})
    if not ident.get("asset_class"):
        ident = {**reference_identity(symbol), **{k: v for k, v in ident.items() if v}}
    asset_class = ident.get("asset_class")
    start = to_day((window or {}).get("start"), asset_class)
    end = to_day((window or {}).get("end"), asset_class)
    state = "registrado"
    if start is None or end is None:
        start = start or to_day((requested or {}).get("start"), asset_class)
        end = end or to_day((requested or {}).get("end"), asset_class)
        state = "deduzido"
    trade_list = closed_trades(trades)
    if trade_list and (start is None or end is None):
        start = start or to_day(trade_list[0].get("entry_time"), asset_class)
        end = end or to_day(max(str(t.get("exit_time")) for t in trade_list), asset_class)
        state = "deduzido"
    side = str(direction or "long").lower()
    return StrategySide(
        symbol=str(symbol or "").upper(),
        asset_class=asset_class,
        currency=ident.get("currency"),
        window_start=start,
        window_end=end,
        trades=trade_list,
        direction="short" if side == "short" else "long",
        window_state=state,
        snapshot_id=snapshot_id,
        version_label=version_label,
    )


def strategy_from_context(context: dict[str, Any]) -> StrategySide:
    """Lado da estratégia a partir do resultado de ``optimize``/``backtest`` (ou do corpo da troca)."""

    execution = context.get("execution") if isinstance(context.get("execution"), dict) else {}
    window = (execution.get("window") or {}) if isinstance(execution, dict) else {}
    prov = (
        context.get("data_provenance") if isinstance(context.get("data_provenance"), dict) else {}
    )
    symbol = str(context.get("symbol") or "").strip().upper()
    if not symbol:
        raise BenchmarkError("Informe o símbolo da estratégia.", code="strategy_symbol_required")
    parameters = context.get("parameters") if isinstance(context.get("parameters"), dict) else {}
    direction = context.get("direction") or parameters.get("direction")
    requested = (
        {"start": context.get("start_date"), "end": context.get("end_date")}
        if context.get("start_date") or context.get("end_date")
        else window.get("requested")
    )
    return strategy_side(
        symbol=symbol,
        asset=context.get("asset") if isinstance(context.get("asset"), dict) else None,
        window=window.get("covered"),
        requested=requested,
        trades=context.get("trades") if isinstance(context.get("trades"), list) else [],
        direction=direction,
        snapshot_id=context.get("snapshot_id") or prov.get("snapshot_id"),
        version_label=prov.get("version_label"),
    )


def _decode_json(value: Any) -> Any:
    import json

    for _ in range(2):
        if isinstance(value, str):
            try:
                value = json.loads(value)
            except (TypeError, ValueError):
                return None
    return value


def strategy_from_favorite(favorite: Any) -> StrategySide:
    """Lado da estratégia com os trades e a janela gravados no favorito (último refresh)."""

    metrics = _decode_json(favorite.metrics)
    metrics = metrics if isinstance(metrics, dict) else {}
    parameters = _decode_json(favorite.parameters)
    parameters = parameters if isinstance(parameters, dict) else {}
    execution = (
        metrics.get("analysis_execution")
        if isinstance(metrics.get("analysis_execution"), dict)
        else {}
    )
    window = (execution.get("window") or {}) if isinstance(execution, dict) else {}
    prov = (
        metrics.get("data_provenance") if isinstance(metrics.get("data_provenance"), dict) else {}
    )
    asset = metrics.get("analysis_asset") or metrics.get("asset")
    return strategy_side(
        symbol=str(favorite.symbol),
        asset=asset if isinstance(asset, dict) else None,
        window=window.get("covered"),
        requested={"start": favorite.start_date, "end": favorite.end_date},
        trades=metrics.get("trades") if isinstance(metrics.get("trades"), list) else [],
        direction=parameters.get("direction"),
        snapshot_id=favorite.snapshot_id,
        version_label=prov.get("version_label"),
    )


def switch_favorite_comparison(db, favorite: Any, payload: dict[str, Any]) -> None:
    """Troca o ponteiro do favorito, fixa a amostra nova e solta a anterior (mesmo commit)."""

    previous = get_comparison(db, favorite.benchmark_comparison_id)
    favorite.benchmark_comparison_id = payload["id"]
    db.flush()
    pin_reference(db, payload)
    if previous and previous.get("id") != payload.get("id"):
        release_reference(db, previous, keep=[reference_snapshot_id(payload)])


def refresh_favorite_comparison(
    db, favorite_id: int, *, source: Optional["ReferenceSource"] = None
) -> Optional[dict[str, Any]]:
    """Refresh do favorito com sucesso: refaz com a referência escolhida (ou o próprio ativo).

    É o único recálculo (decisão 5) e acompanha o "Backtest atualizado" já visível em Favoritos.
    """

    from app.models import FavoriteStrategy

    favorite = db.query(FavoriteStrategy).filter(FavoriteStrategy.id == favorite_id).first()
    if favorite is None:
        return None
    previous = get_comparison(db, favorite.benchmark_comparison_id)
    reference = None
    if previous and (previous.get("reference") or {}).get("kind") != "own":
        reference = (previous.get("reference") or {}).get("symbol")
    strategy = strategy_from_favorite(favorite)
    payload = create_comparison(
        db,
        strategy,
        reference,
        owner_kind="favorite",
        user_id=favorite.user_id,
        trigger="favorite_refresh",
        favorite_id=favorite.id,
        source=source,
        commit=False,
    )
    switch_favorite_comparison(db, favorite, payload)
    db.commit()
    return payload


def record_run_default(
    result: dict[str, Any], user_id: Optional[str], *, source: Optional["ReferenceSource"] = None
) -> tuple[Optional[dict[str, Any]], Optional[dict[str, Any]]]:
    """Comparação padrão (próprio ativo, ``trigger=run``) de uma rodada nova.

    Nunca derruba a rodada: falha vira ``(None, erro)`` e a tela mostra o motivo.
    """

    if not auto_record_enabled():
        return None, None
    from app.database import SessionLocal

    db = SessionLocal()
    try:
        strategy = strategy_from_context(result)
        payload = create_comparison(
            db, strategy, None, owner_kind="result", user_id=user_id, trigger="run", source=source
        )
        return payload, None
    except BenchmarkError as exc:
        db.rollback()
        return None, exc.detail()
    except Exception as exc:  # pragma: no cover - a rodada segue sem a comparação
        db.rollback()
        logger.warning("Comparação padrão da rodada falhou: %s", exc, exc_info=True)
        return None, {
            "code": "benchmark_failed",
            "message": "Não foi possível gravar a comparação com o próprio ativo.",
        }
    finally:
        db.close()


# --------------------------------------------------------------------------- série da referência


def daily_closes(frame: pd.DataFrame | None, asset_class: Optional[str]) -> pd.Series:
    """Fechamentos 1d indexados pela data do calendário da referência (UTC ou Nova York)."""

    if frame is None or len(frame) == 0 or "close" not in frame:
        return pd.Series(dtype="float64")
    index = pd.DatetimeIndex(frame.index)
    if index.tz is None:
        index = index.tz_localize("UTC")
    tz = NY_TZ if _is_equity(asset_class) else "UTC"
    days = [ts.date() for ts in index.tz_convert(tz)]
    series = pd.Series(pd.to_numeric(frame["close"], errors="coerce").to_numpy(), index=days)
    series = series[series.notna() & (series > 0)]
    series = series[~series.index.duplicated(keep="last")]
    return series.sort_index()


# --------------------------------------------------------------------------- cálculo puro


def _cagr(total_return: float, days: int) -> Optional[float]:
    if days <= 0:
        return None
    base = 1.0 + total_return
    if base <= 0:
        return -1.0
    return base ** (DAYS_PER_YEAR / days) - 1.0


def _trade_days(
    trade: dict[str, Any], asset_class: Optional[str]
) -> tuple[Optional[date], Optional[date]]:
    return to_day(trade.get("entry_time"), asset_class), to_day(trade.get("exit_time"), asset_class)


def _insufficient(code: str, text: str, short: str) -> dict[str, Any]:
    return {"code": code, "text": text, "short": short}


def compute(
    strategy: StrategySide,
    reference: dict[str, Any],
    closes: pd.Series,
    *,
    min_days: int = MIN_COMMON_DAYS,
) -> dict[str, Any]:
    """Contrato ``BenchmarkComparison`` sem id, dono e amostras (design, decisão 4).

    ``reference``: ``{kind: own|catalog, symbol, asset_id, asset_class, currency, name}``.
    ``closes``: fechamentos 1d da referência indexados por data (``daily_closes``).
    """

    ref_class = reference.get("asset_class")
    ref_symbol = str(reference.get("symbol") or "")
    ref = {
        "kind": reference.get("kind") or "catalog",
        "symbol": ref_symbol,
        "asset_id": reference.get("asset_id"),
        "asset_class": ref_class,
        "currency": reference.get("currency"),
        "name": reference.get("name") or ref_symbol,
        "return_kind": return_kind_of(ref_class),
        "long_only": True,
    }
    out: dict[str, Any] = {
        "reference": ref,
        "strategy": {
            **strategy.as_dict(),
            "return": None,
            "cagr": None,
            "trades_in": None,
            "trades_out": None,
        },
        "reference_result": None,
        "common_window": None,
        "left_out": [],
        "delta": None,
        "currency_note": currency_note_of(strategy.currency, ref.get("currency")),
        "status": "insufficient",
        "reason": None,
        "history": {
            "first": iso_day(closes.index[0]) if len(closes) else None,
            "last": iso_day(closes.index[-1]) if len(closes) else None,
        },
        "min_days": int(min_days),
    }
    s_start, s_end = strategy.window_start, strategy.window_end
    if len(closes) == 0:
        out["reason"] = _insufficient(
            "no_history",
            f"{ref_symbol} não tem fechamento diário guardado na Binance. Não há período comum.",
            f"Sem histórico diário de {ref_symbol}.",
        )
        return out
    first_day, last_day = closes.index[0], closes.index[-1]
    if s_start is None or s_end is None:
        out["reason"] = _insufficient(
            "no_overlap",
            "A janela da estratégia não foi registrada. Não há período comum.",
            "Sem janela registrada da estratégia.",
        )
        return out
    lo, hi = max(s_start, first_day), min(s_end, last_day)
    inside = closes[(closes.index >= lo) & (closes.index <= hi)] if lo <= hi else closes.iloc[0:0]
    if len(inside) == 0:
        if first_day > s_end:
            text = (
                f"{ref_symbol} tem histórico desde {br_date(first_day)}, depois do fim da estratégia "
                f"({br_date(s_end)}). Não há período comum."
            )
        elif last_day < s_start:
            text = (
                f"{ref_symbol} tem histórico até {br_date(last_day)}, antes do início da estratégia "
                f"({br_date(s_start)}). Não há período comum."
            )
        else:
            text = f"{ref_symbol} não tem fechamento diário no período da estratégia. Não há período comum."
        out["reason"] = _insufficient("no_overlap", text, f"Sem período comum com {ref_symbol}.")
        return out
    c_start, c_end = inside.index[0], inside.index[-1]
    days = (c_end - c_start).days
    out["common_window"] = {"start": iso_day(c_start), "end": iso_day(c_end), "days": int(days)}
    if days < min_days:
        short = f"Período comum de {days} dias: o mínimo é {min_days}."
        if first_day > s_start:
            detail = (
                f" {ref_symbol} tem histórico desde {br_date(first_day)} e a estratégia termina em "
                f"{br_date(s_end)}."
            )
        elif last_day < s_end:
            detail = (
                f" {ref_symbol} tem histórico até {br_date(last_day)} e a estratégia começa em "
                f"{br_date(s_start)}."
            )
        else:
            detail = f" A janela da estratégia vai de {br_date(s_start)} a {br_date(s_end)}."
        out["reason"] = _insufficient("short_overlap", short + detail, short)
        return out

    trades_in: list[dict[str, Any]] = []
    before = after = 0
    for trade in strategy.trades:
        entry, exit_ = _trade_days(trade, strategy.asset_class)
        if entry is not None and exit_ is not None and entry >= c_start and exit_ <= c_end:
            trades_in.append(trade)
        elif entry is not None and entry < c_start:
            before += 1
        else:
            after += 1
    equity = 1.0
    for trade in trades_in:
        profit = _finite(trade.get("profit")) or 0.0
        equity *= 1.0 + profit
    s_return = equity - 1.0
    r_first, r_last = float(inside.iloc[0]), float(inside.iloc[-1])
    r_return = r_last / r_first - 1.0
    s_cagr = _cagr(s_return, days)
    r_cagr = _cagr(r_return, days)

    left_out: list[dict[str, Any]] = []
    covers_strategy_start = first_day <= s_start
    covers_strategy_end = last_day >= s_end
    if c_start > s_start:
        left_out.append(
            {
                "start": iso_day(s_start),
                "end": iso_day(c_start - timedelta(days=1)),
                "trades": before,
                "note": (
                    "no_session"
                    if covers_strategy_start and _is_equity(ref_class)
                    else "no_reference"
                ),
            }
        )
    elif before:
        left_out.append(
            {"start": iso_day(s_start), "end": iso_day(c_start), "trades": before, "note": "edge"}
        )
    if c_end < s_end:
        left_out.append(
            {
                "start": iso_day(c_end + timedelta(days=1)),
                "end": iso_day(s_end),
                "trades": after,
                "note": (
                    "no_session"
                    if covers_strategy_end and _is_equity(ref_class)
                    else "no_reference"
                ),
            }
        )
    elif after:
        left_out.append(
            {"start": iso_day(c_end), "end": iso_day(s_end), "trades": after, "note": "edge"}
        )

    out["strategy"].update(
        {
            "return": s_return,
            "cagr": s_cagr,
            "trades_in": len(trades_in),
            "trades_out": before + after,
        }
    )
    out["reference_result"] = {
        "return": r_return,
        "cagr": r_cagr,
        "first_close": {"date": iso_day(c_start), "price": r_first},
        "last_close": {"date": iso_day(c_end), "price": r_last},
    }
    out["left_out"] = left_out
    out["delta"] = {
        "cagr_pp": (s_cagr - r_cagr) * 100.0 if s_cagr is not None and r_cagr is not None else None
    }
    out["status"] = "valid"
    out["reason"] = None
    return out


def expired_sample_payload(
    strategy: StrategySide, reference: dict[str, Any], expired_at: Optional[str]
) -> dict[str, Any]:
    """Célula da coluna extra cujo candidato perdeu a amostra: sem dado novo, sem número."""

    payload = compute(strategy, reference, pd.Series(dtype="float64"))
    when = ""
    if expired_at:
        day = to_day(expired_at)
        when = f" em {br_date(day)}" if day else ""
    payload["common_window"] = None
    payload["reason"] = _insufficient(
        SAMPLE_EXPIRED,
        f"Amostra do candidato vencida{when}. Rode a varredura de novo para comparar.",
        f"Amostra do candidato vencida{when}.",
    )
    payload["reason"]["expired_at"] = expired_at
    return payload


# --------------------------------------------------------------------------- fonte da referência


@dataclass
class LoadedReference:
    identity: dict[str, Any]
    frame: pd.DataFrame  # 1d inteiro guardado (índice UTC)
    collected: bool = False
    partial_note: Optional[str] = None


class ReferenceSource:
    """Coleta, leitura e congelamento da série 1d da referência (#1118). Trocável nos testes."""

    def __init__(self, timeout_seconds: Optional[float] = None) -> None:
        env = os.getenv("BENCHMARK_COLLECT_TIMEOUT_SECONDS", "").strip()
        self.timeout = float(
            timeout_seconds or (env and float(env)) or DEFAULT_COLLECT_TIMEOUT_SECONDS
        )

    # -- identidade --------------------------------------------------------------
    def identity(self, symbol: str) -> dict[str, Any]:
        return reference_identity(symbol)

    def _series(self, symbol: str):
        from app.services.market_history.facade import get_history_service, spec_for_request

        service = get_history_service()
        return service, service.resolve(spec_for_request(symbol=symbol, timeframe="1d"))

    def has_history(self, symbol: str) -> bool:
        """Já há 1d guardado? (só leitura; decide "Coletando…" antes do cálculo)."""

        try:
            service, series = self._series(symbol)
            result = service.read(series, limit=1)
            return result.candles is not None and not result.candles.empty
        except Exception:
            return False

    # -- coleta + leitura ----------------------------------------------------------
    def _collect(self, symbol: str, identity: dict[str, Any], start: Any, end: Any) -> None:
        from app.services.equity_backtest import (
            EquityRunError,
            inclusive_end,
            prepare_equity_history,
        )

        if _is_equity(identity.get("asset_class")):
            try:
                prepare_equity_history(symbol, "1d", start, end, intrabar=False)
            except EquityRunError as exc:
                if exc.extra.get("error_code"):
                    raise BenchmarkCollectionError(
                        exc.message, symbol=identity.get("symbol"), reason=exc.extra.get("reason")
                    ) from exc
                # Binance sem candles nessa janela: não é falha; o motivo sai do histórico guardado.
            return
        service, series = self._series(symbol)
        outcome = service.ensure(series, start, inclusive_end(end) if end else None)
        if outcome.status == "failed":
            stored = service.read(series, limit=1)
            if stored.candles is None or stored.candles.empty:
                from app.services.equity_backtest import failure_text

                raise BenchmarkCollectionError(
                    f"Não foi possível coletar o histórico de {identity.get('symbol')} na Binance "
                    f"({failure_text(outcome.error_code)}).",
                    symbol=identity.get("symbol"),
                    reason=failure_text(outcome.error_code),
                )

    def load(
        self, symbol: str, start: Any = None, end: Any = None, *, collect: bool = True
    ) -> LoadedReference:
        identity = self.identity(symbol)
        if identity.get("asset_class") is None:
            raise BenchmarkError(
                f"{symbol} não está no catálogo de ativos.",
                code="reference_not_in_catalog",
                symbol=symbol,
            )
        collected = False
        if collect:
            had = self.has_history(symbol)
            pool = concurrent.futures.ThreadPoolExecutor(max_workers=1)
            future = pool.submit(self._collect, symbol, identity, start, end)
            try:
                future.result(timeout=self.timeout)
            except concurrent.futures.TimeoutError as exc:
                if not self.has_history(symbol):
                    raise BenchmarkCollectionError(
                        f"Não foi possível coletar o histórico de {identity.get('symbol')} na Binance "
                        "(tempo esgotado).",
                        symbol=identity.get("symbol"),
                        reason="tempo esgotado",
                    ) from exc
            finally:
                pool.shutdown(wait=False)
            collected = not had
        service, series = self._series(symbol)
        result = service.read(series)
        return LoadedReference(identity=identity, frame=result.candles, collected=collected)

    # -- amostra ----------------------------------------------------------------
    def freeze(
        self,
        symbol: str,
        frame: pd.DataFrame,
        start: Optional[date],
        end: Optional[date],
        owner_ref: str,
    ) -> dict[str, Any]:
        """Congela só a série 1d do período comum (papel ``benchmark``) e devolve a proveniência."""

        from app.services.market_history.sample import ExecutionSample, to_loader_format

        piece = frame
        if start is not None and end is not None and frame is not None and len(frame):
            index = pd.DatetimeIndex(frame.index)
            if index.tz is None:
                index = index.tz_localize("UTC")
            lo = pd.Timestamp(start, tz="UTC") - pd.Timedelta(days=1)
            hi = pd.Timestamp(end, tz="UTC") + pd.Timedelta(days=2)
            piece = frame[(index >= lo) & (index < hi)]
        sample = ExecutionSample("benchmark", owner_ref=owner_ref)
        sample.freeze_symbol(
            "benchmark", symbol, "1d", iso_day(start), iso_day(end), to_loader_format(piece)
        )
        sample.finish()
        prov = sample.provenance("benchmark")
        return {
            "snapshot_id": sample.snapshot_id,
            "version_label": prov.get("version_label"),
            "data_version": prov.get("data_version"),
            "content_sha256": prov.get("content_sha256"),
            "source": prov.get("data_source"),
            "session": prov.get("session"),
            "adjustment": prov.get("adjustment"),
        }

    def version_only(self, symbol: str) -> dict[str, Any]:
        try:
            service, series = self._series(symbol)
            series = service.read(series, limit=1).series
            from app.services.market_history.model import SOURCE_LABELS

            return {
                "snapshot_id": None,
                "version_label": str(series.data_version),
                "data_version": series.data_version,
                "content_sha256": None,
                "source": SOURCE_LABELS.get(series.source, series.source),
                "session": series.session,
                "adjustment": series.adjustment,
            }
        except Exception:
            return {"snapshot_id": None, "version_label": None}


_default_source: Optional[ReferenceSource] = None


def get_reference_source() -> ReferenceSource:
    global _default_source
    if _default_source is None:
        _default_source = ReferenceSource()
    return _default_source


def set_reference_source(source: Optional[ReferenceSource]) -> None:
    global _default_source
    _default_source = source


# --------------------------------------------------------------------------- gravação


def _reference_for(
    strategy: StrategySide, reference_symbol: Optional[str], source: ReferenceSource
) -> tuple[str, str]:
    symbol = str(reference_symbol or "").strip().upper()
    if not symbol or symbol in {"OWN", "PROPRIO", "PRÓPRIO"} or symbol == strategy.symbol:
        return strategy.symbol, "own"
    return symbol, "catalog"


def build_payload(
    strategy: StrategySide,
    reference_symbol: Optional[str] = None,
    *,
    source: Optional[ReferenceSource] = None,
    owner_ref: str = "benchmark",
    collect: bool = True,
    loaded: Optional[LoadedReference] = None,
    reference_sample: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    """Carrega (coletando se faltar), calcula e congela. Levanta ``BenchmarkCollectionError``."""

    source = source or get_reference_source()
    symbol, kind = _reference_for(strategy, reference_symbol, source)
    if loaded is None:
        loaded = source.load(
            symbol, iso_day(strategy.window_start), iso_day(strategy.window_end), collect=collect
        )
    identity = {**loaded.identity, "kind": kind}
    closes = daily_closes(loaded.frame, identity.get("asset_class"))
    payload = compute(strategy, identity, closes)
    common = payload.get("common_window")
    if reference_sample is not None:
        ref_sample = dict(reference_sample)
    elif common:
        ref_sample = source.freeze(
            symbol,
            loaded.frame,
            date.fromisoformat(common["start"]),
            date.fromisoformat(common["end"]),
            owner_ref,
        )
    else:
        ref_sample = source.version_only(symbol)
    payload["samples"] = {
        "strategy": (
            {"snapshot_id": strategy.snapshot_id, "version_label": strategy.version_label}
            if strategy.snapshot_id or strategy.version_label
            else None
        ),
        "reference": ref_sample,
    }
    payload["collected"] = bool(loaded.collected)
    return payload


def persist(
    db,
    payload: dict[str, Any],
    *,
    owner_kind: str,
    user_id: Optional[str],
    trigger: str,
    favorite_id: Optional[int] = None,
    result_id: Optional[str] = None,
    column_id: Optional[str] = None,
    commit: bool = True,
):
    from app.models_benchmark import BenchmarkComparison

    cid = str(uuid.uuid4())
    created = _utcnow().replace(microsecond=0)
    body = dict(payload)
    body.update(
        {
            "id": cid,
            "created_at": created.isoformat().replace("+00:00", "Z"),
            "trigger": trigger,
            "owner": {
                "kind": owner_kind,
                "favorite_id": favorite_id,
                "result_id": result_id,
                "column_id": column_id,
            },
            "user_id": user_id,
        }
    )
    # Contrato da decisão 4: nunca grava número numa comparação insuficiente.
    from app.schemas.benchmark import BenchmarkComparisonContract

    BenchmarkComparisonContract.check(body)
    row = BenchmarkComparison(
        id=cid,
        user_id=user_id,
        favorite_id=favorite_id,
        owner_kind=owner_kind,
        result_id=result_id,
        column_id=column_id,
        created_at=created.replace(tzinfo=None),
        status=body.get("status") or "insufficient",
        payload=body,
    )
    db.add(row)
    if commit:
        db.commit()
    else:
        db.flush()
    return row


def create_comparison(
    db,
    strategy: StrategySide,
    reference_symbol: Optional[str],
    *,
    owner_kind: str,
    user_id: Optional[str],
    trigger: str,
    favorite_id: Optional[int] = None,
    result_id: Optional[str] = None,
    source: Optional[ReferenceSource] = None,
    commit: bool = True,
) -> dict[str, Any]:
    owner_ref = f"benchmark:{owner_kind}:{favorite_id or result_id or strategy.symbol}"
    payload = build_payload(strategy, reference_symbol, source=source, owner_ref=owner_ref)
    row = persist(
        db,
        payload,
        owner_kind=owner_kind,
        user_id=user_id,
        trigger=trigger,
        favorite_id=favorite_id,
        result_id=result_id,
        commit=commit,
    )
    return dict(row.payload)


def get_comparison(db, comparison_id: Optional[str]) -> Optional[dict[str, Any]]:
    """Leitura do que foi gravado. Nunca calcula."""

    if not comparison_id:
        return None
    from app.models_benchmark import BenchmarkComparison

    row = db.query(BenchmarkComparison).filter(BenchmarkComparison.id == str(comparison_id)).first()
    return dict(row.payload) if row is not None else None


def get_comparisons(db, ids: Iterable[Optional[str]]) -> dict[str, dict[str, Any]]:
    wanted = sorted({str(i) for i in ids if i})
    if not wanted:
        return {}
    from app.models_benchmark import BenchmarkComparison

    rows = db.query(BenchmarkComparison).filter(BenchmarkComparison.id.in_(wanted)).all()
    return {row.id: dict(row.payload) for row in rows}


def reference_snapshot_id(payload: Optional[dict[str, Any]]) -> Optional[str]:
    samples = (payload or {}).get("samples") or {}
    return ((samples.get("reference") or {}) or {}).get("snapshot_id")


def summary(payload: Optional[dict[str, Any]]) -> Optional[dict[str, Any]]:
    """Resumo para a lista de Favoritos ("Ref.: SPY · comparação gravada 27/10")."""

    if not payload:
        return None
    ref = payload.get("reference") or {}
    return {
        "id": payload.get("id"),
        "status": payload.get("status"),
        "created_at": payload.get("created_at"),
        "trigger": payload.get("trigger"),
        "owner_kind": (payload.get("owner") or {}).get("kind"),
        "reference": {
            "kind": ref.get("kind"),
            "symbol": ref.get("symbol"),
            "asset_class": ref.get("asset_class"),
            "currency": ref.get("currency"),
        },
        "delta_cagr_pp": (payload.get("delta") or {}).get("cagr_pp"),
        "reason_code": (payload.get("reason") or {}).get("code"),
        "currency_note": payload.get("currency_note"),
    }


# --------------------------------------------------------------------------- amostras fixadas


def pin_reference(db, payload: Optional[dict[str, Any]]) -> None:
    sid = reference_snapshot_id(payload)
    if not sid:
        return
    from app.services.market_history import snapshots

    try:
        with db.begin_nested():
            snapshots.pin(db, sid)
    except Exception:  # pragma: no cover - fixação nunca derruba a gravação
        logger.warning("Não foi possível fixar a amostra da referência %s", sid, exc_info=True)


def release_reference(
    db, payload: Optional[dict[str, Any]], *, keep: Iterable[Optional[str]] = ()
) -> None:
    """Solta a amostra da referência anterior (30 dias), salvo se outro favorito ainda a usa."""

    sid = reference_snapshot_id(payload)
    if not sid or sid in {k for k in keep if k}:
        return
    from sqlalchemy import text

    from app.services.market_history import snapshots

    try:
        with db.begin_nested():
            _release_if_unused(db, sid, snapshots, text)
    except Exception:  # pragma: no cover
        logger.warning("Não foi possível soltar a amostra da referência %s", sid, exc_info=True)


def _release_if_unused(db, sid: str, snapshots: Any, text: Any) -> None:
    still = db.execute(
        text(
            "SELECT 1 FROM favorite_strategies f JOIN benchmark_comparisons b "
            "ON b.id = f.benchmark_comparison_id "
            "WHERE CAST(b.payload AS jsonb) -> 'samples' -> 'reference' ->> 'snapshot_id' = :sid "
            "LIMIT 1"
        ),
        {"sid": sid},
    ).first()
    if still is None:
        snapshots.release(db, sid)
