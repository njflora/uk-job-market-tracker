"""Check that Python can reach the Supabase database.

Run from the repo root:
    python -m scripts.test_db
"""

import os

import psycopg
from dotenv import load_dotenv

load_dotenv()

with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
    version = conn.execute("select version()").fetchone()[0]
    tables = conn.execute(
        "select table_name from information_schema.tables "
        "where table_schema = 'public' order by table_name"
    ).fetchall()

print("Connected to Supabase.")
print(version.split(",")[0])
print("Tables in public schema:", [t[0] for t in tables] or "none yet")
