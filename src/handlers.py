from telegram import Update
from telegram.ext import ContextTypes
from src.deepseek_api import generate_code

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("💡 コード生成ボットです！\n例: PythonでQRコードを作るコード")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = update.message.text
    await update.message.reply_text("🧠 DeepSeekでコード生成中...")
    code = generate_code(prompt)
    await update.message.reply_text(f"✅ 結果:\n```\n{code}\n```", parse_mode="Markdown")
