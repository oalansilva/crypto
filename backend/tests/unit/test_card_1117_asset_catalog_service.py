"""Card #1117: catálogo persistido, atualização, falha, consulta e validação.

Usa o PostgreSQL de teste (marcador ``postgres``): reconciliação e contagem,
removido preservado, falha sem esvaziar, pesquisa, "Todos" por filtro e a
recusa estruturada nas análises.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import create_engine, select, text

import app.models  # noqa: F401  (registra favorite_strategies e demais tabelas no reset)
import app.models_discovery  # noqa: F401
from app.database import Base, SessionLocal
from app.models_asset_catalog import AssetCatalog, AssetCatalogRefresh
from app.services import asset_analysis_guard as guard
from app.services import asset_catalog_adapters as adapters
from app.services import asset_catalog_service as catalog
from app.services.asset_catalog_adapters import CatalogSourceError


@pytest.fixture(autouse=True)
def _catalog_db(unit_database_url):
    """Isolamento barato por teste: só as tabelas que o teste toca (o reset global custa segundos).

    Também limpa depois, porque outros testes assumem catálogo vazio (validação fail-open).
    """
    engine = create_engine(unit_database_url)
    Base.metadata.create_all(bind=engine)
    tables = "asset_catalog, asset_catalog_refresh, favorite_strategies, discovery_results, backtest_runs"
    with engine.begin() as connection:
        connection.execute(text(f"TRUNCATE TABLE {tables} RESTART IDENTITY"))
    yield
    with engine.begin() as connection:
        connection.execute(text(f"TRUNCATE TABLE {tables} RESTART IDENTITY"))
    engine.dispose()


T0 = datetime(2026, 10, 20, 6, 0, tzinfo=timezone.utc)


def _spot(rows: list[tuple[str, str, bool]]) -> adapters.ParsedCatalog:
    return adapters.parse_spot_exchange_info(
        {
            "symbols": [
                {
                    "symbol": f"{base}USDT",
                    "status": status,
                    "baseAsset": base,
                    "quoteAsset": "USDT",
                    "isSpotTradingAllowed": spot,
                }
                for base, status, spot in rows
            ]
        }
    )


def _equity(static: list[dict], rules: list[dict]) -> adapters.ParsedCatalog:
    ok = lambda data: {"code": "000000", "data": data}  # noqa: E731
    return adapters.parse_equity_payloads(ok(static), ok({"symbols": rules}))


def _s(ac: str, symbol: str, name: str, kind: str = "STOCK") -> dict:
    return {"ac": ac, "s": symbol, "n": name, "t": kind, "os": True}


def _r(ac: str, symbol: str, tradability: str = "BUY_SELL") -> dict:
    return {"assetCode": ac, "symbol": symbol, "tradability": tradability, "delistingTime": None}


CRYPTO_BASE = [
    ("BTC", "TRADING", True),
    ("ETH", "TRADING", True),
    ("WAVES", "BREAK", True),
    ("ZRX", "TRADING", True),
]
EQUITY_STATIC = [
    _s("EQ_NVDA", "NVDA", "NVIDIA Corporation Common Stock"),
    _s("EQ_NVDX", "NVDX", "T-Rex 2X Long NVIDIA Daily Target ETF", "ETF"),
    _s("EQ_SPY", "SPY", "State Street SPDR S&P 500 ETF Trust", "ETF"),
    _s("EQ_QQQ", "QQQ", "Invesco QQQ Trust, Series 1", "ETF"),
    _s("EQ_AVB", "AVB", "AvalonBay Communities, Inc."),
    _s("EQ_TMHC", "TMHC", "Taylor Morrison Home Corporation Common Stock"),
    _s("EQ_ACAO", "ACAO", "Ação São Paulo Holdings"),
]
EQUITY_RULES = [
    _r("EQ_NVDA", "NVDA"),
    _r("EQ_NVDX", "NVDX"),
    _r("EQ_SPY", "SPY"),
    _r("EQ_QQQ", "QQQ"),
    _r("EQ_AVB", "AVB", "OFFMARKET"),
    _r("EQ_ACAO", "ACAO"),
]


def _refresh(group: str, parsed_or_error, *, now: datetime = T0, trigger: str = "scheduled"):
    def fetcher():
        if isinstance(parsed_or_error, Exception):
            raise parsed_or_error
        return parsed_or_error

    return catalog.refresh_group(group, trigger=trigger, fetcher=fetcher, now=now)


def _load_both() -> None:
    assert _refresh("crypto", _spot(CRYPTO_BASE))["status"] == "ok"
    assert _refresh("equity", _equity(EQUITY_STATIC, EQUITY_RULES))["status"] == "ok"


def _rows() -> dict[str, AssetCatalog]:
    with SessionLocal() as db:
        return {row.asset_id: row for row in db.execute(select(AssetCatalog)).scalars()}


# --- Atualização, reconciliação e contagens ---------------------------------------


def test_refresh_populates_both_groups_and_records_verifiable_counts():
    _load_both()

    rows = _rows()
    assert rows["binance:spot:BTC/USDT"].asset_class == "crypto"
    assert rows["binance:spot:WAVES/USDT"].state == "suspended"
    assert rows["binance:equity:EQ_NVDA"].asset_class == "stock"
    assert rows["binance:equity:EQ_SPY"].asset_class == "etf"
    assert rows["binance:equity:EQ_TMHC"].state == "no_rules"
    assert rows["binance:equity:EQ_AVB"].state == "off_market"

    with SessionLocal() as db:
        refresh = {r.catalog_group: r for r in db.execute(select(AssetCatalogRefresh)).scalars()}
    equity = refresh["equity"].counts
    assert equity["input"]["union"] - equity["excluded_total"] == equity["result_total"] == 7
    assert equity["result"] == {"stock": 4, "etf": 3}
    assert refresh["crypto"].counts["result"] == {"crypto": 4}
    assert refresh["crypto"].status == refresh["equity"].status == "ok"


def test_missing_asset_becomes_removed_and_is_preserved_with_its_date():
    _load_both()
    later = T0 + timedelta(hours=6)
    smaller = [row for row in CRYPTO_BASE if row[0] != "WAVES"]
    assert _refresh("crypto", _spot(smaller), now=later)["status"] == "ok"

    waves = _rows()["binance:spot:WAVES/USDT"]
    assert waves.state == "removed"
    assert waves.removed_at == later
    assert "20/10/2026" in waves.state_reason
    assert waves.first_seen_at == T0

    # um terceiro refresh não reescreve a data de remoção
    assert _refresh("crypto", _spot(smaller), now=later + timedelta(hours=6))["status"] == "ok"
    assert _rows()["binance:spot:WAVES/USDT"].removed_at == later


def test_removed_asset_that_returns_becomes_negotiable_again():
    _load_both()
    smaller = [row for row in CRYPTO_BASE if row[0] != "ZRX"]
    _refresh("crypto", _spot(smaller), now=T0 + timedelta(hours=6))
    assert _rows()["binance:spot:ZRX/USDT"].state == "removed"

    _refresh("crypto", _spot(CRYPTO_BASE), now=T0 + timedelta(hours=12))
    zrx = _rows()["binance:spot:ZRX/USDT"]
    assert zrx.state == "tradable" and zrx.removed_at is None


@pytest.mark.parametrize(
    "error",
    [
        CatalogSourceError("network", "Sem resposta da Binance"),
        CatalogSourceError("rate_limited", "429"),
        CatalogSourceError("binance_error", "code 100001"),
        CatalogSourceError("schema", "formato inesperado"),
        RuntimeError("boom"),
    ],
)
def test_failure_keeps_last_valid_list_and_records_the_error(error):
    _load_both()
    before = {k: (v.state, v.last_seen_at, v.name) for k, v in _rows().items()}

    result = _refresh("equity", error, now=T0 + timedelta(hours=6))

    assert result["status"] == "error"
    assert {k: (v.state, v.last_seen_at, v.name) for k, v in _rows().items()} == before
    with SessionLocal() as db:
        fresh = catalog.freshness_by_class(db)
        last = (
            db.execute(
                select(AssetCatalogRefresh)
                .where(AssetCatalogRefresh.catalog_group == "equity")
                .order_by(AssetCatalogRefresh.id.desc())
            )
            .scalars()
            .first()
        )
    assert last.status == "error" and last.error_message
    assert fresh["stock"]["status"] == "stale"
    assert fresh["etf"]["status"] == "stale"
    assert fresh["stock"]["updated_at"] == T0.isoformat() or fresh["stock"]["updated_at"]
    assert fresh["crypto"]["status"] == "ok"


def test_sharp_drop_and_empty_result_keep_the_previous_list():
    _load_both()
    before = _rows()

    tiny = _spot([("BTC", "TRADING", True)])  # 1 de 4 (< 50%)
    dropped = _refresh("crypto", tiny, now=T0 + timedelta(hours=6))
    assert dropped["status"] == "error" and dropped["error_code"] == "sharp_drop"

    empty = adapters.ParsedCatalog(group="crypto", records=[], input_counts={}, excluded={})
    emptied = _refresh("crypto", empty, now=T0 + timedelta(hours=7))
    assert emptied["status"] == "error" and emptied["error_code"] == "empty"

    after = _rows()
    assert {k: v.state for k, v in after.items()} == {k: v.state for k, v in before.items()}
    assert "binance:spot:ETH/USDT" in after and after["binance:spot:ETH/USDT"].state == "tradable"


def test_first_failure_without_list_is_unavailable_and_never_a_fixed_list():
    result = _refresh("crypto", CatalogSourceError("network", "offline"))
    assert result["status"] == "error"

    with SessionLocal() as db:
        fresh = catalog.freshness_by_class(db)
        page = catalog.search_catalog(db, q="btc")
    assert fresh["crypto"]["status"] == "unavailable"
    assert fresh["crypto"]["reason"] == "offline"
    assert page["items"] == [] and page["total"] == 0
    assert page["counts"]["crypto"] == {"total": None, "eligible": None}
    assert catalog.list_tradable_crypto_symbols() is None


def test_successful_refresh_after_failure_returns_to_ok():
    _refresh("crypto", CatalogSourceError("network", "offline"))
    _refresh("crypto", _spot(CRYPTO_BASE), now=T0 + timedelta(minutes=5))
    with SessionLocal() as db:
        assert catalog.freshness_by_class(db)["crypto"]["status"] == "ok"
    assert catalog.list_tradable_crypto_symbols() == ["BTC/USDT", "ETH/USDT", "ZRX/USDT"]


def test_backfill_adds_favorite_and_result_symbols_missing_from_catalog_as_removed():
    with SessionLocal() as db:
        db.execute(
            text(
                "INSERT INTO favorite_strategies (user_id, name, symbol, timeframe, strategy_name, parameters, notify_telegram) "
                "VALUES ('u1', 'fav', 'AGLD/USDT', '1d', 'ema', '{}', true), "
                "('u1', 'fav2', 'BTC/USDT', '1d', 'ema', '{}', true), "
                "('u1', 'fav3', 'ETH/BTC', '1d', 'ema', '{}', true), "
                "('u1', 'fav4', 'NVDA', '1d', 'ema', '{}', true)"
            )
        )
        db.commit()

    _load_both()

    rows = _rows()
    agld = rows["binance:spot:AGLD/USDT"]
    assert agld.state == "removed" and agld.asset_class == "crypto"
    assert agld.extra == {"source": "backfill"}
    assert rows["binance:spot:BTC/USDT"].state == "tradable"
    # par não-USDT e ticker sem "/" não viram ativo do catálogo nem são associados a ação
    assert "binance:spot:ETH/BTC" not in rows
    assert [a for a in rows.values() if a.symbol == "NVDA" and a.asset_class != "stock"] == []
    assert sum(1 for a in rows.values() if a.symbol == "NVDA") == 1


def test_history_summary_comes_from_local_candles_for_crypto_only(monkeypatch):
    # Tabela em schema privado: nunca toca o market_ohlcv compartilhado.
    schema = "c1117_hist_" + uuid.uuid4().hex[:8]
    with SessionLocal() as db:
        db.execute(text(f"CREATE SCHEMA {schema}"))
        db.execute(
            text(
                f"CREATE TABLE {schema}.market_ohlcv (symbol text, timeframe text, "
                "candle_time timestamptz, open numeric, high numeric, low numeric, close numeric, "
                "volume numeric, source text)"
            )
        )
        db.execute(
            text(
                f"INSERT INTO {schema}.market_ohlcv (symbol, timeframe, candle_time, open, high, low, close, volume, source) "
                "VALUES ('BTC/USDT','1d','2017-08-17','1','1','1','1','1','t'), "
                "('BTC/USDT','1d','2026-10-19','1','1','1','1','1','t'), "
                "('BTC/USDT','15m','2010-01-01','1','1','1','1','1','t')"
            )
        )
        db.commit()
    monkeypatch.setattr(catalog, "MARKET_OHLCV_TABLE", f"{schema}.market_ohlcv")
    try:
        _load_both()
        with SessionLocal() as db:
            page = catalog.search_catalog(db, q="btc/usdt")
            nvda = catalog.search_catalog(db, q="nvda")["items"][0]
            eth = catalog.search_catalog(db, q="eth/usdt")["items"][0]
    finally:
        with SessionLocal() as db:
            db.execute(text(f"DROP SCHEMA {schema} CASCADE"))
            db.commit()

    btc = page["items"][0]
    # Card #1118: sem a série na autoridade nova, o resumo de 1d do #1117 ainda vale para a cripto
    # (lacunas desconhecidas) e ação/ETF nunca mais aparecem como "não coletado".
    assert btc["history"]["status"] == "covered"
    assert btc["history"]["from"].startswith("2017-08-17")
    assert btc["history"]["to"].startswith("2026-10-19")
    assert btc["history"]["gap_count"] is None
    assert [t["timeframe"] for t in btc["history"]["timeframes"]] == ["1d"]
    assert eth["history"]["status"] == "on_demand"
    assert nvda["history"]["status"] == "on_demand"
    assert nvda["history"]["from"] is None and nvda["history"]["timeframes"] == []


# --- Consulta ---------------------------------------------------------------------


def test_search_finds_the_verification_examples_on_the_first_page():
    _load_both()
    with SessionLocal() as db:
        for query, symbol, asset_class in (
            ("BTC/USDT", "BTC/USDT", "crypto"),
            ("btc", "BTC/USDT", "crypto"),
            ("NVDA", "NVDA", "stock"),
            ("SPY", "SPY", "etf"),
            ("QQQ", "QQQ", "etf"),
        ):
            page = catalog.search_catalog(db, q=query)
            first = page["items"][0]
            assert (first["symbol"], first["asset_class"]) == (symbol, asset_class), query


def test_search_by_name_ignores_case_and_accents_and_ranks_exact_then_prefix_then_name():
    _load_both()
    with SessionLocal() as db:
        nvidia = catalog.search_catalog(db, q="nvidia")
        accent = catalog.search_catalog(db, q="AÇÃO")
        accent_plain = catalog.search_catalog(db, q="acao sao")
        ranked = catalog.search_catalog(db, q="nvd")

    assert [i["symbol"] for i in nvidia["items"]] == ["NVDA", "NVDX"]  # ação antes de ETF
    assert [i["symbol"] for i in accent["items"]] == ["ACAO"]
    assert [i["symbol"] for i in accent_plain["items"]] == ["ACAO"]
    assert [i["symbol"] for i in ranked["items"]] == ["NVDA", "NVDX"]


def test_search_exact_symbol_ranks_before_prefix_and_name_matches():
    _refresh(
        "crypto",
        _spot([("ETH", "TRADING", True), ("ETHFI", "TRADING", True), ("WETH", "TRADING", True)]),
    )
    with SessionLocal() as db:
        page = catalog.search_catalog(db, q="eth")
    assert [i["symbol"] for i in page["items"]] == ["ETH/USDT", "ETHFI/USDT", "WETH/USDT"]


def test_search_treats_like_wildcards_literally():
    _load_both()
    with SessionLocal() as db:
        assert catalog.search_catalog(db, q="%")["total"] == 0
        assert catalog.search_catalog(db, q="_")["total"] == 0


def test_class_filter_counts_pagination_and_eligible_total():
    _load_both()
    with SessionLocal() as db:
        everything = catalog.search_catalog(db, page_size=3)
        etfs = catalog.search_catalog(db, asset_class="etf")
        page2 = catalog.search_catalog(db, page=2, page_size=3)

    assert everything["total"] == 11 and everything["pages"] == 4
    assert everything["eligible_total"] == 8  # WAVES (suspenso), AVB (fora) e TMHC ficam fora
    assert everything["marked_total"] == 3
    assert everything["counts"]["all"] == {"total": 11, "eligible": 8}
    assert everything["counts"]["crypto"] == {"total": 4, "eligible": 3}
    assert everything["counts"]["stock"] == {"total": 4, "eligible": 2}
    assert everything["counts"]["etf"] == {"total": 3, "eligible": 3}
    assert etfs["total"] == 3 and all(i["asset_class"] == "etf" for i in etfs["items"])
    assert len(page2["items"]) == 3 and page2["page"] == 2
    seen = [i["asset_id"] for i in everything["items"]]
    assert not set(seen) & {i["asset_id"] for i in page2["items"]}


def test_marked_rows_are_listed_with_state_reason_and_without_selectable_flag():
    _load_both()
    with SessionLocal() as db:
        waves = catalog.search_catalog(db, q="waves")["items"][0]
        avb = catalog.search_catalog(db, q="avb")["items"][0]
        tmhc = catalog.search_catalog(db, q="tmhc")["items"][0]

    assert (waves["state"], waves["selectable"]) == ("suspended", False)
    assert "BREAK" in waves["state_reason"]
    assert (avb["state"], avb["selectable"]) == ("off_market", False)
    assert (tmhc["state"], tmhc["state_label"]) == ("no_rules", "Sem regras de negociação")


def test_resolve_returns_only_tradable_ids_of_the_filter_and_never_marked():
    _load_both()
    with SessionLocal() as db:
        etfs = catalog.resolve_filter(db, asset_class="etf")
        nvidia = catalog.resolve_filter(db, q="nvidia")
        everything = catalog.resolve_filter(db)
        stocks = catalog.resolve_filter(db, asset_class="stock")

    assert sorted(etfs["asset_ids"]) == sorted(
        ["binance:equity:EQ_NVDX", "binance:equity:EQ_SPY", "binance:equity:EQ_QQQ"]
    )
    assert etfs["marked_total"] == 0
    assert [i["symbol"] for i in nvidia["items"]] == ["NVDA", "NVDX"]
    assert "binance:spot:WAVES/USDT" not in everything["asset_ids"]
    assert "binance:equity:EQ_AVB" not in everything["asset_ids"]
    assert everything["eligible_total"] == 8 and everything["marked_total"] == 3
    assert stocks["marked_total"] == 2  # AVB e TMHC ficam de fora


def test_resolve_and_search_hide_a_class_without_valid_list():
    _refresh("equity", _equity(EQUITY_STATIC, EQUITY_RULES))
    _refresh("crypto", CatalogSourceError("network", "offline"))
    with SessionLocal() as db:
        page = catalog.search_catalog(db, q="btc")
        everything = catalog.search_catalog(db)
        resolved = catalog.resolve_filter(db)
    assert page["items"] == []
    assert everything["counts"]["all"]["total"] == 7  # só ações e ETFs
    assert all(not i["asset_id"].startswith("binance:spot:") for i in resolved["items"])


def test_lookup_rehydrates_ids_and_symbols_with_current_state():
    _load_both()
    with SessionLocal() as db:
        items = catalog.lookup_assets(
            db,
            asset_ids=[
                "binance:spot:WAVES/USDT",
                "binance:equity:EQ_NVDA",
                "binance:spot:NOPE/USDT",
            ],
            symbols=["spy"],
        )
    by_symbol = {i["symbol"]: i for i in items}
    assert set(by_symbol) == {"WAVES/USDT", "NVDA", "SPY"}
    assert by_symbol["WAVES/USDT"]["selectable"] is False
    assert by_symbol["SPY"]["asset_class"] == "etf"


# --- Validação das análises -------------------------------------------------------


def test_guard_refuses_equity_and_etf_with_structured_portuguese_detail():
    _load_both()
    detail = guard.refusal_for_symbols(["BTC/USDT", "NVDA", "SPY"], new_analysis=True)

    assert detail["code"] == "asset_class_not_supported"
    assert detail["asset_classes"] == ["etf", "stock"]
    assert {a["symbol"]: a["asset_class"] for a in detail["assets"]} == {
        "NVDA": "stock",
        "SPY": "etf",
    }
    assert (
        "Ação e ETF por enquanto rodam só com 1 ativo (Combo ou Otimização); o lote vem depois."
        in detail["message"]
    )
    assert "NVDA (Ação)" in detail["message"] and "SPY (ETF)" in detail["message"]
    # o backtest que reabre resultados salvos também recusa ação e ETF
    assert (
        guard.refusal_for_symbols(["NVDA"], new_analysis=False)["code"]
        == "asset_class_not_supported"
    )


def test_guard_refuses_marked_asset_only_for_new_analysis():
    _load_both()
    detail = guard.refusal_for_symbols(["BTC/USDT", "WAVES/USDT"], new_analysis=True)

    assert detail["code"] == "asset_not_selectable"
    assert detail["state"] == "suspended" and "BREAK" in detail["reason"]
    assert detail["assets"][0]["symbol"] == "WAVES/USDT"
    # reabertura de resultado salvo de ativo pausado continua funcionando
    assert guard.refusal_for_symbols(["WAVES/USDT"], new_analysis=False) is None


def test_guard_reopening_removed_asset_still_works_and_new_analysis_refuses_it():
    _load_both()
    _refresh(
        "crypto", _spot([r for r in CRYPTO_BASE if r[0] != "ZRX"]), now=T0 + timedelta(hours=6)
    )

    assert guard.refusal_for_symbols(["ZRX/USDT"], new_analysis=False) is None
    detail = guard.refusal_for_symbols(["ZRX/USDT"], new_analysis=True)
    assert detail["code"] == "asset_not_selectable" and detail["state"] == "removed"


def test_guard_unknown_symbol_gets_not_in_catalog_for_new_analysis():
    _load_both()
    detail = guard.refusal_for_symbols(["XYZ/USDT"], new_analysis=True)
    assert detail["code"] == "asset_not_in_catalog"
    assert detail["assets"] == [{"symbol": "XYZ/USDT"}]
    assert "XYZ/USDT" in detail["message"]
    assert guard.refusal_for_symbols(["XYZ/USDT"], new_analysis=False) is None
    # ticker desconhecido com catálogo de ações carregado
    assert guard.refusal_for_symbols(["ZZZZ"], new_analysis=False)["code"] == "asset_not_in_catalog"


def test_guard_precedence_class_then_marked_then_missing():
    _load_both()
    assert (
        guard.refusal_for_symbols(["XYZ/USDT", "WAVES/USDT", "QQQ"], new_analysis=True)["code"]
        == "asset_class_not_supported"
    )
    assert (
        guard.refusal_for_symbols(["XYZ/USDT", "WAVES/USDT"], new_analysis=True)["code"]
        == "asset_not_selectable"
    )


def test_guard_without_valid_crypto_list_does_not_block_crypto_pairs():
    _refresh("crypto", CatalogSourceError("network", "offline"))
    assert guard.refusal_for_symbols(["BTC/USDT"], new_analysis=True) is None
    # sem catálogo de ações, ticker segue recusado como classe não suportada
    assert (
        guard.refusal_for_symbols(["NVDA"], new_analysis=True)["code"]
        == "asset_class_not_supported"
    )


def test_discovery_symbol_reasons_cover_equity_marked_and_missing():
    _load_both()
    reasons = guard.discovery_symbol_reasons(
        ["BTC/USDT", "NVDA", "SPY", "WAVES/USDT", "AVB", "XYZ/USDT"]
    )

    assert "BTC/USDT" not in reasons
    assert (
        reasons["NVDA"]["reason"]
        == "ação e ETF por enquanto rodam só com 1 ativo (Combo ou Otimização); o lote vem depois"
    )
    assert reasons["SPY"]["kind"] == "class"
    assert reasons["WAVES/USDT"]["kind"] == "marked"
    assert "Suspenso na Binance" in reasons["WAVES/USDT"]["reason"]
    assert "não entra em análise nova" in reasons["AVB"]["reason"]
    assert reasons["XYZ/USDT"]["reason"] == "ativo fora do catálogo da Binance"
