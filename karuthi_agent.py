# karuthi_memory_bot.py
from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Dict
import google.generativeai as genai
from datetime import datetime
import json
import os
from dotenv import load_dotenv
import re

# -------------------------------------------------
# ENV & MODEL
# -------------------------------------------------
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("Set GEMINI_API_KEY in .env")
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')   # fast & reliable

# -------------------------------------------------
# FILES
# -------------------------------------------------
REMINDERS_FILE = "karuthi_reminders.txt"   # medicine
ITEMS_FILE     = "karuthi_items.txt"       # item → location
LANG_FILE      = "karuthi_lang.txt"

for f in (REMINDERS_FILE, ITEMS_FILE):
    if not os.path.exists(f):
        with open(f, "w", encoding="utf-8") as fp:
            fp.write(f"KARUTHI — {'MEDICINE REMINDERS' if f==REMINDERS_FILE else 'ITEM LOCATIONS'}\n")
            fp.write("="*60 + "\n")

# language persistence
if os.path.exists(LANG_FILE):
    with open(LANG_FILE, "r", encoding="utf-8") as fp:
        language = fp.read().strip()
else:
    language = "nepali"
