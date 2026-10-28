"""Card #1123, retrabalho pós Não homologar: cripto da Descoberta sem amostra guardada.

Sem ``MARKET_HISTORY_UNIFIED`` a cripto da Descoberta nunca guarda amostra. A coluna extra refaz os
trades pelo caminho antigo, relendo o cache local (sem rede e sem escrever nele) na janela da
varredura, e só calcula se as métricas refeitas baterem com as gravadas (decisão do Alan, "Conferir
pelas métricas": trades e taxa de acerto iguais, CAGR igual na casa decimal que a Descoberta mostra).
A versão das velas (SHA-256) não é condição. Quando não bate, a célula diz o motivo verdadeiro, nunca
"vencida".
"""

from __future__ import annotations

import hashlib
import io
import os
from pathlib import Path

import openpyxl
import pandas as pd
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.routes import discovery_routes
from app.services import benchmark_comparison as bench
from app.services import discovery_inputs as di
from app.services import discovery_reference_column as refcol
from support_card_1123 import (
    BTC_TRADES,
    FakeSource,
    client_for,
    ensure_snapshot_table,
    make_user,
)
from test_card_1123_discovery_column import SWEEP, TRADES, _seed

BTC = "RS-BTC1123A1"
START, END = "2019-01-01", "2024-12-31"
TEMPLATE_METADATA = {"name": "multi_ma_crossover", "indicators": [{"type": "sma"}]}


def _loader_frame(index: pd.DatetimeIndex, base: float) -> pd.DataFrame:
    """Formato do parquet do ``IncrementalLoader`` (``timestamp`` em ms e ``timestamp_utc``)."""

    n = len(index)
    close = [base + i * 0.5 for i in range(n)]
    return pd.DataFrame(
        {
            "timestamp": index.as_unit("ms").asi8.astype("int64"),
            "timestamp_utc": index,
            "open": close,
            "high": [c + 1 for c in close],
            "low": [c - 1 for c in close],
            "close": close,
            "volume": [10.0] * n,
        }
    )


@pytest.fixture
def db(postgres_isolation, unit_database_url):
    engine = create_engine(unit_database_url)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = Session()
    ensure_snapshot_table(session)
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


@pytest.fixture
def source():
    fake = FakeSource()
    bench.set_reference_source(fake)
    yield fake
    bench.set_reference_source(None)


@pytest.fixture
def cache(tmp_path, monkeypatch):
    """Cache local da Binance (1d e "15m") cobrindo a janela; rede bloqueada e histórico novo desligado."""

    from src.data.incremental_loader import IncrementalLoader

    root = tmp_path / "storage"
    (root / "binance").mkdir(parents=True)
    days = pd.date_range("2018-12-01", "2025-01-31", freq="D", tz="UTC")
    _loader_frame(days, 3000.0).to_parquet(root / "binance" / "BTC_USDT_1d.parquet", index=False)
    # O 15m só precisa cobrir a janela no formato do loader (o otimizador é simulado).
    quarter = pd.date_range("2018-12-01", "2025-01-31", freq="6h", tz="UTC")
    _loader_frame(quarter, 3000.0).to_parquet(
        root / "binance" / "BTC_USDT_15m.parquet", index=False
    )
    monkeypatch.setenv("DISCOVERY_MARKET_CACHE_DIR", str(root))
    monkeypatch.setenv("DISCOVERY_SPOOL_DIR", str(tmp_path / "spool"))
    monkeypatch.setattr(di, "_unified", lambda: False)
    monkeypatch.setattr(
        IncrementalLoader, "_unified_history_enabled", staticmethod(lambda s: False)
    )

    def no_network(*_a, **_k):
        raise AssertionError("o caminho antigo refeito não pode ir à Binance")

    monkeypatch.setattr(IncrementalLoader, "_download_loop", no_network)
    return root / "binance"


def _digest(folder: Path) -> dict[str, str]:
    return {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(folder.iterdir())}


# Métricas que a varredura gravou para o BTC/USDT (9 trades, 7 ganhos) e que o refeito tem de repetir.
RECORDED = {"trades_count": len(BTC_TRADES), "win_rate": 7 / 9, "cagr": 0.4213}


