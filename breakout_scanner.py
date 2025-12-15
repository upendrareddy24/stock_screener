"""
Tiered Breakout Scanner (Single File Version)

What this does:
- Uses Twelve Data to fetch OHLCV candles for multiple stocks.
- Applies a Wyckoff + Volume Price Analysis + EMA-trend breakout strategy:
  - Tight consolidation range over last N bars
  - Breakout above that range high
  - Volume spike vs recent average
  - Bullish breakout candle
  - Trend filter: 20 EMA > 50 EMA > 200 EMA and price above 20 EMA
- Runs on 3 tiers:
  - fast_1m: very liquid names, scanned every 1 minute
  - intraday_5m: active names, scanned every 5 minutes
  - swing_15m: broader list, scanned every 15 minutes
- Sends alerts via Telegram when a breakout is detected.

Setup:
1. pip install requests schedule python-dotenv
2. Create a .env file with:
   TWELVE_DATA_API_KEY=your_twelvedata_api_key_here
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
   TELEGRAM_CHAT_ID=your_telegram_chat_id_here
3. python breakout_scanner.py
"""

import os
import time
from dataclasses import dataclass
from typing import List, Optional, Dict

import requests
import schedule
from dotenv import load_dotenv
from stock_universe import ALL_STOCKS_1MIN, ALL_STOCKS_5MIN, ALL_STOCKS_15MIN
from enhanced_signals import (
    PositionTracker, calculate_atr, calculate_risk_metrics,
    analyze_vpa_advanced, generate_options_recommendation,
    generate_pyramid_signal, calculate_signal_strength, EnhancedSignal
)
from dual_api_client import TripleAPIClient
from alert_formatter import format_detailed_alert
from api_optimizer import prioritize_symbols

# ------------------- Load environment variables -------------------

load_dotenv()

FMP_API_KEY = os.getenv("FMP_API_KEY")
TWELVE_DATA_API_KEY = os.getenv("TWELVE_DATA_API_KEY")
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY", "LFFBABGTSL3S1295") # Default fallback if env missing
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

if not FMP_API_KEY and not TWELVE_DATA_API_KEY:
    raise RuntimeError("At least one primary API key (FMP or Twelve Data) must be set in .env file.")

USE_TELEGRAM = bool(TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID)


# ------------------- Tier configuration (comprehensive US market) -------------------

TIERS: Dict[str, Dict] = {
    "fast_1m": {
        "description": f"Ultra liquid stocks & ETFs scanned on 1m ({len(ALL_STOCKS_1MIN)} symbols)",
        "interval": "1min",
        "symbols": ALL_STOCKS_1MIN,
    },
    "intraday_5m": {
        "description": f"Large & mid cap stocks on 5m ({len(ALL_STOCKS_5MIN)} symbols)",
        "interval": "5min",
        "symbols": ALL_STOCKS_5MIN,
    },
    "swing_15m": {
        "description": f"Comprehensive market coverage on 15m ({len(ALL_STOCKS_15MIN)} symbols)",
        "interval": "15min",
        "symbols": ALL_STOCKS_15MIN,
    },
}


# ------------------- Data models -------------------

@dataclass
class Candle:
    time: str
    open: float
    high: float
    low: float
    close: float
    volume: float


@dataclass
class Signal:
    ticker: str
    interval: str
    price: float
    range_pct: float
    volume_multiple: float
    time: str
    tier: str

# Global position tracker and API client
position_tracker = None
api_client = None


# ------------------- Twelve Data helper -------------------

def fetch_candles(symbol: str, interval: str, outputsize: int = 120) -> List[Candle]:
    """
    Fetch OHLCV candles using optimized API client with caching.
    Returns list of Candle sorted oldest→newest.
    """
    global api_client
    
    # Use optimized client
    values = api_client.fetch_candles(symbol, interval, outputsize)
    
    if not values:
        return []
    
    candles: List[Candle] = []
    for v in values:
        try:
            candles.append(
                Candle(
                    time=v["datetime"],
                    open=float(v["open"]),
                    high=float(v["high"]),
                    low=float(v["low"]),
                    close=float(v["close"]),
                    volume=float(v.get("volume", 0.0)),
                )
            )
        except Exception:
            # Skip malformed row
            continue

    return candles


# ------------------- Strategy logic -------------------

