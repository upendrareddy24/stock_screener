# Get Your Telegram Chat ID

To complete the Telegram bot setup, you need your chat ID. Here's how to get it:

## Quick Method

1. **Open Telegram** on your phone or desktop
2. **Search for** `@userinfobot`
3. **Start a chat** with the bot
4. **Send any message** (like "hi")
5. The bot will reply with your **chat ID** (a number like `123456789`)

## Alternative Method

1. **Message your bot** first:
   - Search for your bot in Telegram (the one you created with @BotFather)
   - Send it any message (like "/start")

2. **Get the chat ID via API**:
   - Open this URL in your browser:
   ```
   https://api.telegram.org/bot8389784209:AAFcaAwFqpV2o_cTfkHGDoO9othRdB9h5TU/getUpdates
   ```
   - Look for `"chat":{"id":123456789` in the response
   - Copy that number

## Update Your .env File

Once you have your chat ID, open `d:\AntiGravity\stock_screener\.env` and update:

```env
TELEGRAM_CHAT_ID=your_actual_chat_id_here
```

Replace `your_actual_chat_id_here` with the number you got from @userinfobot.

## Your Current Configuration

✅ **Bot Token**: Already configured
⏳ **Chat ID**: Needs to be added
⏳ **Twelve Data API Key**: Needs to be added

---

**Next**: Get your chat ID and Twelve Data API key, then you'll be ready to run the scanner!
