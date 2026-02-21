rom langgraph.graph import StateGraph, END
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