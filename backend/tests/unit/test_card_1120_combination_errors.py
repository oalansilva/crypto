"""Combinação com erro e template ``bollinger_rsi_adx`` (card #1120, grupo 8, decisões de Alan).

- uma combinação com erro é descartada e contada; o ativo só falha se nenhuma funcionar;
- a Descoberta (#1093) continua abortando no primeiro erro;
- o template ``bollinger_rsi_adx`` avalia toda a faixa de ``rsi_length``, ``adx_length`` e
  ``adx_threshold``, no seed e na migração de dados do registro existente.
"""

from __future__ import annotations

import importlib.util
import itertools
import json
import uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pandas as pd
import pytest

from app.migrations.seed_prebuilt_strategies import prebuilt_strategies
from app.services import combo_optimizer as opt
from app.services.combo_optimizer import ComboOptimizer
from app.services.discovery_resources import CalculationFailure, OperationalFailure
from app.services.discovery_stream import (
    FailureLog,
    NoValidCombination,
    ResultSpool,
    execute_stream,
    failure_reason,
)
from app.services.strategy_transparency import build_strategy_transparency
from app.strategies.combos.combo_strategy import ComboStrategy
from oracles._build_card_945 import apply_param_overrides, load_templates, metadata_from_export
from test_card_1118_api_and_catalog import public_db  # noqa: F401
from test_card_1118_optimizer_regression import _walk
from test_card_1120_batch_run import (  # noqa: F401
    _favorites,
    _items,
    _payload,
    _run,
    _start,
    batch_env,
)

BACKEND = Path(__file__).parents[2]
MIGRATION = BACKEND / "alembic/versions/20261025_0001_bollinger_rsi_adx_rules_follow_params.py"
UNKNOWN_RSI = (
    "Error evaluating vectorized logic '(close < bb_lower) & (RSI_14 < 30) & (ADX_14 > 20)': "
    "Logic references unknown columns/functions: RSI_14. Available example columns: open, high"
)


def _migration():
    spec = importlib.util.spec_from_file_location("migration_1120_bollinger", MIGRATION)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _exported_bollinger() -> dict:
    """O registro de hoje (com o defeito), no formato em que ele está no banco."""
    rows = json.loads((BACKEND / "config/combo_templates_export.json").read_text())
    return next(row for row in rows if row["name"] == "bollinger_rsi_adx")["template_data"]


def _seeded_bollinger() -> dict:
    row = next(r for r in prebuilt_strategies() if r["name"] == "bollinger_rsi_adx")
    return row["template_data"]


def _frame(rows: int = 600) -> pd.DataFrame:
    index = pd.date_range("2024-01-01", periods=rows, freq="1D", tz="UTC")
    return _walk(index, 5, 100.0, 0.03)


def _rules_evaluate(data: dict, params: dict, frame: pd.DataFrame) -> pd.Series:
    indicators, stop_loss = apply_param_overrides(data, params)
    strategy = ComboStrategy(
        indicators=indicators,
        entry_logic=data["entry_logic"],
        exit_logic=data["exit_logic"],
        stop_loss=stop_loss,
    )
    calculated = strategy.calculate_indicators(frame)
    strategy._evaluate_logic_vectorized(calculated, data["exit_logic"])
    return strategy._evaluate_logic_vectorized(calculated, data["entry_logic"])


# ------------------------------------------------------------------ 8.x motivo da combinação


def test_failure_reason_drops_the_rule_text_and_the_column_list_so_reasons_group():
    reason = failure_reason(UNKNOWN_RSI)
    assert reason == "a regra usa coluna que a combinação não tem (RSI_14)"
    other = UNKNOWN_RSI.replace("open, high", "open, high, RSI_12, ADX_20")
    assert failure_reason(other) == reason  # a lista de colunas varia por combinação
    assert failure_reason(None) == "erro sem mensagem"
    assert len(failure_reason("x" * 1000)) == 300


def test_failure_log_groups_counts_and_bounds_the_reasons():
    log = FailureLog()
    for _ in range(3):
        log.add(UNKNOWN_RSI)
    log.add("divisão por zero")
    for number in range(40):
        log.add(f"erro distinto {number}")
    summary = log.summary()
    assert summary["failed"] == 44
    grouped = {r["reason"]: r["count"] for r in summary["reasons"]}
    assert grouped["a regra usa coluna que a combinação não tem (RSI_14)"] == 3
    assert grouped["outros motivos"] == 32  # passou de 10 motivos: o resto vai junto
    assert len(grouped) == 11  # 10 motivos + "outros motivos"
    assert summary["message"].startswith("44 combinações com erro: ")
    assert FailureLog().summary() is None


