"""Adaptadores de origem do catálogo de ativos Binance (card #1117).

Dois adaptadores isolados, ambos puros depois do download:

* cripto: ``api/v3/exchangeInfo`` (spot), só ``quoteAsset=USDT``;
* ações e ETFs: união por ``ac`` entre ``get-symbols-static`` e
  ``get-exchange-info`` (rotas BAPI públicas, sem contrato estável).

As funções ``parse_*`` não fazem I/O e validam o schema: qualquer formato
inesperado levanta :class:`CatalogSourceError`, para que a atualização mantenha
a última lista válida (design.md, decisão 12).
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from typing import Any

import httpx

from app.symbols_config import get_excluded_symbols

# --- Constantes de domínio ---------------------------------------------------

CLASS_CRYPTO = "crypto"
CLASS_STOCK = "stock"
CLASS_ETF = "etf"
ASSET_CLASSES = (CLASS_CRYPTO, CLASS_STOCK, CLASS_ETF)

GROUP_CRYPTO = "crypto"
GROUP_EQUITY = "equity"
CATALOG_GROUPS = (GROUP_CRYPTO, GROUP_EQUITY)

STATE_TRADABLE = "tradable"
STATE_SUSPENDED = "suspended"
STATE_OFF_MARKET = "off_market"
STATE_NO_TRADING = "no_trading"
STATE_NO_RULES = "no_rules"
STATE_REMOVED = "removed"
ASSET_STATES = (
    STATE_TRADABLE,
    STATE_SUSPENDED,
    STATE_OFF_MARKET,
    STATE_NO_TRADING,
    STATE_NO_RULES,
    STATE_REMOVED,
)

# Motivos de exclusão contados em cada atualização.
EXCLUDE_LEVERAGED = "leveraged_token"
EXCLUDE_EXPLICIT = "excluded_symbols"
EXCLUDE_RIGHT_TYPE = "right_type"
EXCLUDE_RIGHT = "right"
EXCLUDE_WARRANT = "warrant"
EXCLUDE_CVR = "contingent_value_right"
EXCLUDE_NO_STATIC = "no_static_record"
EXCLUDE_UNKNOWN_TYPE = "unknown_type"
EXCLUDE_NO_IDENTIFIER = "no_identifier"
EXCLUDE_DUPLICATE = "duplicate_identifier"

SPOT_EXCHANGE_INFO_URL = "https://api.binance.com/api/v3/exchangeInfo"
EQUITY_STATIC_URL = "https://www.binance.com/bapi/equity/v1/public/equity/symbol/get-symbols-static"
EQUITY_RULES_URL = "https://www.binance.com/bapi/equity/v1/public/equity/symbol/get-exchange-info"
BINANCE_OK_CODE = "000000"

_BUSINESS_SUFFIX_UP_DOWN = ("UP", "DOWN")


class CatalogSourceError(Exception):
    """Falha de origem: rede, 429, código de negócio, schema ou queda brusca."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


@dataclass
class AssetRecord:
    asset_id: str
    asset_class: str
    symbol: str
    name: str
    binance_id: str
    state: str
    state_reason: str | None = None
    info_note: str | None = None
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass
class ParsedCatalog:
    group: str
    records: list[AssetRecord]
    input_counts: dict[str, int]
    excluded: dict[str, int]

    @property
    def result_counts(self) -> dict[str, int]:
        counts = {name: 0 for name in ASSET_CLASSES if self._group_has(name)}
        for record in self.records:
            counts[record.asset_class] = counts.get(record.asset_class, 0) + 1
        return counts

    def _group_has(self, asset_class: str) -> bool:
        if self.group == GROUP_CRYPTO:
            return asset_class == CLASS_CRYPTO
        return asset_class in (CLASS_STOCK, CLASS_ETF)

    @property
    def excluded_total(self) -> int:
        return sum(self.excluded.values())

    def to_counts(self) -> dict[str, Any]:
        return {
            "input": dict(self.input_counts),
            "excluded": dict(self.excluded),
            "excluded_total": self.excluded_total,
            "result": self.result_counts,
            "result_total": len(self.records),
        }


# --- Utilidades --------------------------------------------------------------


