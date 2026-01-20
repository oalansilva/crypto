"""
Combo Strategy API Routes

Isolated endpoints for combo strategies.
Does not modify existing routes.
"""

import logging
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List
import pandas as pd
import numpy as np

from app.schemas.combo_params import (
    ComboBacktestRequest,
    ComboBacktestResponse,
    ComboOptimizationRequest,
    ComboOptimizationResponse,
    TemplateListResponse,
    ComboTemplateMetadata
)
from app.services.combo_service import ComboService
from src.data.incremental_loader import IncrementalLoader
from app.services.combo_optimizer import ComboOptimizer

# Setup Logger
logger = logging.getLogger(__name__)


router = APIRouter(prefix="/api/combos", tags=["combos"])


@router.get("/templates", response_model=TemplateListResponse)
async def list_combo_templates():
    """List all available combo strategy templates."""
    try:
        service = ComboService()
        templates = service.list_templates()
        logger.info(f"Listed templates: {len(templates.get('prebuilt', [])) + len(templates.get('examples', [])) + len(templates.get('custom', []))} total")
        return TemplateListResponse(**templates)
    except Exception as e:
        logger.error(f"Error listing templates: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/meta/{template_name}", response_model=ComboTemplateMetadata)
async def get_template_metadata(template_name: str):
    """Get metadata for a specific template."""
    service = ComboService()
    metadata = service.get_template_metadata(template_name)
    
    if not metadata:
        logger.warning(f"Template not found: {template_name}")
        raise HTTPException(status_code=404, detail=f"Template '{template_name}' not found")
    
    return metadata


