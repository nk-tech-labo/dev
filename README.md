# Slack への Generative AI ニュース通知

このリポジトリは毎朝8:00(JST)にGenerative AI関連の最新ニュースを10件Slackに送信します。

## セットアップ

1. [NewsAPI](https://newsapi.org/) からAPIキーを取得してください。
2. SlackワークスペースのIncoming Webhook URLを作成してください。
3. 次のリポジトリシークレットを設定します:
   - `NEWS_API_KEY`: NewsAPIのAPIキー
   - `SLACK_WEBHOOK_URL`: SlackのWebhook URL

## 仕組み

`.github/workflows/news_to_slack.yml` に定義されたGitHub Actionsワークフローが毎日23:00 UTC (日本時間8:00) に実行されます。`fetch_ai_news.py` が「generative AI」を含む最新記事を10件取得し、Webhook経由でSlackへ投稿します。

## ローカル実行

```bash
pip install -r requirements.txt
export NEWS_API_KEY=あなたのNewsAPIキー
export SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
python fetch_ai_news.py
```
