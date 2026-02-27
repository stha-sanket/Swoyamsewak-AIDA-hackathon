from flask import Flask, render_template, request, jsonify, session
from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Dict
import google.generativeai as genai
from datetime import datetime, date
import json
import os
from dotenv import load_dotenv
import re

app = Flask(__name__)

# -------------------------------------------------
# ENV & MODEL
# -------------------------------------------------
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("Set GEMINI_API_KEY in .env")
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# -------------------------------------------------
# FILES
# -------------------------------------------------
FILES = {
    "reminders": "karuthi_reminders.txt",
    "items": "karuthi_items.txt",
    "lang": "karuthi_lang.txt",
    "mood": "karuthi_mood.txt"
}