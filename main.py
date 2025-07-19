import os
import json
import asyncio
import websockets
import talib
import numpy as np
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

BOT_TOKEN = os.getenv("BOT_TOKEN")
DERIV_TOKEN = os.getenv("DERIV_TOKEN")

ema_period = 50

def sniper_strategy(candles):
    closes = np.array([c['close'] for c in candles], dtype=float)
    ema = talib.EMA(closes, timeperiod=ema_period)
    rsi = talib.RSI(closes, timeperiod=14)
    macd, macdsignal, _ = talib.MACD(closes, fastperiod=12, slowperiod=26, signalperiod=9)

    if (closes[-1] < ema[-1]) and (macd[-1] < macdsignal[-1]) and (rsi[-1] < 50):
        return "SELL"
    elif (closes[-1] > ema[-1]) and (macd[-1] > macdsignal[-1]) and (rsi[-1] > 50):
        return "BUY"
    return None

def start(update: Update, context: CallbackContext):
    update.message.reply_text("✅ Boom600 Sniper Bot is Live! Signals will appear automatically.")

def normal(update: Update, context: CallbackContext):
    update.message.reply_text("Normal Mode ✅ — Waiting for sniper entry...")

def flip(update: Update, context: CallbackContext):
    update.message.reply_text("Flip Mode Coming Soon...")

async def deriv_candle_stream(bot):
    url = "wss://ws.derivws.com/websockets/v3?app_id=1089"
    async with websockets.connect(url) as ws:
        await ws.send(json.dumps({"authorize": DERIV_TOKEN}))
        await ws.send(json.dumps({
            "ticks_history": "BOOM600",
            "adjust_start_time": 1,
            "count": 100,
            "granularity": 300,
            "end": "latest",
            "style": "candles"
        }))
        while True:
            data = json.loads(await ws.recv())
            if "candles" in data:
                candles = data["candles"]
                signal = sniper_strategy(candles)
                if signal:
                    price = candles[-1]['close']
                    bot.send_message(chat_id=YOUR_CHAT_ID, text=f"🔥 SNIPER SIGNAL 🔥\nDirection: {signal}\nPrice: {price}")

def main():
    updater = Updater(BOT_TOKEN)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("normal", normal))
    dp.add_handler(CommandHandler("flip", flip))
    loop = asyncio.get_event_loop()
    loop.create_task(deriv_candle_stream(updater.bot))
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
