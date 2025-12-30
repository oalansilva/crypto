import pandas as pd
import pandas_ta as ta
import inspect
import json

def get_indicators_metadata():
    metadata = {}
    
    # Common categories in pandas_ta
    categories = ['momentum', 'overlap', 'trend', 'volatility', 'volume']
    
    # We can also get list of all indicators from df.ta.indicators(as_list=True) if updated
    # But getting them by category is safer for grouping
    
    # pandas_ta attaches methods to DataFrame as ta.<method> extension
    # But for introspection, we might check the module or the strategy class
    
    # Let's try to inspect the DataFrame extension methods directly
    df = pd.DataFrame()
    
    # Get all attributes of df.ta that are callable
    # Note: df.ta is an accessor.
    
    # pandas_ta exposes .indicators() but it prints.
    # Let's use the underlying module structure if possible.
    
    # Actually, let's just inspect the ta module for functions that are indicators.
    # ta.rsi, ta.sma, etc.
    
    for name in dir(ta):
        func = getattr(ta, name)
        if callable(func) and not name.startswith('_'):
            # Filter somewhat... pandas_ta has many utility functions.
            # Best way is to use category maps if available.
            pass

    # Better approach: Iterate known categories if exposed
    if hasattr(ta, 'Category'):
        print("Categories found:", ta.Category)
    
    # Let's try introspecting RSI
    sig = inspect.signature(ta.rsi)
    print(f"RSI Signature: {sig}")
    
    # Serialize params
    params = []
    for param_name, param in sig.parameters.items():
        if param_name in ['close', 'open', 'high', 'low', 'volume']: continue # Data inputs
        if param_name in ['kwargs', 'talib']: continue
        
        default = param.default if param.default != inspect.Parameter.empty else None
        p_type = str(param.annotation) if param.annotation != inspect.Parameter.empty else "any"
        
        params.append({
            "name": param_name,
            "default": default,
            "type": p_type
        })
        
    print(f"RSI Params: {json.dumps(params, indent=2)}")

get_indicators_metadata()
