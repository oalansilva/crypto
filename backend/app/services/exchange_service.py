"""
Exchange Service for fetching market data from exchanges.
Handles caching to optimize performance and reduce API calls.
"""
import ccxt
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict


class ExchangeService:
    """Service to interact with cryptocurrency exchanges via ccxt."""
    
    CACHE_DIR = Path("data")
    CACHE_FILE = CACHE_DIR / "symbols_cache.json"
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
