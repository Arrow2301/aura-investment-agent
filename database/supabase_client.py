import os
from supabase import create_client


url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_ANON_KEY")


if not url or not key:
    raise Exception(
        "Supabase credentials missing"
    )


supabase = create_client(
    url,
    key
)


def save_signal(data):

    response = (
        supabase
        .table("signals")
        .insert(data)
        .execute()
    )

    return response
