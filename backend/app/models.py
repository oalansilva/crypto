# file: backend/app/models.py
from sqlalchemy import Column, String, Float, Boolean, JSON, DateTime, Numeric, Text
# from sqlalchemy.dialects.postgresql import UUID, JSONB  <-- Remove Postgres types
from app.database import Base
from sqlalchemy import TypeDecorator
import uuid
import json

# Compatibility types for SQLite
class JSONType(TypeDecorator):
    impl = Text
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        
        # simple helper to handle NaN/Inf and Numpy types
        def safe_serialize(obj):
            import math
            import numpy as np
            if isinstance(obj, (np.integer, np.int64, np.int32)):
                return int(obj)
            if isinstance(obj, (np.floating, np.float64, np.float32)):
                val = float(obj)
                if math.isnan(val) or math.isinf(val):
                    return None
                return val
            if isinstance(obj, float):
                if math.isnan(obj) or math.isinf(obj):
                    return None
                return obj
            if isinstance(obj, dict):
                return {k: safe_serialize(v) for k, v in obj.items()}
            if isinstance(obj, list):
                return [safe_serialize(v) for v in obj]
            return obj

        try:
            cleaned = safe_serialize(value)
            return json.dumps(cleaned)
        except Exception as e:
            # Fallback for debugging
            print(f"JSON Serialization error: {e}")
            return json.dumps(value, default=str)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        # SQLite might return float/int directly if affinity matches
        if isinstance(value, (dict, list, int, float, bool)):
            return value
        try:
            return json.loads(value)
        except (TypeError, json.JSONDecodeError):
            # Fallback for weird cases or if it's a plain string
            return value

class UUIDType(TypeDecorator):
    impl = String
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return uuid.UUID(value)

# Use conditional types based on DB engine? No, keep it simple for now. 
# We'll use these custom types which work on both (String/Text are universal).
# Ideally we'd check dialect but for MVP SQLite local is fine.

class BacktestRun(Base):
    __tablename__ = "backtest_runs"

    id = Column(UUIDType, primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime, default=None) # handled by app or server_default
    status = Column(Text, nullable=False)
    mode = Column(Text, nullable=False)
    
    exchange = Column(Text, nullable=False)
    symbol = Column(Text, nullable=False)
    timeframe = Column(Text, nullable=False)
    since = Column(String, nullable=True) # Store ISO string in simple DBs
    until = Column(String)
    full_period = Column(Boolean, default=False)
    
    strategies = Column(JSONType, nullable=False)
    params = Column(JSONType)
    
    fee = Column(Float, default=0.001)
    slippage = Column(Float, default=0.0005)
    cash = Column(Float, default=10000)
    stop_pct = Column(JSONType)
    take_pct = Column(JSONType)
    fill_mode = Column(Text, default='close')
    
    error_message = Column(Text)

class BacktestResult(Base):
    __tablename__ = "backtest_results"

    run_id = Column(UUIDType, primary_key=True)
    result_json = Column(JSONType, nullable=False)
    metrics_summary = Column(JSONType)
    updated_at = Column(DateTime)
