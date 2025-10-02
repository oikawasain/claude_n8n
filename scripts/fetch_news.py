#!/usr/bin/env python3
"""Fetch news using a cascade:
1) NewsAPI (if key present)
2) RSS feeds (configurable)
3) Lightweight HTML scrape fallback
Outputs JSONL lines to ./data/news_output.jsonl
"""
import os
import json
from pathlib import Path
from dotenv import load_dotenv
import requests
import feedparser
from bs4 import BeautifulSoup
from datetime import datetime
from tqdm import tqdm

load_dotenv()
NEWSAPI_KEY = os.getenv('NEWSAPI_KEY')
OUT = Path('data/news_output.jsonl')
OUT.parent.mkdir(parents=True, exist_ok=True)

def fetch_newsapi(topics=None):
    if not NEWSAPI_KEY:
        return []
    url = 'https://newsapi.org/v2/top-headlines'
    params = {'pageSize': 50, 'apiKey': NEWSAPI_KEY}
    if topics:
        params['q'] = topics
    r = requests.get(url, params=params, timeout=15)
    r.raise_for_status()
    data = r.json()
    articles = data.get('articles', [])
    out = []
    for a in articles:
        out.append({
            'source': a.get('source',{}).get('name'),
            'title': a.get('title'),
            'url': a.get('url'),
            'publishedAt': a.get('publishedAt'),
            'fetched_via': 'newsapi'
        })
    return out

# simple RSS list (you can add more)
RSS_FEEDS = [
    'https://news.google.com/rss',
    'https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml',
    'https://feeds.bbci.co.uk/news/rss.xml',
]

def fetch_rss():
    results = []
    for feed in RSS_FEEDS:
        try:
            d = feedparser.parse(feed)
            for e in d.entries[:20]:
                results.append({
                    'source': d.feed.get('title'),
                    'title': e.get('title'),
                    'url': e.get('link'),
                    'publishedAt': getattr(e, 'published', None),
                    'fetched_via': 'rss'
                })
        except Exception as e:
            print('RSS error', feed, e)
    return results

def scrape_page(url):
    try:
        r = requests.get(url, timeout=10, headers={'User-Agent':'Mozilla/5.0'})
        r.raise_for_status()
        soup = BeautifulSoup(r.text, 'html.parser')
        title = soup.title.string if soup.title else None
        # very small heuristics for article text
        p = soup.find_all('p')
        text = ' '.join([pp.get_text() for pp in p[:10]])
        return {'title': title, 'url': url, 'text_snippet': text[:1000], 'fetched_via': 'scrape'}
    except Exception as e:
        return {'url': url, 'error': str(e), 'fetched_via': 'scrape'}

def main():
    out_items = []
    print('Trying NewsAPI...')
    try:
        out_items.extend(fetch_newsapi())
    except Exception as e:
        print('newsapi failed', e)

    print('Fetching RSS feeds...')
    out_items.extend(fetch_rss())

    # dedupe by URL
    seen = set()
    final = []
    for it in out_items:
        u = it.get('url')
        if not u or u in seen:
            continue
        seen.add(u)
        final.append(it)
    print(f'Collected {len(final)} items.')

    # write summary and then try lightweight scrape for top 10
    with OUT.open('w', encoding='utf8') as fh:
        for item in final:
            fh.write(json.dumps(item, default=str, ensure_ascii=False) + '\n')

    # optional: scrape top 10 to enrich
    enriched = []
    for item in final[:10]:
        if item.get('url'):
            enriched.append(scrape_page(item['url']))
    if enriched:
        (OUT.parent / 'enriched.jsonl').write_text('\n'.join(json.dumps(x, ensure_ascii=False) for x in enriched), encoding='utf8')
        print('Wrote enriched output.')

if __name__ == '__main__':
    main()
