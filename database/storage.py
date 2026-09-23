import os
try:
 from supabase import create_client
except: create_client=None
def client():
    if create_client and os.getenv('SUPABASE_URL'):
        return create_client(os.getenv('SUPABASE_URL'),os.getenv('SUPABASE_KEY'))
    return None
def save(table,data):
    c=client()
    if c: return c.table(table).insert(data).execute()
    return data