def _legacy_btc(db, *, manifest=True, window=True, sweep_window=True):
    """Deixa o BTC/USDT como a varredura antiga gravou: sem amostra, com o SHA do spool do ``prepare``."""

    from app.models_discovery import DiscoveryCombination, DiscoveryResult, DiscoverySweep

    inputs = {"symbol": "BTC/USDT", "timeframe": "1d", "start_date": START, "end_date": END}
    recorded = di.prepare(dict(inputs))  # caminho antigo de verdade (cache local, sem rede)
    candles = recorded["files"]["candles"]["sha256"]
    di.discard(recorded)  # a varredura limpa o spool ("inputs_cleaned")
    result = db.query(DiscoveryResult).filter(DiscoveryResult.id == BTC).one()
    snapshot = {"template_metadata": TEMPLATE_METADATA, "inputs_cleaned": True}
    if window:
        snapshot.update({"start_date": START, "end_date": END})
    if manifest:
        snapshot["candle_manifest"] = recorded
    if not sweep_window:
        sweep = db.query(DiscoverySweep).filter(DiscoverySweep.id == SWEEP).one()
        sweep.snapshot = {}
    db.add(
        DiscoveryCombination(
            id=result.combination_id,
            sweep_id=SWEEP,
            template_id=result.template_id,
            symbol="BTC/USDT",
            timeframe="1d",
            direction="long",
            state="succeeded",
            input_snapshot=snapshot,
            result_id=BTC,
        )
    )
    result.snapshot_id = None
    result.data_source = None
    result.asset_class = None
    result.session = None
    result.adjustment = None
    result.candle_source = "ccxt"
    result.candle_version = candles if manifest else None
    result.trades_count = RECORDED["trades_count"]
    result.win_rate = RECORDED["win_rate"]
    result.cagr = RECORDED["cagr"]
    db.commit()
    return recorded


class FakeOptimizer:
    """Otimizador simulado: confere que lê só o spool do cache e devolve trades e métricas do refeito."""

    calls: list[dict] = []
    metrics: dict = {}

    def run_optimization(self, **kwargs):
        assert os.environ.get("DISCOVERY_FROZEN_INPUT_DIR")
        assert not os.environ.get(di.SNAPSHOT_ID_ENV)
        candles = di.read("candles")
        intraday = di.read("intraday")
        from app.services.combo_service import ComboService

        metadata = ComboService.get_template_metadata(None, kwargs["template_name"])
        FakeOptimizer.calls.append(
            {
                **kwargs,
                "candles": candles,
                "intraday_rows": len(intraday),
                "template_metadata": metadata,
            }
        )
        trades = FakeOptimizer.metrics.get("trades", BTC_TRADES)
        best = {k: v for k, v in FakeOptimizer.metrics.items() if k != "trades"}
        return {"trades": trades, "best_metrics": best, "candles": []}


def _redone(**changes):
    FakeOptimizer.metrics = {"win_rate": RECORDED["win_rate"], "cagr": RECORDED["cagr"], **changes}


@pytest.fixture
def run(db, source, monkeypatch):
    user = make_user(db, "alan", admin=True)
    actor = str(user.id)
    _seed(db, actor=actor)
    queued: list[str] = []
    monkeypatch.setattr(refcol, "enqueue", lambda cid: queued.append(cid))
    FakeOptimizer.calls = []
    _redone()
    snapshot_regenerated: list[str] = []

    def regenerate(_db, result):
        if result.snapshot_id:
            # Ação/ETF e cripto com amostra seguem pelo caminho da amostra (inalterado).
            snapshot_regenerated.append(result.id)
            return TRADES.get(result.id, [])
        return refcol.regenerate_trades(_db, result, optimizer_factory=FakeOptimizer)

    Session = sessionmaker(bind=db.get_bind())
    client = client_for(db, [discovery_routes.router], {"user": actor, "admin": True})

    def go(symbol="SPY"):
        res = client.put(
            f"/api/combos/discovery/sweeps/{SWEEP}/reference-column",
            json={"reference_symbol": symbol},
        )
        assert res.status_code == 202, res.text
        refcol.run_column(queued.pop(0), db_factory=Session, source=source, regenerate=regenerate)
        board = client.get(
            f"/api/combos/discovery/sweeps/{SWEEP}/leaderboard",
            params={"metric": "delta_cagr_vs_bh"},
        ).json()
        return board, {r["result_id"]: r.get("reference_comparison") for r in board["results"]}

    return {
        "go": go,
        "client": client,
        "actor": actor,
        "snapshot_regenerated": snapshot_regenerated,
    }


