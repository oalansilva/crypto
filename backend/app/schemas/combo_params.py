"""
Pydantic schemas for combo strategy API requests and responses.
"""

from pydantic import BaseModel, Field, model_validator
from typing import List, Dict, Any, Literal, Optional

from app.schemas.strategy_transparency import StrategyTransparency


class IndicatorConfig(BaseModel):
    """Configuration for a single indicator in a combo."""

    type: str = Field(..., description="Indicator type (ema, sma, rsi, etc.)")
    alias: Optional[str] = Field(None, description="Alias for the indicator")
    params: Dict[str, Any] = Field(default_factory=dict, description="Indicator parameters")
    optimization_range: Optional[Dict[str, Any]] = Field(
        None, description="Optimization range (min, max, step)"
    )


class ComboTemplateMetadata(BaseModel):
    """Metadata for a combo template."""

    id: Optional[int] = None
    name: str
    display_name: Optional[str] = None
    description: Optional[str] = None
    is_example: bool = False
    is_prebuilt: bool = False
    is_readonly: bool = False
    indicators: List[IndicatorConfig]
    entry_logic: str
    exit_logic: str
    stop_loss: Dict[str, Any] = Field(default_factory=lambda: {"default": 0.015})
    optimization_schema: Optional[Dict[str, Any]] = Field(
        None, description="Optimization ranges for parameters"
    )


class ComboBacktestRequest(BaseModel):
    """Request to run a combo strategy backtest."""

    template_name: str = Field(..., description="Name of the combo template")
    symbol: str = Field(..., description="Trading pair (e.g., BTC/USDT)")
    timeframe: str = Field(..., description="Timeframe (e.g., 1h, 4h)")
    data_source: Optional[str] = Field(
        None,
        description="Optional market data source ('ccxt' default, 'stooq' for US stocks EOD)",
    )
    start_date: Optional[str] = Field(None, description="Start date (YYYY-MM-DD)")
    end_date: Optional[str] = Field(None, description="End date (YYYY-MM-DD)")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Custom parameter values")
    stop_loss: Optional[float] = Field(None, description="Stop loss percentage")
    deep_backtest: bool = Field(
        True,
        description="Enable Deep Backtesting with 15m intraday precision (default: True for 1D strategies)",
    )
    initial_capital: float = Field(
        100,
        description="Initial capital in USD for metrics calculation (default: $100, TradingView-style)",
    )
    direction: str = Field("long", description="Backtest direction: 'long' (default) or 'short'")

    @model_validator(mode="after")
    def validate_data_source(self):
        source = str(self.data_source or "").strip().lower()
        if source in {"", "ccxt", "binance", "crypto", "default"}:
            return self
        if source in {"stooq", "stooq-eod", "stooq_eod"}:
            if str(self.timeframe or "").strip().lower() != "1d":
                raise ValueError("data_source=stooq supports only timeframe='1d' (EOD).")
            return self
        raise ValueError("Unsupported data_source. Supported values: 'ccxt' (default) or 'stooq'.")


class ComboBacktestResponse(BaseModel):
    """Response from combo strategy backtest."""

    template_name: str
    symbol: str
    timeframe: str
    parameters: Dict[str, Any]
    metrics: Dict[str, Any]
    trades: List[Dict[str, Any]]
    indicator_data: Dict[str, List[Optional[float]]]  # Allow None for NaN values
    candles: List[Dict[str, Any]] = Field(default_factory=list, description="OHLCV data for chart")
    execution_mode: str = Field(
        default="fast_1d", description="Execution mode: 'fast_1d' or 'deep_15m'"
    )
    direction: str = Field(default="long", description="Backtest direction: 'long' or 'short'")
    display_name: Optional[str] = Field(None, description="Resolved public strategy title")
    strategy_description: Optional[str] = Field(
        None, description="Resolved public strategy description"
    )
    strategy_transparency: Optional[StrategyTransparency] = None
    # Card #1119 (decisão 12): identidade, amostra, precisão efetiva e convenções da execução.
    asset: Optional[Dict[str, Any]] = Field(
        None, description="{symbol, asset_id, asset_class, name, currency}"
    )
    data_provenance: Optional[Dict[str, Any]] = Field(
        None, description="Fonte, sessão, ajuste, janelas e versão da amostra usada"
    )
    snapshot_id: Optional[str] = None
    execution: Optional[Dict[str, Any]] = Field(
        None,
        description="Precisão pedida/efetiva, trecho sem intradiário, janela coberta e stops com gap",
    )
    conventions: Optional[Dict[str, Any]] = Field(
        None, description="Custos, anualização, calendário, fração e short"
    )


