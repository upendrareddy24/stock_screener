"""
Triple API Client - FMP Primary, Twelve Data Secondary, Yahoo Finance Final Fallback

Uses Financial Modeling Prep API as primary source with automatic
fallback to Twelve Data, then Yahoo Finance if both fail.
"""

import os
import requests
import time
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import yfinance as yf
import pandas as pd
from api_optimizer import APICache, APIRateLimiter


class TripleAPIClient:
    """
    Triple API client with three-tier fallback system.
    
    Tier 1 - FMP: 250 calls/day (primary)
    Tier 2 - Twelve Data: 800 calls/MONTH (~25/day conservative limit)
    Tier 3 - Yahoo Finance: Unlimited, FREE (final fallback)
    
    Includes aggressive caching and rate limiting to preserve paid API quotas.
    """
    
    def __init__(self, fmp_api_key: str, twelve_data_key: str,
                 cache_ttl_minutes: Dict[str, int] = None):
        self.fmp_key = fmp_api_key
        self.twelve_key = twelve_data_key
        
        # Separate caches for each API
        self.cache = APICache(cache_file="api_cache.json")
        
        # Rate limiters
        self.fmp_limiter = APIRateLimiter(
            max_calls_per_day=250,  # FMP free tier: 250/day
            max_calls_per_minute=10,
            usage_file="fmp_usage.json"
        )
        # Twelve Data: 800 calls/MONTH (not per day!)
        # Conservative limit: ~26 calls/day to avoid exhausting monthly quota
        self.twelve_limiter = APIRateLimiter(
            max_calls_per_day=25,  # Conservative: 800/month ≈ 25/day
            max_calls_per_minute=5,  # Also reduce per-minute to be safe
            usage_file="twelve_usage.json"
        )
        
        # Cache TTL - More aggressive to preserve Twelve Data's monthly quota
        self.cache_ttl = cache_ttl_minutes or {
            "1min": 2,   # 2 min cache for 1min data (was 1)
            "5min": 5,   # 5 min cache for 5min data (was 3)
            "15min": 15, # 15 min cache for 15min data (was 10)
        }
        
        self.stats = {
            "fmp_calls": 0,
            "twelve_calls": 0,
            "yahoo_calls": 0,
            "cache_hits": 0,
            "errors": 0
        }
    
    def _interval_to_fmp(self, interval: str) -> str:
        """Convert interval to FMP format"""
        mapping = {
            "1min": "1min",
            "5min": "5min",
            "15min": "15min",
            "30min": "30min",
            "1h": "1hour",
            "1hour": "1hour",
        }
        return mapping.get(interval, "5min")
    
    def _fetch_from_fmp(self, symbol: str, interval: str, 
                        outputsize: int = 120) -> Optional[List[Dict]]:
        """Fetch candles from FMP API"""
        try:
            if not self.fmp_limiter.can_make_call():
                print(f"[FMP] Rate limit reached, falling back to Twelve Data")
                return None
            
            fmp_interval = self._interval_to_fmp(interval)
            
            # FMP historical intraday endpoint
            url = f"https://financialmodelingprep.com/api/v3/historical-chart/{fmp_interval}/{symbol}"
            params = {
                "apikey": self.fmp_key
            }
            
            resp = requests.get(url, params=params, timeout=10)
            data = resp.json()
            
            self.fmp_limiter.record_call()
            self.stats["fmp_calls"] += 1
            
            if isinstance(data, dict) and "Error Message" in data:
                print(f"[FMP Error] {symbol}: {data['Error Message']}")
                return None
            
            if not isinstance(data, list) or len(data) == 0:
                return None
            
            # FMP returns newest first, reverse to oldest first
            data = list(reversed(data[:outputsize]))
            
            # Convert FMP format to standard format
            converted = []
            for candle in data:
                converted.append({
                    "datetime": candle.get("date", ""),
                    "open": str(candle.get("open", 0)),
                    "high": str(candle.get("high", 0)),
                    "low": str(candle.get("low", 0)),
                    "close": str(candle.get("close", 0)),
                    "volume": str(candle.get("volume", 0))
                })
            
            print(f"[FMP SUCCESS] {symbol} {interval} - {self.fmp_limiter.get_remaining_calls()} calls remaining")
            return converted
            
        except Exception as e:
            print(f"[FMP Error] {symbol}: {e}")
            self.stats["errors"] += 1
            return None
    
    def _fetch_from_twelve(self, symbol: str, interval: str,
                          outputsize: int = 120) -> Optional[List[Dict]]:
        """Fetch candles from Twelve Data API (backup)"""
        try:
            if not self.twelve_limiter.can_make_call():
                print(f"[TwelveData] Rate limit reached")
                return None
            
            url = "https://api.twelvedata.com/time_series"
            params = {
                "symbol": symbol,
                "interval": interval,
                "outputsize": outputsize,
                "apikey": self.twelve_key,
                "order": "ASC",
            }
            
            resp = requests.get(url, params=params, timeout=10)
            data = resp.json()
            
            self.twelve_limiter.record_call()
            self.stats["twelve_calls"] += 1
            
            if isinstance(data, dict) and data.get("status") == "error":
                print(f"[TwelveData Error] {symbol}: {data.get('message')}")
                return None
            
            values = data.get("values", [])
            if not values:
                return None
            
            print(f"[TwelveData BACKUP] {symbol} {interval} - {self.twelve_limiter.get_remaining_calls()} calls remaining")
            return values
            
        except Exception as e:
            print(f"[TwelveData Error] {symbol}: {e}")
            self.stats["errors"] += 1
            return None
    
    def _interval_to_yahoo(self, interval: str) -> str:
        """Convert interval to Yahoo Finance format"""
        mapping = {
            "1min": "1m",
            "5min": "5m",
            "15min": "15m",
            "30min": "30m",
            "1h": "1h",
            "1hour": "1h",
        }
        return mapping.get(interval, "5m")
    
    def _fetch_from_yahoo(self, symbol: str, interval: str,
                         outputsize: int = 120) -> Optional[List[Dict]]:
        """Fetch candles from Yahoo Finance (free, unlimited fallback)"""
        try:
            yahoo_interval = self._interval_to_yahoo(interval)
            
            # Calculate period based on interval and outputsize
            # Yahoo Finance uses period (1d, 5d, 1mo, etc.)
            if interval in ["1min", "5min"]:
                period = "5d"  # 5 days for intraday
            elif interval == "15min":
                period = "1mo"  # 1 month for 15min
            else:
                period = "3mo"  # 3 months for longer intervals
            
            # Download data using yfinance
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period, interval=yahoo_interval)
            
            if df is None or df.empty:
                print(f"[Yahoo Finance] No data for {symbol}")
                return None
            
            # Take last outputsize candles
            df = df.tail(outputsize)
            
            # Convert to standard format
            converted = []
            for idx, row in df.iterrows():
                converted.append({
                    "datetime": idx.strftime("%Y-%m-%d %H:%M:%S"),
                    "open": str(row["Open"]),
                    "high": str(row["High"]),
                    "low": str(row["Low"]),
                    "close": str(row["Close"]),
                    "volume": str(int(row["Volume"]))
                })
            
            self.stats["yahoo_calls"] += 1
            print(f"[Yahoo Finance] {symbol} {interval} - FREE unlimited")
            return converted
            
        except Exception as e:
            print(f"[Yahoo Finance Error] {symbol}: {e}")
            self.stats["errors"] += 1
            return None
    
    def fetch_candles(self, symbol: str, interval: str,
                     outputsize: int = 120) -> Optional[List[Dict]]:
        """
        Fetch candles with three-tier fallback: FMP → Twelve Data → Yahoo Finance.
        Returns list of candle dicts or None if all three fail.
        """
        # Try cache first
        cached = self.cache.get(symbol, interval)
        if cached is not None:
            self.stats["cache_hits"] += 1
            print(f"[Cache HIT] {symbol} {interval}")
            return cached
        
        # Try FMP first
        data = self._fetch_from_fmp(symbol, interval, outputsize)
        
        # Tier 2: Fallback to Twelve Data if FMP fails
        if data is None:
            print(f"⚠️  [Tier 2 Fallback] FMP failed for {symbol}, trying Twelve Data (LIMITED MONTHLY QUOTA)")
            data = self._fetch_from_twelve(symbol, interval, outputsize)
        
        # Tier 3: Final fallback to Yahoo Finance if both fail
        if data is None:
            print(f"🆓 [Tier 3 Fallback] Both FMP and Twelve Data failed for {symbol}, using Yahoo Finance (FREE)")
            data = self._fetch_from_yahoo(symbol, interval, outputsize)
        
        # Cache if successful
        if data:
            ttl_minutes = self.cache_ttl.get(interval, 5)
            self.cache.set(symbol, interval, data, ttl_minutes * 60)
        
        return data
    
    def get_stats(self) -> Dict:
        """Get combined API usage statistics"""
        fmp_stats = self.fmp_limiter.get_usage_stats()
        twelve_stats = self.twelve_limiter.get_usage_stats()
        
        total_api_calls = self.stats["fmp_calls"] + self.stats["twelve_calls"] + self.stats["yahoo_calls"]
        
        return {
            "fmp": fmp_stats,
            "twelve_data": twelve_stats,
            "yahoo_finance": {
                "calls_used": self.stats["yahoo_calls"],
                "limit": "unlimited",
                "cost": "FREE"
            },
            "session": self.stats,
            "total_api_calls": total_api_calls,
            "cache_hit_rate": (self.stats["cache_hits"] / max(1, self.stats["cache_hits"] + total_api_calls)) * 100
        }
    
    def clear_cache(self):
        """Clear all cached data"""
        self.cache.cache = {}
        self.cache._save_cache()
        print("[Cache] Cleared all cache")


# Backward compatibility alias
DualAPIClient = TripleAPIClient

# Example usage
if __name__ == "__main__":
    client = TripleAPIClient(
        fmp_api_key="test_fmp",
        twelve_data_key="test_twelve"
    )
    
    print("Triple API Client initialized")
    print("Tier 1: FMP (250 calls/day)")
    print("Tier 2: Twelve Data (800 calls/MONTH - ~25/day limit)")
    print("Tier 3: Yahoo Finance (unlimited, FREE)")
