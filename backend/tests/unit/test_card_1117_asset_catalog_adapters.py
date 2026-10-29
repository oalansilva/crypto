"""Card #1117: adaptadores do catálogo de ativos Binance (cripto, ações e ETFs).

Cobre reconciliação por ``ac`` (união - excluídos = escolhíveis), exclusões por
motivo, mapa de estados e rejeição de schema inesperado.
"""

from __future__ import annotations

import pytest

from app.services import asset_catalog_adapters as adapters
from app.services.asset_catalog_adapters import CatalogSourceError


def _spot(symbol_status: list[tuple[str, str, bool]], *, quote: str = "USDT") -> dict:
    return {
        "symbols": [
            {
                "symbol": f"{base}{quote}",
                "status": status,
                "baseAsset": base,
                "quoteAsset": quote,
                "isSpotTradingAllowed": spot,
            }
            for base, status, spot in symbol_status
        ]
    }


def _static(ac: str, symbol: str, name: str, kind: str = "STOCK", **extra) -> dict:
    return {"ac": ac, "s": symbol, "n": name, "t": kind, "os": True, **extra}


def _rule(ac: str | None, symbol: str, tradability: str = "BUY_SELL", **extra) -> dict:
    return {
        "assetCode": ac,
        "symbol": symbol,
        "tradability": tradability,
        "delistingTime": None,
        **extra,
    }


def _ok(data):
    return {"code": "000000", "message": None, "data": data}


# --- Cripto ----------------------------------------------------------------------


def test_crypto_keeps_only_usdt_pairs_and_maps_states():
    payload = _spot(
        [
            ("BTC", "TRADING", True),
            ("WAVES", "BREAK", True),
            ("OLD", "HALT", True),
            ("OFF", "TRADING", False),
        ]
    )
    payload["symbols"] += _spot([("ETH", "TRADING", True)], quote="BTC")["symbols"]
    payload["symbols"] += _spot([("BTC", "TRADING", True)], quote="USDC")["symbols"]

    parsed = adapters.parse_spot_exchange_info(payload)
    by_symbol = {r.symbol: r for r in parsed.records}

    assert set(by_symbol) == {"BTC/USDT", "WAVES/USDT", "OLD/USDT", "OFF/USDT"}
    assert by_symbol["BTC/USDT"].state == adapters.STATE_TRADABLE
    assert by_symbol["BTC/USDT"].asset_id == "binance:spot:BTC/USDT"
    assert by_symbol["WAVES/USDT"].state == adapters.STATE_SUSPENDED
    assert "status BREAK" in by_symbol["WAVES/USDT"].state_reason
    assert by_symbol["OLD/USDT"].state == adapters.STATE_SUSPENDED
    assert "status HALT" in by_symbol["OLD/USDT"].state_reason
    assert by_symbol["OFF/USDT"].state == adapters.STATE_SUSPENDED
    assert "à vista desligada" in by_symbol["OFF/USDT"].state_reason
    assert parsed.input_counts["usdt_pairs"] == 4


def test_crypto_excludes_explicit_and_leveraged_tokens_but_keeps_jup_and_syrup():
    payload = _spot(
        [
            ("BTC", "TRADING", True),
            ("BTCUP", "BREAK", False),  # alavancado: sufixo + spot desligado
            ("BTCDOWN", "BREAK", False),
            ("JUP", "TRADING", True),  # termina em UP, mas JU não é listado
            ("SYRUP", "TRADING", True),
            ("AION", "BREAK", True),  # exclusão explícita de excluded_symbols.json
        ]
    )

    parsed = adapters.parse_spot_exchange_info(payload)

    assert {r.symbol for r in parsed.records} == {"BTC/USDT", "JUP/USDT", "SYRUP/USDT"}
    assert parsed.excluded == {adapters.EXCLUDE_LEVERAGED: 2, adapters.EXCLUDE_EXPLICIT: 1}
    # entrada - excluídos = resultado
    assert parsed.input_counts["usdt_pairs"] - parsed.excluded_total == len(parsed.records)


