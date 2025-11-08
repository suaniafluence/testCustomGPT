#!/usr/bin/env python3
"""
Create an OpenAI Assistant for RTF conversion testing
"""

import os
import sys
import json
from pathlib import Path

# Fix encoding for Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

from openai import OpenAI

# Load .env file
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

if not API_KEY:
    print("❌ Error: OPENAI_API_KEY not found in .env")
    exit(1)

client = OpenAI(api_key=API_KEY)

# System prompt for RTF conversion
SYSTEM_PROMPT = """Tu es un expert en conversion de texte vers le format RTF (Rich Text Format).

Ta mission : Convertir le texte ou le contenu fourni en document RTF valide avec :
- Structure RTF correcte (début par {\\rtf1\\ansi...)
- Formatage approprié (titres en gras, sections structurées)
- Caractères accentués supportés
- Listes à puces quand approprié
- Paragraphes bien structurés

Exigences :
1. Retourner UNIQUEMENT le code RTF, rien d'autre
2. RTF doit être valide et compilable
3. Respecter la hiérarchie des titres
4. Garder le contenu original intact
5. Utiliser \\par pour les sauts de paragraphe
6. Appliquer le formatage \\b pour le gras sur les titres

Format de réponse : Code RTF complet et valide uniquement."""

def create_assistant():
    """Create an RTF conversion assistant"""
    print("\n📝 Creating RTF Conversion Assistant...")

    assistant = client.beta.assistants.create(
        name="RTF Conversion Engine",
        description="Converts text content to valid RTF format",
        instructions=SYSTEM_PROMPT,
        model="gpt-4-turbo",
    )

    print(f"✅ Assistant created successfully!")
    print(f"\n📋 Assistant Details:")
    print(f"  ID: {assistant.id}")
    print(f"  Name: {assistant.name}")
    print(f"  Model: {assistant.model}")

    return assistant

def save_assistant_id(assistant_id):
    """Save assistant ID to .env file"""
    env_file = Path(__file__).parent.parent / ".env"

    # Read existing content
    content = ""
    if env_file.exists():
        with open(env_file) as f:
            content = f.read()

    # Remove existing OPENAI_ASSISTANT_ID if present
    lines = content.split("\n")
    lines = [line for line in lines if not line.startswith("OPENAI_ASSISTANT_ID")]

    # Add new assistant ID
    content = "\n".join(lines).strip() + "\n"
    content += f"OPENAI_ASSISTANT_ID={assistant_id}\n"

    # Write back
    with open(env_file, "w") as f:
        f.write(content)

    print(f"\n💾 Assistant ID saved to .env")

def main():
    """Main function"""
    print("="*60)
    print("OpenAI Assistant Creator for RTF Conversion")
    print("="*60)

    try:
        # Create assistant
        assistant = create_assistant()

        # Save ID to .env
        save_assistant_id(assistant.id)

        print("\n" + "="*60)
        print("✅ Setup Complete!")
        print("="*60)
        print(f"\nNext step: Run tests with the new assistant")
        print(f"  pytest tests/test_runner.py -v")

    except Exception as e:
        print(f"\n❌ Error creating assistant: {str(e)}")
        exit(1)

if __name__ == "__main__":
    main()