def _state(run):
    return run["client"].get(f"/api/combos/discovery/sweeps/{SWEEP}/reference-column").json()


def _sample(run):
    return {c["result_id"]: c for c in _state(run)["candidates"]}[BTC]["sample"]


def _export_situation(run, symbol="BTC/USDT"):
    res = run["client"].get(f"/api/combos/discovery/sweeps/{SWEEP}/leaderboard/export")
    assert res.status_code == 200 and res.headers["X-Export-Extra"] == "included"
    sheet = openpyxl.load_workbook(io.BytesIO(res.content))["Ranking"]
    header = [c.value for c in sheet[1]]
    rows = [dict(zip(header, [c.value for c in r])) for r in sheet.iter_rows(min_row=2)]
    row = next(r for r in rows if r["Candidato"].split(" · ")[0] == symbol)
    return row["Situação da comparação (extra)"], row["CAGR da referência (extra)"]


def _same_as_btc_trades(source):
    return bench.compute(
        bench.strategy_side(
            symbol="BTC/USDT",
            asset=None,
            window={"start": START, "end": END},
            trades=BTC_TRADES,
        ),
        {**source.identity("SPY"), "kind": "catalog"},
        bench.daily_closes(source.frames["SPY"], "etf"),
    )


def _close_last_candle_differently(cache):
    """Depois da varredura o cache reescreveu a última vela da janela (a vela diária ainda aberta)."""

    path = cache / "BTC_USDT_1d.parquet"
    frame = pd.read_parquet(path)
    frame.loc[frame["timestamp_utc"] == pd.Timestamp(END, tz="UTC"), "close"] += 7.5
    frame.to_parquet(path, index=False)


def test_rebuilt_candles_equal_the_recorded_bytes_with_the_same_serialization(db, cache):
    """O recorte do cache, serializado como o caminho antigo, dá o mesmo SHA-256 do ``prepare``."""

    inputs = {"symbol": "BTC/USDT", "timeframe": "1d", "start_date": START, "end_date": END}
    recorded = di.prepare(dict(inputs))
    try:
        frames = dict(di.legacy_cache_frames("BTC/USDT", "1d", START, END))
        for role in ("candles", "intraday"):
            buf = io.BytesIO()
            frames[role].to_parquet(buf, index=True)
            assert hashlib.sha256(buf.getvalue()).hexdigest() == recorded["files"][role]["sha256"]
    finally:
        di.discard(recorded)


