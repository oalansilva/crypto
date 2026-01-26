import pandas as pd
import numpy as np
import re
from typing import Dict, Any, List, Optional

class ProximityAnalyzer:
    """
    Analyzes strategy logic to determine 'Proximity' to a signal.
    
    Classifies status as:
    - SIGNAL: Logic is currently True
    - NEAR: Logic is False, but within threshold distance (e.g. < 0.5%)
    - NEUTRAL: Far from signal
    """

    def __init__(self, threshold_pct: float = 0.01):
        """
        Args:
            threshold_pct: Distance threshold to consider 'NEAR' (default 1% = 0.01)
        """
        self.threshold = threshold_pct

    def analyze(self, df: pd.DataFrame, entry_logic: str) -> Dict[str, Any]:
        """
        Analyze the latest candle in the DataFrame against the entry logic.
        
        Args:
            df: DataFrame with all indicators calculated (last row used)
            entry_logic: The boolean expression string (e.g. "close > ema_short")
            
        Returns:
            Dict with keys: status (SIGNAL|NEAR|NEUTRAL), details (dist %), missing_condition
        """
        if df.empty:
            return {
                'status': 'NEUTRAL',
                'badge': 'neutral',
                'message': 'No Data',
                'distance': 0.0,
                'details': 'No Data'
            }

        # Pre-process 'crossover(a, b)' function calls
        crossover_rx = re.compile(r'crossover\(\s*(\w+)\s*,\s*(\w+)\s*\)')
        crossunder_rx = re.compile(r'crossunder\(\s*(\w+)\s*,\s*(\w+)\s*\)')
        
        def replace_crossover(match):
            v1, v2 = match.groups()
            if len(df) < 2: return "False"
            try:
                curr, prev = df.iloc[-1], df.iloc[-2]
                if v1 not in curr or v2 not in curr: return "False"
                crossed = (prev[v1] <= prev[v2]) and (curr[v1] > curr[v2])
                return str(crossed)
            except: return "False"

        def replace_crossunder(match):
            v1, v2 = match.groups()
            if len(df) < 2: return "False"
            try:
                curr, prev = df.iloc[-1], df.iloc[-2]
                if v1 not in curr or v2 not in curr: return "False"
                # Crossunder: Prev A >= Prev B  AND  Curr A < Curr B
                crossed = (prev[v1] >= prev[v2]) and (curr[v1] < curr[v2])
                return str(crossed)
            except: return "False"

        # Apply replacements
        processed_logic = crossover_rx.sub(replace_crossover, entry_logic)
        processed_logic = crossunder_rx.sub(replace_crossunder, processed_logic)

        # Get latest row
        last_row = df.iloc[-1]
        
        # 1. Check if SIGNAL is Active NOW
        # We wrap the logic in try/except because eval can fail
        try:
            # Evaluate logic on the Series (row) - requires variables in local scope
            # We convert row to dict for eval context
            context = last_row.to_dict()
            is_signal = eval(processed_logic, {}, context)
            
            if is_signal:
                return {
                    'status': 'SIGNAL', 
                    'badge': 'success',
                    'message': 'Signal Active',
                    'distance': 0.0
                }
        except Exception as e:
            return {
                'status': 'ERROR', 
                'badge': 'error',
                'message': f"Logic Eval Error: {str(e)}",
                'distance': 0.0
            }

        # 2. Check Proximity (Heuristic Parsing)
        # We look for Simple Comparisons: A > B or A < B
        # Regex to capture: (var1) (>|<|>=|<=) (var2)
        # We ignore complex AND/OR for proximity for now, focusing on the first failed condition?
        # A simple approach: Parse all comparisons, find the 'closest' one that is FALSE.
        
        conditions = self._extract_comparisons(entry_logic)
        
        min_distance = float('inf')
        nearest_condition = None
        
        for cond in conditions:
            left, op, right = cond
            
            try:
                # Get values from last_row
                val_left = float(last_row[left]) if left in last_row else float(left)
                val_right = float(last_row[right]) if right in last_row else float(right)
                
                # Check if this specific condition is met
                is_met = self._check_condition(val_left, op, val_right)
                
                if not is_met:
                    # Directional Validation for CrossOver
                    # If waiting for CROSS_UP (Left crosses over Right), we must be BELOW Right currently.
                    # If Left > Right, we are technically "past" the cross (or crossed down and valid? no crossover implies low->high).
                    # Actually, if Left > Right, we are NOT approaching a crossover, we are diverging or holding.
                    if op == 'CROSS_UP' and val_left > val_right:
                             # Calculate spread/distance for context
                             if val_right == 0: dist = 0.0
                             else: dist = abs(val_left - val_right) / abs(val_right)
                             
                             return {
                                'status': 'HOLDING',
                                'badge': 'info',
                                'message': f"In Uptrend ({left}: {val_left:.4f} > {right}: {val_right:.4f})",
                                'distance': round(dist * 100, 2),
                                'details': 'Trend Active'
                             }

                    if op == 'CROSS_DOWN' and val_left < val_right:
                        # ACTIVE DOWNTREND (Held Short or Past Exit)
                        # If checking Exit Proximity, "Past Exit" means we are safe below ??
                        # Actually, if Exit is CROSS_DOWN (Price crosses below MA),
                        # and we are BELOW (Left < Right), then signal triggers or triggered.
                        # Holding state for SHORT is fine.
                        if 'HOLDING' not in str(nearest_condition):
                             if val_right == 0: dist = 0.0
                             else: dist = abs(val_left - val_right) / abs(val_right)
                             
                             return {
                                'status': 'HOLDING',
                                'badge': 'info',
                                'message': f"In Downtrend ({left}: {val_left:.4f} < {right}: {val_right:.4f})",
                                'distance': round(dist * 100, 2),
                                'details': 'Trend Active'
                             }

                    # Calculate distance
                    # Dist = abs(Left - Right) / Right
                    if val_right == 0:
                        dist = 0 
                    else:
                        dist = abs(val_left - val_right) / abs(val_right)
                    
                    if dist < min_distance:
                        min_distance = dist
                        # Format message based on OP
                        if op == 'CROSS_UP':
                             nearest_condition = f"{left}: {val_left:.4f} crossing UP {right}: {val_right:.4f}"
                        elif op == 'CROSS_DOWN':
                             nearest_condition = f"{left}: {val_left:.4f} crossing DOWN {right}: {val_right:.4f}"
                        else:
                             nearest_condition = f"{left}: {val_left:.4f} {op} {right}: {val_right:.4f}"

            except Exception:
                continue # Skip unparseable (e.g. strict boolean columns)

        # 3. Determine Status
        if min_distance <= self.threshold:
            return {
                'status': 'NEAR',
                'badge': 'warning', # Yellow
                'message': f"Approaching {nearest_condition}",
                'distance': round(min_distance * 100, 2)
            }
        else:
             return {
                'status': 'NEUTRAL',
                'badge': 'neutral', # Grey
                'message': 'Waiting for setup',
                'distance': round(min_distance * 100, 2) if min_distance != float('inf') else None
            }

    def _extract_comparisons(self, logic: str) -> List[tuple]:
        """
        Extracts simple comparisons from logic string.
        Returns list of (left, operator, right).
        Also handles "crossover(A, B)" by mapping to special operator 'CROSS_UP'.
        """
        results = []
        
        # 1. Capture crossover(A, B) -> CROSS_UP
        co_rx = re.compile(r'crossover\(\s*(\w+)\s*,\s*(\w+)\s*\)')
        for match in co_rx.finditer(logic):
            results.append((match.group(1), 'CROSS_UP', match.group(2)))

        # 1b. Capture crossunder(A, B) -> CROSS_DOWN
        cu_rx = re.compile(r'crossunder\(\s*(\w+)\s*,\s*(\w+)\s*\)')
        for match in cu_rx.finditer(logic):
            results.append((match.group(1), 'CROSS_DOWN', match.group(2)))

        # 2. Standard Comparisons
        clean_logic = logic.replace('(', '').replace(')', '')
        parts = re.split(r'\s+(?:AND|OR|&|\|)\s+', clean_logic, flags=re.IGNORECASE)
        rx = re.compile(r'(\w+)\s*(>|<|>=|<=|==)\s*(\w+)')
        
        for p in parts:
            match = rx.search(p.strip())
            if match:
                results.append(match.groups())
                
        return results

    def _check_condition(self, val_left, op, val_right):
        if op == '>': return val_left > val_right
        if op == '<': return val_left < val_right
        if op == '>=': return val_left >= val_right
        if op == '<=': return val_left <= val_right
        if op == '==': return val_left == val_right
        return False
