from flask import Flask, render_template, request, jsonify
import threading
import requests
import json
import time

app = Flask(__name__)

# === YOUR TOKEN ===
TOKEN = "8200120783:AAEs9qK64Y6Cl8_Tj1h6ZeoB_2h8x1ON0dU"
WEBHOOK_URL = "http://localhost:5000/webhook"  # Change when deploying
