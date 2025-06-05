import os
import sys
from datetime import datetime

import requests

NEWS_API_KEY = os.getenv('NEWS_API_KEY')
SLACK_WEBHOOK_URL = os.getenv('SLACK_WEBHOOK_URL')

NEWS_API_URL = 'https://newsapi.org/v2/everything'


def get_news():
    params = {
        'q': 'generative AI',
        'pageSize': 10,
        'sortBy': 'publishedAt',
        'language': 'en',
        'apiKey': NEWS_API_KEY,
    }
    try:
        response = requests.get(NEWS_API_URL, params=params, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Failed to fetch news: {e}", file=sys.stderr)
        return []
    data = response.json()
    return data.get('articles', [])


def send_to_slack(articles):
    if not SLACK_WEBHOOK_URL:
        print('SLACK_WEBHOOK_URL is not set', file=sys.stderr)
        return
    if not articles:
        print('No articles to send', file=sys.stderr)
        return
    text_lines = [f"*Generative AI news for {datetime.utcnow().date()}*\n"]
    for i, a in enumerate(articles, 1):
        title = a.get('title', 'No title')
        url = a.get('url', '')
        text_lines.append(f"{i}. <{url}|{title}>")
    payload = {'text': '\n'.join(text_lines)}
    try:
        resp = requests.post(SLACK_WEBHOOK_URL, json=payload, timeout=10)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"Failed to post to Slack: {e}", file=sys.stderr)


def main():
    if not NEWS_API_KEY:
        print('NEWS_API_KEY is not set', file=sys.stderr)
        return
    articles = get_news()
    send_to_slack(articles)


if __name__ == '__main__':
    main()
