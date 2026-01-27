import sqlite3
import pandas as pd
import logging
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from pathlib import Path

from app.strategies.combos.proximity_analyzer import ProximityAnalyzer
from app.strategies.combos.combo_strategy import ComboStrategy
from app.services.combo_service import ComboService
from src.data.incremental_loader import IncrementalLoader
from app.database import DB_PATH

logger = logging.getLogger(__name__)

class OpportunityService:
    """
    Service to manage Strategy Favorites and calculate Opportunities (Proximity to Signal).
    Reads from existing favorite_strategies table.
    """

    def __init__(self, db_path: str = None):
        if db_path is None:
            # Use the canonical DB path from app.database
            db_path = str(DB_PATH)
        self.db_path = db_path
        self.loader = IncrementalLoader()
        self.combo_service = ComboService(db_path)
        self.analyzer = ProximityAnalyzer()

    def get_favorites(self) -> List[Dict[str, Any]]:
        """List all favorites from existing table."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Query existing favorite_strategies table
        cursor.execute("""
            SELECT id, name, symbol, timeframe, strategy_name, parameters, notes
            FROM favorite_strategies
        """)
        rows = cursor.fetchall()
        
        favorites = []
        for row in rows:
            r = dict(row)
            # Parse parameters JSON if string
            if isinstance(r['parameters'], str):
                try:
                    r['parameters'] = json.loads(r['parameters'])
                except Exception as e:
                    logger.warning(f"Failed to parse parameters JSON for favorite {r.get('id')}: {e}")
                    r['parameters'] = {}
            favorites.append(r)
        
        logger.info(f"Loaded {len(favorites)} favorite strategies from database")
        for fav in favorites:
            logger.debug(f"  - ID {fav['id']}: {fav['symbol']} {fav['timeframe']} - {fav['strategy_name']}")
            
        conn.close()
        return favorites

    def get_opportunities(self) -> List[Dict[str, Any]]:
        """
        Analyze all favorites and return their current status (is_holding, distance_to_next_status).
        
        IMPORTANT: Buy/sell rules (entry_logic and exit_logic) are loaded dynamically from database:
        - Template metadata is fetched from combo_templates table
        - entry_logic (buy rule) and exit_logic (sell rule) come from template_data JSON field
        - Each favorite strategy uses its own template's rules from the database
        """
        favorites = self.get_favorites()
        opportunities = []
        
        logger.info(f"Processing {len(favorites)} favorite strategies")
        
        # Cache for data to avoid refetching same symbol/timeframe
        data_cache = {}
        
        # Track skipped strategies for debugging
        skipped_strategies = []

        for fav in favorites:
            try:
                symbol = fav['symbol']
                tf = fav['timeframe']
                template_name = fav['strategy_name']
                params = fav['parameters']
                
                logger.debug(f"Processing strategy {fav['id']}: {symbol} {tf} - {template_name}")
                
                # 1. Fetch Data (1D usually)
                # 1. Fetch Data (1D usually)
                cache_key = f"{symbol}_{tf}"
                if cache_key not in data_cache:
                    # Calculate start date (e.g. 500 days ago to be safe for EMA 200)
                    start_date = (datetime.now() - timedelta(days=500)).strftime("%Y-%m-%d")
                    
                    # Fetching enough data for indicators (e.g. 200 candles)
                    df = self.loader.fetch_data(
                        symbol=symbol,
                        timeframe=tf,
                        since_str=start_date,
                        limit=None 
                    )
                    data_cache[cache_key] = df
                
                df = data_cache[cache_key].copy()
                
                if df.empty:
                    logger.warning(f"Strategy {fav['id']} ({symbol} {tf}): No data available (df.empty)")
                    logger.warning(f"  This may indicate: 1) Symbol not available on exchange, 2) Cache file is empty/corrupt, 3) Network/API issue")
                    skipped_strategies.append({
                        'id': fav['id'],
                        'symbol': symbol,
                        'timeframe': tf,
                        'reason': 'No data available (df.empty) - Check if symbol is valid or cache needs refresh'
                    })
                    continue

                # 2. Get Template Metadata from Database (entry_logic and exit_logic)
                # This dynamically loads the buy/sell rules from combo_templates table
                meta = self.combo_service.get_template_metadata(template_name)
                if not meta:
                    logger.warning(f"Strategy {fav['id']} ({symbol} {tf}): Template '{template_name}' not found")
                    skipped_strategies.append({
                        'id': fav['id'],
                        'symbol': symbol,
                        'timeframe': tf,
                        'template_name': template_name,
                        'reason': f"Template '{template_name}' not found"
                    })
                    continue
                
                # Metadata is already flattened (contains indicators, entry_logic, exit_logic from DB)
                template_data = meta
                
                # 3. Merge Saved Params into Template Data
                # We need to inject params into indicators to make sure we use the favorited settings
                indicators = template_data.get('indicators', [])
                
                # Create a deep copy of indicators to modify
                # Helper to update indicator params based on alias/name matching
                final_indicators = []
                for ind in indicators:
                    ind_new = ind.copy()
                    ind_new['params'] = ind_new.get('params', {}).copy()
                    
                    alias = ind_new.get('alias', '')
                    ind_type = ind_new.get('type', '').lower()
                    
                    # Debug: Log indicator info for SOL
                    if symbol == 'SOL/USDT':
                        logger.info(f"SOL/USDT - Processing indicator: alias={alias}, type={ind_type}, current_params={ind_new['params']}")
                    
                    # Improved parameter mapping logic
                    # Supports formats: ema_short, sma_medium, sma_long, etc.
                    for pk, pv in params.items():
                        if pk == 'stop_loss':
                            continue
                            
                        pk_lower = pk.lower()
                        matched = False
                        
                        # 1. Exact alias match (e.g., pk='short', alias='short')
                        if pk == alias:
                            matched = True
                        # 2. Format: type_alias (e.g., pk='ema_short', type='ema', alias='short')
                        # Also match if param has different type prefix but same alias (e.g., ema_short matches sma with alias short)
                        elif ind_type and alias:
                            expected_format = f"{ind_type}_{alias}"
                            # Match exact format
                            if pk_lower == expected_format.lower():
                                matched = True
                            # Also match if alias matches even if type differs (e.g., ema_short matches sma_short)
                            elif pk_lower.endswith(f"_{alias}") or pk_lower.startswith(f"{alias}_"):
                                matched = True
                        # 3. Alias contained in param key (e.g., pk='ema_short', alias='short')
                        elif alias and alias.lower() in pk_lower:
                            matched = True
                        # 4. Param key contained in alias (less common, but possible)
                        elif alias and pk_lower in alias.lower():
                            matched = True
                        
                        if matched:
                            # Determine which parameter to update
                            # Most indicators use 'length' or 'period'
                            old_value = ind_new['params'].get('length') or ind_new['params'].get('period')
                            if 'length' in ind_new['params']:
                                ind_new['params']['length'] = int(pv)
                                if symbol == 'SOL/USDT':
                                    logger.info(f"SOL/USDT - Updated {alias} ({ind_type}) length from {old_value} to {pv} using param {pk}")
                            elif 'period' in ind_new['params']:
                                ind_new['params']['period'] = int(pv)
                                if symbol == 'SOL/USDT':
                                    logger.info(f"SOL/USDT - Updated {alias} ({ind_type}) period from {old_value} to {pv} using param {pk}")
                            else:
                                # Fallback: try to infer the main parameter
                                # For most indicators, 'length' is the default
                                ind_new['params']['length'] = int(pv)
                                if symbol == 'SOL/USDT':
                                    logger.info(f"SOL/USDT - Updated {alias} ({ind_type}) length (fallback) to {pv} using param {pk}")
                                
                    final_indicators.append(ind_new)
                
                # Debug: Log final indicators for SOL
                if symbol == 'SOL/USDT':
                    logger.info(f"SOL/USDT - Final indicators config:")
                    for ind in final_indicators:
                        logger.info(f"  - {ind.get('alias')} ({ind.get('type')}): {ind.get('params')}")
                
                # 4. Instantiate Strategy with rules from database
                # entry_logic and exit_logic come from combo_templates.template_data (JSON field)
                sl_param = params.get('stop_loss', template_data.get('stop_loss', 0.0))
                
                # Extract buy/sell rules dynamically from database template
                entry_logic = template_data.get('entry_logic', '')  # Buy rule from DB
                exit_logic = template_data.get('exit_logic', '')    # Sell rule from DB
                
                strategy = ComboStrategy(
                    indicators=final_indicators,
                    entry_logic=entry_logic,  # Dynamic buy rule from database
                    exit_logic=exit_logic,    # Dynamic sell rule from database
                    stop_loss=float(sl_param),
                )
                
                df_with_inds = strategy.calculate_indicators(df)
                
                # Debug: Log indicator values for SOL if symbol matches
                if symbol == 'SOL/USDT':
                    last_row = df_with_inds.iloc[-1]
                    logger.info(f"SOL/USDT - Last row (current candle) indicators: {[k for k in last_row.index if k not in ['open', 'high', 'low', 'close', 'volume', 'timestamp']]}")
                    # Log specific indicators if they exist
                    for ind_name in ['ema_short', 'sma_medium', 'sma_long', 'short', 'medium', 'long']:
                        if ind_name in last_row:
                            logger.info(f"SOL/USDT - {ind_name} (current): {last_row[ind_name]}")
                    logger.info(f"SOL/USDT - close (current): {last_row['close']}")
                    logger.info(f"SOL/USDT - entry_logic: {strategy.entry_logic}")
                    logger.info(f"SOL/USDT - params used: {params}")
                
                # 5. Analyze Entry Proximity using buy rule from database
                # Use CURRENT candle (last row) for distance calculation to match TradingView
                # This ensures the distance shown matches what the user sees on TradingView
                df_current = df_with_inds.iloc[-1:].copy()  # Current candle for distance
                df_closed = df_with_inds.iloc[:-1].copy()  # Closed candles for signal detection
                
                # Debug: Log current candle values for SOL
                if symbol == 'SOL/USDT' and not df_current.empty:
                    current_row = df_current.iloc[-1]
                    logger.info(f"SOL/USDT - Current candle (for distance calc) indicators:")
                    for ind_name in ['short', 'medium', 'long']:
                        if ind_name in current_row:
                            logger.info(f"SOL/USDT - {ind_name} (current): {current_row[ind_name]}")
                    logger.info(f"SOL/USDT - close (current): {current_row['close']}")
                
                # Check if short is above medium (entry condition) BEFORE analyzing
                # NEW CONCEPT: HOLD is determined by short > medium (not short > long)
                current_row = df_current.iloc[-1] if not df_current.empty else None
                short_above_medium = False
                if current_row is not None and 'short' in current_row and 'medium' in current_row:
                    short_val = current_row['short']
                    medium_val = current_row['medium']
                    short_above_medium = short_val > medium_val
                
                # Also check short > long for reference
                short_above_long = False
                if current_row is not None and 'short' in current_row and 'long' in current_row:
                    short_val = current_row['short']
                    long_val = current_row['long']
                    short_above_long = short_val > long_val
                
                # Analyze proximity to entry signal using CURRENT candle (matches TradingView)
                analysis = self.analyzer.analyze(df_current, strategy.entry_logic)
                
                # But verify signal on closed candles (stable signals only)
                if not df_closed.empty:
                    signal_analysis = self.analyzer.analyze(df_closed, strategy.entry_logic)
                    if signal_analysis.get('status') == 'SIGNAL':
                        # Signal confirmed on closed candle, but use current distance
                        analysis['status'] = 'SIGNAL'
                        analysis['badge'] = 'success'
                        analysis['message'] = 'Signal Active'
                        analysis['distance'] = 0.0
                
                # Debug: Log analysis result for SOL
                if symbol == 'SOL/USDT':
                    logger.info(f"SOL/USDT - Analysis result: status={analysis.get('status')}, distance={analysis.get('distance')}, message={analysis.get('message')}")
                    # Calculate manual distance for BOTH crossovers to verify
                    if not df_current.empty:
                        current_row = df_current.iloc[-1]
                        if 'short' in current_row and 'long' in current_row and 'medium' in current_row:
                            short_val = current_row['short']
                            long_val = current_row['long']
                            medium_val = current_row['medium']
                            
                            # Distance to cross UP long
                            dist_to_long = (long_val - short_val) / abs(long_val) * 100 if short_val < long_val else 0
                            # Distance to cross UP medium
                            dist_to_medium = (medium_val - short_val) / abs(medium_val) * 100 if short_val < medium_val else 0
                            
                            # The minimum distance (closest crossover)
                            min_dist = min(dist_to_long, dist_to_medium) if dist_to_long > 0 and dist_to_medium > 0 else (dist_to_long if dist_to_long > 0 else dist_to_medium)
                            
                            logger.info(f"SOL/USDT - Manual distance calc:")
                            logger.info(f"  - CROSS_UP long: ({long_val:.4f} - {short_val:.4f}) / {long_val:.4f} * 100 = {dist_to_long:.2f}%")
                            logger.info(f"  - CROSS_UP medium: ({medium_val:.4f} - {short_val:.4f}) / {medium_val:.4f} * 100 = {dist_to_medium:.2f}%")
                            logger.info(f"  - Minimum distance (closest): {min_dist:.2f}%")
                
                # -------------------------------------------------------------------------
                # NEW CONCEPT: HOLD status is determined ONLY by entry conditions being met
                # If short > medium (entry conditions satisfied), we ARE in HOLD
                # Stop loss is NOT used to determine HOLD status - it's just historical info
                # -------------------------------------------------------------------------
                
                # Determine if holding based ONLY on entry conditions (short > medium)
                # Ignore stop loss history - if conditions are met NOW, we're in HOLD
                is_holding = short_above_medium
                
                # Run backtest logic on closed candles for reference (but don't use for HOLD determination)
                df_signals = strategy.generate_signals(df_closed)
                
                # Find the LAST confirmed signal (1=Buy, -1=Sell/Stop) - for reference only
                last_sig_idx = df_signals[df_signals['signal'] != 0].last_valid_index()
                last_signal_val = 0
                if last_sig_idx is not None:
                     last_signal_val = df_signals.loc[last_sig_idx, 'signal']
                
                # Debug for TRX
                if symbol == 'TRX/USDT':
                    logger.info(f"TRX/USDT - short_above_medium={short_above_medium}, is_holding={is_holding} (based on short > medium, ignoring stop loss)")
                    if current_row is not None:
                        if 'short' in current_row and 'medium' in current_row:
                            logger.info(f"TRX/USDT - Current candle: short={current_row['short']:.4f}, medium={current_row['medium']:.4f}")
                        if 'short' in current_row and 'long' in current_row:
                            logger.info(f"TRX/USDT - short={current_row['short']:.4f}, long={current_row['long']:.4f}")
                
                # Debug for ETH
                if symbol == 'ETH/USDT':
                    logger.info(f"ETH/USDT - short_above_medium={short_above_medium}, is_holding={is_holding} (based on short > medium, ignoring stop loss)")
                    if current_row is not None:
                        if 'short' in current_row and 'medium' in current_row:
                            logger.info(f"ETH/USDT - short={current_row['short']:.4f}, medium={current_row['medium']:.4f}")
                        if 'short' in current_row and 'long' in current_row:
                            logger.info(f"ETH/USDT - short={current_row['short']:.4f}, long={current_row['long']:.4f}")
                
                # -------------------------------------------------------------------------
                # With new concept: is_holding is already determined by short_above_long
                # No need for special cases - if short > long, we're in HOLD
                # Stop loss history is ignored for HOLD determination
                # -------------------------------------------------------------------------
                
                # Removed: Complex logic checking stop loss history
                # Now: Simple - if short > long, we're in HOLD
                
                # (Old complex logic removed - not needed with new concept)
                if False:  # This block is disabled with new concept
                    # Check if entry logic would be satisfied on current candle
                    # For entry_logic like: (crossover(short, long) | crossover(short, medium)) & (short > long)
                    # If short > long is True, we need to check if there was a recent crossover
                    
                    # Check previous closed candle to see if short was below long
                    if not df_closed.empty and len(df_closed) > 0:
                        prev_closed_row = df_closed.iloc[-1]
                        if 'short' in prev_closed_row and 'long' in prev_closed_row:
                            prev_short = prev_closed_row['short']
                            prev_long = prev_closed_row['long']
                            prev_short_above_long = prev_short > prev_long
                            
                            # If previous candle had short <= long, but current has short > long,
                            # it means we crossed over on current candle -> we're in HOLD
                            if not prev_short_above_long and short_above_long:
                                # Crossover happened on current candle -> we're in HOLD
                                is_holding = True
                                if symbol == 'TRX/USDT':
                                    logger.info(f"TRX/USDT - Crossover detected on current candle! prev: short={prev_short:.4f} <= long={prev_long:.4f}, current: short={current_row['short']:.4f} > long={current_row['long']:.4f}")
                                    logger.info(f"TRX/USDT - Setting is_holding=True because entry happened on current candle")
                            elif prev_short_above_long and short_above_long:
                                # Both previous and current have short > long
                                # Check how many candles ago was the last stop
                                if last_sig_idx is not None and last_sig_idx in df_closed.index:
                                    try:
                                        last_stop_pos = df_closed.index.get_loc(last_sig_idx)
                                        current_date_pos = len(df_closed) - 1
                                        candles_since_stop = current_date_pos - last_stop_pos
                                        
                                        # If stop was recent (within last few candles) and we're still above,
                                        # we might have re-entered. Check if there was a crossover after stop
                                        if candles_since_stop > 0 and candles_since_stop <= 10:  # Within last 10 candles
                                            # Check if short was below long right after stop, then crossed
                                            # Look for crossover after stop
                                            after_stop_df = df_closed.iloc[last_stop_pos+1:]
                                            if len(after_stop_df) > 0:
                                                # Check if there was a period where short was below long after stop
                                                had_crossover = False
                                                for idx, row in after_stop_df.iterrows():
                                                    if 'short' in row and 'long' in row:
                                                        if row['short'] <= row['long']:
                                                            had_crossover = True  # Found a period where short was below
                                                            break
                                                
                                                # If we had short below after stop, but now we're above, we crossed -> HOLD
                                                if had_crossover or candles_since_stop == 1:
                                                    is_holding = True
                                                    if symbol == 'TRX/USDT':
                                                        logger.info(f"TRX/USDT - short > long maintained since stop ({candles_since_stop} candles ago), assuming re-entry -> is_holding=True")
                                    except (KeyError, IndexError) as e:
                                        if symbol == 'TRX/USDT':
                                            logger.warning(f"TRX/USDT - Error checking candles since stop: {e}")
                
                # -------------------------------------------------------------------------
                # With new concept: if short > long, we're already in HOLD (is_holding = True)
                # No need for STOPPED_OUT or MISSED_ENTRY statuses when short > long
                # All cases where short > long are treated as HOLD
                # -------------------------------------------------------------------------
                
                # Standardize Entry Status Names for frontend clarity
                # BUT: If we're in HOLD, set status to HOLDING
                if is_holding:
                    analysis['status'] = 'HOLDING'
                    analysis['badge'] = 'info'
                elif analysis['status'] == 'SIGNAL':
                    analysis['status'] = 'BUY_SIGNAL'
                elif analysis['status'] == 'NEAR':
                    analysis['status'] = 'BUY_NEAR'
                
                # -------------------------------------------------------------------------
                # NEW: Stateful Check (Stop Loss / Confirmed Signals)
                # Proximity Analyzer is stateless (doesn't know if we hit -5% SL logic).
                # We assume "HOLDING" if Proximity says so, BUT we must check if strategy killed it.
                # -------------------------------------------------------------------------
                
                # Override Logic: REMOVED with new concept
                # We no longer check stop loss history to determine HOLD status
                # HOLD is determined ONLY by short > long (entry conditions met)
                if False:  # Disabled - not needed with new concept
                    # If the Sell was on the very last closed candle, it's an EXIT SIGNAL (Actionable)
                    if last_sig_idx == df_closed.index[-1]:
                         analysis['status'] = 'EXIT_SIGNAL'
                         analysis['badge'] = 'critical'
                         # Show Re-entry Distance (calculated by ProximityAnalyzer for Entry Logic)
                         re_entry_dist = analysis.get('distance', 0.0)
                         analysis['message'] = f'EXIT: Stop Loss Dist: {re_entry_dist}%'
                         # Keep the distance to show proximity to re-entry
                         pass
                    else:
                         # If Sell was older, we are effectively WAITING (Neutral), not Holding.
                         # Unless Proximity sees a NEW Buy Signal right now.
                         if analysis['status'] == 'HOLDING': 
                             analysis['status'] = 'NEUTRAL'
                             analysis['badge'] = 'neutral'
                             re_entry_dist = analysis.get('distance', 0.0)
                             analysis['message'] = f'Waiting (Re-entry Dist: {re_entry_dist}%)'
                             # Preserve distance logic
                             pass

                # 6. Secondary Analysis: Exit Proximity using sell rule from database
                # Only check exit if we are technically Holding (is_holding == True)
                # This is critical: when in HOLD, we need to show distance to EXIT, not to entry
                if is_holding:
                     if strategy.exit_logic:  # exit_logic comes from database (combo_templates.template_data)
                         # Use df_closed here too for consistency
                         # Analyze proximity to exit signal using exit_logic from database
                         exit_analysis = self.analyzer.analyze(df_closed, strategy.exit_logic)
                         
                         # LOGIC CHANGE: If we are HOLDING, the relevant distance is ALWAYS the Exit Distance.
                         # Even if it's NEUTRAL (not < 1%), we want to see "Distance to Sell", not "Distance to Buy" (which is history).
                         
                         # 1. Critical/Warning: Exit is NEAR or SIGNAL
                         if exit_analysis['status'] in ['SIGNAL', 'NEAR']:
                             analysis['status'] = 'EXIT_NEAR' if exit_analysis['status'] == 'NEAR' else 'EXIT_SIGNAL'
                             analysis['badge'] = 'critical' if exit_analysis['status'] == 'SIGNAL' else 'warning'
                             analysis['message'] = f"EXIT: {exit_analysis['message']}"
                             analysis['distance'] = exit_analysis.get('distance')
                             analysis['exit_details'] = exit_analysis
                             if isinstance(analysis.get('details'), dict):
                                analysis['details']['exit_analysis'] = exit_analysis
                        
                             # 2. Informational: Exit is NEUTRAL (Far away), but we are HOLDING
                         else:
                             # We're in HOLD, exit is not near, but we still want to show exit distance
                             # Keep status as HOLDING, but update specific details to reflect Exit focus
                             # Use the Exit distance
                             exit_dist = exit_analysis.get('distance', 999)
                             analysis['distance'] = exit_dist if exit_dist < 999 else None
                             # Update message to be clear we are tracking exit
                             if exit_dist < 999:
                                 analysis['message'] = f"Em Hold. Distância para saída: {exit_dist:.2f}%"
                             else:
                                 analysis['message'] = "Em Hold. Aguardando sinal de saída."
                             analysis['exit_details'] = exit_analysis 
                             # Safety: Ensure details is not overwritten or accessed incorrectly if string
                             if isinstance(analysis.get('details'), dict):
                                 analysis['details']['exit_analysis'] = exit_analysis
                             else:
                                 # Convert string detail to dict if needed, or just ignore
                                 pass
                     else:
                         # No exit_logic defined, but we're in HOLD
                         # Set a default message
                         analysis['status'] = 'HOLDING'
                         analysis['badge'] = 'info'
                         analysis['message'] = "Em Hold. Sem regra de saída definida."
                         if symbol in ['ETH/USDT', 'TRX/USDT']:
                             logger.info(f"{symbol} - In HOLD but no exit_logic defined")
                
                # is_holding was already determined above based on short_above_long
                # With new concept, we don't use STOPPED_OUT or MISSED_ENTRY when short > long
                # All cases where short > long are treated as HOLD
                is_stopped_out = False  # Disabled with new concept
                is_missed_entry = False  # Disabled with new concept
                
                # Calculate distance to next status
                # If holding: distance to exit, else: distance to entry
                if is_holding:
                    # Use exit analysis if available (from step 6)
                    if 'exit_details' in analysis and analysis.get('exit_details'):
                        exit_details = analysis['exit_details']
                        if isinstance(exit_details, dict):
                            distance_to_next = exit_details.get('distance', 999)
                        else:
                            distance_to_next = analysis.get('distance', 999)
                    elif 'distance' in analysis:
                        # Fallback: use distance from analysis (might be entry distance, but better than nothing)
                        distance_to_next = analysis.get('distance', 999)
                    else:
                        distance_to_next = 999
                    next_status_label = "exit"
                elif is_stopped_out or is_missed_entry:
                    # For stopped out or missed entry, use the spread distance we calculated
                    distance_to_next = analysis.get('distance', None)
                    if is_stopped_out:
                        next_status_label = "re-entry"
                    else:
                        next_status_label = "confirmation"
                else:
                    # Distance to entry (from entry analysis)
                    distance_to_next = analysis.get('distance', 999)
                    next_status_label = "entry"
                
                # Ensure distance is always a number (not None) for sorting and display
                final_distance = None
                if distance_to_next is not None and distance_to_next < 999:
                    final_distance = round(distance_to_next, 2)
                elif is_stopped_out or is_missed_entry:
                    # For stopped out/missed entry, use the spread distance we calculated
                    final_distance = analysis.get('distance')
                    if final_distance is not None:
                        final_distance = round(final_distance, 2)
                
                opportunities.append({
                    'id': fav['id'],
                    'symbol': symbol,
                    'timeframe': tf,
                    'template_name': template_name,
                    'name': fav['name'], # User custom name
                    'notes': fav.get('notes'),
                    'is_holding': is_holding,
                    'distance_to_next_status': final_distance,
                    'next_status_label': next_status_label,
                    # Keep legacy fields for backward compatibility
                    'status': analysis['status'],
                    'badge': analysis['badge'],
                    'message': analysis['message'],
                    'details': analysis,
                    'last_price': float(df.iloc[-1]['close']),
                    'timestamp': str(df.index[-1])
                })
                
            except Exception as e:
                import traceback
                logger.error(f"Error analyzing favorite {fav.get('id', 'unknown')} ({fav.get('symbol', 'unknown')} {fav.get('timeframe', 'unknown')}): {e}")
                logger.error(traceback.format_exc())
                skipped_strategies.append({
                    'id': fav.get('id', 'unknown'),
                    'symbol': fav.get('symbol', 'unknown'),
                    'timeframe': fav.get('timeframe', 'unknown'),
                    'reason': f"Exception: {str(e)}"
                })
                continue

        # Sort by distance to next status (closest first)
        # Holding positions first, then by distance
        opportunities.sort(key=lambda x: (
            0 if x['is_holding'] else 1,  # Holding first
            x['distance_to_next_status'] if x['distance_to_next_status'] is not None else 999
        ))
        
        # Log summary
        logger.info(f"Successfully processed {len(opportunities)} strategies out of {len(favorites)} favorites")
        if skipped_strategies:
            logger.warning(f"Skipped {len(skipped_strategies)} strategies:")
            for skipped in skipped_strategies:
                logger.warning(f"  - ID {skipped['id']}: {skipped.get('symbol', 'unknown')} {skipped.get('timeframe', 'unknown')} - {skipped['reason']}")
        
        return opportunities