def normalize_search_text(value: Any) -> str:
    """Minúsculas e sem acento, para pesquisa."""
    text = unicodedata.normalize("NFKD", str(value or ""))
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    return text.lower().strip()


def build_search_key(symbol: str, name: str) -> str:
    return f"{normalize_search_text(symbol)}\n{normalize_search_text(name)}"


def crypto_asset_id(symbol: str) -> str:
    return f"binance:spot:{symbol.strip().upper()}"


def equity_asset_id(ac: str) -> str:
    return f"binance:equity:{ac.strip()}"


def _as_dict_list(value: Any, what: str) -> list[dict[str, Any]]:
    if not isinstance(value, list) or any(not isinstance(item, dict) for item in value):
        raise CatalogSourceError("schema", f"Formato inesperado em {what}.")
    return value


# --- Cripto ------------------------------------------------------------------


def is_leveraged_token(base: str, *, spot_allowed: bool, bases: set[str]) -> bool:
    """Token alavancado UP/DOWN (derivativo), sem confundir JUP ou SYRUP.

    Um par só conta como alavancado quando o sufixo UP/DOWN vem acompanhado de
    spot desligado ou quando o ativo sem o sufixo também é listado (BTCUP ->
    BTC). JUP e SYRUP não passam por nenhum dos dois critérios.
    """

    base = base.strip().upper()
    for suffix in _BUSINESS_SUFFIX_UP_DOWN:
        if base.endswith(suffix) and len(base) > len(suffix):
            stripped = base[: -len(suffix)]
            if not spot_allowed or stripped in bases:
                return True
    return False


def parse_spot_exchange_info(payload: Any) -> ParsedCatalog:
    """Interpreta ``api/v3/exchangeInfo`` (spot) e mantém só os pares USDT."""
    if not isinstance(payload, dict):
        raise CatalogSourceError("schema", "A resposta do exchangeInfo não é um objeto.")
    if "code" in payload and "symbols" not in payload:
        raise CatalogSourceError(
            "binance_error", f"A Binance respondeu com erro {payload.get('code')}."
        )
    symbols = _as_dict_list(payload.get("symbols"), "symbols do exchangeInfo")

    usdt: list[dict[str, Any]] = []
    for item in symbols:
        if "quoteAsset" not in item or "baseAsset" not in item or "status" not in item:
            raise CatalogSourceError(
                "schema", "Par do exchangeInfo sem baseAsset, quoteAsset ou status."
            )
        if str(item.get("quoteAsset") or "").upper() == "USDT":
            usdt.append(item)

    bases = {str(item["baseAsset"]).strip().upper() for item in usdt}
    explicit = get_excluded_symbols()
    excluded: dict[str, int] = {}
    records: list[AssetRecord] = []
    seen: set[str] = set()

    for item in usdt:
        base = str(item["baseAsset"]).strip().upper()
        if not base:
            excluded[EXCLUDE_NO_IDENTIFIER] = excluded.get(EXCLUDE_NO_IDENTIFIER, 0) + 1
            continue
        symbol = f"{base}/USDT"
        status = str(item.get("status") or "").upper()
        spot_allowed = item.get("isSpotTradingAllowed") is True

        if is_leveraged_token(base, spot_allowed=spot_allowed, bases=bases):
            excluded[EXCLUDE_LEVERAGED] = excluded.get(EXCLUDE_LEVERAGED, 0) + 1
            continue
        if symbol in explicit:
            excluded[EXCLUDE_EXPLICIT] = excluded.get(EXCLUDE_EXPLICIT, 0) + 1
            continue
        if symbol in seen:
            continue
        seen.add(symbol)

        if status == "TRADING" and spot_allowed:
            state, reason = STATE_TRADABLE, None
        elif status != "TRADING":
            state = STATE_SUSPENDED
            reason = f"Negociação pausada pela Binance (status {status or 'desconhecido'})."
        else:
            state = STATE_SUSPENDED
            reason = "Negociação à vista desligada pela Binance."

        records.append(
            AssetRecord(
                asset_id=crypto_asset_id(symbol),
                asset_class=CLASS_CRYPTO,
                symbol=symbol,
                name=base,
                binance_id=str(item.get("symbol") or f"{base}USDT"),
                state=state,
                state_reason=reason,
                extra={"status": status, "spot_allowed": spot_allowed},
            )
        )

    return ParsedCatalog(
        group=GROUP_CRYPTO,
        records=sorted(records, key=lambda r: r.symbol),
        input_counts={"usdt_pairs": len(usdt), "exchange_symbols": len(symbols)},
        excluded=excluded,
    )


