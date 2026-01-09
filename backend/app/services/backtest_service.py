# file: backend/app/services/backtest_service.py
import sys
import os
from datetime import datetime
from typing import Optional, Union
import pandas as pd
import itertools
import numpy as np
import logging
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
import app.workers.optimization_worker as opt_worker

# Configure logging to file
log_dir = Path(__file__).parent.parent.parent / 'logs'
log_dir.mkdir(exist_ok=True)
log_file = log_dir / 'backtest_debug.log'

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)
logger.info("="*80)
logger.info("BacktestService initialized - logging to: %s", log_file)

# Add parent directory to path to import existing modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../'))

from src.data.incremental_loader import IncrementalLoader
from src.engine.backtester import Backtester
# from src.strategy.sma_cross import SMACrossStrategy
# from src.strategy.rsi_reversal import RSIReversalStrategy
# from src.strategy.bb_meanrev import BBMeanReversionStrategy
from app.strategies.dynamic_strategy import DynamicStrategy
from src.report.metrics import calculate_metrics

# Import new metrics module
from app.metrics import (
    calculate_cagr,
    calculate_monthly_return,
    calculate_avg_drawdown,
    calculate_max_dd_duration,
    calculate_recovery_factor,
    calculate_sortino_ratio,
    calculate_calmar_ratio,
    calculate_expectancy,
    calculate_max_consecutive_wins,
    calculate_max_consecutive_losses,
    calculate_trade_concentration,
    calculate_buy_and_hold,
    calculate_alpha,
    calculate_correlation,
    evaluate_go_nogo
)
# New imports for context/regime
from app.metrics.regime import calculate_regime_classification
from app.metrics.indicators import calculate_avg_indicators

# Import Job Manager
from app.services.job_manager import JobManager