def test_crypto_without_sample_is_redone_by_the_old_path_when_metrics_match(db, cache, run, source):
    _legacy_btc(db)
    before = _digest(cache)
    state = _state(run)
    windows = {c["result_id"]: c for c in state["candidates"]}
    assert windows[BTC]["sample"] == "legacy"  # refazível: não é aviso antes da escolha
    assert windows["RS-NVDA1123B2"]["sample"] == "kept"

    board, cells = run["go"]("SPY")
    btc = cells[BTC]
    assert btc["state"] == "valid"
    assert btc["common_window"] == {"start": "2019-01-02", "end": "2024-12-31", "days": 2190}
    assert btc["delta_cagr_pp"] == pytest.approx(_same_as_btc_trades(source)["delta"]["cagr_pp"])
    # Mesmos parâmetros, janela pedida, direção, template congelado e split da varredura.
    (call,) = FakeOptimizer.calls
    assert call["symbol"] == "BTC/USDT" and call["timeframe"] == "1d"
    assert call["start_date"] == START and call["end_date"] == END
    assert call["direction"] == "long" and call["data_source"] == "ccxt"
    assert call["split_train_ratio"] == 0.7 and call["deep_backtest"] is True
    from app.services.favorite_backtest_refresh_service import _fixed_optimization_ranges

    assert call["custom_ranges"] == _fixed_optimization_ranges({"direction": "long", "fast": 10})
    assert call["template_metadata"] == TEMPLATE_METADATA
    assert call["candles"].index[0] == pd.Timestamp(START, tz="UTC")
    assert call["candles"].index[-1] == pd.Timestamp(END, tz="UTC")
    # Ação/ETF com amostra seguem pelo caminho da amostra; nada mudou neles.
    assert "RS-NVDA1123B2" in run["snapshot_regenerated"] and BTC not in run["snapshot_regenerated"]
    assert cells["RS-NVDA1123B2"]["state"] == "valid"
    assert cells["RS-SPY1123C3"]["state"] == "valid"
    col = board["reference_column"]["column"]
    assert col["counts"]["valid"] == 4 and col["counts"][refcol.SAMPLE_UNAVAILABLE] == 0
    assert col["counts"][bench.SAMPLE_EXPIRED] == 0
    # Só leitura do cache; o spool privado foi apagado e o ambiente restaurado.
    assert _digest(cache) == before
    assert not os.environ.get("DISCOVERY_FROZEN_INPUT_DIR")
    assert not [p for p in (Path(os.environ["DISCOVERY_SPOOL_DIR"])).glob("inputs-*")]
    # A linha do candidato continua dizendo que não há amostra guardada.
    row = next(r for r in board["results"] if r["result_id"] == BTC)
    assert (row.get("sample") or {}).get("state") == "none"
    situation, ref_cagr = _export_situation(run)
    assert situation == "Válida" and ref_cagr is not None


def test_changed_candle_bytes_still_compare_when_the_redone_metrics_match(db, cache, run, source):
    """Caso do ETH/USDT no DEV: a vela diária fechou depois da varredura; o SHA muda, os trades não."""

    _legacy_btc(db)
    _close_last_candle_differently(cache)
    rebuilt = dict(di.legacy_cache_frames("BTC/USDT", "1d", START, END))["candles"]
    buf = io.BytesIO()
    rebuilt.to_parquet(buf, index=True)
    from app.models_discovery import DiscoveryResult

    recorded_sha = db.query(DiscoveryResult).filter(DiscoveryResult.id == BTC).one().candle_version
    assert hashlib.sha256(buf.getvalue()).hexdigest() != recorded_sha
    # CAGR refeito dentro da tolerância (abaixo de meia casa decimal do percentual mostrado).
    _redone(cagr=RECORDED["cagr"] + refcol.CAGR_MATCH_TOLERANCE / 2)

    _board, cells = run["go"]("SPY")
    assert cells[BTC]["state"] == "valid"
    assert cells[BTC]["delta_cagr_pp"] == pytest.approx(
        _same_as_btc_trades(source)["delta"]["cagr_pp"]
    )
    assert len(FakeOptimizer.calls) == 1


@pytest.mark.parametrize(
    "changes",
    [
        {"trades": BTC_TRADES[:-1]},  # um trade a menos
        {"win_rate": 6 / 9},  # outra taxa de acerto
        {"cagr": RECORDED["cagr"] + 2 * refcol.CAGR_MATCH_TOLERANCE},  # outro CAGR na tela
        {"cagr": None},  # refeito sem CAGR
    ],
    ids=["trades", "win_rate", "cagr", "no_cagr"],
)
def test_redone_metrics_that_differ_close_the_cell_without_a_number(
    db, cache, run, source, changes
):
    _legacy_btc(db)
    before = _digest(cache)
    _redone(**changes)

    board, cells = run["go"]("SPY")
    btc = cells[BTC]
    assert btc["state"] == "insufficient"
    assert btc["reason_code"] == refcol.SAMPLE_UNAVAILABLE
    assert btc["reason"] == "Trades refeitos não batem com a varredura."
    assert "vencida" not in btc["reason"] and "delta_cagr_pp" not in btc
    assert len(FakeOptimizer.calls) == 1  # refez, conferiu e recusou
    counts = board["reference_column"]["column"]["counts"]
    assert counts[refcol.SAMPLE_UNAVAILABLE] == 1 and counts[bench.SAMPLE_EXPIRED] == 0
    situation, ref_cagr = _export_situation(run)
    assert situation == "Sem comparação: Trades refeitos não batem com a varredura."
    assert ref_cagr in (None, "")
    payload = refcol.column_cells(db, board["reference_column"]["column"]["id"], [BTC])[BTC]
    assert payload["reason"]["detail"] == refcol.METRICS_MISMATCH
    assert payload["reason"]["text"].endswith("Rode a varredura de novo para comparar.")
    assert not (payload.get("delta") or {}).get("cagr_pp")
    assert (payload.get("reference_result") or {}).get("cagr") is None
    # Mesmo recusado, o cache não foi tocado e o spool sumiu.
    assert _digest(cache) == before
    assert not os.environ.get("DISCOVERY_FROZEN_INPUT_DIR")
    assert not [p for p in (Path(os.environ["DISCOVERY_SPOOL_DIR"])).glob("inputs-*")]


