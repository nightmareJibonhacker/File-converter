# keep_alive.py
from flask import Flask
from threading import Thread
import requests
import time
import os

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is alive!", 200

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

def ping_self():
    url = os.environ.get("KEEP_ALIVE_URL")
    if not url:
        print("[WARN] KEEP_ALIVE_URL not set. Self-ping disabled.")
        return
    while True:
        try:
            requests.get(url)
            print(f"[KEEP_ALIVE] Pinged {url}")
        except Exception as e:
            print(f"[KEEP_ALIVE ERROR] {e}")
        time.sleep(300)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()

    p = Thread(target=ping_self)
    p.daemon = True
    p.start()
  
