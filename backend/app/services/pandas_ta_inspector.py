import pandas_ta as ta
import inspect
import typing
import numpy as np

def _simplify_type(annotation):
    """Simplifies complex type hints into string representations for JSON."""
    if annotation == inspect.Parameter.empty:
        return "any"
    
    s = str(annotation)
    
    # Handle Unions (e.g. Union[int, float])
    if "Union" in s:
        if "int" in s and "float" in s:
            return "number"
        if "int" in s:
            return "int"
        if "float" in s:
            return "float"
        if "str" in s:
            return "string"
        return "any"
    
    if "int" in s:
        return "int"
    if "float" in s:
        return "float"
    if "str" in s:
        return "string"
    if "bool" in s:
        return "bool"
        
    return "any"

def get_all_indicators_metadata():
    """
    Introspects pandas_ta to return a structured dictionary of available indicators.
    Returns:
        Dict[category_name, List[indicator_metadata]]
    """
    metadata = {}
    
    # Categories provided by pandas_ta
    # ta.Category is a dict: {'candle': [...], 'momentum': [...]}
    if not hasattr(ta, 'Category'):
        return {}

    for category, indicators in ta.Category.items():
        metadata[category] = []
        
        for name in indicators:
            if not hasattr(ta, name):
                continue
                
            func = getattr(ta, name)
            if not callable(func):
                continue
            
            try:
                sig = inspect.signature(func)
                doc = inspect.getdoc(func) or ""
                summary = doc.split('\n')[0] if doc else ""
                
                params = []
                for param_name, param in sig.parameters.items():
                    # Skip data arguments usually handled by the framework
                    if param_name in ['open', 'high', 'low', 'close', 'volume', 'time', 'kwargs', 'talib', 'offset', 'mamode', 'drift', 'scalar']:
                        # Keep mamode/scalar/drift/offset if they are crucial? 
                        # Usually offset/mamode are advanced. Let's include them as advanced or skip for now to simplify.
                        # User requested "generic parameters". Maybe include 'length' and specific ones.
                        # It is safer to Exclude only the Series inputs.
                        pass
                    
                    if param_name in ['open', 'high', 'low', 'close', 'volume']: 
                         continue
                        
                    if param_name in ['kwargs', 'talib']:
                        continue

                    # Simplify defaults
                    default = param.default
                    if default == inspect.Parameter.empty:
                        default = None
                    elif isinstance(default, (type(None), int, float, str, bool)):
                         pass
                    else:
                         default = str(default) # Fallback

                    p_type = _simplify_type(param.annotation)
                    
                    params.append({
                        "name": param_name,
                        "type": p_type,
                        "default": default
                    })
                
                metadata[category].append({
                    "id": name,
                    "name": name.upper(),
                    "category": category,
                    "description": summary,
                    "params": params
                })
            except Exception as e:
                # Skip indicators that fail inspection
                print(f"Failed to inspect {name}: {e}")
                continue
                
    return metadata
