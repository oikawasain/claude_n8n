#!/usr/bin/env python3
"""Simple file classifier:
- Rules: allowed extensions, max size, blocked keywords
- Usage: python classify_files.py ./path/to/files
Outputs CSV-like summary to data/file_classification.csv
"""
import os
import sys
from pathlib import Path
import csv

ALLOWED_EXT = {'.pdf', '.docx', '.doc', '.txt', '.md'}
MAX_BYTES = 10 * 1024 * 1024  # 10 MB
BLOCKED_KEYWORDS = {'password','secret','ssn','private','credential'}

def inspect_file(p: Path):
    verdict = 'upload'
    reasons = []
    if p.suffix.lower() not in ALLOWED_EXT:
        verdict = 'skip'
        reasons.append(f'ext:{p.suffix}')
    try:
        size = p.stat().st_size
        if size > MAX_BYTES:
            verdict = 'skip'
            reasons.append(f'size:{size}')
    except Exception:
        reasons.append('stat_failed')
    # read small chunk for keywords
    try:
        with p.open('r',errors='ignore') as fh:
            text = fh.read(2000).lower()
            for kw in BLOCKED_KEYWORDS:
                if kw in text:
                    verdict = 'skip'
                    reasons.append(f'keyword:{kw}')
    except Exception:
        # binary files or unreadable
        reasons.append('unreadable')
    return verdict, ';'.join(reasons)

def main():
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('./data/sample_files')
    out = Path('data/file_classification.csv')
    out.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    for p in sorted(target.glob('**/*')):
        if p.is_file():
            v, r = inspect_file(p)
            rows.append((str(p), p.suffix, p.stat().st_size if p.exists() else 0, v, r))
    with out.open('w', newline='', encoding='utf8') as fh:
        writer = csv.writer(fh)
        writer.writerow(['path','ext','size_bytes','verdict','reasons'])
        writer.writerows(rows)
    print('Wrote', out)

if __name__ == '__main__':
    main()
