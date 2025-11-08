#!/usr/bin/env python3
import os
from pathlib import Path
from openai import OpenAI
import time
import sys

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# Load .env
env_file = Path(__file__).parent.parent / ".env"
with open(env_file) as f:
    for line in f:
        if '=' in line and not line.startswith('#'):
            key, value = line.strip().split('=', 1)
            os.environ[key] = value

client = OpenAI()
thread = client.beta.threads.create()
client.beta.threads.messages.create(thread_id=thread.id, role='user', content='Test')
run = client.beta.threads.runs.create(thread_id=thread.id, assistant_id=os.getenv('OPENAI_ASSISTANT_ID'))

while run.status != 'completed':
    time.sleep(0.5)
    run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)

msgs = client.beta.threads.messages.list(thread_id=thread.id)
for msg in msgs.data:
    if msg.role == 'assistant':
        obj = msg.content[0]
        print(f'Type: {type(obj).__name__}')
        attrs = [x for x in dir(obj) if not x.startswith('_')]
        print(f'Attributes: {attrs}')

        # Check each attribute
        for attr in ['value', 'text', 'content']:
            if hasattr(obj, attr):
                val = getattr(obj, attr)
                print(f'  .{attr} = {type(val).__name__} = {str(val)[:100]}')
