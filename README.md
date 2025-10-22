# Telegram Code Writer Bot

Telegram 上でコード生成ボットを動かすためのプロジェクトです。
- `/start`：初期化
- `/help`：コマンド一覧
- `/setmodel <deepseek|openai>`：モデル切替
- `/lang <言語>`：出力言語指定
- `/file <プロンプト>`：コードを `.py` ファイルで生成・送信
- `/explain <コード>`：生成コードの解説

## 環境変数
- `TELEGRAM_TOKEN`：Telegram ボットトークン
- `DEEPSEEK_API_KEY`：OpenRouter API キー（DeepSeek 用）

## デプロイ
GitHub に push → Zeabur で自動デプロイ可能
