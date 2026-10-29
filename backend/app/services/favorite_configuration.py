"""Configuração de dados do favorito: fonte, sessão e ajuste (card #1122, decisão 11).

Um helper único deriva a configuração de ``data_source`` + ``asset`` + ``conventions`` e devolve os
rótulos curto, compacto e longo. A mesma regra vale para o backfill da migração, para a gravação
(resultado, lote, Descoberta) e para a chave de duplicata.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any

SOURCE_CCXT = "ccxt"
SOURCE_BINANCE_EQUITY = "binance_equity"
SOURCE_STOOQ = "stooq"

SESSION_24X7 = "24x7"
SESSION_REGULAR_NY = "regular_ny"
SESSION_EOD = "eod"

ADJUSTMENT_NONE = "none"
ADJUSTMENT_SPLIT = "split"
ADJUSTMENT_LEGACY = "legacy"

_PERIOD_KEY = re.compile(
    r"(period|length|window|lookback|ema|sma|wma|\bma\d|slow|fast|long|signal)", re.IGNORECASE
)


@dataclass(frozen=True)
class FavoriteConfiguration:
    data_source: str
    session: str
    adjustment: str

    def as_tuple(self) -> tuple[str, str, str]:
        return (self.data_source, self.session, self.adjustment)

    @property
    def is_crypto(self) -> bool:
        return self.data_source == SOURCE_CCXT

    @property
    def is_legacy(self) -> bool:
        return self.data_source == SOURCE_STOOQ

    def labels(self) -> dict[str, str]:
        return configuration_labels(self.data_source, self.session, self.adjustment)

    def payload(self) -> dict[str, str]:
        return {
            "data_source": self.data_source,
            "session": self.session,
            "adjustment": self.adjustment,
            **self.labels(),
        }


CRYPTO_CONFIGURATION = FavoriteConfiguration(SOURCE_CCXT, SESSION_24X7, ADJUSTMENT_NONE)
EQUITY_CONFIGURATION = FavoriteConfiguration(
    SOURCE_BINANCE_EQUITY, SESSION_REGULAR_NY, ADJUSTMENT_SPLIT
)
LEGACY_CONFIGURATION = FavoriteConfiguration(SOURCE_STOOQ, SESSION_EOD, ADJUSTMENT_LEGACY)


def _decode(value: Any) -> Any:
    if isinstance(value, str):
        try:
            return json.loads(value)
        except (TypeError, ValueError):
            return None
    return value


def _normalized_source(value: Any) -> str | None:
    raw = str(value or "").strip().lower()
    if raw in {"binance_equity", "binance-equity"}:
        return SOURCE_BINANCE_EQUITY
    if raw in {"stooq", "stooq-eod", "stooq_eod"}:
        return SOURCE_STOOQ
    if raw in {"ccxt", "binance", "crypto", "default"}:
        return SOURCE_CCXT
    return None


def derive_configuration(
    symbol: str,
    *,
    data_source: Any = None,
    parameters: Any = None,
    conventions: Any = None,
) -> FavoriteConfiguration:
    """Configuração pela regra do spec ``favorite-configuration-identity``.

    - par com ``/`` → ``ccxt``/``24x7``/``none``;
    - fonte ``binance_equity`` → ``regular_ny``/``split`` (ou o que ``conventions`` disser);
    - ticker sem fonte → ``stooq``/``eod``/``legacy`` (fonte antiga).
    """

    sym = str(symbol or "").strip().upper()
    if "/" in sym:
        return CRYPTO_CONFIGURATION
    params = _decode(parameters)
    params = params if isinstance(params, dict) else {}
    source = _normalized_source(data_source) or _normalized_source(params.get("data_source"))
    if source == SOURCE_BINANCE_EQUITY:
        conv = _decode(conventions)
        conv = conv if isinstance(conv, dict) else {}
        calendar = conv.get("calendar") if isinstance(conv.get("calendar"), dict) else {}
        session = SESSION_REGULAR_NY
        if calendar.get("kind") and calendar.get("kind") != "nyse_regular_session":
            session = str(calendar.get("kind"))
        adjustment = ADJUSTMENT_SPLIT
        if conv.get("adjusted_prices") is False:
            adjustment = ADJUSTMENT_NONE
        return FavoriteConfiguration(SOURCE_BINANCE_EQUITY, session, adjustment)
    if source == SOURCE_CCXT:
        # Ticker gravado com fonte de cripto não existe; trata como fonte antiga.
        return LEGACY_CONFIGURATION
    return LEGACY_CONFIGURATION


def configuration_of_row(row: Any) -> FavoriteConfiguration:
    """Configuração gravada na linha; sem colunas (linha antiga em memória), deriva pela regra."""

    source = getattr(row, "data_source", None)
    session = getattr(row, "session", None)
    adjustment = getattr(row, "adjustment", None)
    if source and session and adjustment:
        return FavoriteConfiguration(str(source), str(session), str(adjustment))
    metrics = _decode(getattr(row, "metrics", None))
    conventions = metrics.get("analysis_conventions") if isinstance(metrics, dict) else None
    return derive_configuration(
        getattr(row, "symbol", ""),
        parameters=getattr(row, "parameters", None),
        conventions=conventions,
    )


def default_configuration_for_symbol(symbol: str) -> FavoriteConfiguration:
    """Configuração padrão do símbolo pela classe do catálogo: cripto ``ccxt``; ação/ETF Binance."""

    return CRYPTO_CONFIGURATION if "/" in str(symbol or "") else EQUITY_CONFIGURATION


def configuration_labels(data_source: str, session: str, adjustment: str) -> dict[str, str]:
    source = _normalized_source(data_source) or str(data_source or "")
    if source == SOURCE_CCXT:
        return {
            "label_short": "Binance Spot · 24/7",
            "label_compact": "Binance Spot · 24/7",
            "label_long": "Binance Spot · 24/7",
        }
    if source == SOURCE_STOOQ:
        return {
            "label_short": "Stooq · fonte antiga · diário",
            "label_compact": "Stooq · antiga · diário",
            "label_long": "Stooq · fonte antiga · diário",
        }
    session_short = "NY" if session == SESSION_REGULAR_NY else str(session or "")
    session_long = "pregão regular de NY" if session == SESSION_REGULAR_NY else str(session or "")
    adj_short = "split" if adjustment == ADJUSTMENT_SPLIT else "sem ajuste"
    adj_long = "ajustado por split" if adjustment == ADJUSTMENT_SPLIT else "sem ajuste"
    return {
        "label_short": f"Binance Ações · {session_short} · {adj_short}",
        "label_compact": f"Binance · {session_short} · {adj_short}",
        "label_long": f"Binance Ações · {session_long} · {adj_long}",
    }


def configuration_from_request(
    symbol: str,
    *,
    data_source: Any = None,
    session: Any = None,
    adjustment: Any = None,
    parameters: Any = None,
    conventions: Any = None,
) -> FavoriteConfiguration:
    """Configuração de um pedido (``exists``/create): campos explícitos ou a padrão do símbolo."""

    explicit = _normalized_source(data_source)
    if explicit is None:
        params = _decode(parameters)
        params = params if isinstance(params, dict) else {}
        explicit = _normalized_source(params.get("data_source"))
    if explicit is None:
        base = default_configuration_for_symbol(symbol)
    else:
        base = derive_configuration(symbol, data_source=explicit, conventions=conventions)
    return FavoriteConfiguration(
        base.data_source,
        str(session).strip() if session else base.session,
        str(adjustment).strip() if adjustment else base.adjustment,
    )


def required_candles(parameters: Any) -> int:
    """Candles que a análise do favorito precisa: maior período dos parâmetros + 1 (0 sem período)."""

    params = _decode(parameters)
    params = params if isinstance(params, dict) else {}
    longest = 0
    for key, value in params.items():
        if key in {"stop_loss", "direction", "data_source"} or isinstance(value, bool):
            continue
        if not _PERIOD_KEY.search(str(key)):
            continue
        try:
            longest = max(longest, int(float(value)))
        except (TypeError, ValueError):
            continue
    return longest + 1 if longest >= 2 else 0