class ComboOptimizationRequest(BaseModel):
    """Request to run combo strategy optimization."""

    template_name: str
    symbol: str
    timeframe: str = Field(default="1h")
    data_source: Optional[str] = Field(
        None,
        description="Optional market data source ('ccxt' default, 'stooq' for US stocks EOD)",
    )
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    period_type: Optional[str] = Field(None, description="'6m' | '2y' | 'all'")
    deep_backtest: bool = Field(
        default=True,
        description="Use Deep Backtesting (15m precision) for realistic stop-loss simulation",
    )
    custom_ranges: Optional[Dict[str, Dict[str, Any]]] = Field(
        None, description="Custom optimization ranges for parameters"
    )
    initial_capital: float = Field(
        100,
        description="Initial capital in USD for metrics calculation (default: $100, TradingView-style)",
    )
    direction: str = Field("long", description="Backtest direction: 'long' (default) or 'short'")
    run_scope: Optional[Literal["single"]] = Field(
        None,
        description=(
            "'single' = backtest de exatamente 1 ativo (Combo ou Otimização com 1 ativo); só com "
            "ele o servidor aceita ação e ETF (card #1119, decisão 2)."
        ),
    )
    split_train_ratio: Optional[float] = Field(
        None,
        ge=0.01,
        le=0.99,
        description="Walk-forward split: train fraction for optimization (ex.: 0.7). When set, holdout metrics and GO/NO-GO verdict are produced (card #470).",
    )

    @model_validator(mode="after")
    def validate_data_source(self):
        source = str(self.data_source or "").strip().lower()
        if source in {"", "ccxt", "binance", "crypto", "default"}:
            return self
        if source in {"stooq", "stooq-eod", "stooq_eod"}:
            if str(self.timeframe or "").strip().lower() != "1d":
                raise ValueError("data_source=stooq supports only timeframe='1d' (EOD).")
            return self
        raise ValueError("Unsupported data_source. Supported values: 'ccxt' (default) or 'stooq'.")


class ComboOptimizationResponse(BaseModel):
    """Response from combo strategy optimization."""

    job_id: str
    template_name: str
    symbol: str
    timeframe: str
    stages: List[Dict[str, Any]]
    best_parameters: Dict[str, Any]
    best_metrics: Dict[str, Any]
    # Walk-forward (card #470): holdout metrics and GO/NO-GO verdict (null when split not used)
    oos_metrics: Optional[Dict[str, Any]] = None
    oos_verdict: Optional[Dict[str, Any]] = None
    oos_proof: Optional[str] = None
    promotion_metrics: Optional[Dict[str, Any]] = None
    # Complete backtest data for visualization
    trades: List[Dict[str, Any]] = Field(default_factory=list)
    candles: List[Dict[str, Any]] = Field(default_factory=list)
    indicator_data: Dict[str, List[Optional[float]]] = Field(default_factory=dict)
    parameters: Dict[str, Any] = Field(default_factory=dict)  # Alias for best_parameters
    direction: str = Field(default="long", description="Backtest direction: 'long' or 'short'")
    execution_mode: str = Field(
        default="fast_1d",
        description="Execution mode used by final trades: 'fast_1d' or 'deep_15m'",
    )
    display_name: Optional[str] = Field(None, description="Resolved public strategy title")
    strategy_description: Optional[str] = Field(
        None, description="Resolved public strategy description"
    )
    strategy_transparency: Optional[StrategyTransparency] = None
    # Card #1119 (decisão 12): identidade, amostra, precisão efetiva e convenções da execução.
    asset: Optional[Dict[str, Any]] = Field(
        None, description="{symbol, asset_id, asset_class, name, currency}"
    )
    data_provenance: Optional[Dict[str, Any]] = Field(
        None, description="Fonte, sessão, ajuste, janelas e versão da amostra usada"
    )
    snapshot_id: Optional[str] = None
    execution: Optional[Dict[str, Any]] = Field(
        None,
        description="Precisão pedida/efetiva, trecho sem intradiário, janela coberta e stops com gap",
    )
    conventions: Optional[Dict[str, Any]] = Field(
        None, description="Custos, anualização, calendário, fração e short"
    )
    combination_errors: Optional[Dict[str, Any]] = Field(
        None,
        description="Combinações descartadas por erro: {failed, executed, reasons[{reason, count}], message}; "
        "ausente quando todas funcionaram",
    )


class UpdateTemplateRequest(BaseModel):
    """Request to update a combo template."""

    description: Optional[str] = Field(None, description="Template description")
    optimization_schema: Optional[Dict[str, Any]] = Field(
        None, description="Optimization ranges for parameters"
    )
    template_data: Optional[Dict[str, Any]] = Field(
        None, description="Full template data (for advanced editing)"
    )


class UpdateTemplateIdentityRequest(BaseModel):
    """Request to update public catalog identity (title + description)."""

    display_name: str = Field(..., min_length=1, max_length=120)
    description: str = Field(..., min_length=1, max_length=500)


class CloneTemplateRequest(BaseModel):
    """Request to clone a combo template."""

    new_name: str = Field(
        ..., description="Name for the cloned template", min_length=3, max_length=100
    )


