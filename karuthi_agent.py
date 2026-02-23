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
    """Robust JSON extraction from Gemini output."""
    try:
        m = re.search(r'\{.*\}', text, re.DOTALL)
        return json.loads(m.group()) if m else {}
    except Exception:
        return {}

def save_language(lang: str):
    with open(LANG_FILE, "w", encoding="utf-8") as fp:
        fp.write(lang)

# -------------------------------------------------
# NODES
# -------------------------------------------------
def detect_intent(state: AgentState) -> dict:
    txt = state["input"].lower()

    # ---- language switch ----
    if any(p in txt for p in ["english", "speak in english", "english ma"]):
        return {"intent": "switch", "language": "english"}
    if any(p in txt for p in ["nepali", "नेपाली", "nepali ma"]):
        return {"intent": "switch", "language": "nepali"}

    # ---- medicine reminder ----
    med_kw = ["remind", "khana", "lanu", "pill", "tablet", "ausadhi",
              "am", "pm", "बिहान", "बेलुका", "दिन", "रात"]
    if any(k in txt for k in med_kw):
        return {"intent": "medicine"}

    # ---- item location ----
    item_kw = ["note", "remember", "item", "location", "राखेको", "ठाउँ", "जहाँ"]
    if any(k in txt for k in item_kw):
        return {"intent": "item"}

    return {"intent": "chat"}


# ---------- MEDICINE ----------
def save_medicine(state: AgentState) -> dict:
    lang = state.get("language", "nepali")
    txt  = state["input"]

    prompt = (
        f'Extract medicine reminder from: "{txt}"\n'
        'Return JSON:\n'
        '{\n'
        '  "medicine": "Paracetamol",\n'
        '  "pills": 2,\n'
        '  "times": ["8 AM", "8 PM"]\n'
        '}\n'
        'If not a reminder → {"medicine": null}\n'
        'JSON only.'
        if lang == "english" else
        f'यो भनाइबाट औषधि निकाल: "{txt}"\n'
        'JSON:\n'
        '{\n'
        '  "medicine": "प्यारासिटामोल",\n'
        '  "pills": 2,\n'
        '  "times": ["बिहान ८", "बेलुका ८"]\n'
        '}\n'
        'औषधि होइन → {"medicine": null}\n'
        'JSON मात्र।'
    )

    try:
        data = extract_json(model.generate_content(prompt).text)
        med  = data.get("medicine")
        if not med:
            return {"response": "Got it!" if lang=="english" else "ठिक छ आमा।"}

        pills = data.get("pills", "?")
        times = data.get("times", [])
        times_str = ", ".join(times)

        line = f"{datetime.now():%Y-%m-%d %H:%M} | {med} | {pills} pill(s) | {times_str}\n"
        with open(REMINDERS_FILE, "a", encoding="utf-8") as fp:
            fp.write(line)

        resp = (
            f"Saved! I'll remind you to take {pills} {med} at {times_str}."
            if lang == "english" else
            f"बचत भयो! म {times_str} मा {pills} {med} खान सम्झाउँछु।"
        )
        return {"response": resp}
    except Exception as e:
        print("[MED] error:", e)
        return {"response": "Okay!" if lang=="english" else "ठिक छ।"}


# ---------- ITEM LOCATION ----------
def save_item_location(state: AgentState) -> dict:
    lang = state.get("language", "nepali")
    txt  = state["input"]

    prompt = (
        f'Extract item & location from: "{txt}"\n'
        'Return JSON:\n'
        '{\n'
        '  "item": "keys",\n'
        '  "location": "kitchen drawer"\n'
        '}\n'
        'If not an item-location → {"item": null}\n'
        'JSON only.'
        if lang == "english" else
        f'यो भनाइबाट वस्तु र ठाउँ निकाल: "{txt}"\n'
        'JSON:\n'
        '{\n'
        '  "item": "चाबी",\n'
        '  "location": "भान्साको दराज"\n'
        '}\n'
        'वस्तु/ठाउँ होइन → {"item": null}\n'
        'JSON मात्र।'
    )

    try:
        data = extract_json(model.generate_content(prompt).text)
        item = data.get("item")
        if not item:
            return {"response": "Got it!" if lang=="english" else "ठिक छ आमा।"}

        loc = data.get("location", "unknown")
        line = f"{datetime.now():%Y-%m-%d %H:%M} | {item} → {loc}\n"
        with open(ITEMS_FILE, "a", encoding="utf-8") as fp:
            fp.write(line)

        resp = (
            f"Saved! {item} is in {loc}."
            if lang == "english" else
            f"बचत भयो! {item} {loc} मा छ।"
        )
        return {"response": resp}
    except Exception as e:
        print("[ITEM] error:", e)
        return {"response": "Okay!" if lang=="english" else "ठिक छ।"}


# ---------- NORMAL CHAT ----------
def normal_chat(state: AgentState) -> dict:
    lang = state.get("language", "nepali")
    prompt = (
        f"You are Karuthi, Amma's loving digital daughter. Reply warmly in English.\nAmma: {state['input']}"
        if lang == "english" else
        f"तिमी करुठी हौ, आमाको मायालु डिजिटल छोरी। नेपालीमा मायालु जवाफ देऊ।\nआमा: {state['input']}"
    )
    try:
        return {"response": model.generate_content(prompt).text.strip()}
    except Exception:
        return {"response": "I'm here, Amma." if lang=="english" else "म यहाँ छु आमा।"}


# ---------- LANGUAGE SWITCH ----------
def switch_language(state: AgentState) -> dict:
    new_lang = state.get("language", "english")
    save_language(new_lang)
    msg = (
        "Hello Amma! Now in English. How can I help?"
        if new_lang == "english" else
        "ठिक छ आमा, अब नेपालीमा। के भन्नुहुन्छ?"
    )
    return {"response": msg, "language": new_lang}


# -------------------------------------------------
# GRAPH
# -------------------------------------------------
graph = StateGraph(AgentState)

graph.add_node("detect", detect_intent)
graph.add_node("medicine", save_medicine)
graph.add_node("item", save_item_location)
graph.add_node("chat", normal_chat)
graph.add_node("switch", switch_language)

graph.add_conditional_edges(
    "detect",
    lambda s: s["intent"],
    {
        "medicine": "medicine",
        "item":     "item",
        "chat":     "chat",
        "switch":   "switch"
    }
)

for node in ("medicine", "item", "chat", "switch"):
    graph.add_edge(node, END)

graph.set_entry_point("detect")
agent = graph.compile()


# -------------------------------------------------
# CHAT LOOP
# -------------------------------------------------
print("KARUTHI — SIMPLE MEMORY BOT")
print("Medicine reminders | Item locations | Normal chat")
print("Type 'exit' to quit\n")

chat_history: List[Dict[str, str]] = []

while True:
    try:
        user = input("आमा: ").strip()
        if user.lower() in {"exit", "quit", "bye", "बाई"}:
            print("करुठी: Take care, Amma! म... Love you!")
            break

        chat_history.append({"role": "user", "text": user})

        result = agent.invoke({
            "input": user,
            "chat_history": chat_history,
            "response": "",
            "language": language
        })

        resp = result.get("response", "")
        language = result.get("language", language)

        print(f"करुठी: {resp}\n")
        chat_history.append({"role": "karuthi", "text": resp})

    except KeyboardInterrupt:
        print("\nकरुठी: अलविदा आमा!")
        break
    except Exception as e:
        print(f"[ERROR] {e}")