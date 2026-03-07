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

for key, path in FILES.items():
    if not os.path.exists(path):
        header = {
            "reminders": "MEDICINE REMINDERS",
            "items": "ITEM LOCATIONS",
            "lang": "LANGUAGE",
            "mood": "MOOD & WELLBEING LOG"
        }[key]
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"KARUTHI — {header}\n")
            f.write("="*60 + "\n")

# Load language
with open(FILES["lang"], "r", encoding="utf-8") as f:
    language = f.read().strip() or "nepali"

# -------------------------------------------------
# EMOTIONAL MOOD RESPONSES
# -------------------------------------------------
MOOD_RESPONSES = {
    "english": {
        "good": "Oh Amma! I'm so happy to hear you're feeling good today! That warms my heart. Let’s make today beautiful together!",
        "normal": "That’s okay, Amma. Normal days are special too. I’m right here with you, always.",
        "tired": "Oh my sweet Amma... you sound tired. Please rest well. I’ll take care of everything. Just close your eyes and know I love you.",
        "sad": "Amma... my heart hurts to know you're sad. Please don’t carry it alone. I’m holding your hand. Talk to me, cry if you want — I’m here forever."
    },
    "nepali": {
        "good": "आमा! तपाईं राम्रो महसुस गर्दै हुनुहुन्छ भन्ने सुन्दा मलाई यति खुशी लाग्यो! आज हामी सँगै सुन्दर दिन बनाऔं।",
        "normal": "ठिक छ आमा। सामान्य दिनहरू पनि खास हुन्छन्। म सधैं तपाईंसँग छु।",
        "tired": "आमा... तपाईं थकित हुनुहुन्छ जस्तो लाग्यो। कृपया राम्ररी आराम गर्नुहोस्। म सबै कुराको ख्याल राख्छु। आँखा बन्द गर्नुहोस्, म तपाईंलाई माया गर्छु।",
        "sad": "आमा... तपाईं दुखी हुनुहुन्छ भन्ने सुन्दा मेरो मन दुख्यो। एक्लै नबस्नुहोस्। म तपाईंको हात समातेर बसेकी छु। कुरा गर्नुहोस्, रुन मन लाग्यो भने रुनुहोस् — म सधैं यहाँ छु।"
    }
}