class ComboBatchBacktestRequest(BaseModel):
    """Request to run batch backtests for multiple symbols."""

    template_name: str = Field(..., description="Name of the combo template")
    symbols: List[str] = Field(
        ..., min_length=1, description="List of symbols to run (e.g. ['BTC/USDT', 'ETH/USDT'])"
    )
    timeframe: str = Field(default="1d")
    data_source: Optional[str] = Field(
        None,
        description="Optional market data source ('ccxt' default, 'stooq' for US stocks EOD)",
    )
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    period_type: Optional[str] = Field(None, description="'6m' | '2y' | 'all'; used for skip logic")
    deep_backtest: bool = Field(
        default=True,
        description="Use Deep Backtesting (15m precision) for realistic stop-loss simulation",
    )
    custom_ranges: Optional[Dict[str, Dict[str, Any]]] = Field(None)
    initial_capital: float = Field(100)
    direction: str = Field("long", description="Backtest direction: 'long' (default) or 'short'")
    split_train_ratio: Optional[float] = Field(
        None,
        ge=0.01,
        le=0.99,
        description="Walk-forward split: train fraction (ex.: 0.7). When set, holdout gate GO/NO-GO applies and NO-GO candidates are not saved (card #470).",
    )

    page: Optional[Literal["combo", "optimize"]] = Field(
        None,
        description="Tela que pede o lote (card #1120): 'optimize' usa a janela fixa e as regras de cobertura do 5m.",
    )

    @model_validator(mode="after")
    def validate_data_source(self):
        source = str(self.data_source or "").strip().lower()
        if source in {"", "ccxt", "binance", "crypto", "default"}:
            return self
        if source in {"stooq", "stooq-eod", "stooq_eod"}:
            if str(self.timeframe or "").strip().lower() != "1d":
                raise ValueError("data_source=stooq supports only timeframe='1d' (EOD).")
            return self
        raise ValueError("Unsupported data_source. Supported values: 'ccxt' (default) or 'stooq'.")


class ComboBatchBacktestResponse(BaseModel):
    """Response from starting a batch backtest job."""

    job_id: str = Field(..., description="Job ID to poll for progress")


class ComboBatchItemResponse(BaseModel):
    """Estado de um ativo no lote (card #1120, decisão 8)."""

    position: int = 0
    symbol: str
    asset_class: Optional[str] = None
    currency: Optional[str] = None
    state: str = Field(
        "queued",
        description="queued | collecting | optimizing | success | success_daily | insufficient | rejected | failed | skipped | out | not_run",
    )
    reason: Optional[str] = None
    progress: Optional[str] = None
    favorite_id: Optional[int] = None
    execution: Optional[Dict[str, Any]] = None
    snapshot_id: Optional[str] = None
    started_at: Optional[str] = None
    finished_at: Optional[str] = None
    collect_kind: Optional[str] = Field(None, description="none | missing | tail (plano)")
    needs_collection: List[Dict[str, str]] = Field(default_factory=list)


class ComboBatchProgressResponse(BaseModel):
    """Progress and result of a batch backtest job."""

    job_id: str
    task_id: Optional[str] = Field(None, description="Celery task id handling this batch job")
    status: str = Field(
        ...,
        description="queued | running | retrying | paused | cancelled | completed | failed",
    )
    processed: int = 0
    total: int = 0
    succeeded: int = 0
    failed: int = 0
    skipped: int = Field(0, description="Skipped (already in favorites)")
    errors: List[Dict[str, Any]] = Field(default_factory=list, description="Per-symbol errors")
    started_at: Optional[str] = None
    elapsed_sec: float = 0.0
    estimated_remaining_sec: Optional[float] = None
    current_symbol: Optional[str] = Field(None, description="Symbol currently being optimized")
    current_stage: Optional[str] = Field(None, description="Etapa em curso do ativo atual")
    retry_count: int = 0
    last_error: Optional[str] = None
    dead_lettered: bool = False
    # Card #1120: pedidos de pausa/encerramento, ativos e totais. Lote antigo: sem ``items``.
    pause_requested: bool = False
    cancel_requested: bool = False
    created_at: Optional[str] = None
    finished_at: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    items: Optional[List[ComboBatchItemResponse]] = None
    totals: Optional[Dict[str, int]] = None


class ComboBatchPreviewItem(BaseModel):
    symbol: str
    asset_id: Optional[str] = None
    asset_class: Optional[str] = None
    currency: Optional[str] = None
    plan: str = Field(..., description="run | out")
    reason: Optional[str] = None
    out_kind: Optional[str] = None
    needs_collection: List[Dict[str, str]] = Field(default_factory=list)
    collect_kind: str = Field("none", description="none | missing | tail")
    covered_until: Optional[str] = None
    data_source: Optional[str] = None
    collect_note: Optional[str] = None


class ComboBatchPreviewResponse(BaseModel):
    """Plano do lote antes de começar (card #1120, decisão 4): nada é coletado."""

    items: List[ComboBatchPreviewItem]
    totals: Dict[str, Any]
    config: Dict[str, Any] = Field(default_factory=dict)


class TemplateListResponse(BaseModel):
    """Response listing available combo templates."""

    prebuilt: List[Dict[str, Any]]
    examples: List[Dict[str, Any]]
    custom: List[Dict[str, Any]]
