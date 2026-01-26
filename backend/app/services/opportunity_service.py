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
            SELECT id, name, symbol, timeframe, strategy_name, parameters
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
                except:
                    r['parameters'] = {}
            favorites.append(r)
            
        conn.close()
        return favorites

    def get_opportunities(self) -> List[Dict[str, Any]]:
        """
        Analyze all favorites and return their current status (SIGNAL, NEAR, NEUTRAL).
        """
        favorites = self.get_favorites()
        opportunities = []
        
        # Cache for data to avoid refetching same symbol/timeframe
        data_cache = {}

        for fav in favorites:
            try:
                symbol = fav['symbol']
                tf = fav['timeframe']
                template_name = fav['strategy_name']
                params = fav['parameters']
                
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
                    continue

                # 2. Get Template Metadata (for logic structure)
                meta = self.combo_service.get_template_metadata(template_name)
                if not meta:
                    logger.warning(f"Template {template_name} not found for favorite {fav['id']}")
                    continue
                
                # Metadata is already flattened (contains indicators, entry_logic, etc.)
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
                    
                    alias = ind_new.get('alias')
                    # If we find a parameter key that matches alias or is relevant
                    # E.g. fav params: {'ema_short': 9, 'ema_long': 21}
                    # Indicator alias: 'ema_short'
                    
                    alias = ind_new.get('alias')
                    # If we find a parameter key that matches alias or is relevant
                    # E.g. fav params: {'ema_short': 9, 'ema_long': 21}
                    # Indicator alias: 'short'
                    
                    for pk, pv in params.items():
                        # match exact alias OR alias contained in param key (e.g. 'short' in 'ema_short')
                        # OR param key contained in alias
                        if pk == alias or (alias and alias in pk):
                            # Heuristic: Update 'length' or specific param?
                            # Most indicators use 'length'. MACD uses fast/slow.
                            # We can try to map simplistic ones.
                            if 'length' in ind_new['params']:
                                ind_new['params']['length'] = int(pv)
                            elif 'media_curta' in pk or 'media_longa' in pk:
                                ind_new['params']['length'] = int(pv)
                                
                    final_indicators.append(ind_new)
                
                # 4. Instantiate Strategy
                # FIX: Use user parameter for stop_loss if available, else template default
                sl_param = params.get('stop_loss', template_data.get('stop_loss', 0.0))
                
                strategy = ComboStrategy(
                    indicators=final_indicators,
                    entry_logic=template_data.get('entry_logic', ''),
                    exit_logic=template_data.get('exit_logic', ''),
                    stop_loss=float(sl_param),
                )
                
                df_with_inds = strategy.calculate_indicators(df)
                
                # 5. Analyze Entry Proximity
                # User Request: Monitor Close Candles Only (Stable Signals)
                df_closed = df_with_inds.iloc[:-1].copy()
                
                analysis = self.analyzer.analyze(df_closed, strategy.entry_logic)
                
                # Standardize Entry Status Names for frontend clarity
                if analysis['status'] == 'SIGNAL':
                    analysis['status'] = 'BUY_SIGNAL'
                elif analysis['status'] == 'NEAR':
                    analysis['status'] = 'BUY_NEAR'
                
                # -------------------------------------------------------------------------
                # NEW: Stateful Check (Stop Loss / Confirmed Signals)
                # Proximity Analyzer is stateless (doesn't know if we hit -5% SL logic).
                # We assume "HOLDING" if Proximity says so, BUT we must check if strategy killed it.
                # -------------------------------------------------------------------------
                
                # Run backtest logic on closed candles to see the 'State'
                df_signals = strategy.generate_signals(df_closed)
                
                # Find the LAST confirmed signal (1=Buy, -1=Sell/Stop)
                last_sig_idx = df_signals[df_signals['signal'] != 0].last_valid_index()
                last_signal_val = 0
                if last_sig_idx is not None:
                     last_signal_val = df_signals.loc[last_sig_idx, 'signal']
                
                # Override Logic:
                # If Last Signal was SELL (-1), we are NOT Holding, regardless of what Proximity says.
                if last_signal_val == -1:
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

                # 6. Secondary Analysis: Exit Proximity (Portfolio Tracker Mode)
                # Only check exit if we are technically Holding AND Strategy confirms we haven't stopped out (last_signal != -1)
                # Or if we blindly follow Proximity for Buy Signals (which are new entries).
                if analysis['status'] in ['HOLDING', 'BUY_SIGNAL', 'BUY_NEAR']:
                     if strategy.exit_logic:
                         # Use df_closed here too for consistency
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
                         elif analysis['status'] == 'HOLDING':
                             # Keep status as HOLDING (Blue), but update specific details to reflect Exit focus
                             # Use the Exit distance
                             analysis['distance'] = exit_analysis.get('distance')
                             # Update message to be clear we are tracking exit
                             # exit_analysis['message'] might be "Waiting for setup" or "Approaching...".
                             # Let's be explicit
                             analysis['message'] = f"Holding (Exit Dist: {analysis['distance']}%)"
                             analysis['exit_details'] = exit_analysis 
                             # Safety: Ensure details is not overwritten or accessed incorrectly if string
                             if isinstance(analysis.get('details'), dict):
                                 analysis['details']['exit_analysis'] = exit_analysis
                             else:
                                 # Convert string detail to dict if needed, or just ignore
                                 pass
                
                opportunities.append({
                    'id': fav['id'],
                    'symbol': symbol,
                    'timeframe': tf,
                    'template_name': template_name,
                    'name': fav['name'], # User custom name
                    'status': analysis['status'],
                    'badge': analysis['badge'],
                    'message': analysis['message'],
                    'details': analysis,
                    'last_price': float(df.iloc[-1]['close']),
                    'timestamp': str(df.index[-1])
                })
                
            except Exception as e:
                logger.error(f"Error analyzing favorite {fav['id']}: {e}")
                continue

        # Sort by Priority: EXIT -> BUY -> HOLDING
        priority_map = {
            'EXIT_SIGNAL': 0, 
            'BUY_SIGNAL': 1, 
            'EXIT_NEAR': 2, 
            'BUY_NEAR': 3, 
            'HOLDING': 4,
            'NEUTRAL': 90, 
            'ERROR': 99
        }
        opportunities.sort(key=lambda x: priority_map.get(x['status'], 50))
        
        return opportunities