def ema(series: List[float], length: int) -> float:
    """
    Simple EMA implementation.
    """
    if len(series) < length:
        return series[-1]
    k = 2 / (length + 1)
    ema_val = series[-length]
    for v in series[-length + 1:]:
        ema_val = v * k + ema_val * (1 - k)
    return ema_val


def detect_breakout(
    symbol: str,
    interval: str,
    candles: List[Candle],
    lookback_bars: int = 20,
    vol_length: int = 20,
    vol_multiplier: float = 2.0,
    max_range_pct: float = 3.0,
    min_avg_volume: float = 100_000,
) -> Optional[EnhancedSignal]:
    """
    Enhanced Wyckoff + VPA + EMA trend breakout detector.
    Returns EnhancedSignal with full analysis if conditions are met.
    """
    global position_tracker
    
    n = len(candles)
    if n < max(lookback_bars + 1, vol_length + 1, 50):
        return None

    closes = [c.close for c in candles]
    highs = [c.high for c in candles]
    lows = [c.low for c in candles]
    vols = [c.volume for c in candles]

    last = candles[-1]
    last_close = last.close
    last_open = last.open
    last_vol = last.volume

    if last_close == 0:
        return None

    # Accumulation range over previous lookback_bars (excluding current bar)
    start_idx = n - 1 - lookback_bars
    end_idx = n - 1
    hh = max(highs[start_idx:end_idx])
    ll = min(lows[start_idx:end_idx])

    range_pct = (hh - ll) / last_close * 100.0
    is_consolidating = range_pct <= max_range_pct

    # Volume
    recent_vols = vols[-vol_length:]
    avg_vol = sum(recent_vols) / len(recent_vols)
    if avg_vol < min_avg_volume:
        return None

    vol_spike = last_vol >= vol_multiplier * avg_vol

    # Break of structure & candle shape
    price_breaks = last_close > hh
    bullish_bar = last_close > last_open

    # Trend filter (20 > 50 > 200 and price above 20 EMA)
    ema20 = ema(closes, 20)
    ema50 = ema(closes, 50)
    ema200 = ema(closes, min(200, len(closes)))
    trend_ok = (last_close > ema20) and (ema20 > ema50) and (ema50 > ema200)

    if is_consolidating and vol_spike and price_breaks and bullish_bar and trend_ok:
        vol_multiple = last_vol / avg_vol
        
        # Calculate enhanced metrics
        atr_data = calculate_atr(candles, period=14)
        risk_metrics = calculate_risk_metrics(last_close, atr_data, atr_multiplier=2.0)
        vpa_analysis = analyze_vpa_advanced(candles, vol_multiple)
        options_rec = generate_options_recommendation(last_close, atr_data, interval)
        pyramid_signal = generate_pyramid_signal(symbol, last_close, position_tracker, atr_data)
        signal_strength = calculate_signal_strength(vpa_analysis, risk_metrics, vol_multiple, range_pct)
        
        # Add to position tracker if new entry
        if pyramid_signal.action == "INITIAL":
            position_tracker.add_position(
                symbol, last_close, last.time, interval, risk_metrics.atr_stop
            )
        elif position_tracker.has_active_position(symbol):
            position_tracker.update_position(symbol, last_close)
            if pyramid_signal.action in ["ADD_25%", "ADD_50%"]:
                add_pct = 25.0 if "25%" in pyramid_signal.action else 50.0
                position_tracker.add_pyramid(symbol, last_close, add_pct)
        
        return EnhancedSignal(
            ticker=symbol,
            interval=interval,
            price=last_close,
            time=last.time,
            range_pct=range_pct,
            volume_multiple=vol_multiple,
            atr_data=atr_data,
            risk_metrics=risk_metrics,
            vpa_analysis=vpa_analysis,
            options_rec=options_rec,
            pyramid_signal=pyramid_signal,
            signal_strength=signal_strength
        )

    return None


