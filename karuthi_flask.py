from flask import Flask, render_template, request, jsonify, session
from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Dict
import google.generativeai as genai
from datetime import datetime, date
import json
import os
from dotenv import load_dotenv
import re
