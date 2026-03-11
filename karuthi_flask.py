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

# -------------------------------------------------
# STATE
# -------------------------------------------------
class AgentState(TypedDict):
    input: str
    chat_history: List[Dict[str, str]]
    response: str
    language: str

# -------------------------------------------------
# HELPERS
# -------------------------------------------------
def extract_json(text: str) -> dict:
    try:
        m = re.search(r'\{.*\}', text, re.DOTALL)
        return json.loads(m.group()) if m else {}
    except:
        return {}

def save_file(key: str, line: str):
    with open(FILES[key], "a", encoding="utf-8") as f:
        f.write(line)

def save_language(lang: str):
    with open(FILES["lang"], "w", encoding="utf-8") as f:
        f.write(lang)

# -------------------------------------------------
# NODES
# -------------------------------------------------
def detect_intent(state: AgentState) -> dict:
    txt = state["input"].lower()
    if any(p in txt for p in ["english", "speak in english", "english ma"]):
        return {"intent": "switch", "language": "english"}
    if any(p in txt for p in ["nepali", "नेपाली", "nepali ma"]):
        return {"intent": "switch", "language": "nepali"}

    time_kw = ["am", "pm", "बिहान", "दिउँसो", "बेलुका", "at ", "मा ", "बजे"]
    med_kw = ["pill", "tablet", "ausadhi", "medicine", "paracetamol", "remind", "खानु", "lanu"]
    if any(t in txt for t in time_kw) and any(m in txt for m in med_kw):
        return {"intent": "medicine"}

    item_kw = ["note", "remember", "is in", "are in", "राखेको", "ठाउँ", "box", "drawer"]
    if any(k in txt for k in item_kw):
        return {"intent": "item"}

    return {"intent": "chat"}


def save_medicine(state: AgentState) -> dict:
    lang = state.get("language", "nepali")
    txt = state["input"]
    prompt = f'Extract medicine reminder with time from: "{txt}"\nReturn JSON: {{"medicine": "...", "pills": 1, "times": ["8 AM"]}}\nIf none → {{"medicine": null}}\nJSON only.'
    if lang == "nepali":
        prompt = f'समयसहित औषधि निकाल: "{txt}"\nJSON: {{"medicine": "...", "pills": 1, "times": ["बिहान ८"]}}\nहोइन → {{"medicine": null}}\nJSON मात्र।'

    try:
        data = extract_json(model.generate_content(prompt).text)
        med = data.get("medicine")
        if not med: return {"response": "ठिक छ आमा।" if lang == "nepali" else "Got it!"}
        pills = data.get("pills", 1)
        times = ", ".join(data.get("times", []))
        line = f"{datetime.now():%Y-%m-%d %H:%M} | {med} | {pills} pill(s) | {times}\n"
        save_file("reminders", line)
        return {"response": f"Saved! I'll remind you at {times}." if lang == "english" else f"बचत भयो! म {times} मा सम्झाउँछु।"}
    except Exception as e:
        print(e)
        return {"response": "ठिक छ।"}

def save_item_location(state: AgentState) -> dict:
    lang = state.get("language", "nepali")
    txt = state["input"]
    prompt = f'Extract item & location: "{txt}"\nJSON: {{"item": "...", "location": "..."}}\nNone → {{"item": null}}\nJSON only.'
    if lang == "nepali":
        prompt = f'वस्तु र ठाउँ निकाल: "{txt}"\nJSON: {{"item": "...", "location": "..."}}\nहोइन → {{"item": null}}\nJSON मात्र।'

    try:
        data = extract_json(model.generate_content(prompt).text)
        item = data.get("item")
        if not item: return {"response": "ठिक छ आमा।"}
        loc = data.get("location", "unknown")
        line = f"{datetime.now():%Y-%m-%d %H:%M} | {item} → {loc}\n"
        save_file("items", line)
        return {"response": f"Saved! {item} is in {loc}." if lang == "english" else f"बचत भयो! {item} {loc} मा छ।"}
    except Exception as e:
        print(e)
        return {"response": "ठिक छ।"}