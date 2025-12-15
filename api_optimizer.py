"""
API Optimization Module

Strategies to stay within Twelve Data's 800 calls/day limit:
1. Intelligent caching with TTL
2. Rate limiting and throttling
3. Batch API requests
4. Priority-based scanning
5. Usage tracking and monitoring
"""

import os
import json
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import requests
from dataclasses import dataclass, asdict


@dataclass
class CachedData:
    """Cached candle data with metadata"""
    symbol: str
    interval: str
    data: List[Dict]
    timestamp: float
    ttl_seconds: int
    
    def is_expired(self) -> bool:
        """Check if cache entry has expired"""
        return time.time() - self.timestamp > self.ttl_seconds


class APICache:
    """Cache for API responses with TTL"""
    
    def __init__(self, cache_file: str = "api_cache.json"):
        self.cache_file = cache_file
        self.cache: Dict[str, CachedData] = self._load_cache()
    
    def _load_cache(self) -> Dict[str, CachedData]:
        """Load cache from file"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    data = json.load(f)
                    return {
                        k: CachedData(**v) for k, v in data.items()
                    }
            except Exception as e:
                print(f"[Cache] Error loading cache: {e}")
                return {}
        return {}
    
    def _save_cache(self):
        """Save cache to file"""
        try:
            data = {k: asdict(v) for k, v in self.cache.items()}
            with open(self.cache_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"[Cache] Error saving cache: {e}")
    
    def get_cache_key(self, symbol: str, interval: str) -> str:
        """Generate cache key"""
        return f"{symbol}_{interval}"
    
    def get(self, symbol: str, interval: str) -> Optional[List[Dict]]:
        """Get cached data if not expired"""
        key = self.get_cache_key(symbol, interval)
        if key in self.cache:
            cached = self.cache[key]
            if not cached.is_expired():
                return cached.data
            else:
                # Remove expired entry
                del self.cache[key]
                self._save_cache()
        return None
    
    def set(self, symbol: str, interval: str, data: List[Dict], ttl_seconds: int):
        """Cache data with TTL"""
        key = self.get_cache_key(symbol, interval)
        self.cache[key] = CachedData(
            symbol=symbol,
            interval=interval,
            data=data,
            timestamp=time.time(),
            ttl_seconds=ttl_seconds
        )
        self._save_cache()
    
    def clear_expired(self):
        """Remove all expired entries"""
        expired_keys = [
            k for k, v in self.cache.items() if v.is_expired()
        ]
        for key in expired_keys:
            del self.cache[key]
        if expired_keys:
            self._save_cache()
            print(f"[Cache] Cleared {len(expired_keys)} expired entries")


class APIRateLimiter:
    """Rate limiter to prevent hitting API limits"""
    
    def __init__(self, max_calls_per_day: int = 800, 
                 max_calls_per_minute: int = 8,
                 usage_file: str = "api_usage.json"):
        self.max_calls_per_day = max_calls_per_day
        self.max_calls_per_minute = max_calls_per_minute
        self.usage_file = usage_file
        self.usage = self._load_usage()
        self.minute_calls = []
    
    def _load_usage(self) -> Dict:
        """Load usage tracking"""
        if os.path.exists(self.usage_file):
            try:
                with open(self.usage_file, 'r') as f:
                    return json.load(f)
            except:
                return self._init_usage()
        return self._init_usage()
    
    def _init_usage(self) -> Dict:
        """Initialize usage tracking"""
        return {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "calls": 0,
            "last_reset": datetime.now().isoformat()
        }
    
    def _save_usage(self):
        """Save usage tracking"""
        with open(self.usage_file, 'w') as f:
            json.dump(self.usage, f, indent=2)
    
    def _reset_if_new_day(self):
        """Reset counter if it's a new day"""
        today = datetime.now().strftime("%Y-%m-%d")
        if self.usage["date"] != today:
            self.usage = self._init_usage()
            self._save_usage()
            print(f"[RateLimit] Reset daily counter for {today}")
    
    def can_make_call(self) -> bool:
        """Check if we can make an API call"""
        self._reset_if_new_day()
        
        # Check daily limit
        if self.usage["calls"] >= self.max_calls_per_day:
            return False
        
        # Check per-minute limit
        now = time.time()
        self.minute_calls = [t for t in self.minute_calls if now - t < 60]
        if len(self.minute_calls) >= self.max_calls_per_minute:
            return False
        
        return True
    
    def wait_if_needed(self):
        """Wait if rate limit would be exceeded"""
        while not self.can_make_call():
            # Check daily limit
            if self.usage["calls"] >= self.max_calls_per_day:
                remaining = self._time_until_reset()
                print(f"[RateLimit] Daily limit reached ({self.usage['calls']}/{self.max_calls_per_day})")
                print(f"[RateLimit] Waiting {remaining} until reset...")
                time.sleep(min(300, remaining))  # Wait max 5 min at a time
                self._reset_if_new_day()
            else:
                # Per-minute limit
                print(f"[RateLimit] Per-minute limit reached, waiting 10s...")
                time.sleep(10)
    
    def _time_until_reset(self) -> int:
        """Seconds until daily reset (midnight)"""
        now = datetime.now()
        tomorrow = now + timedelta(days=1)
        midnight = datetime(tomorrow.year, tomorrow.month, tomorrow.day)
        return int((midnight - now).total_seconds())
    
    def record_call(self):
        """Record an API call"""
        self._reset_if_new_day()
        self.usage["calls"] += 1
        self.minute_calls.append(time.time())
        self._save_usage()
    
    def get_remaining_calls(self) -> int:
        """Get remaining calls for today"""
        self._reset_if_new_day()
        return max(0, self.max_calls_per_day - self.usage["calls"])
    
    def get_usage_stats(self) -> Dict:
        """Get usage statistics"""
        self._reset_if_new_day()
        return {
            "date": self.usage["date"],
            "calls_used": self.usage["calls"],
            "calls_remaining": self.get_remaining_calls(),
            "limit": self.max_calls_per_day,
            "usage_pct": (self.usage["calls"] / self.max_calls_per_day) * 100
        }


