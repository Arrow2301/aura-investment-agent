import os
from supabase import create_client

def client():
    return create_client(os.environ['SUPABASE_URL'],os.environ['SUPABASE_KEY'])
