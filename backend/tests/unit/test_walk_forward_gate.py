"""Testes do walk-forward gate e split temporal (card #470)."""

from __future__ import annotations

import pandas as pd
import pytest

from app.services.combo_optimizer import split_train_holdout
from app.services.walk_forward_revalidation import oos_gate_decision


def _frame(n: int) -> pd.DataFrame:
    idx = pd.date_range("2020-01-01", periods=n, freq="D")
    return pd.DataFrame({"close": range(1, n + 1), "open": range(1, n + 1)}, index=idx)


class TestSplitTrainHoldout:
    def test_split_70_30_contiguous_and_disjoint(self):
        df = _frame(100)
        train, holdout = split_train_holdout(df, 0.7)
        assert len(train) == 70
        assert len(holdout) == 30
        assert train.index[-1] < holdout.index[0]
        assert not train.index.intersection(holdout.index).size

    def test_split_sorts_by_time(self):
        df = _frame(10).iloc[::-1]  # reversed order
        train, holdout = split_train_holdout(df, 0.7)
        assert train.index.is_monotonic_increasing
        assert holdout.index.is_monotonic_increasing
        assert len(train) == 7
        assert len(holdout) == 3

    def test_split_rejects_invalid_ratio(self):
        with pytest.raises(ValueError):
            split_train_holdout(_frame(10), 1.0)
        with pytest.raises(ValueError):
            split_train_holdout(_frame(10), 0.0)

    def test_split_rejects_short_frame(self):
        with pytest.raises(ValueError):
            split_train_holdout(_frame(1), 0.7)
        with pytest.raises(ValueError):
            split_train_holdout(pd.DataFrame(), 0.7)


class TestOosGateDecision:
    def test_go_allows(self):
        decision = oos_gate_decision({"status": "GO", "reasons": ["ok"]})
        assert decision["allowed"] is True

    def test_no_verdict_legacy_allows(self):
        assert oos_gate_decision(None)["allowed"] is True
        assert oos_gate_decision({})["allowed"] is True

    def test_no_go_blocks_with_reason(self):
        decision = oos_gate_decision({"status": "NO-GO", "reasons": ["Sharpe baixo", "DD alto"]})
        assert decision["allowed"] is False
        assert "Sharpe baixo" in decision["reason"]
        assert "DD alto" in decision["reason"]

    def test_no_go_admin_override_allows(self):
        decision = oos_gate_decision(
            {"status": "NO-GO", "reasons": ["DD alto"]},
            override=True,
            is_admin=True,
        )
        assert decision["allowed"] is True

    def test_no_go_override_without_admin_blocks(self):
        decision = oos_gate_decision(
            {"status": "NO-GO", "reasons": ["DD alto"]},
            override=True,
            is_admin=False,
        )
        assert decision["allowed"] is False

    def test_error_verdict_blocks(self):
        decision = oos_gate_decision({"status": "ERROR", "reasons": ["holdout falhou"]})
        assert decision["allowed"] is False


class TestHoldoutMetricsEnableGo:
    """Regressão do P0: com cagr/calmar/benchmark no holdout, o gate pode
    retornar GO (avaliado via evaluate_go_nogo com métricas completas)."""

    def test_evaluate_go_nogo_returns_go_with_full_holdout_metrics(self):
        from app.metrics.criteria import evaluate_go_nogo

        metrics = {
            "total_trades": 120,
            "win_rate": 0.55,
            "total_return": 0.6,
            "sharpe_ratio": 1.2,
            "max_drawdown": 0.12,  # decimal
            "profit_factor": 1.8,
            "expectancy": 0.005,
            "cagr": 0.35,
            "calmar_ratio": 2.9,
            "benchmark": {"cagr": 0.10},
        }
        result = evaluate_go_nogo(metrics)
        assert result.status == "GO", result.reasons

    def test_evaluate_go_nogo_without_cagr_always_no_go(self):
        """Sem cagr/benchmark/calmar (métricas legadas do _metrics_from_trades),
        o veredito seria NO-GO — motivo pelo qual o holdout agora computa essas
        métricas explicitamente."""
        from app.metrics.criteria import evaluate_go_nogo

        metrics = {
            "total_trades": 120,
            "win_rate": 0.55,
            "total_return": 0.6,
            "sharpe_ratio": 1.2,
            "max_drawdown": 0.12,
            "profit_factor": 1.8,
            "expectancy": 0.005,
        }
        result = evaluate_go_nogo(metrics)
        assert result.status == "NO-GO"
        assert any("CAGR" in r or "Calmar" in r for r in result.reasons)


