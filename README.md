# Web Automation Package
Opinionated starter kit to:
- fetch news (APIs, RSS, and lightweight scraping)
- classify files (uploadable vs not)
- generate embeddings (OpenAI) for search/classification

## Quickstart
1. Unzip and inspect files.
2. Copy `.env.template` to `.env` and fill your API keys:
   - NEWSAPI_KEY (optional)
   - OPENAI_API_KEY (optional)
3. (Optional) Install Playwright if you plan to scrape JS-heavy pages:
   ```
   pip install playwright
   playwright install
   ```
4. Install Python deps:
   ```
   pip install -r requirements.txt
   ```
5. Run everything:
   ```
   bash run_all.sh
   ```

## What's inside
- `scripts/fetch_news.py` — fetches headlines using (NewsAPI -> RSS -> basic scrape)
- `scripts/classify_files.py` — simple local file classifier (size, extension, keyword rules)
- `scripts/train_embeddings.py` — example that creates and stores embeddings using OpenAI
- `.env.template` — example env variables
- `run_all.sh` — convenience runner

## Notes & Pitfalls
- **Credentials**: Never commit `.env` with real keys to public repos.
- **Robots.txt & legality**: Respect websites' `robots.txt`. Use APIs where possible.
- **Playwright**: Required for JS-heavy sites; it's heavier to install.
- **Rate limits**: APIs and scraping are rate-limited. Add backoff / caching for production.