def test_sweep_without_recorded_candle_version_compares_when_metrics_match(db, cache, run, source):
    """1746 das 1747 cripto sem amostra do DEV não gravaram versão das velas nem janela na combinação:
    a janela vem da varredura e a conferência é pelas métricas."""

    _legacy_btc(db, manifest=False, window=False)
    assert _sample(run) == "legacy"
    _board, cells = run["go"]("SPY")
    assert cells[BTC]["state"] == "valid"
    (call,) = FakeOptimizer.calls
    assert call["start_date"] == START and call["end_date"] == END  # do ``snapshot`` da varredura


def test_candles_no_longer_in_the_cache_close_the_cell_with_the_true_reason(db, cache, run, source):
    _legacy_btc(db)
    (cache / "BTC_USDT_15m.parquet").unlink()
    assert _sample(run) == "unavailable"
    _board, cells = run["go"]("SPY")
    assert cells[BTC]["reason_code"] == refcol.SAMPLE_UNAVAILABLE
    assert cells[BTC]["reason"] == "Velas do candidato não estão mais guardadas."
    assert FakeOptimizer.calls == []


def _train_end(start=START, end=END, ratio=0.7):
    """Última vela do treino de uma janela diária (o ``end_at`` que a varredura grava)."""

    days = pd.date_range(start, end, freq="D")
    return days[int(len(days) * ratio) - 1].to_pydatetime()


def test_old_sweep_without_any_recorded_window_derives_it_from_the_recorded_training(
    db, cache, run, source
):
    """Varreduras antigas pediam "2y"/"all" sem gravar datas (a maioria das cripto sem amostra do
    DEV): o resultado grava a primeira e a última vela do treino, e a janela é a menor com o mesmo
    corte do split (mesmo treino, mesmas métricas)."""

    from app.models_discovery import DiscoveryResult

    _legacy_btc(db, manifest=False, window=False, sweep_window=False)
    db.query(DiscoveryResult).filter(DiscoveryResult.id == BTC).one().end_at = _train_end()
    db.commit()
    assert _sample(run) == "legacy"
    _board, cells = run["go"]("SPY")
    assert cells[BTC]["state"] == "valid"
    (call,) = FakeOptimizer.calls
    assert call["start_date"] == "2019-01-01T00:00:00+00:00"
    assert call["end_date"] == "2024-12-31T23:59:59+00:00"  # até o fim da última vela
    assert call["candles"].index[0] == pd.Timestamp(START, tz="UTC")
    assert call["candles"].index[-1] == pd.Timestamp(END, tz="UTC")  # a vela seguinte fica fora
    assert call["intraday_rows"] > 0


def test_derived_window_beyond_the_cache_is_missing(db, cache, run, source):
    from app.models_discovery import DiscoveryResult

    _legacy_btc(db, manifest=False, window=False, sweep_window=False)
    # Treino até o fim de 2024: a janela inteira passaria do que o cache tem (jan/2025).
    db.query(DiscoveryResult).filter(DiscoveryResult.id == BTC).one().end_at = _train_end(
        end="2028-12-31"
    )
    db.commit()
    _board, cells = run["go"]("SPY")
    assert cells[BTC]["reason"] == "Velas do candidato não estão mais guardadas."
    assert FakeOptimizer.calls == []