def test_run_backtest_logic_error_names_the_cause_not_the_generic_code():
    data = metadata_from_export(load_templates()["bollinger_rsi_adx"])
    metrics, _ = opt._run_backtest_logic(
        {**data, "name": "bollinger_rsi_adx"},
        {"rsi_length": 12, "direction": "long"},
        _frame(),
        False,
        "TST/USDT",
        None,
        None,
    )
    assert "RSI_14" in metrics["error"]
    assert metrics["error"] != "calculation_error"


# ------------------------------------------------------------------ execute_stream


def _args(count):
    return lambda: (({}, {}, None, "x", i, False, "X", None, None, i) for i in range(count))


def _row(trial, ok=True, error=None):
    if ok:
        return {
            "trial_index": trial,
            "value": trial,
            "success": True,
            "metrics": {"sharpe_ratio": trial, "total_return": trial, "total_trades": 0},
        }
    return {"trial_index": trial, "success": False, "error": error or UNKNOWN_RSI}


def _worker(bad):
    def run(batch):
        return [_row(arg[9], arg[9] not in bad) for arg in batch]

    return run


def test_strict_stream_aborts_on_the_first_failed_combination(tmp_path):
    with ThreadPoolExecutor(1) as pool, ResultSpool(root=tmp_path) as spool:
        with pytest.raises(CalculationFailure) as failure:
            execute_stream(pool, _worker({1}), _args(4), 4, spool)
    assert failure.value.code == "calculation_error"
    assert failure.value.counters["failed"] == 1


def test_tolerant_stream_skips_the_failed_combinations_and_counts_them(tmp_path):
    log = FailureLog()
    with ThreadPoolExecutor(1) as pool, ResultSpool(root=tmp_path) as spool:
        counters = execute_stream(pool, _worker({1, 3}), _args(6), 6, spool, failures=log)
        ranked = spool.ranked(0, {}, {"parameter": "x"}, 10)
    assert counters["executed"] == 6 and counters["failed"] == 2 and counters["succeeded"] == 4
    assert counters["unknown"] == 0 and counters["remaining"] == 0
    assert sorted(r["trial_index"] for r in ranked) == [0, 2, 4, 5]  # só as que funcionaram
    assert log.summary()["failed"] == 2 and log.summary()["executed"] == 6
    assert log.summary()["reasons"] == [
        {"reason": "a regra usa coluna que a combinação não tem (RSI_14)", "count": 2}
    ]


def test_tolerant_stream_without_a_working_combination_reports_it_to_the_caller(tmp_path):
    log = FailureLog()
    with ThreadPoolExecutor(1) as pool, ResultSpool(root=tmp_path) as spool:
        counters = execute_stream(pool, _worker({0, 1, 2}), _args(3), 3, spool, failures=log)
        assert spool.ranked(0, {}, {"parameter": "x"}, 10) == []
    assert counters["failed"] == 3 and counters["succeeded"] == 0
    assert log.succeeded == 0 and log.failed == 3
    failure = NoValidCombination(log, counters)  # o otimizador é quem decide falhar o ativo
    assert isinstance(failure, CalculationFailure) and failure.code == "no_valid_combination"
    assert "RSI_14" in str(failure) and "3 com erro" in str(failure)
    assert "calculation_error" not in str(failure)


def test_tolerant_stream_still_fails_on_a_lost_batch(tmp_path):
    def lost(batch):
        return [_row(arg[9]) for arg in batch][:-1]  # um resultado a menos: incompleto

    with ThreadPoolExecutor(1) as pool, ResultSpool(root=tmp_path) as spool:
        with pytest.raises(OperationalFailure, match="incomplete_batch"):
            execute_stream(pool, lost, _args(4), 4, spool, failures=FailureLog())


# ------------------------------------------------------------------ otimizador (Combo/Otimização × Descoberta)


class _Templates:
    def __init__(self, data: dict):
        self.metadata = {"name": "bollinger_rsi_adx", **data}

    def get_template_metadata(self, _name):
        return self.metadata

    def create_strategy(self, template_name, parameters=None):
        meta = self.metadata
        indicators, stop_loss = apply_param_overrides(
            {"indicators": meta["indicators"], "stop_loss": meta.get("stop_loss", 0.015)},
            parameters or {},
        )
        return ComboStrategy(
            indicators=indicators,
            entry_logic=meta["entry_logic"],
            exit_logic=meta["exit_logic"],
            stop_loss=stop_loss,
            direction=(parameters or {}).get("direction", "long"),
        )