# --- Ações e ETFs ------------------------------------------------------------

_WARRANT_NAME = re.compile(r"\bwarrants?\s*(\([^)]*\))?\s*$", re.IGNORECASE)
_RIGHT_NAME = re.compile(r"\brights?\s*(\([^)]*\))?\s*$", re.IGNORECASE)
_RIGHTS_OFFERING = re.compile(r"\brights?\s+offering\b", re.IGNORECASE)
_CVR_NAME = re.compile(r"\bcontingent\s+value\s+rights?\b", re.IGNORECASE)


def equity_exclusion_reason(static: dict[str, Any]) -> str | None:
    """Motivo de exclusão de um registro estático, ou None se for escolhível."""
    kind = str(static.get("t") or "").upper()
    symbol = str(static.get("s") or "")
    name = str(static.get("n") or "")
    if kind == "RIGHT":
        return EXCLUDE_RIGHT_TYPE
    if kind not in ("STOCK", "ETF"):
        return EXCLUDE_UNKNOWN_TYPE
    upper_symbol = symbol.upper()
    if upper_symbol.endswith(".WS"):
        return EXCLUDE_WARRANT
    if upper_symbol.endswith(".RT"):
        return EXCLUDE_RIGHT
    if _CVR_NAME.search(name):
        return EXCLUDE_CVR
    if _RIGHTS_OFFERING.search(name):
        return EXCLUDE_RIGHT
    if _WARRANT_NAME.search(name):
        return EXCLUDE_WARRANT
    if _RIGHT_NAME.search(name):
        return EXCLUDE_RIGHT
    return None


_TRADABILITY_STATES = {
    "BUY_SELL": (STATE_TRADABLE, None),
    "OFFMARKET": (
        STATE_OFF_MARKET,
        "A Binance marcou o ativo como fora de mercado (OFFMARKET).",
    ),
    "NONE": (STATE_NO_TRADING, "A Binance marcou o ativo como sem negociação (NONE)."),
}


def _equity_state(rules: dict[str, Any] | None) -> tuple[str, str | None]:
    if rules is None:
        return STATE_NO_RULES, "Está no catálogo da Binance, mas sem regras de negociação."
    tradability = str(rules.get("tradability") or "").upper()
    if tradability in _TRADABILITY_STATES:
        return _TRADABILITY_STATES[tradability]
    return (
        STATE_NO_TRADING,
        f"A Binance informou um estado de negociação desconhecido ({tradability or 'vazio'}).",
    )