def test_undeterminable_data_says_so_without_a_number(db, cache, run, source):
    from app.models_discovery import DiscoveryResult

    _legacy_btc(db)
    # Sem as métricas gravadas não há o que conferir: nada roda.
    db.query(DiscoveryResult).filter(DiscoveryResult.id == BTC).one().trades_count = None
    db.commit()
    _board, cells = run["go"]("SPY")
    assert cells[BTC]["reason_code"] == refcol.SAMPLE_UNAVAILABLE
    assert cells[BTC]["reason"] == "Varredura sem dados para refazer os trades."
    assert "delta_cagr_pp" not in cells[BTC]
    assert FakeOptimizer.calls == []
    # Janela sem início ou sem fim não chega a montar o spool.
    for start, end in ((None, END), (START, None)):
        with pytest.raises(di.LegacyInputsUnavailable) as exc:
            with di.legacy_frozen_inputs("BTC/USDT", "1d", start, end):
                pass
        assert exc.value.detail == di.LEGACY_UNRECORDED


def test_undeterminable_window_end_to_end_is_unrecorded_without_running(db, cache, run, source):
    """Sem janela na combinação, sem janela na varredura e sem ``start_at``/``end_at``: o GET já diz
    ``unavailable`` e o job fecha a célula ``unrecorded`` sem chamar o otimizador.

    O esquema atual grava ``start_at``/``end_at`` NOT NULL; o ramo é defensivo. Para exercitá-lo de
    ponta a ponta o teste solta a restrição só no banco de teste e a devolve no fim.
    """

    from sqlalchemy import text

    from app.models_discovery import DiscoveryResult

    _legacy_btc(db, manifest=False, window=False, sweep_window=False)
    db.execute(
        text(
            "ALTER TABLE discovery_results ALTER COLUMN start_at DROP NOT NULL, "
            "ALTER COLUMN end_at DROP NOT NULL"
        )
    )
    db.commit()
    try:
        row = db.query(DiscoveryResult).filter(DiscoveryResult.id == BTC).one()
        row.start_at = None
        row.end_at = None
        db.commit()
        assert _sample(run) == "unavailable"
        board, cells = run["go"]("SPY")
        assert cells[BTC]["reason_code"] == refcol.SAMPLE_UNAVAILABLE
        assert cells[BTC]["reason"] == "Varredura sem dados para refazer os trades."
        assert "delta_cagr_pp" not in cells[BTC]
        assert FakeOptimizer.calls == []
        payload = refcol.column_cells(db, board["reference_column"]["column"]["id"], [BTC])[BTC]
        assert payload["reason"]["detail"] == di.LEGACY_UNRECORDED == "unrecorded"
    finally:
        db.rollback()
        db.execute(
            text(
                "UPDATE discovery_results SET start_at = COALESCE(start_at, '2019-01-01'), "
                "end_at = COALESCE(end_at, '2024-12-31')"
            )
        )
        db.execute(
            text(
                "ALTER TABLE discovery_results ALTER COLUMN start_at SET NOT NULL, "
                "ALTER COLUMN end_at SET NOT NULL"
            )
        )
        db.commit()


