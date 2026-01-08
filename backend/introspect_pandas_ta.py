"""
Script to introspect pandas-ta and discover all available indicators with their parameters.
This will help us auto-generate indicator schemas.
"""

import pandas as pd
import pandas_ta as ta
import inspect
from typing import get_type_hints

def introspect_pandas_ta():
    """Discover all pandas-ta indicators and their parameters."""
    
    print("Pandas-TA Indicator Introspection")
    print("="*60)
    
    # Get all functions from pandas_ta module
    all_functions = [name for name in dir(ta) if not name.startswith('_')]
    
    # Filter to likely indicator functions (exclude classes, constants, etc.)
    indicator_functions = []
    for name in all_functions:
        obj = getattr(ta, name)
        if callable(obj) and not inspect.isclass(obj):
            indicator_functions.append(name)
    
    print(f"\nTotal callable functions: {len(indicator_functions)}")
    
    # Sample indicators to introspect
    sample_indicators = ['ema', 'sma', 'rsi', 'macd', 'bbands', 'atr', 'adx', 'stoch', 'cci']
    
    results = {}
    
    for indicator_name in sample_indicators:
        if indicator_name in indicator_functions:
            print(f"\n{'='*60}")
            print(f"Indicator: {indicator_name.upper()}")
            print(f"{'='*60}")
            
            try:
                indicator_func = getattr(ta, indicator_name)
                
                # Get function signature
                sig = inspect.signature(indicator_func)
                
                print(f"\nFunction signature:")
                print(f"  {indicator_name}{sig}")
                
                params_info = {}
                print(f"\nParameters:")
                for param_name, param in sig.parameters.items():
                    default = param.default
                    if default == inspect.Parameter.empty:
                        default_str = "REQUIRED"
                    else:
                        default_str = str(default)
                    
                    params_info[param_name] = {
                        'default': default if default != inspect.Parameter.empty else None,
                        'required': default == inspect.Parameter.empty
                    }
                    print(f"  - {param_name}: {default_str}")
                
                results[indicator_name] = params_info
                
                # Try to get docstring
                if indicator_func.__doc__:
                    doc_lines = [line.strip() for line in indicator_func.__doc__.strip().split('\n') if line.strip()][:3]
                    print(f"\nDocstring (first 3 lines):")
                    for line in doc_lines:
                        print(f"  {line}")
                        
            except Exception as e:
                print(f"  Error introspecting {indicator_name}: {e}")
    
    # Print summary
    print(f"\n\n{'='*60}")
    print("SUMMARY: Common Parameter Patterns")
    print(f"{'='*60}")
    
    for ind_name, params in results.items():
        param_names = list(params.keys())
        print(f"{ind_name:12s}: {', '.join(param_names)}")
    
    # List all available indicators
    print(f"\n\n{'='*60}")
    print(f"All {len(indicator_functions)} available indicators:")
    print(f"{'='*60}")
    for i, ind in enumerate(sorted(indicator_functions), 1):
        if i % 5 == 0:
            print(f"{ind:15s}")
        else:
            print(f"{ind:15s}", end="")

if __name__ == "__main__":
    introspect_pandas_ta()