def parse_equity_payloads(static_payload: Any, rules_payload: Any) -> ParsedCatalog:
    """Une ``get-symbols-static`` e ``get-exchange-info`` pelo ``ac``."""
    for payload, what in (
        (static_payload, "get-symbols-static"),
        (rules_payload, "get-exchange-info"),
    ):
        if not isinstance(payload, dict):
            raise CatalogSourceError("schema", f"A resposta de {what} não é um objeto.")
        code = payload.get("code")
        if code is not None and str(code) != BINANCE_OK_CODE:
            raise CatalogSourceError(
                "binance_error",
                f"{what} respondeu com código {code}: {payload.get('message') or 'sem mensagem'}.",
            )
        if code is None and "data" not in payload:
            raise CatalogSourceError("schema", f"{what} sem código nem dados.")

    static_rows = _as_dict_list(static_payload.get("data"), "data de get-symbols-static")
    rules_data = rules_payload.get("data")
    if not isinstance(rules_data, dict):
        raise CatalogSourceError("schema", "data de get-exchange-info não é um objeto.")
    rule_rows = _as_dict_list(rules_data.get("symbols"), "symbols de get-exchange-info")

    static_by_ac: dict[str, dict[str, Any]] = {}
    excluded: dict[str, int] = {}
    for row in static_rows:
        ac = str(row.get("ac") or "").strip()
        if not ac or not str(row.get("s") or "").strip():
            excluded[EXCLUDE_NO_IDENTIFIER] = excluded.get(EXCLUDE_NO_IDENTIFIER, 0) + 1
            continue
        if ac in static_by_ac:
            excluded[EXCLUDE_DUPLICATE] = excluded.get(EXCLUDE_DUPLICATE, 0) + 1
            continue
        static_by_ac[ac] = row

    rules_by_ac: dict[str, dict[str, Any]] = {}
    rules_without_static = 0
    for row in rule_rows:
        ac = str(row.get("assetCode") or "").strip()
        if not ac or ac not in static_by_ac:
            rules_without_static += 1
            continue
        rules_by_ac[ac] = row

    # Todo registro estático e todo registro de regras sem par estático entram
    # na união; união - excluídos = escolhíveis (spec binance-asset-catalog).
    union = len(static_rows) + rules_without_static
    if rules_without_static:
        excluded[EXCLUDE_NO_STATIC] = excluded.get(EXCLUDE_NO_STATIC, 0) + rules_without_static

    records: list[AssetRecord] = []
    for ac, row in static_by_ac.items():
        reason = equity_exclusion_reason(row)
        if reason:
            excluded[reason] = excluded.get(reason, 0) + 1
            continue
        kind = str(row.get("t")).upper()
        rules = rules_by_ac.get(ac)
        state, state_reason = _equity_state(rules)
        notes = []
        if row.get("dlt") is True or row.get("d") is True:
            notes.append("A Binance anunciou a retirada deste ativo.")
        if rules is not None and rules.get("delistingTime"):
            notes.append("A Binance informou uma data de retirada para este ativo.")
        extra = {
            key: row[key] for key in ("os", "att", "opt", "ssi", "mc", "d", "dlt") if key in row
        }
        if rules is not None:
            extra["rules"] = {
                key: rules.get(key)
                for key in ("tradability", "listingTime", "delistingTime", "fractionable")
                if key in rules
            }
        records.append(
            AssetRecord(
                asset_id=equity_asset_id(ac),
                asset_class=CLASS_ETF if kind == "ETF" else CLASS_STOCK,
                symbol=str(row.get("s")).strip().upper(),
                name=str(row.get("n") or "").strip(),
                binance_id=ac,
                state=state,
                state_reason=state_reason,
                info_note=" ".join(notes) or None,
                extra=extra,
            )
        )

    return ParsedCatalog(
        group=GROUP_EQUITY,
        records=sorted(records, key=lambda r: (r.asset_class, r.symbol)),
        input_counts={
            "static": len(static_rows),
            "rules": len(rule_rows),
            "union": union,
        },
        excluded=excluded,
    )


# --- Download ----------------------------------------------------------------


def _get_json(client: httpx.Client, url: str, what: str) -> Any:
    try:
        response = client.get(url, headers={"Accept": "application/json"})
    except httpx.HTTPError as exc:
        raise CatalogSourceError(
            "network", f"Sem resposta da Binance em {what}: {exc.__class__.__name__}."
        ) from exc
    if response.status_code == 429:
        raise CatalogSourceError(
            "rate_limited", f"A Binance limitou as requisições em {what} (429)."
        )
    if response.status_code >= 400:
        raise CatalogSourceError(
            "http_error", f"A Binance respondeu HTTP {response.status_code} em {what}."
        )
    try:
        return response.json()
    except ValueError as exc:
        raise CatalogSourceError("schema", f"Resposta de {what} não é JSON.") from exc


def fetch_crypto_catalog(*, timeout: float = 30.0) -> ParsedCatalog:
    with httpx.Client(timeout=httpx.Timeout(timeout)) as client:
        payload = _get_json(client, SPOT_EXCHANGE_INFO_URL, "exchangeInfo")
    return parse_spot_exchange_info(payload)


def fetch_equity_catalog(*, timeout: float = 45.0) -> ParsedCatalog:
    with httpx.Client(timeout=httpx.Timeout(timeout)) as client:
        static_payload = _get_json(client, EQUITY_STATIC_URL, "get-symbols-static")
        rules_payload = _get_json(client, EQUITY_RULES_URL, "get-exchange-info")
    return parse_equity_payloads(static_payload, rules_payload)


FETCHERS = {GROUP_CRYPTO: fetch_crypto_catalog, GROUP_EQUITY: fetch_equity_catalog}
