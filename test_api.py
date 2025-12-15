"""
Quick API Test Script

Tests your Twelve Data API key and fetches sample stock data.

Usage:
1. Add TWELVE_DATA_API_KEY to your .env file
2. Run: python test_api.py
"""

import os
from dotenv import load_dotenv
import requests

load_dotenv()

TWELVE_DATA_API_KEY = os.getenv("TWELVE_DATA_API_KEY")

def test_api():
    """Test Twelve Data API connection and fetch sample data."""
    
    print("🔍 Testing Twelve Data API...\n")
    
    if not TWELVE_DATA_API_KEY:
        print("❌ ERROR: TWELVE_DATA_API_KEY is not set in .env file")
        print("\nGet a free API key at: https://twelvedata.com/")
        return False
    
    print(f"✅ API Key: {TWELVE_DATA_API_KEY[:10]}...\n")
    
    # Test API with a simple quote request
    print("📡 Fetching AAPL quote...")
    try:
        url = "https://api.twelvedata.com/quote"
        params = {
            "symbol": "AAPL",
            "apikey": TWELVE_DATA_API_KEY,
        }
        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()
        
        if isinstance(data, dict) and data.get("status") == "error":
            print(f"❌ API Error: {data.get('message')}")
            return False
        
        if "symbol" in data:
            print(f"✅ API working! Current AAPL data:")
            print(f"   Symbol: {data.get('symbol')}")
            print(f"   Price: ${data.get('close', 'N/A')}")
            print(f"   Volume: {data.get('volume', 'N/A')}")
            print(f"   Exchange: {data.get('exchange', 'N/A')}")
        else:
            print(f"❌ Unexpected response: {data}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # Test time series data
    print("\n📊 Fetching time series data...")
    try:
        url = "https://api.twelvedata.com/time_series"
        params = {
            "symbol": "SPY",
            "interval": "5min",
            "outputsize": 5,
            "apikey": TWELVE_DATA_API_KEY,
        }
        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()
        
        if isinstance(data, dict) and data.get("status") == "error":
            print(f"❌ API Error: {data.get('message')}")
            return False
        
        values = data.get("values", [])
        if values:
            print(f"✅ Time series working! Latest SPY 5min candles:")
            for i, candle in enumerate(values[:3], 1):
                print(f"   {i}. {candle.get('datetime')} - Close: ${candle.get('close')}")
        else:
            print(f"❌ No data returned")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("  TWELVE DATA API TEST")
    print("=" * 60)
    print()
    
    success = test_api()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ API is working correctly!")
        print("\nYour scanner is ready to run:")
        print("  python breakout_scanner.py")
    else:
        print("❌ API test failed. Please check:")
        print("- Your API key is correct")
        print("- You haven't exceeded rate limits")
        print("- Your internet connection is working")
    print("=" * 60)