def scan_tier(tier_name: str, interval_override: Optional[str] = None) -> List[EnhancedSignal]:
    """
    Scan symbols in a tier with API optimization.
    Prioritizes high-value symbols and respects rate limits.
    """
    global api_client
    
    if tier_name not in TIERS:
        raise ValueError(f"Unknown tier '{tier_name}'")

    tier_cfg = TIERS[tier_name]
    symbols: List[str] = tier_cfg.get("symbols", [])
    if not symbols:
        return []

    interval = interval_override or tier_cfg.get("interval", "5min")
    
    # Prioritize symbols to scan most important first
    # Limit based on remaining API calls
    stats = api_client.get_stats()
    fmp_remaining = stats["fmp"]["calls_remaining"]
    twelve_remaining = stats["twelve_data"]["calls_remaining"]
    total_remaining = fmp_remaining + twelve_remaining
    
    # Reserve some calls for other tiers
    max_to_scan = min(len(symbols), total_remaining // 3) if total_remaining > 0 else 0
    
    if max_to_scan == 0:
        print(f"[{tier_name}] No API calls remaining, skipping scan")
        return []
    
    prioritized = prioritize_symbols(symbols, max_symbols=max_to_scan)
    
    print(f"[{tier_name}] Scanning {len(prioritized)}/{len(symbols)} symbols (FMP: {fmp_remaining}, Twelve: {twelve_remaining} remaining)")

    signals: List[EnhancedSignal] = []
    for symbol in prioritized:
        try:
            candles = fetch_candles(symbol, interval, outputsize=120)
            if not candles:  # Skip if cache miss and API limit hit
                continue
                
            sig = detect_breakout(symbol, interval, candles)
            if sig:
                sig.tier = tier_name
                signals.append(sig)
        except Exception as e:
            print(f"[{tier_name}] Error scanning {symbol}: {e}")

    return signals


# ------------------- Alerting -------------------

def send_telegram(msg: str):
    if not USE_TELEGRAM:
        print("ALERT:", msg)
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": msg,
        "parse_mode": "Markdown",
    }
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"[send_telegram] Error sending message: {e}")


def run_tier_scan(tier_name: str, interval_override: Optional[str] = None):
    print(f"Running scan for tier={tier_name}, interval_override={interval_override}")
    signals = scan_tier(tier_name, interval_override=interval_override)

    if not signals:
        print(f"No signals for tier={tier_name}")
        return

    for sig in signals:
        # Use enhanced detailed alert format
        msg = format_detailed_alert(sig)
        send_telegram(msg)


# ------------------- Scheduler -------------------

def main():
    global position_tracker, api_client
    
    # Initialize position tracker
    position_tracker = PositionTracker(db_file="positions.json")
    print("✅ Position tracker initialized")
    
    # Initialize dual API client (FMP primary, Twelve Data backup, Yahoo Finance final fallback)
    api_client = TripleAPIClient(
        fmp_api_key=FMP_API_KEY,
        twelve_data_key=TWELVE_DATA_API_KEY,
        alpha_vantage_key=ALPHA_VANTAGE_API_KEY,
        cache_ttl_minutes={
            "1min": 2,   # 2 min cache for 1min data (more aggressive)
            "5min": 5,   # 5 min cache for 5min data (more aggressive)
            "15min": 15, # 15 min cache for 15min data (more aggressive)
        }
    )
    print("✅ Triple API client initialized")
    print("   Tier 1: FMP (250 calls/day)")
    print("   Tier 2: Twelve Data (800 calls/MONTH)")
    print("   Tier 3: Alpha Vantage (Fallback)")
    print("   Tier 4: Yahoo Finance (unlimited, FREE)")
    
    # Show initial API stats
    stats = api_client.get_stats()
    print(f"\n📊 API Status:")
    print(f"   FMP: {stats['fmp']['calls_used']}/{stats['fmp']['limit']} used")
    print(f"   Twelve: {stats['twelve_data']['calls_used']}/{stats['twelve_data']['limit']} used")
    print(f"   Yahoo: {stats['yahoo_finance']['calls_used']} used (unlimited, free)")
    
    # fast_1m → every 1 min
    schedule.every(1).minutes.do(run_tier_scan, tier_name="fast_1m", interval_override="1min")

    # intraday_5m → every 5 min
    schedule.every(5).minutes.do(run_tier_scan, tier_name="intraday_5m", interval_override="5min")

    # swing_15m → every 15 min
    schedule.every(15).minutes.do(run_tier_scan, tier_name="swing_15m", interval_override="15min")
    
    # Periodic cache cleanup (every hour)
    schedule.every(1).hours.do(lambda: api_client.cache.clear_expired())

    print("\n📡 Enhanced breakout scanner started...")
    print("Tiers:", ", ".join(TIERS.keys()))
    print("Features: Triple API (FMP/Twelve/Yahoo), Detailed Alerts, ATR, VPA, Options, Pyramiding")
    if USE_TELEGRAM:
        print("Telegram: Enhanced detailed alerts enabled")
    else:
        print("Telegram not configured, alerts will be printed to stdout.")

    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    main()
