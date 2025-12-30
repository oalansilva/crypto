# file: backend/app/schemas/backtest.py
from pydantic import BaseModel, Field
from typing import Optional, Literal, Union, List
from datetime import datetime
from uuid import UUID

class RangeParam(BaseModel):
    min: float
    max: float
    step: float

class BacktestRunCreate(BaseModel):
    mode: Literal["run", "compare", "optimize"]
    exchange: str = "binance"
    symbol: str
    timeframe: Union[str, List[str]]  # Can be single or multiple for optimization
    timeframes: Optional[list[str]] = None  # Deprecated, kept for backward compatibility
    full_period: bool = False  # NEW: Fetch all data from inception
    since: Optional[str] = None  # ISO format (Optional if full_period=True)
    until: Optional[str] = None
    strategies: list[Union[str, dict]]
    params: Optional[dict] = None
    fee: float = 0.001
    slippage: float = 0.0005
    cash: float = 10000
    stop_pct: Optional[Union[float, RangeParam, dict]] = None
    take_pct: Optional[Union[float, RangeParam, dict]] = None
    fill_mode: Literal["close", "next_open"] = "close"

class BacktestRunResponse(BaseModel):
    run_id: UUID
    status: Literal["PENDING", "RUNNING", "DONE", "FAILED"]
    message: str

class BacktestStatusResponse(BaseModel):
    run_id: UUID
    status: Literal["PENDING", "RUNNING", "DONE", "FAILED"]
    created_at: datetime
    progress: float = 0.0  # NEW: Progress percentage (0-100)
    current_step: Optional[str] = None  # NEW: Description of current activity
    error_message: Optional[str] = None

class BacktestRunListItem(BaseModel):
    id: UUID
    created_at: datetime
    status: str
    mode: str
    symbol: str
    timeframe: Union[str, List[str]]
    strategies: list[Union[str, dict]]
    message: Optional[str] = None
    progress: float = 0.0

class PresetResponse(BaseModel):
    id: str
    name: str
    description: str
    config: BacktestRunCreate


# ===== NEW: Enhanced Metrics Schemas =====

class BenchmarkMetrics(BaseModel):
    """Métricas do benchmark (Buy & Hold)."""
    return_pct: float
    cagr: float
    final_value: float


class CriteriaResult(BaseModel):
    """Resultado da avaliação GO/NO-GO."""
    status: Literal["GO", "NO-GO"]
    reasons: List[str]
    warnings: List[str]


class EnhancedMetrics(BaseModel):
    """
    Métricas avançadas de backtesting.
    Inclui métricas existentes + novas métricas calculadas.
    """
    # Existentes (mantidas para compatibilidade)
    total_return_pct: Optional[float] = None
    max_drawdown: Optional[float] = None
    sharpe_ratio: Optional[float] = None
    profit_factor: Optional[float] = None
    win_rate: Optional[float] = None
    total_trades: Optional[int] = None
    
    # Novos - Performance
    cagr: Optional[float] = None
    monthly_return_avg: Optional[float] = None
    
    # Novos - Risco
    avg_drawdown: Optional[float] = None
    max_dd_duration_days: Optional[int] = None
    recovery_factor: Optional[float] = None
    
    # Novos - Risk-Adjusted
    sortino_ratio: Optional[float] = None
    calmar_ratio: Optional[float] = None
    
    # Novos - Trade Stats
    expectancy: Optional[float] = None
    max_consecutive_wins: Optional[int] = None
    max_consecutive_losses: Optional[int] = None
    trade_concentration_top_10_pct: Optional[float] = None
    
    # Benchmark
    benchmark: Optional[BenchmarkMetrics] = None
    
    # Critérios GO/NO-GO
    criteria_result: Optional[CriteriaResult] = None
