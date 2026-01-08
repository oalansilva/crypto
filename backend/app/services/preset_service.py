# file: backend/app/services/preset_service.py
from app.schemas.backtest import PresetResponse, BacktestRunCreate
from datetime import datetime, timedelta

def get_presets() -> list[PresetResponse]:
    """Return predefined backtest presets for Playground"""
    
    # Calculate date ranges
    now = datetime.now()
    two_years_ago = (now - timedelta(days=730)).strftime("%Y-%m-%d %H:%M:%S")
    one_year_ago = (now - timedelta(days=365)).strftime("%Y-%m-%d %H:%M:%S")
    
    presets = [
        PresetResponse(
            id="btc-swing-2y",
            name="BTC Swing (2 anos, 4h)",
            description="Compare 3 estratégias em BTC/USDT 4h com stop/take ativado",
            config=BacktestRunCreate(
                mode="compare",
                exchange="binance",
                symbol="BTC/USDT",
                timeframe="4h",
                since=two_years_ago,
                strategies=["sma_cross", "rsi_reversal", "bb_meanrev"],
                params={
                    "sma_cross": {"fast": 20, "slow": 50},
                    "rsi_reversal": {"rsi_period": 14, "oversold": 30, "overbought": 70},
                    "bb_meanrev": {"bb_period": 20, "bb_std": 2.0, "exit_mode": "mid"}
                },
                fee=0.001,
                slippage=0.0005,
                cash=10000,
                stop_pct=0.03,
                take_pct=0.06,
                fill_mode="close"
            )
        ),
        PresetResponse(
            id="eth-swing-2y",
            name="ETH Swing (2 anos, 1d)",
            description="Compare 3 estratégias em ETH/USDT diário",
            config=BacktestRunCreate(
                mode="compare",
                exchange="binance",
                symbol="ETH/USDT",
                timeframe="1d",
                since=two_years_ago,
                strategies=["sma_cross", "rsi_reversal", "bb_meanrev"],
                fee=0.001,
                slippage=0.0005,
                cash=10000,
                fill_mode="close"
            )
        ),
        PresetResponse(
            id="btc-trend-1y",
            name="BTC Trend (1 ano, 1d)",
            description="Estratégia SMA Cross em BTC/USDT diário sem stop/take",
            config=BacktestRunCreate(
                mode="run",
                exchange="binance",
                symbol="BTC/USDT",
                timeframe="1d",
                since=one_year_ago,
                strategies=["sma_cross"],
                params={"sma_cross": {"fast": 20, "slow": 50}},
                fee=0.001,
                slippage=0.0005,
                cash=10000,
                fill_mode="close"
            )
        ),
        PresetResponse(
            id="link-trend-4h",
            name="LINK Trend (6 meses, 4h)",
            description="Estratégia SMA Cross para LINK/USDT no gráfico de 4h",
            config=BacktestRunCreate(
                mode="run",
                exchange="binance",
                symbol="LINK/USDT",
                timeframe="4h",
                since=(now - timedelta(days=180)).strftime("%Y-%m-%d %H:%M:%S"),
                strategies=["sma_cross"],
                params={"sma_cross": {"fast": 20, "slow": 50}},
                fee=0.001,
                slippage=0.0005,
                cash=10000,
                fill_mode="close"
            )
        )
    ]
    
    return presets
