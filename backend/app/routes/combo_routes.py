"""
Combo Strategy Routes

Endpoints for combo strategy templates, backtesting, and optimization.
"""

import logging
from fastapi import APIRouter, HTTPException
from typing import Optional
import pandas as pd
import numpy as np
from datetime import datetime

from app.schemas.combo_params import (
    ComboBacktestRequest,
    ComboBacktestResponse,
    ComboOptimizationRequest,
    ComboOptimizationResponse,
    TemplateListResponse,
    ComboTemplateMetadata,
    UpdateTemplateRequest,
    CloneTemplateRequest
)
from app.services.combo_service import ComboService
from src.data.incremental_loader import IncrementalLoader
from app.services.combo_optimizer import ComboOptimizer

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/combos", tags=["combos"])


@router.get("/templates", response_model=TemplateListResponse)
async def list_combo_templates():
    """List all available combo templates."""
    try:
        service = ComboService()
        templates = service.list_templates()
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


@router.put("/meta/{template_name}", response_model=ComboTemplateMetadata)
async def update_template(template_name: str, request: UpdateTemplateRequest):
    """
    Update a combo template's metadata and optimization schema.
    
    Args:
        template_name: Name of the template to update
        request: Update request with optional description, optimization_schema, template_data
    
    Returns:
        Updated template metadata
    
    Raises:
        403: If template is read-only
        404: If template not found
        400: If validation fails
    """
    try:
        service = ComboService()
        
        # Update template
        success = service.update_template(
            template_name=template_name,
            description=request.description,
            optimization_schema=request.optimization_schema,
            template_data=request.template_data
        )
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update template")
        
        # Return updated metadata
        updated_metadata = service.get_template_metadata(template_name)
        if not updated_metadata:
            raise HTTPException(status_code=404, detail=f"Template '{template_name}' not found after update")
        
        logger.info(f"Template '{template_name}' updated successfully")
        return updated_metadata
        
    except ValueError as e:
        error_msg = str(e)
        if "read-only" in error_msg.lower():
            raise HTTPException(status_code=403, detail=error_msg)
        elif "not found" in error_msg.lower():
            raise HTTPException(status_code=404, detail=error_msg)
        else:
            raise HTTPException(status_code=400, detail=error_msg)
    except Exception as e:
        logger.error(f"Error updating template '{template_name}': {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/meta/{template_name}/clone", response_model=ComboTemplateMetadata)
async def clone_template(template_name: str, request: CloneTemplateRequest):
    """
    Clone an existing template with a new name.
    
    Args:
        template_name: Name of the template to clone
        request: Clone request with new_name
    
    Returns:
        Metadata of the cloned template
    
    Raises:
        404: If source template not found
        409: If new name already exists
    """
    try:
        service = ComboService()
        
        # Clone template
        cloned_metadata = service.clone_template(
            template_name=template_name,
            new_name=request.new_name
        )
        
        if not cloned_metadata:
            raise HTTPException(status_code=500, detail="Failed to clone template")
        
        logger.info(f"Template '{template_name}' cloned as '{request.new_name}'")
        return cloned_metadata
        
    except ValueError as e:
        error_msg = str(e)
        if "not found" in error_msg.lower():
            raise HTTPException(status_code=404, detail=error_msg)
        elif "already exists" in error_msg.lower():
            raise HTTPException(status_code=409, detail=error_msg)
        else:
            raise HTTPException(status_code=400, detail=error_msg)
    except Exception as e:
        logger.error(f"Error cloning template '{template_name}': {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/meta/{template_name}")
async def delete_template(template_name: str):
    """
    Delete a custom combo template.
    
    Args:
        template_name: Name of the template to delete
    
    Returns:
        Success message
    
    Raises:
        404: If template not found or not deletable
    """
    try:
        service = ComboService()
        success = service.delete_template_by_name(template_name)
        
        if not success:
            raise HTTPException(status_code=404, detail=f"Template '{template_name}' not found or cannot be deleted")
            
        return {"message": f"Template '{template_name}' deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting template '{template_name}': {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


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
        
        # Load market data
        loader = IncrementalLoader()
        df = loader.fetch_data(
            symbol=request.symbol,
            timeframe=request.timeframe,
            since_str=request.start_date,
            until_str=request.end_date
        )
        logger.info(f"Loaded {len(df)} candles for {request.symbol} {request.timeframe}")
        
        if df.empty:
            raise HTTPException(status_code=400, detail="No data available for the specified period")
        
        # Generate signals
        df_with_signals = strategy.generate_signals(df)
        logger.info(f"Generated signals for {len(df_with_signals)} candles")
        
        # Execute backtest
        from src.engine.backtester import Backtester
        
        # Override stop_loss if provided in request, otherwise use strategy's default
        stop_loss_pct = request.stop_loss if request.stop_loss is not None else strategy.stop_loss
        
        backtester = Backtester(
            initial_capital=10000,
            stop_loss_pct=stop_loss_pct
        )
        
        # Backtester run expects df and strategy
        # It handles signal generation internally, so we can pass raw df or df_with_signals
        df_results = backtester.run(
            df,
            strategy=strategy
        )
        
        trades = backtester.trades
        logger.info(f"Backtest complete: {len(trades)} trades executed")
        
        # Calculate metrics
        total_trades = len(trades)
        winning_trades = sum(1 for t in trades if t.get('profit', 0) > 0)
        
        # Convert timestamps and numpy types in trades to string/native (JSON serialization)
        for t in trades:
            if 'entry_time' in t and hasattr(t['entry_time'], 'isoformat'):
                t['entry_time'] = t['entry_time'].isoformat()
            if 'exit_time' in t and hasattr(t['exit_time'], 'isoformat'):
                t['exit_time'] = t['exit_time'].isoformat()
            
            # Convert numpy types
            for k, v in t.items():
                if isinstance(v, (np.integer, np.int64)):
                    t[k] = int(v)
                elif isinstance(v, (np.floating, np.float64)):
                    t[k] = float(v)
        
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
        
        response = ComboBacktestResponse(
            template_name=request.template_name,
            symbol=request.symbol,
            timeframe=request.timeframe,
            metrics=metrics,
            trades=trades,
            candles=candles,
            indicator_data=indicator_data,
            parameters=request.parameters,
            execution_mode="fast_1d"
        )
        logger.info("Response object created successfully")
        from fastapi.encoders import jsonable_encoder
        return jsonable_encoder(response)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Backtest error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/optimize", response_model=ComboOptimizationResponse)
async def optimize_combo_strategy(request: ComboOptimizationRequest):
    """
    Run parameter optimization for a combo strategy.
    
    Args:
        request: Optimization configuration
    
    Returns:
        Optimization results with best parameters and metrics
    """
    try:
        logger.info(f"Starting optimization for template: {request.template_name} on {request.symbol} {request.timeframe}")
        
        # Create optimizer
        optimizer = ComboOptimizer()
        
        # Run optimization
        result = optimizer.optimize(
            template_name=request.template_name,
            symbol=request.symbol,
            timeframe=request.timeframe,
            start_date=request.start_date,
            end_date=request.end_date,
            custom_ranges=request.custom_ranges
        )
        
        logger.info(f"Optimization complete. Best score: {result.get('best_score', 'N/A')}")
        
        return ComboOptimizationResponse(**result)
        
    except Exception as e:
        logger.error(f"Optimization error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