class _Provider:
    def __init__(self, frame):
        self.frame = frame

    def fetch_ohlcv(self, symbol, timeframe, since_str=None, until_str=None):
        return self.frame.copy()


def _ranges(rsi_length):
    fixed = lambda value, step=1: {"min": value, "max": value, "step": step}  # noqa: E731
    return {
        "bb_length": fixed(20),
        "bb_std": fixed(2.0, 0.1),
        "adx_length": fixed(14),
        "adx_threshold": fixed(20),
        "stop_loss": fixed(0.02, 0.0001),
        "rsi_length": rsi_length,
    }


def _optimizer(data):
    optimizer = ComboOptimizer(workers=1, provider=_Provider(_frame(700)))
    optimizer.combo_service = _Templates(data)
    return optimizer


def _optimize(optimizer, ranges, **extra):
    return optimizer.run_optimization(
        template_name="bollinger_rsi_adx",
        symbol="TST1120/USDT",
        timeframe="1d",
        data_source="ccxt",
        start_date="2024-01-01",
        end_date="2025-12-01",
        custom_ranges=ranges,
        deep_backtest=False,
        **extra,
    )


@pytest.mark.timeout(300)
def test_discovery_path_stays_strict_and_the_tolerance_is_opt_in():
    import inspect

    default = inspect.signature(ComboOptimizer.run_optimization).parameters
    assert default["tolerate_combination_errors"].default is False
    assert inspect.signature(execute_stream).parameters["failures"].default is None
    broken = metadata_from_export(load_templates()["bollinger_rsi_adx"])
    mixed = _ranges({"min": 12, "max": 14, "step": 2})  # 12 não acha RSI_14; 14 acha
    with pytest.raises(CalculationFailure) as failure:
        _optimize(_optimizer(broken), mixed, direction="long", split_train_ratio=None)
    assert failure.value.code == "calculation_error"


@pytest.mark.timeout(300)
def test_tolerant_optimization_keeps_the_working_combinations_and_reports_the_rest():
    broken = metadata_from_export(load_templates()["bollinger_rsi_adx"])
    result = _optimize(
        _optimizer(broken),
        _ranges({"min": 12, "max": 14, "step": 2}),
        tolerate_combination_errors=True,
    )
    assert result["best_parameters"]["rsi_length"] == 14  # a única que funciona
    errors = result["combination_errors"]
    assert errors["failed"] >= 1 and errors["executed"] > errors["failed"]
    assert errors["reasons"][0]["reason"] == (
        "a regra usa coluna que a combinação não tem (RSI_14)"
    )
    assert errors["message"].startswith(f"{errors['failed']} combinações com erro: ")


@pytest.mark.timeout(300)
def test_tolerant_optimization_without_a_working_combination_fails_with_the_reason():
    broken = metadata_from_export(load_templates()["bollinger_rsi_adx"])
    with pytest.raises(NoValidCombination) as failure:
        _optimize(
            _optimizer(broken),
            _ranges({"min": 12, "max": 12, "step": 1}),
            tolerate_combination_errors=True,
        )
    assert "RSI_14" in str(failure.value) and "calculation_error" not in str(failure.value)


@pytest.mark.timeout(300)
def test_fixed_template_runs_every_combination_and_reports_no_errors():
    fixed = {**_seeded_bollinger(), "stop_loss": 0.02}
    result = _optimize(
        _optimizer(fixed),
        _ranges({"min": 10, "max": 14, "step": 2}),
        tolerate_combination_errors=True,
    )
    assert result["combination_errors"] is None
    assert result["best_parameters"]["rsi_length"] in (10, 12, 14)


# ------------------------------------------------------------------ template


def test_seeded_template_evaluates_every_combination_of_the_default_range():
    seed = next(r for r in prebuilt_strategies() if r["name"] == "bollinger_rsi_adx")
    schema = seed["optimization_schema"]
    frame = _frame()

    def values(spec):
        count = int(round((spec["max"] - spec["min"]) / spec["step"])) + 1
        return [spec["min"] + step * spec["step"] for step in range(count)]

    entries = {}
    for rsi, adx, threshold in itertools.product(
        values(schema["rsi_length"]),
        values(schema["adx_length"]),
        values(schema["adx_threshold"]),
    ):
        params = {"rsi_length": rsi, "adx_length": adx, "adx_threshold": threshold}
        entries[(rsi, adx, threshold)] = int(
            _rules_evaluate(seed["template_data"], params, frame).sum()
        )
    assert len(entries) == 6 * 6 * 4  # nenhuma combinação da faixa ficou de fora
    # o limite do ADX agora age: mais alto exige mais, nunca libera entradas
    for rsi, adx in itertools.product(values(schema["rsi_length"]), values(schema["adx_length"])):
        counts = [entries[(rsi, adx, t)] for t in values(schema["adx_threshold"])]
        assert counts == sorted(counts, reverse=True)
    assert len({entries[k] for k in entries}) > 1  # o parâmetro muda o resultado


