"""Card #1119, tarefa 6.2: o refresh diário de favorito de cripto usa a rotina nova e guarda o número anterior."""

from __future__ import annotations

from datetime import datetime, timedelta

from sqlalchemy.orm import sessionmaker

from app.models import AutoBacktestRun, FavoriteStrategy
from app.services.favorite_backtest_refresh_service import (
    REFRESH_STATUS_SUCCESS,
    FavoriteBacktestRefreshService,
)
from test_card_1118_favorite_samples import (  # noqa: F401
    _RefreshOptimizer,
    _favorite,
    _snapshot,
    engine,  # fixture
)


class _GapAwareOptimizer(_RefreshOptimizer):
    """Resultado do otimizador com a regra do gap: execução, convenções e identidade vêm junto."""

    def run_optimization(self, **kwargs):
        result = super().run_optimization(**kwargs)
        now = datetime.utcnow()
        result["trades"] = [
            {
                "entry_time": (now - timedelta(days=3)).isoformat(),
                "exit_time": (now - timedelta(days=1)).isoformat(),
                "profit": -0.04,
                "exit_reason": "stop_loss_gap",
                "stop_price": 95.0,
                "exit_price": 91.0,
            }
        ]
        result["execution"] = {"precision_effective": "candle", "gap_stops": 1, "timeframe": "1d"}
        result["conventions"] = {"fee": 0.00075, "fee_confirmed": True}
        result["asset"] = {"symbol": "BTC/USDT", "asset_class": "crypto", "currency": "USDT"}
        return result


def test_refresh_runs_the_new_routine_keeps_the_previous_number_and_the_gap_count(engine):
    old = _snapshot(engine, base=50.0)
    Session = sessionmaker(bind=engine)

    class Optimizer(_GapAwareOptimizer):
        pass

    Optimizer.engine = engine
    Optimizer.created = []
    service = FavoriteBacktestRefreshService(
        db_factory=Session,
        optimizer_factory=Optimizer,
        market_data_provider_factory=lambda _source: None,
    )
    service._prepare_market_data = lambda *a, **k: None
    with Session() as db:
        favorite = _favorite(db, old)
        favorite_id = favorite.id
        before = dict(favorite.metrics)
    assert before["total_return_pct"] == 4.0
    result = service.refresh_favorite(favorite_id)
    assert result["status"] == REFRESH_STATUS_SUCCESS
    with Session() as db:
        favorite = db.query(FavoriteStrategy).filter_by(id=favorite_id).one()
        run = db.query(AutoBacktestRun).filter_by(run_id=result["run_id"]).one()
        # número novo em /favorites; sem aviso novo: o anterior vive só no histórico de runs
        assert favorite.metrics["total_return_pct"] == 8.5
        assert favorite.metrics["analysis_execution"]["gap_stops"] == 1
        assert favorite.metrics["analysis_conventions"]["fee"] == 0.00075
        assert favorite.metrics["analysis_asset"]["currency"] == "USDT"
        stage = run.stage_3_result
        assert stage["previous_metrics"] == {"total_return_pct": 4.0}
        assert stage["gap_stops"] == 1
        assert stage["metrics"]["total_return_pct"] == 8.5
