# AURA Production Build

Setup:
1. Copy .env.example to .env
2. Add Supabase credentials
3. pip install -r requirements.txt
4. Run:
PYTHONPATH=. python automation/daily_run.py

Dashboard:
streamlit run dashboard/app.py

This build replaces placeholder scoring with live Yahoo Finance data, technical indicators, fundamentals, risk hooks and Supabase-ready storage.
