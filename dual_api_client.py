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
    Triple API Client with three-tier fallback system (Plus Alpha Vantage).
    
    Tier 1 - FMP: 250 calls/day (primary)
    Tier 2 - Twelve Data: 800 calls/MONTH (~25/day conservative limit)
    Tier 3 - Alpha Vantage: 25 calls/DAY (fallback)
    Tier 4 - Yahoo Finance: Unlimited, FREE (final fallback)
    """
    
    def __init__(self, fmp_api_key: str, twelve_data_key: str, alpha_vantage_key: str = None,
                 cache_ttl_minutes: Dict[str, int] = None):
        self.fmp_key = fmp_api_key
        self.twelve_key = twelve_data_key
        self.alpha_key = alpha_vantage_key
        
        # Separate caches for each API
        self.cache = APICache(cache_file="api_cache.json")
        
        # Rate limiters
        self.fmp_limiter = APIRateLimiter(
            max_calls_per_day=250,
            max_calls_per_minute=10,
            usage_file="fmp_usage.json"
        )
        
        self.twelve_limiter = APIRateLimiter(
            max_calls_per_day=25, 
            max_calls_per_minute=5,
            usage_file="twelve_usage.json"
        )

        # Alpha Vantage: Free tier is 25 calls/day (very strict)
        self.alpha_limiter = APIRateLimiter(
            max_calls_per_day=25,
            max_calls_per_minute=5, 
            usage_file="alpha_usage.json"
        )
        
        self.cache_ttl = cache_ttl_minutes or {
            "1min": 2,
            "5min": 5, 
            "15min": 15,
        }
        
        self.stats = {
            "fmp_calls": 0,
            "twelve_calls": 0,
            "alpha_calls": 0,
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
                print(f"[FMP] Rate limit reached, falling back")
                return None
            
            fmp_interval = self._interval_to_fmp(interval)
            url = f"https://financialmodelingprep.com/api/v3/historical-chart/{fmp_interval}/{symbol}"
            params = {"apikey": self.fmp_key}
            
            resp = requests.get(url, params=params, timeout=10)
            data = resp.json()
            
            self.fmp_limiter.record_call()
            self.stats["fmp_calls"] += 1
            
            if isinstance(data, dict) and "Error Message" in data:
                return None
            
            if not isinstance(data, list) or len(data) == 0:
                return None
            
            data = list(reversed(data[:outputsize]))
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
            
            print(f"[FMP SUCCESS] {symbol} {interval}")
            return converted
            
        except Exception as e:
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
                return None
            
            values = data.get("values", [])
            if not values:
                return None
            
            print(f"[TwelveData BACKUP] {symbol} {interval}")
            return values
            
        except Exception as e:
            self.stats["errors"] += 1
            return None

    def _fetch_from_alpha(self, symbol: str, interval: str, outputsize: int = 120) -> Optional[List[Dict]]:
        """Fetch candles from Alpha Vantage (Tier 3)"""
        if not self.alpha_key: return None
        
        try:
            if not self.alpha_limiter.can_make_call():
                print(f"[Alpha Vantage] Rate limit reached")
                return None

            # Alpha Vantage Intraday
            url = "https://www.alphavantage.co/query"
            av_interval = interval if interval in ["1min", "5min", "15min", "30min", "60min"] else "5min"
            if interval == "1hour": av_interval = "60min"

            params = {
                "function": "TIME_SERIES_INTRADAY",
                "symbol": symbol,
                "interval": av_interval,
                "apikey": self.alpha_key,
                "outputsize": "compact" # returns 100
            }

            resp = requests.get(url, params=params, timeout=15)
            data = resp.json()
            self.alpha_limiter.record_call()
            self.stats["alpha_calls"] += 1
            
            key_name = f"Time Series ({av_interval})"
            if key_name not in data:
                return None
            
            ts_data = data[key_name]
            # Convert to list
            candles = []
            for ts, vals in ts_data.items():
                candles.append({
                    "datetime": ts,
                    "open": vals["1. open"],
                    "high": vals["2. high"],
                    "low": vals["3. low"],
                    "close": vals["4. close"],
                    "volume": vals["5. volume"]
                })
            
            # AV returns newest first. Sort.
            candles.sort(key=lambda x: x["datetime"])
            candles = candles[-outputsize:]
            
            print(f"[Alpha Vantage BACKUP] {symbol} {interval}")
            return candles

        except Exception as e:
            print(f"[Alpha Vantage Error] {symbol}: {e}")
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
            if interval in ["1min", "5min"]: period = "5d"
            elif interval == "15min": period = "1mo"
            else: period = "3mo"
            
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period, interval=yahoo_interval)
            
            if df is None or df.empty: return None
            
            df = df.tail(outputsize)
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
            print(f"[Yahoo Finance] {symbol} {interval}")
            return converted
            
        except Exception as e:
            self.stats["errors"] += 1
            return None
    
    def fetch_candles(self, symbol: str, interval: str,
                     outputsize: int = 120) -> Optional[List[Dict]]:
        """
        Fetch candles with multi-tier fallback: FMP → Twelve Data → Alpha Vantage → Yahoo Finance.
        """
        cached = self.cache.get(symbol, interval)
        if cached is not None:
            self.stats["cache_hits"] += 1
            return cached
        
        # Tier 1: FMP
        data = self._fetch_from_fmp(symbol, interval, outputsize)
        
        # Tier 2: Twelve Data
        if data is None:
            data = self._fetch_from_twelve(symbol, interval, outputsize)

        # Tier 3: Alpha Vantage
        if data is None and self.alpha_key:
             print(f"⚠️ [Tier 3 Fallback] Alpha Vantage for {symbol}")
             data = self._fetch_from_alpha(symbol, interval, outputsize)
        
        # Tier 4: Yahoo Finance
        if data is None:
            print(f"🆓 [Tier 4 Fallback] Yahoo Finance for {symbol}")
            data = self._fetch_from_yahoo(symbol, interval, outputsize)
        
        if data:
            ttl_minutes = self.cache_ttl.get(interval, 5)
            self.cache.set(symbol, interval, data, ttl_minutes * 60)
        
        return data
    
    def get_stats(self) -> Dict:
        """Get combined API usage statistics"""
        return {
            "fmp": self.fmp_limiter.get_usage_stats(),
            "twelve_data": self.twelve_limiter.get_usage_stats(),
            "alpha_vantage": self.alpha_limiter.get_usage_stats(),
            "yahoo_finance": {"calls": self.stats["yahoo_calls"]},
            "total_calls": sum(self.stats.values()) - self.stats["cache_hits"] - self.stats["errors"]
        }
    
    def clear_cache(self):
        self.cache.cache = {}
        self.cache._save_cache()

# Backward compatibility alias
DualAPIClient = TripleAPIClient

if __name__ == "__main__":
    client = TripleAPIClient(fmp_api_key="test", twelve_data_key="test", alpha_vantage_key="test")
    print("Client initialized with 4 tiers.")

