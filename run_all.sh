#!/usr/bin/env bash
set -e
python3 scripts/fetch_news.py
python3 scripts/classify_files.py ./data/sample_files
python3 scripts/train_embeddings.py ./data/sample_files
echo "All steps finished."