def test_crypto_leveraged_suffix_with_spot_on_needs_the_stripped_base_to_be_listed():
    payload = _spot(
        [("BTC", "TRADING", True), ("BTCUP", "TRADING", True), ("FOOUP", "TRADING", True)]
    )
    parsed = adapters.parse_spot_exchange_info(payload)
    assert {r.symbol for r in parsed.records} == {"BTC/USDT", "FOOUP/USDT"}
    assert parsed.excluded == {adapters.EXCLUDE_LEVERAGED: 1}


@pytest.mark.parametrize(
    "payload",
    [None, [], {"symbols": "x"}, {"symbols": [1]}, {"symbols": [{"symbol": "BTCUSDT"}]}],
)
def test_crypto_unexpected_schema_is_a_source_error(payload):
    with pytest.raises(CatalogSourceError) as exc:
        adapters.parse_spot_exchange_info(payload)
    assert exc.value.code == "schema"


def test_crypto_business_error_payload_is_not_an_empty_list():
    with pytest.raises(CatalogSourceError) as exc:
        adapters.parse_spot_exchange_info({"code": -1003, "msg": "Too many requests"})
    assert exc.value.code == "binance_error"


# --- Ações e ETFs -----------------------------------------------------------------


def test_equity_reconciles_by_ac_and_union_minus_excluded_equals_eligible():
    static = _ok(
        [
            _static("EQ_NVDA", "NVDA", "NVIDIA Corporation Common Stock"),
            _static("EQ_SPY", "SPY", "State Street SPDR S&P 500 ETF Trust", "ETF"),
            _static("EQ_QQQ", "QQQ", "Invesco QQQ Trust, Series 1", "ETF"),
            _static("EQ_TMHC", "TMHC", "Taylor Morrison Home Corporation Common Stock", d=True),
            _static("RGT_EOSER", "EOSER", "Eos Energy Right", "RIGHT"),
            _static("EQ_SKYD.WS", "SKYD.WS", "Skydance Corporation Warrants"),
            _static("EQ_UWMC.RT", "UWMC.RT", "UWM Holdings Corporation rights"),
            _static("EQ_KLXER", "KLXER", "KLX Energy Services Holdings, Inc. Rights (KLXER)"),
            _static("EQ_X", "X", "Rent the Runway, Inc. Class A Rights Offering"),
            _static("EQ_CVR", "CVR1", "Coherus Oncology, Inc Contingent Value Right"),
            _static("EQ_AVB", "AVB", "AvalonBay Communities, Inc."),
        ]
    )
    rules = _ok(
        {
            "symbols": [
                _rule("EQ_NVDA", "NVDA"),
                _rule("EQ_SPY", "SPY"),
                _rule("EQ_QQQ", "QQQ", delistingTime=1791187200000),
                _rule("EQ_AVB", "AVB", "OFFMARKET"),
                _rule("EQ_SKYD.WS", "SKYD.WS"),
                _rule(None, "CEPT", "OFFMARKET"),  # sem cadastro estático
            ]
        }
    )

    parsed = adapters.parse_equity_payloads(static, rules)
    by_symbol = {r.symbol: r for r in parsed.records}

    assert parsed.input_counts == {"static": 11, "rules": 6, "union": 12}
    assert parsed.excluded == {
        adapters.EXCLUDE_RIGHT_TYPE: 1,
        adapters.EXCLUDE_WARRANT: 1,
        adapters.EXCLUDE_RIGHT: 3,
        adapters.EXCLUDE_CVR: 1,
        adapters.EXCLUDE_NO_STATIC: 1,
    }
    assert parsed.excluded_total == 7
    assert parsed.input_counts["union"] - parsed.excluded_total == len(parsed.records) == 5
    assert parsed.result_counts == {"stock": 3, "etf": 2}

    assert by_symbol["NVDA"].asset_class == adapters.CLASS_STOCK
    assert by_symbol["NVDA"].asset_id == "binance:equity:EQ_NVDA"
    assert by_symbol["SPY"].asset_class == adapters.CLASS_ETF
    assert by_symbol["QQQ"].asset_class == adapters.CLASS_ETF
    assert "CEPT" not in by_symbol and "SKYD.WS" not in by_symbol


