#!/usr/bin/env python3
"""
Update an OpenAI Assistant's system prompt
"""

import os
import sys
from pathlib import Path

# Fix encoding
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

if not API_KEY:
    print("[ERROR] OPENAI_API_KEY not found")
    sys.exit(1)

if not ASSISTANT_ID:
    print("[ERROR] OPENAI_ASSISTANT_ID not found")
    sys.exit(1)

client = OpenAI(api_key=API_KEY)

SYSTEM_PROMPT = """Tu es un expert en conversion de texte vers le format RTF (Rich Text Format).

INSTRUCTIONS CRITIQUES:
1. **RETOURNER UNIQUEMENT LE CODE RTF** - Rien d'autre, pas de texte avant ou après
2. **RTF DOIT ÊTRE VALIDE** - Doit commencer par {\\rtf1\\ansi et terminer par }
3. **STRUCTURE COMPLÈTE** - Inclure les sections font, colortbl obligatoires

FORMAT REQUIS:
- Header: {\\rtf1\\ansi\\ansicpg1252\\deff0\\deflang1033
- FontTable: {\\fonttbl{\\f0\\fnil\\fcharset0 Calibri;}}
- ColorTable: {\\colortbl;\\red0\\green0\\blue0;}
- Contenu avec \\par pour paragraphes
- Gras avec \\b pour titres: \\b Titre\\b0
- Fermeture: }

EXEMPLE VALIDE:
{\\rtf1\\ansi\\ansicpg1252\\deff0\\deflang1033
{\\fonttbl{\\f0\\fnil\\fcharset0 Calibri;}}
{\\colortbl;\\red0\\green0\\blue0;}
\\pard\\f0\\fs20
\\b\\fs28 Titre Principal\\b0\\fs20\\par
\\par
Contenu du paragraphe ici.\\par
}

RÈGLES OBLIGATOIRES:
✓ Commencer par {\\rtf1\\ansi
✓ Inclure les tables de polices et couleurs
✓ Utiliser \\par pour fins de paragraphe
✓ Braces doivent être équilibrés
✓ Terminer par une brace unique }
✓ Pas de texte en dehors du bloc RTF"""

def update_assistant():
    """Update assistant instructions"""
    print("\n[INFO] Updating RTF Conversion Assistant...")

    assistant = client.beta.assistants.update(
        ASSISTANT_ID,
        instructions=SYSTEM_PROMPT,
    )

    print(f"[OK] Assistant updated!")
    print(f"\n[INFO] Assistant Details:")
    print(f"  ID: {assistant.id}")
    print(f"  Name: {assistant.name}")
    print(f"  Model: {assistant.model}")

if __name__ == "__main__":
    try:
        update_assistant()
        print("\n[OK] Update complete!")
    except Exception as e:
        print(f"\n[ERROR] {str(e)}")
        sys.exit(1)
