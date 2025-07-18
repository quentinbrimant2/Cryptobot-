import os
import time
import requests
from binance.client import Client

# === CONFIG ===
API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")
PAIR = os.getenv("TRADING_PAIR", "BTCUSDT")
LEVERAGE = int(os.getenv("LEVERAGE", 10))
POSITION_SIZE = float(os.getenv("POSITION_SIZE", 0.001))
TAKE_PROFIT = float(os.getenv("TAKE_PROFIT", 0.01))
STOP_LOSS = float(os.getenv("STOP_LOSS", 0.005))
PARTIAL_TAKE_PROFIT = float(os.getenv("PARTIAL_TAKE_PROFIT", 0.005))
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

client = Client(API_KEY, API_SECRET)
client.futures_change_leverage(symbol=PAIR, leverage=LEVERAGE)

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message}
    requests.post(url, data=data)

def get_price():
    return float(client.futures_symbol_ticker(symbol=PAIR)["price"])

def place_order(side, qty):
    return client.futures_create_order(
        symbol=PAIR, side=side, type="MARKET", quantity=qty
    )

def trading_bot():
    send_telegram("🚀 Bot démarré en mode LIVE")
    entry_price = get_price()
    take_profit_price = entry_price * (1 + TAKE_PROFIT)
    stop_loss_price = entry_price * (1 - STOP_LOSS)
    partial_take_profit_price = entry_price * (1 + PARTIAL_TAKE_PROFIT)

    # Ouvrir position LONG
    order = place_order("BUY", POSITION_SIZE)
    send_telegram(f"✅ Position ouverte à {entry_price} (Qty: {POSITION_SIZE})")

    partial_done = False
    while True:
        current_price = get_price()

        # TP partiel
        if not partial_done and current_price >= partial_take_profit_price:
            place_order("SELL", POSITION_SIZE / 2)
            send_telegram(f"💰 Prélèvement partiel à {current_price}")
            partial_done = True

        # TP complet
        if current_price >= take_profit_price:
            place_order("SELL", POSITION_SIZE if not partial_done else POSITION_SIZE / 2)
            send_telegram(f"🎯 TAKE PROFIT atteint à {current_price}")
            break

        # Stop Loss
        if current_price <= stop_loss_price:
            place_order("SELL", POSITION_SIZE if not partial_done else POSITION_SIZE / 2)
            send_telegram(f"❌ STOP LOSS activé à {current_price}")
            break

        time.sleep(3)

if __name__ == "__main__":
    trading_bot()