def test_unexpected_failure_of_the_old_path_does_not_mention_a_sample(
    db, cache, run, source, monkeypatch
):
    """Erro fora de ``LegacyInputsUnavailable`` no refeito da cripto sem amostra: ``regeneration_failed``
    sem citar amostra (ela nunca existiu) e a planilha diz "Sem comparação", não "Histórico insuficiente".
    """

    from app.services import export_context as xc

    _legacy_btc(db)

    def boom(self, **_kwargs):
        raise RuntimeError("otimizador caiu")

    monkeypatch.setattr(FakeOptimizer, "run_optimization", boom)
    board, cells = run["go"]("SPY")
    assert cells[BTC]["reason_code"] == refcol.REGENERATION_FAILED
    assert cells[BTC]["reason"] == "Trades do candidato não refeitos."
    payload = refcol.column_cells(db, board["reference_column"]["column"]["id"], [BTC])[BTC]
    assert payload["reason"]["text"] == refcol.REGENERATION_FAILED_LEGACY_TEXT
    assert "amostra" not in payload["reason"]["text"]
    assert xc.situation_text(payload) == refcol.REGENERATION_FAILED_LEGACY_TEXT
    situation, ref_cagr = _export_situation(run)
    assert situation == "Sem comparação: Trades do candidato não refeitos."
    assert ref_cagr in (None, "")
    # Candidato com amostra que falha continua com o texto e o prefixo de antes.
    with_sample = {
        "status": "insufficient",
        "reason": {
            "code": refcol.REGENERATION_FAILED,
            "text": "Não foi possível refazer os trades do candidato a partir da amostra.",
            "short": "Trades do candidato não refeitos.",
        },
    }
    assert xc.situation_text(with_sample, short=True) == (
        "Histórico insuficiente: Trades do candidato não refeitos."
    )


def test_really_expired_sample_is_still_expired_next_to_a_legacy_candidate(
    db, cache, source, monkeypatch
):
    from app.models_discovery import DiscoveryResult

    user = make_user(db, "carol", admin=True)
    actor = str(user.id)
    _seed(db, actor=actor, expired={"RS-SOL1123D4"})
    _legacy_btc(db)
    queued: list[str] = []
    refcol.set_reference(db, SWEEP, actor, "SPY", enqueue_fn=queued.append, source=source)
    FakeOptimizer.calls = []
    _redone()

    def regenerate(_db, result):
        if result.snapshot_id:
            return TRADES.get(result.id, [])
        return refcol.regenerate_trades(_db, result, optimizer_factory=FakeOptimizer)

    Session = sessionmaker(bind=db.get_bind())
    refcol.run_column(queued[0], db_factory=Session, source=source, regenerate=regenerate)
    state = refcol.state(db, SWEEP, actor)
    counts = state["column"]["counts"]
    assert counts[bench.SAMPLE_EXPIRED] == 1 and counts[refcol.SAMPLE_UNAVAILABLE] == 0
    rows = [
        {"result_id": "RS-SOL1123D4", "eligibility": "eligible"},
        {"result_id": BTC, "eligibility": "eligible"},
    ]
    refcol.attach_to_leaderboard(db, SWEEP, actor, rows)
    assert (
        rows[0]["reference_comparison"]["reason"] == "Amostra do candidato vencida em 30/09/2026."
    )
    assert rows[1]["reference_comparison"]["state"] == "valid"
    samples = {c["result_id"]: c["sample"] for c in state["candidates"]}
    assert samples["RS-SOL1123D4"] == "expired" and samples[BTC] == "legacy"
    assert db.query(DiscoveryResult).filter(DiscoveryResult.id == BTC).one().snapshot_id is None


def test_metrics_match_rule_and_tolerance():
    class Row:
        trades_count = 9
        win_rate = 7 / 9
        cagr = 0.4213

    same = {"trades_count": 9, "win_rate": 7 / 9, "cagr": 0.4213}
    assert refcol.metrics_match(Row, same)
    assert refcol.CAGR_MATCH_TOLERANCE == 0.0005  # meia casa decimal do percentual (fmtPct)
    assert refcol.metrics_match(Row, {**same, "cagr": 0.4213 + 0.0004})
    assert not refcol.metrics_match(Row, {**same, "cagr": 0.4213 + 0.0006})
    assert not refcol.metrics_match(Row, {**same, "trades_count": 10})
    assert not refcol.metrics_match(Row, {**same, "win_rate": 7 / 9 + 0.01})
    assert not refcol.metrics_match(Row, {**same, "cagr": None})
    # Mesma grandeza do ``run_combination``: CAGR das colunas de ranking, ``None`` sem trades.
    redone = refcol.redone_metrics(
        {"trades": BTC_TRADES, "best_metrics": {"win_rate": 7 / 9, "cagr": 0.4213}}
    )
    assert redone == same
    assert refcol.redone_metrics({"trades": [], "best_metrics": {"cagr": 0.1}})["cagr"] is None
