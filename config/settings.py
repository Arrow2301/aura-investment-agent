import os
from dotenv import load_dotenv

load_dotenv()

INITIAL_CAPITAL = 1000000
MAX_POSITION_SIZE = 0.10
MIN_CASH = 0.20

AI_PROVIDER = os.getenv("AI_PROVIDER", "gemini")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