def test_equity_state_map_and_informative_delisting_note():
    static = _ok(
        [
            _static("EQ_A", "A", "A Corp"),
            _static("EQ_B", "B", "B Corp"),
            _static("EQ_C", "C", "C Corp"),
            _static("EQ_D", "D", "D Corp"),
            _static("EQ_E", "E", "E Corp", d=True),
            _static("EQ_F", "F", "F Corp"),
        ]
    )
    rules = _ok(
        {
            "symbols": [
                _rule("EQ_A", "A", "BUY_SELL"),
                _rule("EQ_B", "B", "OFFMARKET"),
                _rule("EQ_C", "C", "NONE"),
                # D sem regras de negociação
                _rule("EQ_E", "E", "BUY_SELL", delistingTime=1791187200000),
                _rule("EQ_F", "F", "SOMETHING_NEW"),
            ]
        }
    )

    by_symbol = {r.symbol: r for r in adapters.parse_equity_payloads(static, rules).records}

    assert by_symbol["A"].state == adapters.STATE_TRADABLE
    assert by_symbol["B"].state == adapters.STATE_OFF_MARKET
    assert by_symbol["C"].state == adapters.STATE_NO_TRADING
    assert by_symbol["D"].state == adapters.STATE_NO_RULES
    assert by_symbol["F"].state == adapters.STATE_NO_TRADING
    assert "desconhecido" in by_symbol["F"].state_reason
    # dlt é informativo e não muda o estado
    assert by_symbol["E"].state == adapters.STATE_TRADABLE
    assert by_symbol["E"].info_note
    assert by_symbol["A"].info_note is None


def test_equity_right_and_warrant_regex_do_not_hit_ordinary_names():
    ordinary = [
        "America Movil S.A.B de C.V American Depositary Shares (each representing the right to receive twenty (20) Series B Shares)",
        "Bright Minds Biosciences Inc. Common Stock",
        "Curtiss-Wright Corp.",
        "RLX Technology Inc. American Depositary Shares, each representing the right to receive one (1) Class A ordinary share",
        "First Trust Dorsey Wright Focus 5 ETF",
    ]
    for name in ordinary:
        assert adapters.equity_exclusion_reason(_static("EQ_Z", "Z", name)) is None, name


@pytest.mark.parametrize(
    "static_payload, rules_payload",
    [
        (None, _ok({"symbols": []})),
        (_ok({"not": "a list"}), _ok({"symbols": []})),
        (_ok([_static("EQ_A", "A", "A")]), _ok({"symbols": "x"})),
        (_ok([_static("EQ_A", "A", "A")]), _ok([])),
        ({"foo": 1}, _ok({"symbols": []})),
    ],
)
def test_equity_unexpected_schema_is_a_source_error(static_payload, rules_payload):
    with pytest.raises(CatalogSourceError) as exc:
        adapters.parse_equity_payloads(static_payload, rules_payload)
    assert exc.value.code == "schema"


def test_equity_business_error_code_is_not_an_empty_list():
    with pytest.raises(CatalogSourceError) as exc:
        adapters.parse_equity_payloads(
            {"code": "100001", "message": "falhou", "data": None}, _ok({"symbols": []})
        )
    assert exc.value.code == "binance_error"


def test_equity_duplicate_and_missing_identifiers_keep_the_invariant():
    static = _ok(
        [
            _static("EQ_A", "A", "A Corp"),
            _static("EQ_A", "A", "A Corp again"),
            {"ac": "", "s": "Q", "n": "Q", "t": "STOCK"},
        ]
    )
    parsed = adapters.parse_equity_payloads(static, _ok({"symbols": [_rule("EQ_A", "A")]}))

    assert len(parsed.records) == 1
    assert parsed.input_counts["union"] - parsed.excluded_total == len(parsed.records)


def test_search_normalization_ignores_case_and_accents():
    assert adapters.normalize_search_text("  Ação São PAULO ") == "acao sao paulo"
    assert adapters.build_search_key("BTC/USDT", "Bitcoin") == "btc/usdt\nbitcoin"
