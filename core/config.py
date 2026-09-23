import os
from dotenv import load_dotenv
load_dotenv()

INITIAL_CAPITAL = 1000000
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
