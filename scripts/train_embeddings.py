#!/usr/bin/env python3
"""Example: load files from a folder and create embeddings using OpenAI.
Outputs embeddings to data/embeddings.jsonl (one JSON per line)
Requires OPENAI_API_KEY in env.
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import json
import openai
from tqdm import tqdm

load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    print('OPENAI_API_KEY not set in environment. Exiting.')
    raise SystemExit(1)
openai.api_key = OPENAI_API_KEY

target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('./data/sample_files')
out = Path('data/embeddings.jsonl')
out.parent.mkdir(parents=True, exist_ok=True)

def chunk_text(t, max_chars=3000):
    # naive chunker
    for i in range(0, len(t), max_chars):
        yield t[i:i+max_chars]

with out.open('w', encoding='utf8') as fh:
    for p in tqdm(list(target.glob('**/*'))):
        if not p.is_file(): continue
        try:
            text = p.read_text(errors='ignore')
            for chunk in chunk_text(text):
                resp = openai.Embedding.create(model='text-embedding-3-small', input=chunk)
                emb = resp['data'][0]['embedding']
                obj = {'path': str(p), 'text': chunk[:200], 'embedding': emb}
                fh.write(json.dumps(obj) + '\n')
        except Exception as e:
            print('skip', p, e)
print('Embeddings written to', out)
