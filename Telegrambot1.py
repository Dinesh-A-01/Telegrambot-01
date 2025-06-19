import requests
import re
import time
from datetime import datetime
import pytz

# === SETTINGS ===
THRESHOLDS = [82.33, 81.50, 85.32]  # Set your desired alert levels
ALERTED_LEVELS = set()  # Keeps track of alerts already sent

BOT_TOKEN = '7938993354:AAEbsE-R0LMCog8GxeX3Xe27EgUVTH355PE'
CHAT_ID = '1637182240'
URL = "https://www.moneycontrol.com/india/stockpricequote/mf-etfs/sbisetfgold/SET"

# === GET PRICE ===
def get_price():
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(URL, headers=headers)
    match = re.search(r'class="inprice1">([0-9]+\.[0-9]+)<', response.text)
    return float(match.group(1)) if match else None

# === SEND TELEGRAM ALERT ===
def send_alert(price, level):
    message = f"📉 SETFGOLD Alert!\nPrice dropped below ₹{level:.2f}\nCurrent price: ₹{price:.2f}"
    requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", data={
        "chat_id": CHAT_ID,
        "text": message
    })

# === CHECK IF WITHIN MARKET TIME ===
def is_market_time():
    now = datetime.now(pytz.timezone("Asia/Kolkata"))
    return (now.hour == 6 and now.minute >= 45) or (7 <= now.hour < 13)

# === MAIN LOOP ===
while True:
    if is_market_time():
        price = get_price()
        now = datetime.now(pytz.timezone("Asia/Kolkata")).strftime("%Y-%m-%d %H:%M")

        if price:
            print(f"[{now}] Current Price: ₹{price}")
            for level in THRESHOLDS:
                if price < level and level not in ALERTED_LEVELS:
                    send_alert(price, level)
                    ALERTED_LEVELS.add(level)
        else:
            print(f"[{now}] ❌ Failed to fetch price.")
    else:
        print("⏸️ Outside market hours. Waiting...")

    time.sleep(60)  # Check every 1 minute