def test_the_old_rules_only_worked_at_length_14_and_the_new_ones_do_not_depend_on_it():
    old = metadata_from_export(load_templates()["bollinger_rsi_adx"])
    frame = _frame()
    with pytest.raises(RuntimeError, match="unknown columns/functions: RSI_14"):
        _rules_evaluate(old, {"rsi_length": 10}, frame)
    with pytest.raises(RuntimeError, match="unknown columns/functions: ADX_14"):
        _rules_evaluate(old, {"adx_length": 10}, frame)
    new = _migration().upgraded(_exported_bollinger())
    for rsi, adx in ((10, 10), (14, 20), (20, 12)):
        _rules_evaluate(new, {"rsi_length": rsi, "adx_length": adx}, frame)


def test_defaults_give_the_same_signals_before_and_after():
    frame = _frame(900)
    old = _exported_bollinger()
    new = _migration().upgraded(old)
    before = _rules_evaluate(old, {}, frame)
    after = _rules_evaluate(new, {}, frame)
    assert before.equals(after)  # com os valores padrão a estratégia é a mesma


def test_fixed_template_still_explains_its_rules_in_the_public_transparency():
    manifest = build_strategy_transparency(
        "bollinger_rsi_adx", _migration().upgraded(_exported_bollinger()), timeframe="1d"
    )
    blocks = {block.participation: block for block in manifest.logic_blocks}
    assert blocks["entry"].description and blocks["entry"].condition_count == 3
    assert blocks["exit"].description and blocks["exit"].condition_count == 2


# ------------------------------------------------------------------ migração de dados


def test_migration_rewrites_only_the_old_record_and_is_idempotent_and_reversible():
    migration = _migration()
    assert migration.revision == "20261025_0001" and migration.down_revision == "20261024_0001"
    old = _exported_bollinger()
    new = migration.upgraded(old)
    assert new["entry_logic"] == "(close < bb_lower) & (rsi < 30) & (adx > adx_threshold)"
    assert new["exit_logic"] == "(close > bb_middle) | (rsi > 70)"
    by_type = {i["type"]: i for i in new["indicators"]}
    assert by_type["rsi"]["alias"] == "rsi" and by_type["adx"]["alias"] == "adx"
    assert by_type["adx"]["params"] == {"length": 14, "threshold": 20}
    assert by_type["bbands"] == next(i for i in old["indicators"] if i["type"] == "bbands")
    for key in ("stop_loss", "optimization_schema", "description", "name"):
        assert new[key] == old[key]  # o resto do registro não muda
    assert migration.upgraded(new) is None  # idempotente
    assert migration.downgraded(new) == old  # reversível
    edited = {**old, "entry_logic": "(close < bb_lower) & (RSI_14 < 25) & (ADX_14 > 20)"}
    assert migration.upgraded(edited) is None  # regra editada à mão fica como está


def test_migration_updates_the_template_record_in_postgres_and_nothing_else(unit_database_url):
    from alembic.migration import MigrationContext
    from alembic.operations import Operations
    from sqlalchemy import create_engine, text

    migration = _migration()
    old = json.dumps(_exported_bollinger())
    other = json.dumps({"indicators": [], "entry_logic": "close > 0", "exit_logic": "close < 0"})
    engine = create_engine(unit_database_url)
    schema = "migration_1120_tpl_" + uuid.uuid4().hex[:12]
    try:
        with engine.begin() as conn:
            conn.execute(text(f"CREATE SCHEMA {schema}"))
            conn.execute(text(f"SET LOCAL search_path TO {schema}"))
            conn.execute(
                text(
                    "CREATE TABLE combo_templates (id serial PRIMARY KEY, name varchar NOT NULL, "
                    "template_data text NOT NULL, updated_at timestamp)"
                )
            )
            for name, data in (
                ("bollinger_rsi_adx", old),
                ("bollinger_rsi_adx (cópia do usuário)", old),
                ("ema_rsi", other),
            ):
                conn.execute(
                    text("INSERT INTO combo_templates (name, template_data) VALUES (:n, :d)"),
                    {"n": name, "d": data},
                )

            def stored():
                rows = conn.execute(
                    text("SELECT name, template_data, updated_at FROM combo_templates")
                ).fetchall()
                return {r[0]: (r[1], r[2]) for r in rows}

            context = MigrationContext.configure(conn)
            with Operations.context(context):
                migration.upgrade()
                migration.upgrade()  # idempotente
            after = stored()
            assert json.loads(after["bollinger_rsi_adx"][0])["entry_logic"].startswith(
                "(close < bb_lower) & (rsi < 30)"
            )
            assert after["bollinger_rsi_adx"][1] is not None
            assert after["bollinger_rsi_adx (cópia do usuário)"][0] == old
            assert after["ema_rsi"][0] == other
            with Operations.context(context):
                migration.downgrade()
            assert json.loads(stored()["bollinger_rsi_adx"][0]) == json.loads(old)
            conn.execute(text(f"DROP SCHEMA {schema} CASCADE"))
    finally:
        engine.dispose()


