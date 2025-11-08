#!/usr/bin/env python3
import os
import sys
from pathlib import Path

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# Load .env
env_file = Path(__file__).parent.parent / ".env"
if env_file.exists():
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                if '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

from tests.test_runner import CustomGPTTester

prompt = "Convertir en RTF: Test"
output = CustomGPTTester.call_custom_gpt(prompt)

print(f"Type: {type(output)}")
print(f"Repr: {repr(output[:100])}")
print(f"Starts with {{\\rtf: {output.startswith('{\\rtf')}")
