"""
Combo Strategy Routes

Endpoints for combo strategy templates, backtesting, and optimization.
"""

import logging
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from typing import Optional, List, Dict, Any
import pandas as pd
import numpy as np
from datetime import datetime
import io

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


@router.post("/export-trades")
async def export_trades_to_excel(request: Dict[str, Any]):
    """
    Export trades to Excel file.
    
    Args:
        request: Dict with 'trades', 'symbol', 'template_name', 'timeframe'
    
    Returns:
        Excel file as streaming response
    """
    try:
        trades = request.get('trades', [])
        symbol = request.get('symbol', 'UNKNOWN')
        template_name = request.get('template_name', 'strategy')
        timeframe = request.get('timeframe', '1d')
        
        # Prepare data for Excel
        excel_data = []
        for trade in trades:
            # Calculate P&L in USD
            pnl_usd = trade.get('pnl', None)
            if pnl_usd is None:
                # If P&L not provided, calculate from profit percentage and initial capital
                profit_pct = trade.get('profit', 0) if trade.get('profit') is not None else 0
                initial_capital = trade.get('initial_capital', 100) if trade.get('initial_capital') is not None else 100
                pnl_usd = initial_capital * profit_pct
            
            # Calculate Return %
            return_pct = (trade.get('profit', 0) * 100) if trade.get('profit') is not None else 0
            
            # Determinar Signal Type (prioridade: signal_type > exit_reason > entry_signal_type)
            signal_type = trade.get('signal_type', '')
            if not signal_type:
                # Se não tiver signal_type, tentar inferir do exit_reason
                exit_reason = trade.get('exit_reason', '')
                if 'stop' in str(exit_reason).lower():
                    signal_type = 'Stop'
                elif exit_reason:
                    signal_type = 'Close entry(s) order...'
                else:
                    # Se for entrada, usar entry_signal_type
                    signal_type = trade.get('entry_signal_type', 'Comprar')
            
            excel_data.append({
                'Entry Time': trade.get('entry_time', ''),
                'Entry Price': trade.get('entry_price', 0),
                'Exit Time': trade.get('exit_time', '') if trade.get('exit_time') else '',
                'Exit Price': trade.get('exit_price', 0) if trade.get('exit_price') else '',
                'Trade Type': trade.get('type', 'Long').upper() if trade.get('type') else 'LONG',
                'Signal': signal_type,  # Tipo de sinal (Stop/Comprar/Close entry(s) order...)
                'P&L (USD)': round(pnl_usd, 2),
                'Return %': round(return_pct, 2),
                'Initial Capital': trade.get('initial_capital', 100) if trade.get('initial_capital') is not None else 100,
                'Final Capital': trade.get('final_capital', 0) if trade.get('final_capital') is not None else (100 + pnl_usd),
            })
        
        # Create DataFrame
        df = pd.DataFrame(excel_data)
        
        # Create Excel file in memory
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Trades')
            
            # Get the workbook and worksheet
            workbook = writer.book
            worksheet = writer.sheets['Trades']
            
            # Auto-adjust column widths
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
        
        output.seek(0)
        
        # Generate filename
        safe_symbol = symbol.replace('/', '_')
        safe_template = template_name.replace(' ', '_')
        filename = f"{safe_template}_{safe_symbol}_{timeframe}_trades.xlsx"
        
        return StreamingResponse(
            io.BytesIO(output.read()),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        logger.error(f"Error exporting trades to Excel: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error exporting trades: {str(e)}")


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
        
        # Use unified trade extraction logic (same as optimizer)
        from app.services.combo_optimizer import extract_trades_from_signals
        
        # Override stop_loss if provided in request, otherwise use strategy's default
        stop_loss_pct = request.stop_loss if request.stop_loss is not None else strategy.stop_loss
        
        # Extract trades using unified logic (executes at CLOSE, includes stop loss, uses 0.075% fee)
        trades = extract_trades_from_signals(df_with_signals, stop_loss_pct)
        
        logger.info(f"Backtest complete: {len(trades)} trades extracted")
        
        # All trades from extract_trades_from_signals are closed (have exit_time)
        trades_for_metrics = trades
        
        # Calculate metrics using same logic as combo_optimizer (TradingView-style)
        initial_capital = request.initial_capital if hasattr(request, 'initial_capital') and request.initial_capital is not None else 100
        
        total_trades = len(trades_for_metrics)
        winning_trades = sum(1 for t in trades_for_metrics if t.get('profit', 0) > 0)
        
        # Simple Return (TradingView-style): baseado em PnL total sem reinvestimento
        # TradingView calcula retorno simples somando PnL de cada trade (posição fixa)
        # Cada trade usa o mesmo capital inicial (não reinveste)
        total_pnl_usd = sum([
            initial_capital * t.get('profit', 0) 
            for t in trades_for_metrics if t.get('profit') is not None
        ])
        # Return simples: (PnL total / capital inicial) * 100
        total_return_pct = (total_pnl_usd / initial_capital) * 100.0
        
        # Max Drawdown from cumulative PnL (TradingView-style)
        # Calcular drawdown baseado em PnL acumulado (não reinveste)
        max_drawdown_pct = 0.0
        if len(trades_for_metrics) > 0:
            cumulative_pnl = 0.0
            peak_pnl = 0.0
            max_dd = 0.0
            for t in trades_for_metrics:
                trade_pnl = initial_capital * t.get('profit', 0)
                cumulative_pnl += trade_pnl
                if cumulative_pnl > peak_pnl:
                    peak_pnl = cumulative_pnl
                # Drawdown = (peak - current) / (initial_capital + peak)
                # Ou simplesmente: drawdown relativo ao capital inicial
                if peak_pnl > 0:
                    drawdown = (peak_pnl - cumulative_pnl) / (initial_capital + peak_pnl)
                else:
                    drawdown = abs(cumulative_pnl) / initial_capital if cumulative_pnl < 0 else 0
                max_dd = max(max_dd, drawdown)
            max_drawdown_pct = max_dd * 100.0  # Convert to percentage
        
        # Profit Factor (TradingView-style): usando PnL absoluto em USD
        gross_profit_usd = sum([
            initial_capital * t.get('profit', 0) 
            for t in trades_for_metrics if t.get('profit', 0) > 0
        ])
        gross_loss_usd = abs(sum([
            initial_capital * t.get('profit', 0) 
            for t in trades_for_metrics if t.get('profit', 0) < 0
        ]))
        profit_factor = gross_profit_usd / gross_loss_usd if gross_loss_usd > 0 else (999 if gross_profit_usd > 0 else 0)
        
        metrics = {
            "total_trades": total_trades,
            "win_rate": winning_trades / total_trades if total_trades > 0 else 0,
            "total_return": total_return_pct / 100.0,  # Store as decimal (0.4653 for 46.53%)
            "total_return_pct": total_return_pct,  # Also store as percentage for compatibility
            "avg_profit": total_return_pct / total_trades if total_trades > 0 else 0,
            "max_drawdown": max_drawdown_pct / 100.0,  # Store as decimal
            "max_drawdown_pct": max_drawdown_pct,  # Also store as percentage
            "profit_factor": profit_factor  # TradingView-style (USD-based)
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
        result = optimizer.run_optimization(
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
