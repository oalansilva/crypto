"""
Exchange Service for fetching market data from exchanges.
Handles caching to optimize performance and reduce API calls.
"""
import ccxt
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional


class ExchangeService:
    """Service to interact with cryptocurrency exchanges via ccxt."""

    CACHE_DIR = Path("data")
    CACHE_FILE = CACHE_DIR / "symbols_cache.json"
    TIMEFRAMES_CACHE_FILE = CACHE_DIR / "timeframes_cache.json"
    CACHE_DURATION_HOURS = 24
    
    def __init__(self):
        self.exchange = ccxt.binance()
    
    def fetch_binance_symbols(self) -> List[str]:
        """
        Fetch all available USDT trading pairs from Binance.
        Uses local cache if available and valid (< 24h old).
        
        Returns:
            List of symbol strings (e.g., ['BTC/USDT', 'ETH/USDT', ...])
        """
        # Check cache first
        if self._is_cache_valid():
            return self._load_from_cache()
        
        # Fetch from API
        symbols = self._fetch_from_api()
        
        # Save to cache
        self._save_to_cache(symbols)
        
        return symbols
    
    def _is_cache_valid(self) -> bool:
        """Check if cache file exists and is not expired."""
        if not self.CACHE_FILE.exists():
            return False
        
        try:
            with open(self.CACHE_FILE, 'r') as f:
                cache_data = json.load(f)
            
            cached_time = datetime.fromisoformat(cache_data.get('timestamp', ''))
            expiry_time = cached_time + timedelta(hours=self.CACHE_DURATION_HOURS)
            
            return datetime.now() < expiry_time
        except (json.JSONDecodeError, ValueError, KeyError):
            return False
    
    def _load_from_cache(self) -> List[str]:
        """Load symbols from cache file."""
        with open(self.CACHE_FILE, 'r') as f:
            cache_data = json.load(f)
        return cache_data.get('symbols', [])
    
    def _fetch_from_api(self) -> List[str]:
        """Fetch symbols from Binance API and filter for USDT pairs."""
        print("📡 Fetching symbols from Binance API...")
        markets = self.exchange.load_markets()
        
        # Filter for USDT pairs only
        usdt_symbols = [
            symbol for symbol in markets.keys()
            if symbol.endswith('/USDT')
        ]
        
        print(f"✅ Found {len(usdt_symbols)} USDT trading pairs")
        return sorted(usdt_symbols)
    
    def fetch_binance_timeframes(self) -> List[str]:
        """Fetch supported timeframes from Binance via ccxt (cached)."""

        if self._is_timeframes_cache_valid():
            return self._load_timeframes_from_cache()

        # ccxt exposes supported timeframes
        try:
            tfs = sorted(list((self.exchange.timeframes or {}).keys()))
        except Exception:
            tfs = []

        # Keep only the common ones we actually support in the UI/backtester
        preferred = ["1m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d", "3d", "1w"]
        if tfs:
            tfs = [tf for tf in preferred if tf in tfs]
        else:
            tfs = preferred

        self._save_timeframes_to_cache(tfs)
        return tfs

    def _is_timeframes_cache_valid(self) -> bool:
        if not self.TIMEFRAMES_CACHE_FILE.exists():
            return False
        try:
            with open(self.TIMEFRAMES_CACHE_FILE, "r") as f:
                cache_data = json.load(f)
            cached_time = datetime.fromisoformat(cache_data.get("timestamp", ""))
            expiry_time = cached_time + timedelta(hours=self.CACHE_DURATION_HOURS)
            return datetime.now() < expiry_time
        except Exception:
            return False

    def _load_timeframes_from_cache(self) -> List[str]:
        with open(self.TIMEFRAMES_CACHE_FILE, "r") as f:
            cache_data = json.load(f)
        return cache_data.get("timeframes", [])

    def _save_timeframes_to_cache(self, timeframes: List[str]) -> None:
        self.CACHE_DIR.mkdir(exist_ok=True)
        cache_data = {
            "timestamp": datetime.now().isoformat(),
            "timeframes": timeframes,
            "count": len(timeframes),
        }
        with open(self.TIMEFRAMES_CACHE_FILE, "w") as f:
            json.dump(cache_data, f, indent=2)

    def _save_to_cache(self, symbols: List[str]) -> None:
        """Save symbols to cache file with timestamp."""
        self.CACHE_DIR.mkdir(exist_ok=True)

        cache_data = {
            'timestamp': datetime.now().isoformat(),
            'symbols': symbols,
            'count': len(symbols)
        }

        with open(self.CACHE_FILE, 'w') as f:
            json.dump(cache_data, f, indent=2)

        print(f"💾 Cached {len(symbols)} symbols to {self.CACHE_FILE}")
