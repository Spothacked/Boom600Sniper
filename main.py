import os
import json
import asyncio
import websockets
import pandas as pd
import pandas_ta as ta
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

BOT_TOKEN = os.getenv("BOT_TOKEN")
DERIV_TOKEN = os.getenv("DERIV_TOKEN")

ema_period = 50

def sniper_strategy(candles):
    df = pd.DataFrame(candles)
    df['ema'] = ta.ema(df['close'], length=ema_period)
    df['rsi'] = ta.rsi(df['close'], length=14)
    macd = ta.macd(df['close'], fast=12, slow=26, signal=9)
    df['macd'] = macd['MACD_12_26_9']
    df['macd_signal'] = macd['MACDs_12_26_9']

    last = df.iloc[-1]
    if (last['close'] < last['ema']) and (last['macd'] < last['macd_signal']) and (last['rsi'] < 50):
        return "SELL"
    elif (last['close'] > last['ema']) and (last['macd'] > last['macd_signal']) and (last['rsi'] > 50):
        return "BUY"
    return None

def start(update: Update, context: CallbackContext):
    update.message.reply_text("✅ Boom600 Sniper Bot Live! Signals will appear automatically.")

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
