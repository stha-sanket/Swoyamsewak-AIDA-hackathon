from flask import Flask, render_template, request, jsonify
import threading
import requests
import json
import time

app = Flask(__name__)

# === YOUR TOKEN ===
TOKEN = "8200120783:AAEs9qK64Y6Cl8_Tj1h6ZeoB_2h8x1ON0dU"
WEBHOOK_URL = "http://localhost:5000/webhook"  # Change when deploying

# Store messages
messages = []
offset = 0

# === TELEGRAM: GET MESSAGES (Long Polling) ===
def get_updates():
    global offset
    url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
    while True:
        try:
            params = {"offset": offset, "timeout": 30}
            response = requests.get(url, params=params, timeout=35)
            data = response.json()
            if data["ok"]:
                for update in data["result"]:
                    offset = update["update_id"] + 1
                    if "message" in update and "text" in update["message"]:
                        msg = update["message"]
                        text = msg["text"]
                        user = msg["from"]["first_name"]
                        chat_id = msg["chat"]["id"]
                        
                        # Add to dashboard
                        messages.append({"sender": user, "text": text, "chat_id": chat_id})
                        
                        # Auto-reply (optional)
                        # send_message(chat_id, f"You said: {text}")
                        
        except Exception as e:
            print("Error:", e)
        time.sleep(1)

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    requests.post(url, json=payload)