def test_migration_transforms_ignore_anything_that_is_not_the_old_or_new_record():
    migration = _migration()
    assert migration.upgraded({}) is None and migration.downgraded({}) is None
    assert migration.upgraded({"entry_logic": "x"}) is None
    assert migration.downgraded(_exported_bollinger()) is None  # ainda não migrado


# ------------------------------------------------------------------ lote (executor real)


def _batch_templates(monkeypatch, data):
    templates = _Templates(data)
    monkeypatch.setattr(
        "app.services.combo_service.ComboService.get_template_metadata",
        lambda self, name: templates.metadata,
    )

    def factory():
        optimizer = ComboOptimizer(workers=1)
        optimizer.combo_service = templates
        return optimizer

    return factory


@pytest.mark.timeout(900)
def test_batch_saves_the_favorite_with_the_working_combinations_and_shows_the_count(
    batch_env, monkeypatch
):
    broken = metadata_from_export(load_templates()["bollinger_rsi_adx"])
    factory = _batch_templates(monkeypatch, broken)
    payload = _payload(
        ["BTC/USDT"],
        template_name="bollinger_rsi_adx",
        custom_ranges=_ranges({"min": 12, "max": 14, "step": 2}),
    )
    job = _run(_start(payload, "00000000-0000-4000-8000-000000001120"), factory)

    item = _items(job)["BTC/USDT"]
    assert item["state"] in ("success", "success_daily"), item
    assert " combinações com erro: " in item["reason"]
    assert "a regra usa coluna que a combinação não tem (RSI_14)" in item["reason"]
    favorite = _favorites(batch_env)[0]
    assert item["favorite_id"] == favorite.id
    assert favorite.parameters["rsi_length"] == 14  # a combinação que funcionou
    assert job["status"] == "completed" and job["failed"] == 0 and job["succeeded"] == 1


@pytest.mark.timeout(900)
def test_batch_asset_without_a_working_combination_fails_with_the_real_reason(
    batch_env, monkeypatch
):
    broken = metadata_from_export(load_templates()["bollinger_rsi_adx"])
    factory = _batch_templates(monkeypatch, broken)
    payload = _payload(
        ["BTC/USDT"],
        template_name="bollinger_rsi_adx",
        custom_ranges=_ranges({"min": 12, "max": 12, "step": 1}),
    )
    job = _run(_start(payload, "00000000-0000-4000-8000-000000001121"), factory)

    item = _items(job)["BTC/USDT"]
    assert item["state"] == "failed"
    assert "nenhuma combinação válida" in item["reason"] and "RSI_14" in item["reason"]
    assert "calculation_error" not in item["reason"]
    assert "Nenhum favorito gravado" in item["reason"]
    assert _favorites(batch_env) == []
    assert job["failed"] == 1 and "RSI_14" in job["errors"][0]["error"]


@pytest.mark.timeout(900)
def test_batch_with_the_fixed_template_runs_every_combination_without_a_note(
    batch_env, monkeypatch
):
    fixed = {**_seeded_bollinger(), "stop_loss": 0.02}
    factory = _batch_templates(monkeypatch, fixed)
    payload = _payload(
        ["BTC/USDT"],
        template_name="bollinger_rsi_adx",
        custom_ranges=_ranges({"min": 10, "max": 14, "step": 2}),
    )
    job = _run(_start(payload, "00000000-0000-4000-8000-000000001122"), factory)

    item = _items(job)["BTC/USDT"]
    assert item["state"] in ("success", "success_daily") and item["reason"] is None
