from supabase import create_client
from core.config import SUPABASE_URL, SUPABASE_ANON_KEY

client = None

if SUPABASE_URL and SUPABASE_ANON_KEY:
    client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

def insert(table, data):
    if client:
        return client.table(table).insert(data).execute()
    return None
