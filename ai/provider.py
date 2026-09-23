import os

def ask_ai(prompt):
    provider = os.getenv("AI_PROVIDER", "gemini")

    # Provider abstraction layer.
    # Actual API calls can be enabled after credentials are added.

    return {
        "provider": provider,
        "analysis": "AI analysis placeholder. Connect provider key to activate."
    }