@router.post("/backtest", response_model=ComboBacktestResponse)
async def run_combo_backtest(request: ComboBacktestRequest):
    """
    Execute a combo strategy backtest.
    
    Args:
        request: Backtest configuration
    
    Returns:
        Backtest results with metrics, trades, and indicator data
    """
    try:
        logger.info(f"Starting combo backtest for template: {request.template_name} on {request.symbol} {request.timeframe}")
        
        # Create strategy instance
        service = ComboService()
        strategy = service.create_strategy(
            template_name=request.template_name,
            parameters=request.parameters
        )
        logger.info(f"Strategy instance created for {request.template_name}")
        
        # Load data
        loader = IncrementalLoader()
        df = loader.fetch_data(
            symbol=request.symbol,
            timeframe=request.timeframe,
            since_str=request.start_date or "2017-01-01",
            until_str=request.end_date
        )
        logger.info(f"Data loaded: {len(df)} candles from {df.index[0]} to {df.index[-1]}")
        
        # Generate signals
        df_with_signals = strategy.generate_signals(df)
        signals_count = len(df_with_signals[df_with_signals['signal'] != 0])
        logger.info(f"Signals generated: {signals_count} signals found")
        
        # Extract trades using proper logic (with stop loss and deep backtest support)
        from app.services.combo_optimizer import extract_trades_with_mode
        
        stop_loss = request.stop_loss or request.parameters.get('stop_loss', 0.015)
        
        trades = extract_trades_with_mode(
            df_with_signals=df_with_signals,
            stop_loss=stop_loss,
            deep_backtest=request.deep_backtest,
            symbol=request.symbol,
            since_str=request.start_date or "2017-01-01",
            until_str=request.end_date
        )
        
        logger.info(f"Extracted {len(trades)} trades (Deep Backtest: {request.deep_backtest})")
        
        # Calculate basic metrics
        total_trades = len(trades)
        winning_trades = len([t for t in trades if t.get('profit', 0) > 0])
        logger.info(f"Backtest execution complete: {total_trades} trades, {winning_trades} wins")
        
        metrics = {
            "total_trades": total_trades,
            "win_rate": winning_trades / total_trades if total_trades > 0 else 0,
            "total_return": sum([t.get('profit', 0) for t in trades]),
            "avg_profit": sum([t.get('profit', 0) for t in trades]) / total_trades if total_trades > 0 else 0
        }
        
        # Get indicator data for chart
        indicator_columns = strategy.get_indicator_columns()
        indicator_data = {}
        for col in indicator_columns:
            if col in df_with_signals.columns:
                # Replace NaN with None for JSON compatibility
                values = df_with_signals[col].tolist()
                indicator_data[col] = [None if pd.isna(v) else float(v) for v in values]
        
        # Extract Candle Data
        candles = []
        if not df_with_signals.empty:
            # Ensure index is datetime if it's not already
            if not isinstance(df_with_signals.index, pd.DatetimeIndex):
                # Try to convert index to datetime if it's string
                try:
                    df_with_signals.index = pd.to_datetime(df_with_signals.index)
                except:
                    pass
            
            # Remove duplicate timestamps and sort by time
            df_clean = df_with_signals[~df_with_signals.index.duplicated(keep='first')]
            df_clean = df_clean.sort_index()

            for idx, row in df_clean.iterrows():
                candles.append({
                    "timestamp_utc": idx.isoformat() if hasattr(idx, 'isoformat') else str(idx),
                    "open": float(row['open']),
                    "high": float(row['high']),
                    "low": float(row['low']),
                    "close": float(row['close']),
                    "volume": float(row['volume'])
                })

        return ComboBacktestResponse(
            template_name=request.template_name,
            symbol=request.symbol,
            timeframe=request.timeframe,
            parameters=request.parameters,
            metrics=metrics,
            trades=trades,
            indicator_data=indicator_data,
            candles=candles,
            execution_mode="deep_15m" if request.deep_backtest else "fast_1d"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/optimize", response_model=ComboOptimizationResponse)
async def run_combo_optimization(request: ComboOptimizationRequest):
    """
    Run sequential optimization for a combo strategy.
    
    Args:
        request: Optimization configuration
    
    Returns:
        Optimization results with best parameters
    """
    try:
        from app.services.combo_optimizer import ComboOptimizer
        
        logger.info(f"Starting combo optimization for {request.template_name} on {request.symbol} {request.timeframe}")
        logger.info(f"Custom ranges: {request.custom_ranges}")
        
        optimizer = ComboOptimizer()
        
        # Run optimization
        result = optimizer.run_optimization(
            template_name=request.template_name,
            symbol=request.symbol,
            timeframe=request.timeframe,
            start_date=request.start_date,
            end_date=request.end_date,
            custom_ranges=request.custom_ranges,
            deep_backtest=request.deep_backtest
        )
        
        # Return complete result with all fields
        return ComboOptimizationResponse(**result)
    
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        logger.error(f"Combo optimization failed: {str(e)}")
        logger.error(f"Traceback: {error_details}")
        raise HTTPException(status_code=500, detail=f"{str(e)}\n\n{error_details}")


@router.post("/templates")
async def create_custom_template(template: ComboTemplateMetadata):
    """
    Create a new custom combo template.
    
    Args:
        template: Template configuration
    
    Returns:
        Created template ID
    """
    try:
        service = ComboService()
        template_id = service.save_custom_template(
            name=template.name,
            description=template.description or "",
            indicators=[ind.dict() for ind in template.indicators],
            entry_logic=template.entry_logic,
            exit_logic=template.exit_logic,
            stop_loss=template.stop_loss
        )
        
        return {"id": template_id, "name": template.name}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/templates/{template_id}")
async def delete_custom_template(template_id: int):
    """
    Delete a custom combo template.
    
    Args:
        template_id: ID of the template to delete
    
    Returns:
        Success message
    """
    service = ComboService()
    deleted = service.delete_custom_template(template_id)
    
    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Template not found or cannot be deleted (prebuilt/example templates cannot be deleted)"
        )
    
    return {"message": "Template deleted successfully"}


@router.get("/data/15m-availability")
async def check_15m_availability(symbol: str = "BTC/USDT", since: str = None):
    loader = IncrementalLoader()
    availability = loader.check_intraday_availability(symbol=symbol, timeframe='15m', since_str=since)
    return {"symbol": symbol, "timeframe": "15m", **availability}

