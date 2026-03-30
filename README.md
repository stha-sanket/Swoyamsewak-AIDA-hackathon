# 🌸 Karuthi (करुठी) - Your Digital Daughter

**"Maya Le Sunne, Samjhane Karuthi." (मायाले सुन्ने, सम्झाउने करुठी)**  
*A Caring Digital Companion for Amma (Mothers).*

Karuthi is a bilingual (English & Nepali) AI assistant built specifically for elderly care. Named "Karuthi" (meaning compassionate/caring), she acts as a digital daughter who remembers your medicines, tracks where you keep your keys, and listens to your heart.

---

## ✨ Key Features

- **💊 Medicine Reminders**: Mention taking a pill in a normal conversation, and Karuthi will extract the name, dosage, and time to remind you later.
- **🏠 Item Persistence**: "Amma, where did you keep the glasses?" Karuthi remembers exactly which drawer or shelf your items are in.
- **🎭 Emotional Wellbeing**: A daily mood tracker that provides warm, daughter-like emotional support based on how you're feeling.
- **🇳🇵 Fluent Bilingualism**: Speak to her in English or Nepali; she understands and responds with cultural warmth (e.g., addressing you as "Amma").
- **🧠 LangGraph Intelligence**: Powered by structured agentic workflows for high accuracy in intent detection and data extraction.

---

## 🛠️ Technology Stack

- **Backend**: Python, Flask
- **AI Engine**: Google Gemini 1.5 Flash (via `google-generativeai`)
- **Agent Orchestration**: [LangGraph](https://github.com/langchain-ai/langgraph)
- **Frontend**: HTML5, Vanilla CSS (Glassmorphism design), JavaScript
- **Persistence**: File-based text logs (`karuthi_reminders.txt`, `karuthi_items.txt`, etc.)

---

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Google Gemini API Key

### Installation

1. **Clone the repository**:
   ```bash
   git clone <repo-url>
   cd "New Folder"
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables**:
   Create a `.env` file in the root directory:
   ```env
   GEMINI_API_KEY=your_api_key_here
   ```

4. **Run the application**:
   ```bash
   python karuthi_flask.py
   ```
   Access the app at `http://127.0.0.1:5000`.

---

## 📐 Architecture

Karuthi uses a **StateGraph** architecture to handle multi-step interactions:

1. **Detect Intent**: The agent analyzes if you're chatting, setting a reminder, storing an item, or switching languages.
2. **Specialized Nodes**:
   - `save_medicine`: Extracts structured JSON (Med name, Dose, Time) from natural language.
   - `save_item_location`: Maps items to locations.
   - `normal_chat`: Generates warm, context-aware responses.
3. **Memory Loops**: Chat history is maintained via Flask sessions, keeping the context alive for 30 messages.

---

## 📂 Project Structure

```text
├── karuthi_flask.py      # Main Flask Web Application
├── karuthi_agent.py      # CLI Agent version
├── karuthi_reminders.txt # Data store for medicines
├── karuthi_items.txt     # Data store for item locations
├── static/
│   └── style.css         # Modern, soft-themed styling
└── templates/
    └── chat.html         # Interactive Chat UI with Mood Popup
```

---

## ❤️ Vision

Karuthi was built during the **Swoyamsewak AIDA Hackathon** to bridge the gap between AI and elderly care in Nepal. Our goal is to reduce loneliness and improve daily medical compliance through a "family" centered AI persona.

**Built with love by Pratistha, Anusha, Ayushma, and Sanket.**
