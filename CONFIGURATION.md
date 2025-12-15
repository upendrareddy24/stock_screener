# Stock Screener Configuration Summary

## 📊 Stock Universe

Your scanner is now monitoring **644 unique US stocks** across three timeframes:

### Tier Breakdown

| Tier | Timeframe | Stocks | Scan Frequency | Focus |
|------|-----------|--------|----------------|-------|
| **fast_1m** | 1 minute | 142 | Every 1 min | Ultra-liquid mega caps, ETFs, semiconductors, fintech |
| **intraday_5m** | 5 minutes | 500 | Every 5 min | S&P 500, mid caps, biotech, software, all sectors |
| **swing_15m** | 15 minutes | 558 | Every 15 min | Comprehensive Russell 1000 coverage |

### Coverage by Sector

- **Technology**: FAANG, semiconductors (NVDA, AMD, INTC), software (SNOW, PLTR, CRWD)
- **Finance**: Banks (JPM, BAC), fintech (COIN, HOOD, SOFI), payments (V, MA, PYPL)
- **Healthcare**: Pharma (LLY, ABBV), biotech (MRNA, VRTX), med devices (ISRG, DXCM)
- **Consumer**: Retail (AMZN, WMT), e-commerce (SHOP, MELI), restaurants (MCD, SBUX)
- **Energy**: Oil & gas (XOM, CVX), services (SLB, HAL), renewables (ENPH, RUN)
- **Industrials**: Aerospace (BA, LMT), machinery (CAT, DE), logistics (UPS, FDX)
- **ETFs**: Major indices (SPY, QQQ, IWM), sector (XLK, XLF), leveraged (TQQQ, SQQQ)

## 🎯 Strategy Parameters

- **Consolidation**: Max 3% range over 20 bars
- **Volume**: 2x average volume required
- **Trend**: 20 EMA > 50 EMA > 200 EMA
- **Breakout**: Close above range high with bullish candle

## ⚙️ API Configuration

✅ **Twelve Data API**: `775bde32c7f343c783facc175901bbae`
✅ **Telegram Bot**: `8389784209:AAFcaAwFqpV2o_cTfkHGDoO9othRdB9h5TU`
✅ **Chat ID**: `5662042103`

## 🚀 Running the Scanner

```bash
cd d:\AntiGravity\stock_screener
python breakout_scanner.py
```

The scanner will:
1. Start immediately
2. Scan each tier at its configured frequency
3. Send Telegram alerts when breakouts are detected
4. Run continuously until stopped (Ctrl+C)

## 📱 Alert Format

You'll receive messages like:

```
🚀 Breakout detected

Ticker: NVDA
Tier: fast_1m
Timeframe: 1min
Time: 2025-12-09 22:30:00
Price: 485.50
Base range: 2.3%
Volume: 3.2x avg

Setup: Wyckoff-style breakout from tight base in strong uptrend.
```

## 📝 Notes

- **API Rate Limits**: Free tier allows 8 API calls/minute. With 644 stocks, scans will be throttled appropriately
- **Market Hours**: Scanner works 24/7 but most signals occur during US market hours (9:30 AM - 4:00 PM ET)
- **Customization**: Edit `stock_universe.py` to add/remove stocks or adjust tier distribution

## 🎉 Ready to Trade!

Your comprehensive breakout scanner is configured and ready to find opportunities across the entire US market!