class BacktestService:
    def __init__(self):
        self.loader = IncrementalLoader()
    
    def _get_strategy(self, name_or_config: Union[str, dict], params: Optional[dict] = None):
        """Instantiate strategy with params"""
        # Import CRUZAMENTOMEDIAS
        from app.strategies.cruzamento_medias import CruzamentoMedias
        
        if isinstance(name_or_config, dict):
            strategy_name = name_or_config.get('name', '').lower()
            
            # Check if it's CRUZAMENTOMEDIAS
            if strategy_name == 'cruzamentomedias':
                # If params are provided (optimization mode), merge them
                if params:
                    merged_config = {**name_or_config, **params}
                    return CruzamentoMedias(merged_config)
                return CruzamentoMedias(name_or_config)
            
            # Otherwise use DynamicStrategy
            if params:
                merged_config = {**name_or_config, **params}
                return DynamicStrategy(merged_config)
            return DynamicStrategy(name_or_config)
            
        # String name
        strategy_name_lower = name_or_config.lower()
        
        # Check if it's CRUZAMENTOMEDIAS
        if strategy_name_lower == 'cruzamentomedias':
            strategy_config = {"name": name_or_config}
            if params:
                strategy_config.update(params)
            return CruzamentoMedias(strategy_config)
        
        # Convert to DynamicStrategy config
        strategy_config = {"name": name_or_config}
        if params:
            strategy_config.update(params)
        return DynamicStrategy(strategy_config)
    
    def run_backtest(self, config: dict, progress_callback=None, job_id: str = None, resume: bool = False) -> dict:
        """
        Execute backtest and return results
        """
        # Extract config
        exchange = config['exchange']
        symbol = config['symbol']
        
        # Handle multiple timeframes
        target_timeframes = config.get('timeframes')
        if not target_timeframes:
            target_timeframes = [config['timeframe']]
            
        full_period = config.get('full_period', False)
        since = config.get('since')
        
        if full_period or not since:
            since = "2017-01-01 00:00:00"  # Default inception for crypto
            
        until = config.get('until')
        strategies = config['strategies']
        params = config.get('params') or {}
        mode = config.get('mode', 'run')
        
        # --- Optimization Mode ---
        # --- Optimization Mode ---
        if mode == 'optimize':
            return self._run_optimization(config, progress_callback, job_id, resume)

        # Prepare results
        results = {}
        first_valid_candles = []
        benchmark_result = {}
        
        total_steps = len(target_timeframes) * len(strategies)
        current_step_count = 0
        
        for timeframe in target_timeframes:
            # Fetch data
            if progress_callback:
                pct = (current_step_count / total_steps) * 100 if total_steps > 0 else 0
                progress_callback(f"Downloading data for {symbol} ({timeframe})...", pct)
                
            # Define data loader callback
            def loader_callback(data):
                if progress_callback:
                    msg = f"Downloading {data['symbol']} {data['timeframe']}: {data['downloaded_candles']} candles ({data['current_date']})"
                    # Keep current overall percentage
                    progress_callback(msg, pct)

            try:
                df = self.loader.fetch_data(symbol, timeframe, since, until, progress_callback=loader_callback)
            except Exception as e:
                print(f"Error fetching data for {timeframe}: {e}")
                current_step_count += len(strategies)
                if progress_callback:
                    pct = (current_step_count / total_steps) * 100
                    progress_callback(f"Error loading {timeframe}. Skipping...", pct)
                continue
            
            
            if df is None or df.empty:
                current_step_count += len(strategies)
                continue
                
            # SAFETY: Ensure index is datetime (handle ms timestamps from Parquet/CCXT)
            if not isinstance(df.index, pd.DatetimeIndex):
                if 'timestamp' in df.columns:
                    df = df.set_index('timestamp')
                
                # Check numeric again after set_index
                if pd.api.types.is_numeric_dtype(df.index):
                    df.index = pd.to_datetime(df.index, unit='ms')
                else:
                    df.index = pd.to_datetime(df.index)

            # Limit check
            # Performance Update: Removed artificial 20k limit for backtesting (now optimized).
            # if len(df) > 20000: ...
            
            # Keep first valid candles for frontend visualization context
            # NOTE: We truncate this for the Frontend to avoid crashing user browser with 1M points.
            if not first_valid_candles:
                 # Take last 2000 candles for visualization
                 viz_df = df.tail(2000).copy()
                 temp_df = viz_df.reset_index()
                 # Ensure timestamp format for JSON
                 if 'timestamp_utc' not in temp_df.columns:
                     if 'timestamp' in temp_df.columns:
                         temp_df['timestamp_utc'] = temp_df['timestamp']
                     else:
                        # Assuming index is datetime if not present
                        try:
                            temp_df['timestamp_utc'] = temp_df.iloc[:, 0]
                        except:
                            pass
                 
                 json_candles = temp_df.to_dict('records')
                 # Sanitize timestamps
                 for c in json_candles:
                     if 'timestamp_utc' in c and hasattr(c['timestamp_utc'], 'isoformat'):
                         c['timestamp_utc'] = c['timestamp_utc'].isoformat()
                 first_valid_candles = json_candles
                 
                 # Calculate benchmark on first valid data data (using full df or viz df?)
                 # Benchmark usually "Buy and Hold" for the period. 
                 # Let's benchmark full period to be fair.
                 benchmark_result = self._calculate_benchmark(df, config.get('cash', 10000))

            # Run each strategy
            for i, strategy_config in enumerate(strategies):
                current_step_count += 1
                
                # Determine strategy name
                if isinstance(strategy_config, dict):
                    base_name = strategy_config.get('name', f'Custom_{i+1}')
                else:
                    base_name = strategy_config
                    
                # Unique result key
                strategy_key = f"{base_name} ({timeframe})" if len(target_timeframes) > 1 else base_name
                
                if progress_callback:
                    pct = (current_step_count / total_steps) * 100
                    progress_callback(f"Testing {strategy_key}...", pct)

                try:
                    # Instantiate strategy
                    if isinstance(strategy_config, dict):
                         strategy = self._get_strategy(strategy_config)
                    else:
                         strategy_params = params.get(base_name, {})
                         strategy = self._get_strategy(strategy_config, strategy_params)
                    
                    # Generate signals
                    signals = strategy.generate_signals(df)
                    
                    # Run engine
                    backtester = Backtester(
                        initial_capital=config.get('cash', 10000),
                        fee=config.get('fee', 0.001),
                        slippage=config.get('slippage', 0.0005),
                        position_size_pct=config.get('position_size_pct', 0.99), # Default to 99% (All-in)
                        stop_loss_pct=config.get('stop_pct'),
                        take_profit_pct=config.get('take_pct')
                    )
                    
                    equity_curve = backtester.run(df, strategy, record_force_close=True)
                    
                    if equity_curve is not None and not equity_curve.empty:
                        metrics = calculate_metrics(equity_curve, backtester.trades, config.get('cash', 10000))
                        
                        # Calculate enhanced metrics (CAGR, Sortino, Calmar, etc.)
                        try:
                            metrics = self._calculate_enhanced_metrics(
                                equity_curve=equity_curve['equity'], # Pass SERIES
                                trades=backtester.trades,
                                df=df,
                                initial_capital=config.get('cash', 10000),
                                existing_metrics=metrics
                            )
                        except Exception as e:
                            print(f"Warning: Could not calculate enhanced metrics: {e}")
                    
                    # Drawdown series
                    running_max = equity_curve['equity'].cummax()
                    drawdown = ((equity_curve['equity'] - running_max) / running_max * 100).fillna(0).tolist()
                    
                    # Markers for TradingView
                    markers = self._generate_markers(backtester.trades)
                    
                    # Equity Data
                    equity_data = equity_curve[['timestamp', 'equity']].copy()
                    equity_data['timestamp'] = equity_data['timestamp'].astype(str)
                    equity_data = equity_data.to_dict('records')
                    
                    # Indicators extraction (simplified)
                    indicators = []
                    if hasattr(backtester, 'simulation_data') and backtester.simulation_data is not None:
                        sim_data = backtester.simulation_data
                        exclude_cols = ['timestamp_utc', 'open', 'high', 'low', 'close', 'volume', 'signal']
                        indicator_cols = [c for c in sim_data.columns if c not in exclude_cols]
                        
                        for col in indicator_cols:
                             series_data = sim_data[['timestamp_utc', col]].dropna()
                             if not series_data.empty:
                                 formatted = series_data.rename(columns={'timestamp_utc': 'time', col: 'value'}).copy()
                                 formatted['time'] = formatted['time'].astype(str)
                                 indicators.append({
                                     'name': col,
                                     'data': formatted.to_dict('records'),
                                     'panel': 'lower' if any(x in col.lower() for x in ['rsi', 'macd', 'stoch', 'cci']) else 'main'
                                 })

                    metrics['strategy'] = base_name
                    metrics['timeframe'] = timeframe

                    results[strategy_key] = {
                        'metrics': metrics,
                        'trades': backtester.trades,
                        'equity': equity_data,
                        'drawdown': drawdown,
                        'markers': markers,
                        'indicators': indicators
                    }
                    
                except Exception as e:
                    import traceback
                    print(f"Error executing {strategy_key}: {e}")
                    results[strategy_key] = {'error': str(e), 'metrics': {}}

        return self._sanitize({
            'dataset': {
                'exchange': exchange,
                'symbol': symbol,
                'timeframe': target_timeframes[0] if target_timeframes else config['timeframe'],
                'since': since,
                'until': until or datetime.now().isoformat(),
                'candle_count': len(first_valid_candles)
            },
            'candles': first_valid_candles,
            'results': results,
            'benchmark': benchmark_result
        })

    def _run_optimization(self, config: dict, progress_callback=None, job_id: str = None, resume: bool = False) -> dict:
        """
        Execute Grid Search Optimization for one or more strategies
        """
        strategies = config['strategies']
        
        # If multiple strategies, run optimization for each and aggregate
        if len(strategies) > 1:
            return self._run_multi_strategy_optimization(config, progress_callback)
        
        # Single strategy optimization (existing logic)
        return self._run_single_strategy_optimization(config, progress_callback, job_id=job_id, resume=resume)
    
    def _run_multi_strategy_optimization(self, config: dict, progress_callback=None) -> dict:
        """
        Execute Grid Search Optimization for multiple strategies
        """
        exchange = config['exchange']
        symbol = config['symbol']
        timeframe = config['timeframe']
        since = config['since']
        until = config.get('until')
        strategies = config['strategies']
        
        # Fetch data ONCE for all strategies
        if progress_callback:
            progress_callback(f"Downloading data for {symbol}...", 0)
        
        try:
            df = self.loader.fetch_data(symbol, timeframe, since, until)
            if len(df) > 20000:
                print(f"Truncating optimization dataset to 20k candles")
                df = df.tail(20000)
        except Exception as e:
            return {'error': f"Failed to load data: {str(e)}"}
        
        # Run optimization for each strategy
        all_strategy_results = []
        total_strategies = len(strategies)
        
        for strat_idx, strategy_config in enumerate(strategies):
            base_name = strategy_config if isinstance(strategy_config, str) else strategy_config.get('name', f'Strategy{strat_idx}')
            
            if progress_callback:
                pct = (strat_idx / total_strategies) * 100
                progress_callback(f"Optimizing {base_name}...", pct)
            
            # Create config for this specific strategy
            single_config = {**config, 'strategies': [strategy_config]}
            
            # Run optimization for this strategy
            try:
                result = self._run_single_strategy_optimization(
                    single_config, 
                    progress_callback=lambda msg, p: progress_callback(
                        f"{base_name}: {msg}", 
                        (strat_idx / total_strategies) * 100 + (p / total_strategies)
                    ) if progress_callback else None,
                    df=df  # Pass pre-loaded data
                )
                
                if 'error' not in result:
                    all_strategy_results.append({
                        'strategy': base_name,
                        'results': result.get('optimization_results', []),
                        'best': result.get('best_result'),
                        'combinations_tested': result.get('combinations_tested', 0)
                    })
            except Exception as e:
                print(f"Error optimizing {base_name}: {e}")
                import traceback
                traceback.print_exc()
        
        # Find overall best across all strategies
        overall_best = None
        best_pnl = float('-inf')
        
        for strat_result in all_strategy_results:
            if strat_result['best'] and strat_result['best']['metrics']['total_pnl'] > best_pnl:
                best_pnl = strat_result['best']['metrics']['total_pnl']
                overall_best = {
                    'strategy': strat_result['strategy'],
                    **strat_result['best']
                }
        
        return self._sanitize({
            'dataset': {
                'exchange': exchange,
                'symbol': symbol,
                'timeframe': timeframe,
                'since': since,
                'until': until,
                'candle_count': len(df) if df is not None else 0
            },
            'mode': 'optimize',
            'multi_strategy': True,
            'strategies': all_strategy_results,
            'overall_best': overall_best,
            'total_combinations': sum(s['combinations_tested'] for s in all_strategy_results)
        })
    
    def _run_single_strategy_optimization(self, config: dict, progress_callback=None, df=None, job_id: str = None, resume: bool = False) -> dict:
        """
        Execute Grid Search Optimization for a single strategy using Parallel Processing
        """
        exchange = config['exchange']
        symbol = config['symbol']
        
        # Handle timeframe as string or list
        timeframe_input = config['timeframe']
        timeframe_list = timeframe_input if isinstance(timeframe_input, list) else [timeframe_input]
        primary_timeframe = timeframe_list[0]
        
        full_period = config.get('full_period', False)
        since = config.get('since')
        
        if full_period or not since:
            since = "2017-01-01 00:00:00"
        
        until = config.get('until')
        strategy_config = config['strategies'][0]
        base_name = strategy_config if isinstance(strategy_config, str) else strategy_config.get('name', 'Strategy')
        
        # 1. Generate Parameter Grid
        # Expand Global Params
        global_grid = {}
        if len(timeframe_list) > 1:
            global_grid['timeframe'] = timeframe_list
        
        for param in ['stop_pct', 'take_pct']:
            val = config.get(param)
            if isinstance(val, dict):
                global_grid[param] = self._expand_range(val)
            elif val is not None:
                global_grid[param] = [val]

        # Expand Strategy Params
        strat_params = config.get('params', {}).get(base_name, {})
        strat_grid = {}
        for k, v in strat_params.items():
            if isinstance(v, dict) and 'min' in v and 'max' in v:
                strat_grid[k] = self._expand_range(v)
            else:
                strat_grid[k] = [v]
        
        # Combine grids
        global_keys = list(global_grid.keys())
        global_values = list(global_grid.values())
        strat_keys = list(strat_grid.keys())
        strat_values = list(strat_grid.values())
        
        all_keys = global_keys + strat_keys
        all_values = global_values + strat_values
        
        combinations = list(itertools.product(*all_values))
        total_steps = len(combinations)
        
        logger.info(f"Optimization ({base_name}): {total_steps} combinations to test. (Parallel)")

        # 2. Pre-load Data for all timeframes
        data_map = {}
        # If df provided and matches primary (and only 1 timeframe), use it
        if df is not None and len(timeframe_list) == 1:
            if len(df) > 20000:
                print(f"Truncating optimization dataset to 20k candles")
                df = df.tail(20000)
            data_map[primary_timeframe] = df
        
        # Fetch missing timeframes
        missing_tfs = [tf for tf in timeframe_list if tf not in data_map]
        if missing_tfs:
            if progress_callback:
                progress_callback(f"Downloading data for {missing_tfs}...", 0)
            try:
                for tf in missing_tfs:
                    d = self.loader.fetch_data(symbol, tf, since, until)
                    if len(d) > 20000:
                        d = d.tail(20000)
                    data_map[tf] = d
            except Exception as e:
                return {'error': f"Failed to load data: {str(e)}"}

        # 3. Resume Logic
        import traceback
        job_manager = JobManager()
        start_index = 0
        
        if resume and job_id:
             state = job_manager.load_state(job_id)
             if state:
                 progress_data = state.get('progress', {})
                 start_index = progress_data.get('current_iteration', 0)
                 # Count existing results in SQLite
                 existing = job_manager.get_results(job_id, page=1, limit=1)
                 existing_count = existing['pagination']['total']
                 logger.info(f"Resuming optimization from index {start_index}. Found {existing_count} previous results in database.")

        # Slice combinations
        remaining_combinations = combinations[start_index:]
        if not remaining_combinations:
            logger.info("No remaining combinations to test.")
        
        # 4. Parallel Execution
        # Chunk size
        batch_size = 50
        chunks = [remaining_combinations[i:i + batch_size] for i in range(0, len(remaining_combinations), batch_size)]
        
        # Max workers (reduce to avoid OOM/locking)
        max_workers = 4 # min(os.cpu_count() or 4, 8) 
        
        logger.info(f"Starting ProcessPoolExecutor with {max_workers} workers.")
        
        try:
            with ProcessPoolExecutor(max_workers=max_workers, initializer=opt_worker.init_worker, initargs=(data_map,)) as executor:
                # Submit all chunks
                # We map future back to its index increment to track progress
                future_to_chunk_idx = {}
                for idx, chunk in enumerate(chunks):
                    future = executor.submit(opt_worker.evaluate_chunk, config, chunk, all_keys)
                    future_to_chunk_idx[future] = idx

                completed_count = 0
                total_chunks = len(chunks)
                
                for future in as_completed(future_to_chunk_idx):
                    # Check Pause Signal
                    if job_id and job_manager.should_pause(job_id):
                        logger.info(f"Pause signal detected for job {job_id}")
                        executor.shutdown(wait=False, cancel_futures=True)
                        
                        # Save state
                        current_processed = start_index + (completed_count * batch_size)
                        current_state = {
                             "job_id": job_id,
                             "status": "PAUSED",
                             "config": config,
                             "progress": {
                                 "current_iteration": current_processed,
                                 "total_iterations": total_steps
                             }
                             # Results are in SQLite, not in state
                        }
                        job_manager.mark_paused(job_id, current_state)
                        # Get top 10 from SQLite for response
                        top_results = job_manager.get_results(job_id, page=1, limit=10)['results']
                        return {'status': 'paused', 'progress': f"{current_processed}/{total_steps}", 'results': top_results}

                    try:
                        chunk_results = future.result()
                        # Save batch to SQLite for better performance
                        result_base_index = start_index + (completed_count * batch_size)
                        job_manager.save_results_batch(job_id, chunk_results, result_base_index)
                        completed_count += 1
                        
                        # Update Progress
                        current_processed_count = start_index + (completed_count * batch_size)
                        # Clamp to total
                        current_processed_count = min(current_processed_count, total_steps)
                        
                        pct = (current_processed_count / total_steps) * 100
                        if progress_callback:
                            progress_callback(f"Optimizing... {current_processed_count}/{total_steps}", pct)
                            
                        # Save Checkpoint every 5 chunks (250 items)
                        if job_id and completed_count % 5 == 0:
                             checkpoint_state = {
                                 "job_id": job_id,
                                 "status": "RUNNING",
                                 "config": config,
                                 "progress": {
                                     "current_iteration": current_processed_count,
                                     "total_iterations": total_steps
                                 }
                                 # Results are in SQLite, not in state
                             }
                             job_manager.save_state(job_id, checkpoint_state)
                             
                    except Exception as exc:
                        logger.error(f"Chunk execution failed: {exc}")
                        # Don't stop, just continue? Or fail? 
                        # Continue allows partial partial success.
        except Exception as e:
            logger.error(f"Executor pool error: {e}")
            # Check if we have any results in SQLite
            result_count = job_manager.get_results(job_id, page=1, limit=1)['pagination']['total']
            if result_count == 0:
                return {'error': str(e)}

        # 5. Finalize Results
        # Fetch all results from SQLite and sort by Net Profit
        # Helper to safely get pnl
        def get_pnl(r):
            m = r.get('metrics', {})
            return m.get('total_pnl', float('-inf')) if m else float('-inf')
        
        # Get top results from SQLite (limit to 10000 for faster sorting)
        all_results_data = job_manager.get_results(job_id, page=1, limit=10000)
        opt_results = all_results_data['results']
        opt_results.sort(key=get_pnl, reverse=True)
        
        print(f" DEBUG: opt_results length: {len(opt_results)}")
        print(f" DEBUG: About to check if opt_results (bool: {bool(opt_results)})")
        
        # 6. Re-run Best Result (to get full rich metrics/equity curve for the UI)
        best_result = None
        if opt_results:
            best_scout = opt_results[0]
            
            print(f" DEBUG: best_scout keys: {best_scout.keys()}")
            print(f" DEBUG: 'error' in best_scout: {'error' in best_scout}")
            
            # Safety check: if the best result is actually an error, don't try to re-run
            if 'error' in best_scout:
                logger.error(f"Top optimization result contains error: {best_scout['error']}")
                best_result = best_scout
            else:
                logger.info("Re-running best strategy configuration to generate full report...")
                try:
                    # Re-construct params for single run
                    best_params = best_scout['params']
                
                    # Setup strategy
                    strat_p = {k: v for k, v in best_params.items() if k in strat_keys}
                    strategy = self._get_strategy(strategy_config, strat_p)
                
                    # Setup backtester
                    backtester = Backtester(
                        initial_capital=config.get('cash', 10000),
                        fee=config.get('fee', 0.001),
                        slippage=config.get('slippage', 0.0005),
                        position_size_pct=0.2,
                        stop_loss_pct=best_params.get('stop_pct'),
                        take_profit_pct=best_params.get('take_pct')
                    )
                
                    # Get data for best timeframe
                    tf_best = best_params.get('timeframe', primary_timeframe)
                    df_best = data_map.get(tf_best)
                
                    signals = strategy.generate_signals(df_best)
                    equity_curve = backtester.run(df_best, strategy)
                
                    if equity_curve is not None and not equity_curve.empty:
                        full_metrics = calculate_metrics(equity_curve, backtester.trades, config.get('cash', 10000))
                        # Add enhanced
                        print(f" DEBUG: About to call _calculate_enhanced_metrics with {len(backtester.trades)} trades")
                        # Call _calculate_enhanced_metrics for the best result
                        try:
                            full_metrics = self._calculate_enhanced_metrics(
                                equity_curve['equity'], backtester.trades, df_best, config.get('cash', 10000), full_metrics
                            )
                            log_debug(f" DEBUG: Best Result Metrics: {full_metrics}")
                            log_debug(f" DEBUG: Profit Factor: {full_metrics.get('profit_factor')}")
                            log_debug(f" DEBUG: _calculate_enhanced_metrics completed. regime_performance: {full_metrics.get('regime_performance', 'MISSING')}")
                        except Exception as e:
                            print(f" ERROR in _calculate_enhanced_metrics: {e}")
                            import traceback
                            traceback.print_exc()
                    
                        best_result = {
                            'strategy': base_name,
                            'params': best_params,
                            'metrics': full_metrics,
                            'timeframe': tf_best,
                            # 'equity_curve': equity_curve.to_dict()... # Keep it light? UI might download via separate endpoint? 
                            # Usually UI expects best_result to have what lists don't.
                        }
                        # Update the top result in the list with better metrics
                        opt_results[0] = best_result # Replace with full version
                except Exception as e:
                    logger.error(f"Failed to re-run best result: {e}")
                    best_result = best_scout # Fallback
        
        # 7. Calculate Heavy Metrics for Top 10 Results (excluding best, which already has them)
        # Heavy metrics: ATR, ADX, Regime Performance, Alpha
        top_n_for_heavy_metrics = 10
        logger.info(f"Calculating heavy metrics for top {top_n_for_heavy_metrics} results...")
        
        for idx in range(1, min(top_n_for_heavy_metrics, len(opt_results))):
            result = opt_results[idx]
            
            if 'error' in result:
                continue
                
            try:
                # Get params and data
                params = result.get('params', {})
                tf = params.get('timeframe', primary_timeframe)
                df_for_metrics = data_map.get(tf)
                
                if df_for_metrics is None or df_for_metrics.empty:
                    continue
                
                # Calculate heavy metrics
                heavy_metrics = self._calculate_heavy_metrics(
                    df_for_metrics, 
                    result.get('metrics', {}),
                    config.get('cash', 10000)
                )
                
                # Update result metrics
                result['metrics'].update(heavy_metrics)
                
            except Exception as e:
                logger.warning(f"Failed to calculate heavy metrics for result #{idx+1}: {e}")

        # Build final object
        dataset_info = {
            'exchange': exchange,
            'symbol': symbol,
            'timeframe': primary_timeframe,
            'since': since,
            'until': until,
            'candle_count': max(len(d) for d in data_map.values()) if data_map else 0
        }
        if len(timeframe_list) > 1:
            dataset_info['timeframes_tested'] = timeframe_list

        if job_id:
             final_state = {
                 "job_id": job_id,
                 "status": "COMPLETED",
                 "config": config,
                 "progress": {
                     "current_iteration": total_steps,
                     "total_iterations": total_steps
                 }
                 # Results are in SQLite, not in state file
             }
             job_manager.mark_completed(job_id, final_state)

        return self._sanitize({
            'dataset': dataset_info,
            'mode': 'optimize',
            'optimization_results': opt_results,  # Return all results
            'best_result': opt_results[0] if opt_results else None,
            'combinations_tested': total_steps,
            'total_results_in_db': len(opt_results)  # Full count
        })

    def _expand_range(self, range_dict: dict) -> list:
        """
        Expand a range dict {min, max, step} into a list of values
        """
        min_val = range_dict.get('min')
        max_val = range_dict.get('max')
        step = range_dict.get('step', 1)
        
        # If min or max is None, return empty list (skip this param)
        if min_val is None or max_val is None:
            return []
        
        try:
            start = float(min_val)
            end = float(max_val)
            step = float(step)
            
            # Handle float precision
            decimals = 0
            if '.' in str(step):
                decimals = len(str(step).split('.')[1])
                
            values = []
            curr = start
            while curr <= end + (step/1000): # Tolerance
                values.append(round(curr, decimals + 2))
                curr += step
                
            return values
        except:
             return [range_def] # Fallback

    
    def _sanitize(self, obj):
        import math
        import numpy as np
        
        if isinstance(obj, float):
            if math.isnan(obj) or math.isinf(obj):
                return None
            return obj
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            if np.isnan(obj) or np.isinf(obj):
                return None
            return float(obj)
        if isinstance(obj, np.bool_):
            return bool(obj)
        if isinstance(obj, (np.datetime64, pd.Timestamp)):
            return str(obj)
        if isinstance(obj, dict):
            return {k: self._sanitize(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [self._sanitize(v) for v in obj]
        return obj
    
    def _generate_markers(self, trades: list) -> list:
        """Convert trades to TradingView markers format"""
        markers = []
        for trade in trades:
            if 'entry_time' in trade and trade['entry_time']:
                # Ensure valid timestamp for entry
                try:
                    ts = trade['entry_time']
                    if not isinstance(ts, (int, float)):
                        ts = pd.to_datetime(ts).timestamp()
                    
                    markers.append({
                        'time': ts,
                        'position': 'belowBar',
                        'color': '#2196F3',
                        'shape': 'arrowUp',
                        'text': 'BUY'
                    })
                except Exception:
                    pass
            
            if 'exit_time' in trade and trade['exit_time']:
                try:
                    ts = trade['exit_time']
                    if not isinstance(ts, (int, float)):
                        ts = pd.to_datetime(ts).timestamp()
                        
                    is_win = trade.get('pnl', 0) > 0
                    markers.append({
                        'time': ts,
                        'position': 'aboveBar',
                        'color': '#e91e63' if not is_win else '#00E676', # Green for win, Pink for loss
                        'shape': 'arrowDown',
                        'text': 'SELL'
                    })
                except Exception:
                    pass
        return markers
    
    def _calculate_benchmark(self, df, initial_capital: float) -> dict:
        """Calculate buy&hold performance"""
        try:
            first_price = df.iloc[0]['close']
            last_price = df.iloc[-1]['close']
            
            quantity = initial_capital / first_price
            final_value = quantity * last_price
            
            return_pct = (final_value - initial_capital) / initial_capital
            
            equity = (df['close'] / first_price * initial_capital).tolist()
            
            return {
                'return_pct': return_pct,
                'final_value': final_value,
                'equity': equity
            }
        except:
            return {}
    
    def _calculate_heavy_metrics(self, df: pd.DataFrame, existing_metrics: dict, initial_capital: float) -> dict:
        """
        Calculate computationally expensive metrics (ATR, ADX, Alpha).
        Only called for top N results to avoid performance impact.
        Does not require trades list - uses only OHLCV data and existing metrics.
        
        Args:
            df: OHLCV DataFrame
            existing_metrics: Already calculated metrics (from worker)
            initial_capital: Initial capital for benchmark calculation
            
        Returns:
            Dict with heavy metrics
        """
        heavy = {}
        
        try:
            import pandas_ta as ta
            context_df = df.copy()
            
            # Calculate indicators if needed
            if not any(c.startswith('ATR') for c in context_df.columns):
                context_df.ta.atr(length=14, append=True)
            if not any(c.startswith('ADX') for c in context_df.columns):
                context_df.ta.adx(length=14, append=True)
                
            # Average indicators
            from app.metrics.indicators import calculate_avg_indicators
            avg_inds = calculate_avg_indicators(context_df)
            heavy.update(avg_inds)
            
            # Buy & Hold Alpha
            from app.metrics.benchmark import calculate_buy_and_hold, calculate_alpha
            prices = df['close']
            bh_result = calculate_buy_and_hold(prices, initial_capital)
            heavy['benchmark'] = bh_result
            
            strategy_cagr = existing_metrics.get('cagr', 0) or 0
            bh_cagr = bh_result.get('cagr', 0) or 0
            heavy['alpha'] = calculate_alpha(strategy_cagr, bh_cagr)
            
            # Regime Performance Analysis
            try:
                from app.metrics.regime import calculate_regime_classification
                
                # Check/Calc SMA (200) for Regime
                if 'SMA_200' not in context_df.columns:
                    context_df.ta.sma(length=200, append=True)
                
                # Regime Classification
                regime_df = calculate_regime_classification(context_df, sma_period=200)
                
                # Segment Trades by Regime
                if trades and not regime_df.empty:
                    regime_stats = {}
                    
                    # Ensure index is datetime
                    if not isinstance(regime_df.index, pd.DatetimeIndex):
                        regime_df.index = pd.to_datetime(regime_df.index)
                    
                    for trade in trades:
                        entry_time = trade.get('entry_time')
                        if entry_time:
                            try:
                                et = pd.to_datetime(entry_time)
                                # Find nearest regime (asof)
                                idx = regime_df.index.asof(et)
                                if pd.notna(idx):
                                    r = regime_df.loc[idx, 'regime']
                                    
                                    if r not in regime_stats:
                                        regime_stats[r] = {'count': 0, 'wins': 0, 'losses': 0, 'pnl': 0.0}
                                    
                                    regime_stats[r]['count'] += 1
                                    pnl = trade.get('pnl', 0)
                                    regime_stats[r]['pnl'] += pnl
                                    if pnl > 0:
                                        regime_stats[r]['wins'] += 1
                                    elif pnl < 0:
                                        regime_stats[r]['losses'] += 1
                            except:
                                pass
                    
                    # Calc rates
                    for r, stats in regime_stats.items():
                        total = stats['count']
                        if total > 0:
                            stats['win_rate'] = (stats['wins'] / total) * 100
                    
                    heavy['regime_performance'] = regime_stats
                else:
                    heavy['regime_performance'] = {}
                    
            except Exception as e:
                logger.warning(f"Error calculating regime performance in heavy metrics: {e}")
                heavy['regime_performance'] = {}
            
        except Exception as e:
            logger.warning(f"Error in _calculate_heavy_metrics: {e}")
            # Set defaults to avoid missing keys
            heavy['avg_atr'] = 0
            heavy['avg_adx'] = 0
            heavy['benchmark'] = None
            heavy['alpha'] = None
            heavy['regime_performance'] = {}
            
        return heavy
    
    def _calculate_enhanced_metrics(
        self,
        equity_curve: pd.Series,
        trades: list,
        df: pd.DataFrame,
        initial_capital: float,
        existing_metrics: dict
    ) -> dict:
        """
        Calcula todas as métricas avançadas usando o módulo de métricas.
        
        Args:
            equity_curve: Série temporal do valor da conta
            trades: Lista de trades executados
            df: DataFrame com dados de preço (para benchmark)
            initial_capital: Capital inicial
            existing_metrics: Métricas já calculadas (sharpe, max_dd, etc.)
            
        Returns:
            Dict com todas as métricas (existentes + novas)
        """
        enhanced = existing_metrics.copy()
        
        try:
            # === Performance Metrics ===
            try:
                enhanced['cagr'] = calculate_cagr(equity_curve)
            except Exception as e:
                print(f"Error calculating CAGR: {e}")
                enhanced['cagr'] = None
            
            try:
                enhanced['monthly_return_avg'] = calculate_monthly_return(equity_curve)
            except Exception as e:
                print(f"Error calculating monthly return: {e}")
                enhanced['monthly_return_avg'] = None
            
            # === Risk Metrics ===
            try:
                enhanced['avg_drawdown'] = calculate_avg_drawdown(equity_curve)
            except Exception as e:
                print(f"Error calculating avg drawdown: {e}")
                enhanced['avg_drawdown'] = None
            
            try:
                enhanced['max_dd_duration_days'] = calculate_max_dd_duration(equity_curve)
            except Exception as e:
                print(f"Error calculating max DD duration: {e}")
                enhanced['max_dd_duration_days'] = None
            
            try:
                total_return = (equity_curve.iloc[-1] / equity_curve.iloc[0]) - 1
                max_dd = existing_metrics.get('max_drawdown', 0)
                enhanced['recovery_factor'] = calculate_recovery_factor(total_return, max_dd)
            except Exception as e:
                print(f"Error calculating recovery factor: {e}")
                enhanced['recovery_factor'] = None
            
            # === Risk-Adjusted Metrics ===
            try:
                returns = equity_curve.pct_change().dropna()
                enhanced['sortino_ratio'] = calculate_sortino_ratio(returns)
            except Exception as e:
                print(f"Error calculating Sortino: {e}")
                enhanced['sortino_ratio'] = None
            
            try:
                cagr = enhanced.get('cagr', 0)
                max_dd = existing_metrics.get('max_drawdown', 0)
                enhanced['calmar_ratio'] = calculate_calmar_ratio(cagr, max_dd)
            except Exception as e:
                print(f"Error calculating Calmar: {e}")
                enhanced['calmar_ratio'] = None
            
            # === Trade Statistics ===
            try:
                enhanced['expectancy'] = calculate_expectancy(trades)
            except Exception as e:
                print(f"Error calculating expectancy: {e}")
                enhanced['expectancy'] = None
            
            try:
                enhanced['max_consecutive_wins'] = calculate_max_consecutive_wins(trades)
            except Exception as e:
                print(f"Error calculating max consecutive wins: {e}")
                enhanced['max_consecutive_wins'] = None
            
            try:
                enhanced['max_consecutive_losses'] = calculate_max_consecutive_losses(trades)
            except Exception as e:
                print(f"Error calculating max consecutive losses: {e}")
                enhanced['max_consecutive_losses'] = None
            
            try:
                enhanced['trade_concentration_top_10_pct'] = calculate_trade_concentration(trades, top_n=10)
            except Exception as e:
                print(f"Error calculating trade concentration: {e}")
                enhanced['trade_concentration_top_10_pct'] = None
            
            # === Benchmark (Buy & Hold) ===
            try:
                prices = df['close']
                bh_result = calculate_buy_and_hold(prices, initial_capital)
                enhanced['benchmark'] = bh_result
                
                # Calculate Alpha
                strategy_cagr = enhanced.get('cagr', 0) or 0
                bh_cagr = bh_result.get('cagr', 0) or 0
                enhanced['alpha'] = calculate_alpha(strategy_cagr, bh_cagr)
            except Exception as e:
                print(f"Error calculating benchmark: {e}")
                enhanced['benchmark'] = None
                enhanced['alpha'] = None
            
            # === Market Context (Avg ATR/ADX) & Regime Analysis ===
            try:
                # 1. Ensure Indicators exist (if simple strategy didn't calculate them)
                # Need pandas_ta or manual calc?
                # We can try using pandas_ta if available on the DF, or just rely on what is there.
                # If the strategy uses them, they are in df (maybe).
                # Actually, DynamicStrategy *returns* signals, but Backtester doesn't modify DF with indicators unless strategy did.
                # The 'df' passed here is the original OHLCV (mostly).
                # If we want context, we might need to calc them here for the reporting.
                import pandas_ta as ta
                
                # We work on a copy to not affect other things
                context_df = df.copy()
                
                # Check/Calc ATR (14)
                if not any(c.startswith('ATR') for c in context_df.columns):
                    context_df.ta.atr(length=14, append=True)
                
                # Check/Calc ADX (14)
                if not any(c.startswith('ADX') for c in context_df.columns):
                    context_df.ta.adx(length=14, append=True)
                    
                # Check/Calc SMA (200) for Regime
                if 'SMA_200' not in context_df.columns:
                     context_df.ta.sma(length=200, append=True)
                
                # DEBUG: Print columns to verify SMA_200 existence
                print(f"DEBUG: Context DF Columns after TA: {context_df.columns.tolist()}")
                
                # 2. Avg Indicators
                avg_inds = calculate_avg_indicators(context_df)
                enhanced.update(avg_inds)
                
                # 3. Regime Classification
                regime_df = calculate_regime_classification(context_df, sma_period=200)
                # DEBUG: Check regime distribution
                print(f"DEBUG: Regime counts: {regime_df['regime'].value_counts().to_dict()}")
                
                # 4. Segment Trades by Regime
                # We need to map trade entry_time to the regime at that time.
                # Trade dict has 'entry_time' (timestamp or str).
                if trades and not regime_df.empty:
                    regime_stats = {}
                    
                    # Ensure index is datetime
                    if not isinstance(regime_df.index, pd.DatetimeIndex):
                         regime_df.index = pd.to_datetime(regime_df.index)
                    
                    for trade in trades:
                        entry_time = trade.get('entry_time')
                        if entry_time:
                            try:
                                et = pd.to_datetime(entry_time)
                                # Find nearest regime (asof)
                                idx = regime_df.index.asof(et)
                                if pd.notna(idx):
                                    r = regime_df.loc[idx, 'regime']
                                    
                                    if r not in regime_stats:
                                        regime_stats[r] = {'count': 0, 'wins': 0, 'losses': 0, 'pnl': 0.0}
                                    
                                    regime_stats[r]['count'] += 1
                                    pnl = trade.get('pnl', 0)
                                    regime_stats[r]['pnl'] += pnl
                                    if pnl > 0:
                                        regime_stats[r]['wins'] += 1
                                    elif pnl < 0:
                                        regime_stats[r]['losses'] += 1
                            except:
                                pass
                                
                    # Calc rates
                    for r, stats in regime_stats.items():
                        total = stats['count']
                        if total > 0:
                            stats['win_rate'] = (stats['wins'] / total) * 100
                            
                    enhanced['regime_performance'] = regime_stats
                    # DEBUG: Print final stats
                    enhanced['regime_performance'] = regime_stats
                    # DEBUG: Print final stats
                    # print(f"DEBUG: Final Regime Stats: {regime_stats}")
                    
            except Exception as e:
                print(f"Error calculating context/regime metrics: {e}")
                enhanced['regime_performance'] = {}
                enhanced['avg_atr'] = 0
                enhanced['avg_adx'] = 0

            # === GO/NO-GO Criteria ===
            try:
                criteria_result = evaluate_go_nogo(enhanced)
                enhanced['criteria_result'] = {
                    'status': criteria_result.status,
                    'reasons': criteria_result.reasons,
                    'warnings': criteria_result.warnings
                }
            except Exception as e:
                print(f"Error evaluating GO/NO-GO: {e}")
                enhanced['criteria_result'] = None
            
        except Exception as e:
            print(f"Error in _calculate_enhanced_metrics: {e}")
        
        return enhanced
