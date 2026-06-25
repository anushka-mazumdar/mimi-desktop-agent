# config/settings.py
from dotenv import load_dotenv
import os

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
APP_NAME = os.getenv("APP_NAME", "Mimi")
DEBUG = os.getenv("DEBUG", "False") == "True"
VOICE_ENABLED = os.getenv("VOICE_ENABLED", "False") == "True"
VISION_ENABLED = os.getenv("VISION_ENABLED", "False") == "True"
MEMORY_ENABLED = os.getenv("MEMORY_ENABLED", "False") == "True"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq")
MODEL_NAME = os.getenv("MODEL_NAME", "llama-3.3-70b-versatile")