#!/usr/bin/env python3
"""
Test the Assistant output directly
"""

import os
import sys
import time
from pathlib import Path

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

from openai import OpenAI

def load_env_file():
    """Load environment variables from .env file"""
    env_file = Path(__file__).parent.parent / ".env"
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    if "=" in line:
                        key, value = line.split("=", 1)
                        os.environ[key.strip()] = value.strip()

load_env_file()

API_KEY = os.getenv("OPENAI_API_KEY")
ASSISTANT_ID = os.getenv("OPENAI_ASSISTANT_ID")

client = OpenAI(api_key=API_KEY)

# Test prompt
TEST_PROMPT = """Convertir le texte suivant en document RTF structuré avec titre, sections et formatage:

# Rapport Mensuel - Novembre 2025

## Objectifs Atteints
- Implémentation des tests automatisés
- Déploiement en production
- Réduction de la dette technique"""

def test_assistant():
    print("[INFO] Testing Assistant with sample input...")
    print(f"[INFO] Prompt: {TEST_PROMPT[:100]}...")
    print()

    # Create thread
    thread = client.beta.threads.create()
    print(f"[OK] Thread created: {thread.id}")

    # Add message
    client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=TEST_PROMPT
    )

    # Run assistant
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=ASSISTANT_ID
    )
    print(f"[OK] Run created: {run.id}")

    # Wait for completion
    while run.status in ["queued", "in_progress"]:
        time.sleep(0.5)
        run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
        print(f"[...] Status: {run.status}")

    print(f"[OK] Run completed with status: {run.status}")

    # Get response
    messages = client.beta.threads.messages.list(thread_id=thread.id)

    print("\n" + "="*60)
    print("ASSISTANT RESPONSE:")
    print("="*60)

    for msg in messages.data:
        if msg.role == "assistant":
            content = str(msg.content[0].text)
            print(content)
            print("\n" + "="*60)
            print("RESPONSE LENGTH:", len(content))
            print("STARTS WITH {\\rtf:", content.strip().startswith("{\\rtf"))
            print("="*60)

if __name__ == "__main__":
    test_assistant()
