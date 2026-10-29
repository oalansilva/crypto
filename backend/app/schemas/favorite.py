from pydantic import BaseModel
from typing import Dict, Any, Optional
from datetime import datetime

from app.schemas.strategy_transparency import StrategyTransparency


class FavoriteStrategyBase(BaseModel):
    name: str
    symbol: str
    timeframe: str
    strategy_name: str
    parameters: Dict[str, Any]
    metrics: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None
    tier: Optional[int] = None  # 1=Core obrigatório, 2=Bons complementares, 3=Outros
    # Card #1122 (d2, decisão 3): todo favorito novo nasce com o alerta ligado (vale com estrela).
    notify_telegram: bool = True
    # Card #1122 (decisão 11): configuração de dados (fonte, sessão, ajuste).
    data_source: Optional[str] = None
    session: Optional[str] = None
    adjustment: Optional[str] = None
    start_date: Optional[str] = None  # Período do backtest (6m/2y/todo)
    end_date: Optional[str] = None
    period_type: Optional[str] = None  # '6m' | '2y' | 'all'; chave para skip
    auto_refresh_status: Optional[str] = None
    auto_refresh_error: Optional[str] = None
    auto_refresh_started_at: Optional[datetime] = None
    auto_refresh_completed_at: Optional[datetime] = None
    auto_refresh_run_id: Optional[str] = None
    # Card #1123 (decisão 5): comparação com referência gravada (herdada do resultado ao salvar).
    benchmark_comparison_id: Optional[str] = None


class FavoriteStrategyCreate(FavoriteStrategyBase):
    # Walk-forward gate (card #470): veredito GO/NO-GO do holdout exigido para
    # candidatos vindos do otimizador com split; override admin explícito libera NO-GO.
    oos_metrics: Optional[Dict[str, Any]] = None
    oos_verdict: Optional[Dict[str, Any]] = None
    oos_proof: Optional[str] = None
    override_oos: bool = False


class FavoriteStrategyResponse(FavoriteStrategyBase):
    id: int
    created_at: datetime
    is_strategy_protected: bool = False
    strategy_display_name: Optional[str] = None
    strategy_description: Optional[str] = None
    strategy_transparency: Optional[StrategyTransparency] = None
    # Card #1120: identidade do ativo (símbolo, classe, moeda); ação e ETF entram na lista única.
    asset: Optional[Dict[str, Any]] = None
    # Card #1122: fonte, sessão, ajuste e rótulos curto/compacto/longo.
    configuration: Optional[Dict[str, Any]] = None
    # Card #1122: linha do catálogo do Cripto Farol (vitrine), sem controle "Alertar".
    is_curated_fallback: bool = False
    # Card #1123: comparação gravada resumida ("Ref.: SPY · comparação gravada 27/10").
    benchmark_comparison: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


class FavoriteStrategyUpdate(BaseModel):
    tier: Optional[int] = None  # 1, 2, 3 ou None
    notify_telegram: Optional[bool] = None
    name: Optional[str] = None
    notes: Optional[str] = None
