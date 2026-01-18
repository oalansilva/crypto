"""
Combo Strategy API Routes

Isolated endpoints for combo strategies.
Does not modify existing routes.
"""

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
from app.services.sequential_optimizer import SequentialOptimizer
from src.data.incremental_loader import IncrementalLoader


router = APIRouter(prefix="/api/combos", tags=["combos"])


@router.get("/templates", response_model=TemplateListResponse)
async def list_templates():
    """
    List all available combo templates.
    
    Returns:
        - prebuilt: Pre-configured templates
        - examples: Example templates
        - custom: User-created templates
    """
    service = ComboService()
    templates = service.list_templates()
    
    return TemplateListResponse(**templates)


@router.get("/meta/{template_name}")
async def get_template_metadata(template_name: str):
    """
    Get metadata for a specific combo template.
    
    Args:
        template_name: Name of the template
    
    Returns:
        Template metadata including indicators, logic, and parameters
    """
    service = ComboService()
    metadata = service.get_template_metadata(template_name)
    
    if not metadata:
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
        # Create strategy instance
        service = ComboService()
        strategy = service.create_strategy(
            template_name=request.template_name,
            parameters=request.parameters
        )
        
        # Load data
        loader = IncrementalLoader()
        df = loader.fetch_data(
            symbol=request.symbol,
            timeframe=request.timeframe,
            since_str=request.start_date or "2017-01-01",
            until_str=request.end_date
        )
        
        # Generate signals
        df_with_signals = strategy.generate_signals(df)
        
        # Calculate metrics (simplified - reuse existing backtest logic)
        trades = []
        in_position = False
        entry_price = 0
        
        for i in range(len(df_with_signals)):
            signal = df_with_signals['signal'].iloc[i]
            
            if signal == 1 and not in_position:
                # Buy signal
                entry_price = df_with_signals['close'].iloc[i]
                in_position = True
                trades.append({
                    "entry_time": str(df_with_signals.index[i]),
                    "entry_price": float(entry_price),
                    "type": "buy"
                })
            
            elif signal == -1 and in_position:
                # Sell signal
                exit_price = df_with_signals['close'].iloc[i]
                profit = (exit_price - entry_price) / entry_price
                
                trades[-1].update({
                    "exit_time": str(df_with_signals.index[i]),
                    "exit_price": float(exit_price),
                    "profit": float(profit)
                })
                
                in_position = False
        
        # Calculate basic metrics
        total_trades = len([t for t in trades if 'exit_price' in t])
        winning_trades = len([t for t in trades if t.get('profit', 0) > 0])
        
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

            for idx, row in df_with_signals.iterrows():
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
            candles=candles
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
        
        optimizer = ComboOptimizer()
        
        # Run optimization
        result = optimizer.run_optimization(
            template_name=request.template_name,
            symbol=request.symbol,
            timeframe=request.timeframe,
            start_date=request.start_date,
            end_date=request.end_date,
            custom_ranges=request.custom_ranges
        )
        
        return ComboOptimizationResponse(
            job_id=result['job_id'],
            template_name=result['template_name'],
            symbol=result['symbol'],
            stages=result['stages'],
            best_parameters=result['best_parameters'],
            best_metrics=result['best_metrics']
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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