class OptimizedAPIClient:
    """Optimized API client with caching and rate limiting"""
    
    def __init__(self, api_key: str, cache_ttl_minutes: Dict[str, int] = None):
        self.api_key = api_key
        self.cache = APICache()
        self.rate_limiter = APIRateLimiter()
        
        # Default cache TTL by interval
        self.cache_ttl = cache_ttl_minutes or {
            "1min": 1,      # 1 minute cache for 1min data
            "5min": 3,      # 3 minute cache for 5min data
            "15min": 10,    # 10 minute cache for 15min data
            "30min": 20,
            "1h": 30,
        }
    
    def fetch_candles(self, symbol: str, interval: str, 
                     outputsize: int = 120) -> Optional[List[Dict]]:
        """
        Fetch candles with caching and rate limiting
        Returns list of candle dicts or None if error
        """
        # Try cache first
        cached = self.cache.get(symbol, interval)
        if cached is not None:
            print(f"[Cache HIT] {symbol} {interval}")
            return cached
        
        # Check if we can make API call
        if not self.rate_limiter.can_make_call():
            print(f"[RateLimit] Cannot fetch {symbol} - limit reached")
            return None
        
        # Wait if needed (throttle)
        self.rate_limiter.wait_if_needed()
        
        # Make API call
        try:
            url = "https://api.twelvedata.com/time_series"
            params = {
                "symbol": symbol,
                "interval": interval,
                "outputsize": outputsize,
                "apikey": self.api_key,
                "order": "ASC",
            }
            
            resp = requests.get(url, params=params, timeout=10)
            data = resp.json()
            
            # Record the call
            self.rate_limiter.record_call()
            
            if isinstance(data, dict) and data.get("status") == "error":
                print(f"[API Error] {symbol}: {data.get('message', 'Unknown')}")
                return None
            
            values = data.get("values", [])
            if not values:
                return None
            
            # Cache the result
            ttl_minutes = self.cache_ttl.get(interval, 5)
            self.cache.set(symbol, interval, values, ttl_minutes * 60)
            
            print(f"[API CALL] {symbol} {interval} - {self.rate_limiter.get_remaining_calls()} calls remaining")
            
            return values
            
        except Exception as e:
            print(f"[API Error] {symbol}: {e}")
            return None
    
    def get_stats(self) -> Dict:
        """Get API usage statistics"""
        return self.rate_limiter.get_usage_stats()
    
    def clear_cache(self):
        """Clear all cached data"""
        self.cache.cache = {}
        self.cache._save_cache()
        print("[Cache] Cleared all cache")


def prioritize_symbols(symbols: List[str], max_symbols: int = None) -> List[str]:
    """
    Prioritize symbols for scanning based on liquidity/importance
    Returns prioritized list, optionally limited to max_symbols
    """
    # Define priority tiers (higher = more important)
    priority_map = {
        # Mega cap tech
        "AAPL": 100, "MSFT": 100, "GOOGL": 100, "AMZN": 100, "NVDA": 100,
        "META": 100, "TSLA": 100,
        
        # Major indices
        "SPY": 95, "QQQ": 95, "IWM": 90, "DIA": 90,
        
        # High volume tech
        "AMD": 85, "INTC": 80, "AVGO": 80, "ORCL": 75,
        
        # Popular stocks
        "NFLX": 80, "COIN": 75, "PLTR": 75, "CRWD": 70,
    }
    
    # Sort by priority (high to low), then alphabetically
    sorted_symbols = sorted(
        symbols,
        key=lambda s: (priority_map.get(s, 50), s),
        reverse=True
    )
    
    if max_symbols:
        return sorted_symbols[:max_symbols]
    
    return sorted_symbols


# Example usage
if __name__ == "__main__":
    # Test the optimized client
    client = OptimizedAPIClient(api_key="test_key")
    
    print("API Usage Stats:")
    stats = client.get_stats()
    for k, v in stats.items():
        print(f"  {k}: {v}")
