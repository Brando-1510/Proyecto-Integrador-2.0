import os
from dotenv import load_dotenv

load_dotenv()

# Email
EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")

# Database
DATABASE_URL = os.getenv("DATABASE_URL")

# Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
GEMINI_TEMPERATURE = float(os.getenv("GEMINI_TEMPERATURE", "0.3"))
GEMINI_MAX_OUTPUT_TOKENS = int(os.getenv("GEMINI_MAX_OUTPUT_TOKENS", "2048"))
GEMINI_TIMEOUT = int(os.getenv("GEMINI_TIMEOUT", "60000"))