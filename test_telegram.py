"""
Telegram Bot Test Script

This script helps you verify your Telegram bot configuration before running the full scanner.

Usage:
1. Make sure your .env file has:
   - TELEGRAM_BOT_TOKEN
   - TELEGRAM_CHAT_ID
   - TWELVE_DATA_API_KEY (optional for this test)

2. Run: python test_telegram.py

This will send a test message to your Telegram chat.
"""

import os
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def test_telegram():
    """Send a test message to verify Telegram configuration."""
    
    print("🔍 Testing Telegram Bot Configuration...\n")
    
    # Check if variables are set
    if not TELEGRAM_BOT_TOKEN:
        print("❌ ERROR: TELEGRAM_BOT_TOKEN is not set in .env file")
        return False
    
    if not TELEGRAM_CHAT_ID:
        print("❌ ERROR: TELEGRAM_CHAT_ID is not set in .env file")
        return False
    
    print(f"✅ Bot Token: {TELEGRAM_BOT_TOKEN[:20]}...")
    print(f"✅ Chat ID: {TELEGRAM_CHAT_ID}\n")
    
    # Test bot info
    print("📡 Testing bot connection...")
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getMe"
        resp = requests.get(url, timeout=10)
        data = resp.json()
        
        if data.get("ok"):
            bot_info = data.get("result", {})
            print(f"✅ Bot connected: @{bot_info.get('username')}")
            print(f"   Name: {bot_info.get('first_name')}")
        else:
            print(f"❌ Bot connection failed: {data.get('description')}")
            return False
    except Exception as e:
        print(f"❌ Error connecting to bot: {e}")
        return False
    
    # Send test message
    print("\n📤 Sending test message...")
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": "🎉 *Test Message*\n\nYour stock screener bot is configured correctly!\n\nYou should receive breakout alerts here when the scanner detects opportunities.",
            "parse_mode": "Markdown",
        }
        resp = requests.post(url, json=payload, timeout=10)
        data = resp.json()
        
        if data.get("ok"):
            print("✅ Test message sent successfully!")
            print("\n🎉 SUCCESS! Check your Telegram app for the test message.")
            return True
        else:
            print(f"❌ Failed to send message: {data.get('description')}")
            print("\nPossible issues:")
            print("- Chat ID might be incorrect")
            print("- You need to start a chat with your bot first (send /start)")
            return False
    except Exception as e:
        print(f"❌ Error sending message: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("  TELEGRAM BOT CONFIGURATION TEST")
    print("=" * 60)
    print()
    
    success = test_telegram()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ All tests passed! Your bot is ready to use.")
        print("\nNext steps:")
        print("1. Add your TWELVE_DATA_API_KEY to .env")
        print("2. Run: python breakout_scanner.py")
    else:
        print("❌ Configuration incomplete. Please fix the errors above.")
        print("\nNeed help?")
        print("- See TELEGRAM_SETUP.md for detailed instructions")
        print("- Make sure you've started a chat with your bot")
    print("=" * 60)
