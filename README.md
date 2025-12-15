# Stock Screener - Tiered Breakout Scanner

A professional-grade stock breakout scanner that uses Wyckoff methodology, Volume Price Analysis (VPA), and EMA trend filters to identify high-probability breakout opportunities across multiple timeframes.

## 🎯 Features

- **Multi-Tier Scanning**: Three scanning tiers for different trading styles
  - `fast_1m`: Ultra-liquid stocks scanned every 1 minute (scalping/day trading)
  - `intraday_5m`: Active large caps scanned every 5 minutes (day trading)
  - `swing_15m`: Broader universe scanned every 15 minutes (swing trading)

- **Advanced Strategy**: Combines multiple technical factors
  - Wyckoff accumulation/consolidation detection
  - Volume Price Analysis (VPA) with volume spikes
  - EMA trend alignment (20 > 50 > 200)
  - Breakout confirmation with bullish candle patterns

- **Real-Time Alerts**: Telegram notifications with detailed trade information
  - Entry price
  - Consolidation range percentage
  - Volume multiple vs average
  - Setup description

## 📋 Prerequisites

1. **Python 3.7+** installed on your system
2. **API Keys** - Triple-tier API setup for maximum reliability:
   - **FMP API Key** (Tier 1) - Get free API key at [financialmodelingprep.com](https://financialmodelingprep.com/) (250 calls/day)
   - **Twelve Data API Key** (Tier 2) - Get free API key at [twelvedata.com](https://twelvedata.com/) (800 calls/MONTH)
   - **Yahoo Finance** (Tier 3) - No API key needed! Unlimited and FREE
   - The scanner automatically cascades through all three tiers
3. **Telegram Bot** (Optional) - For alerts:
   - Create a bot via [@BotFather](https://t.me/BotFather) on Telegram
   - Get your chat ID from [@userinfobot](https://t.me/userinfobot)

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

Or install manually:
```bash
pip install requests schedule python-dotenv
```

### 2. Configure Environment

Create a `.env` file in the project directory:

```bash
cp .env.template .env
```

Edit `.env` and add your API keys:

```env
# Tier 1 (Primary) - 250 calls/day
FMP_API_KEY=your_fmp_api_key_here

# Tier 2 (Backup) - 800 calls/MONTH (use sparingly!)
TWELVE_DATA_API_KEY=your_twelvedata_api_key_here

# Tier 3 (Final Fallback) - Yahoo Finance is FREE and unlimited!
# No API key needed - automatically available

# Telegram (Optional)
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_CHAT_ID=your_telegram_chat_id_here
```

> **Note**: Telegram configuration is optional. If not provided, alerts will be printed to console.

### 3. Run the Scanner

```bash
python breakout_scanner.py
```

The scanner will start and run continuously, scanning each tier at its configured interval.

## ⚙️ Configuration

### Customizing Stock Lists

Edit the `TIERS` dictionary in `breakout_scanner.py`:

```python
TIERS: Dict[str, Dict] = {
    "fast_1m": {
        "description": "Very liquid fast movers scanned on 1m",
        "interval": "1min",
        "symbols": [
            "TSLA", "NVDA", "SPY", "QQQ", "AMD", "META", "MSFT", "AMZN",
        ],
    },
    # ... add more tiers or modify existing ones
}
```

### Adjusting Strategy Parameters

Modify the `detect_breakout()` function parameters:

```python
def detect_breakout(
    symbol: str,
    interval: str,
    candles: List[Candle],
    lookback_bars: int = 20,        # Consolidation period
    vol_length: int = 20,            # Volume average period
    vol_multiplier: float = 2.0,     # Volume spike threshold
    max_range_pct: float = 3.0,      # Max consolidation range %
    min_avg_volume: float = 100_000, # Minimum average volume
)
```

## 📊 Strategy Explanation

The scanner identifies breakouts using a multi-factor approach:

1. **Consolidation Detection**: Identifies tight trading ranges (< 3% by default) over the last 20 bars
2. **Volume Confirmation**: Requires 2x average volume on breakout
3. **Trend Alignment**: Ensures strong uptrend (20 EMA > 50 EMA > 200 EMA)
4. **Price Action**: Confirms bullish breakout candle above consolidation high
5. **Position Filter**: Price must be above 20 EMA

## 🔔 Alert Format

When a breakout is detected, you'll receive:

```
🚀 Breakout detected

Ticker: NVDA
Tier: fast_1m
Timeframe: 1min
Time: 2025-12-09 15:30:00
Price: 485.50
Base range: 2.3%
Volume: 3.2x avg

Setup: Wyckoff-style breakout from tight base in strong uptrend.
```

## 🛠️ Troubleshooting

### API Rate Limits

The scanner uses a **triple-tier API system** for maximum reliability:
- **Tier 1 (Primary)**: FMP (250 calls/day)
- **Tier 2 (Backup)**: Twelve Data (800 calls/MONTH - very limited!)
- **Tier 3 (Final Fallback)**: Yahoo Finance (unlimited, FREE!)
- **Aggressive caching** (2-15 min TTL) to minimize API usage

⚠️ **Important**: The system automatically cascades:
1. Tries FMP first (fast, reliable)
2. Falls back to Twelve Data if FMP fails (preserves monthly quota)
3. Falls back to Yahoo Finance if both fail (unlimited, always works!)

✅ **You'll never run out of data** - Yahoo Finance ensures continuous operation even if paid APIs are exhausted.

If you want to optimize further:
- Reduce symbols in each tier or increase scan intervals
- Consider upgrading FMP to a paid plan
- Yahoo Finance fallback keeps everything running for free!

### No Signals

If you're not getting signals:
- Markets may not be showing breakout patterns
- Adjust strategy parameters (looser criteria)
- Check that markets are open during your scan times
- Verify your symbols are valid

### Telegram Not Working

- Verify bot token and chat ID are correct
- Test by messaging your bot directly
- Check that the bot has permission to send messages

## 📁 Project Structure

```
stock_screener/
├── breakout_scanner.py   # Main scanner script
├── requirements.txt      # Python dependencies
├── .env.template        # Environment template
├── .env                 # Your API keys (create this)
└── README.md           # This file
```

## 🔐 Security

- Never commit your `.env` file to version control
- Keep your API keys secure
- Use environment variables for sensitive data

## 📝 License

This project is provided as-is for educational and personal use.

## 🤝 Support

For issues or questions:
1. Check the Twelve Data API documentation
2. Verify your environment configuration
3. Review the console output for error messages

---

**Happy Trading! 📈**

> **Disclaimer**: This tool is for informational purposes only. Always do your own research and risk management before trading.