class TestRevalidateAllFavorites:
    def test_revalidate_all_iterates_and_aggregates(self, monkeypatch):
        from app.services import walk_forward_revalidation as wfr

        class FakeRow:
            def __init__(self, fid, symbol):
                self.id = fid
                self.symbol = symbol
                self.parameters = {"direction": "long"}
                self.strategy_name = "multi_ma_crossover"
                self.timeframe = "1d"
                self.start_date = None
                self.end_date = None
                self.metrics = {"total_return_pct": 1.0}
                self.user_id = "user-a"

        rows = [FakeRow(1, "BTC/USDT"), FakeRow(2, "ETH/USDT")]

        class FakeSession:
            def __init__(self, *a, **k):
                pass

            def query(self, model):
                return self

            def filter(self, **kwargs):
                return self

            def order_by(self, *_a):
                return self

            def all(self):
                return rows

            def close(self):
                pass

        def fake_revalidate(row, db=None):
            return {
                "favorite_id": row.id,
                "symbol": row.symbol,
                "verdict": "GO" if row.id == 1 else "NO-GO",
            }

        monkeypatch.setattr(wfr, "SessionLocal", FakeSession)
        monkeypatch.setattr(wfr, "revalidate_favorite", fake_revalidate)

        summary = wfr.revalidate_all_favorites()
        assert summary["total"] == 2
        assert summary["revalidated"] == 2
        assert summary["go"] == 1
        assert summary["no_go"] == 1

    def test_revalidate_all_continues_on_failure(self, monkeypatch):
        from app.services import walk_forward_revalidation as wfr

        class FakeRow:
            def __init__(self, fid, symbol):
                self.id = fid
                self.symbol = symbol

        rows = [FakeRow(1, "BTC/USDT"), FakeRow(2, "ETH/USDT")]

        class FakeSession:
            def __init__(self, *a, **k):
                pass

            def query(self, model):
                return self

            def filter(self, **kwargs):
                return self

            def order_by(self, *_a):
                return self

            def all(self):
                return rows

            def close(self):
                pass

        def fake_revalidate(row, db=None):
            if row.id == 1:
                raise RuntimeError("boom")
            return {"favorite_id": row.id, "symbol": row.symbol, "verdict": "GO"}

        monkeypatch.setattr(wfr, "SessionLocal", FakeSession)
        monkeypatch.setattr(wfr, "revalidate_favorite", fake_revalidate)

        summary = wfr.revalidate_all_favorites()
        assert summary["total"] == 2
        assert summary["revalidated"] == 1
        assert summary["failures"] == 1
        assert summary["results"][0]["error"] == "boom"

    def test_revalidate_all_respects_max_favorites(self, monkeypatch):
        from app.services import walk_forward_revalidation as wfr

        class FakeRow:
            def __init__(self, fid):
                self.id = fid
                self.symbol = "X/USDT"

        rows = [FakeRow(1), FakeRow(2), FakeRow(3)]

        class FakeSession:
            def __init__(self, *a, **k):
                pass

            def query(self, model):
                return self

            def filter(self, **kwargs):
                return self

            def order_by(self, *_a):
                return self

            def all(self):
                return rows

            def close(self):
                pass

        monkeypatch.setattr(wfr, "SessionLocal", FakeSession)
        monkeypatch.setattr(
            wfr,
            "revalidate_favorite",
            lambda row, db=None: {
                "favorite_id": row.id,
                "symbol": row.symbol,
                "verdict": "GO",
            },
        )

        summary = wfr.revalidate_all_favorites(max_favorites=2)
        assert summary["total"] == 2


class TestRevalidateFavoriteErrors:
    def test_revalidate_favorite_rolls_back_when_row_missing(self, monkeypatch):
        from app.services import walk_forward_revalidation as wfr

        class FakeRow:
            id = 99
            symbol = "BTC/USDT"
            timeframe = "1d"
            strategy_name = "multi_ma_crossover"
            parameters = {"direction": "long"}
            start_date = None
            end_date = None
            metrics = {}

        rolled_back = []

        class FakeSession:
            def __init__(self, *a, **k):
                pass

            def query(self, model):
                return self

            def filter(self, *args, **kwargs):
                return self

            def first(self):
                return None

            def rollback(self):
                rolled_back.append(True)

            def close(self):
                pass

        class FakeOptimizer:
            def run_optimization(self, **_kwargs):
                return {
                    "best_metrics": {},
                    "oos_metrics": {},
                    "oos_verdict": {"status": "GO", "reasons": []},
                }

        monkeypatch.setattr(wfr, "SessionLocal", FakeSession)
        monkeypatch.setattr(wfr, "ComboOptimizer", FakeOptimizer)

        with pytest.raises(ValueError):
            wfr.revalidate_favorite(FakeRow(), db=FakeSession())
        assert rolled_back == [True]

    def test_revalidate_all_filters_by_user(self, monkeypatch):
        from app.services import walk_forward_revalidation as wfr

        class FakeRow:
            def __init__(self, fid):
                self.id = fid
                self.symbol = "X/USDT"

        rows = [FakeRow(1)]

        class FakeSession:
            def __init__(self, *a, **k):
                pass

            def query(self, model):
                return self

            def filter(self, *args, **kwargs):
                return self

            def order_by(self, *_a):
                return self

            def all(self):
                return rows

            def close(self):
                pass

        monkeypatch.setattr(wfr, "SessionLocal", FakeSession)
        monkeypatch.setattr(
            wfr,
            "revalidate_favorite",
            lambda row, db=None: {
                "favorite_id": row.id,
                "symbol": row.symbol,
                "verdict": "GO",
            },
        )

        summary = wfr.revalidate_all_favorites(user_id="user-a")
        assert summary["total"] == 1
        assert summary["revalidated"] == 1
