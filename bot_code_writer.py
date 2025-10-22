import os
import re
import requests
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from dotenv import load_dotenv
from datetime import datetime
from aiogram.types import FSInputFile

# ----------------------------
# 環境変数読み込み
# ----------------------------
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENROUTER_API_KEY_1 = os.getenv("DEEPSEEK_API_KEY")  # DeepSeek用
OPENROUTER_API_KEY_2 = "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"  # Backup OpenAI

# ----------------------------
# ユーザー設定管理
# ----------------------------
user_model_choice = {}   # {user_id: "deepseek" or "openai"}
user_lang_choice = {}    # {user_id: "python" etc.}

# ----------------------------
# 共通関数
# ----------------------------
def call_openrouter_model(prompt: str, model: str, api_key: str):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://example.com",
        "X-Title": "CodeWriterBot"
    }
    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": "あなたはプロのプログラマーです。安全で正確なコードを出力してください。"},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3,
        "max_tokens": 1200
    }
    return requests.post(url, headers=headers, json=data, timeout=40)

def generate_code(prompt: str, model_choice: str = "deepseek"):
    """DeepSeek → fallback: OpenAI"""
    if model_choice == "openai":
        res = call_openrouter_model(prompt, "openai/o4-mini-deep-research", OPENROUTER_API_KEY_2)
    else:
        res = call_openrouter_model(prompt, "deepseek/deepseek-chat-v3.1:free", OPENROUTER_API_KEY_1)

    if res.status_code == 200:
        try:
            return res.json()["choices"][0]["message"]["content"]
        except Exception as e:
            return f"⚠️ 解析エラー: {e}\n{res.text}"

    # DeepSeek失敗時のフォールバック
    if model_choice == "deepseek":
        print(f"⚠️ DeepSeek失敗: {res.status_code}")
        res2 = call_openrouter_model(prompt, "openai/o4-mini-deep-research", OPENROUTER_API_KEY_2)
        if res2.status_code == 200:
            return f"(Fallback: OpenAI)\n\n{res2.json()['choices'][0]['message']['content']}"
    return f"❌ APIエラー ({res.status_code})\n{res.text}"

def extract_code(text: str):
    """AIの返答からコードブロック部分のみ抽出"""
    match = re.findall(r"```(?:\w+)?\n([\s\S]*?)```", text)
    if match:
        return "\n\n".join(match).strip()
    return text.strip()

# ----------------------------
# Bot設定
# ----------------------------
bot = Bot(
    token=TELEGRAM_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN)
)
dp = Dispatcher()

# ----------------------------
# /start
# ----------------------------
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    user_model_choice[message.from_user.id] = "deepseek"
    user_lang_choice[message.from_user.id] = "python"
    await message.answer(
        "💡 コード生成ボットへようこそ！\n\n"
        "✨ /help で使い方を確認できます。\n"
        "💬 現在のAIモデル: DeepSeek (Free)"
    )

# ----------------------------
# /help
# ----------------------------
@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    help_text = (
        "🧠 **利用可能コマンド一覧**\n\n"
        "🔹 `/start` — ボットを初期化\n"
        "🔹 `/help` — この一覧を表示\n"
        "🔹 `/setmodel <deepseek|openai>` — 使用AIを変更\n"
        "🔹 `/lang <言語>` — 出力言語を指定 (例: `/lang python`, `/lang javascript`)\n"
        "🔹 `/file <プロンプト>` — コードを `.py` ファイルで送信\n"
        "🔹 `/explain <コード>` — コードの意味を解説\n"
        "🔹 `<通常メッセージ>` — コードをテキストで生成\n\n"
        "💡 DeepSeek Free を優先使用し、失敗時は OpenAI に自動切替。"
    )
    await message.answer(help_text, parse_mode="Markdown")

# ----------------------------
# /setmodel
# ----------------------------
@dp.message(Command("setmodel"))
async def cmd_setmodel(message: types.Message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("⚠️ 使用方法: `/setmodel deepseek` または `/setmodel openai`", parse_mode="Markdown")
        return

    choice = args[1].strip().lower()
    if choice not in ["deepseek", "openai"]:
        await message.answer("❌ 無効な指定です。\n選択肢: `deepseek` または `openai`", parse_mode="Markdown")
        return

    user_model_choice[message.from_user.id] = choice
    await message.answer(f"✅ 使用モデルを **{choice}** に変更しました。", parse_mode="Markdown")

# ----------------------------
# /lang
# ----------------------------
@dp.message(Command("lang"))
async def cmd_lang(message: types.Message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("⚠️ 使用方法: `/lang python` や `/lang javascript` など", parse_mode="Markdown")
        return

    lang = args[1].strip().lower()
    user_lang_choice[message.from_user.id] = lang
    await message.answer(f"✅ 出力言語を **{lang}** に設定しました。", parse_mode="Markdown")

# ----------------------------
# /explain
# ----------------------------
@dp.message(Command("explain"))
async def cmd_explain(message: types.Message):
    code_text = message.text.replace("/explain", "").strip()
    if not code_text:
        await message.answer("⚠️ 例: `/explain <コード>`")
        return

    model_choice = user_model_choice.get(message.from_user.id, "deepseek")
    await message.answer(f"🧠 コード内容を解析中...（{model_choice}使用）")

    prompt = f"以下のコードを日本語で丁寧に解説してください:\n\n{code_text}"
    explanation = generate_code(prompt, model_choice)
    await message.answer(f"💬 **解説:**\n{explanation}")

# ----------------------------
# /file
# ----------------------------
@dp.message(Command("file"))
async def cmd_file(message: types.Message):
    prompt = message.text.replace("/file", "").strip()
    if not prompt:
        await message.answer("⚠️ 例: /file PythonでQRコードを作るコード")
        return

    model_choice = user_model_choice.get(message.from_user.id, "deepseek")
    lang_choice = user_lang_choice.get(message.from_user.id, "python")
    await message.answer(f"🧠 コード生成中（{model_choice}使用, 言語: {lang_choice})...")

    prompt_with_lang = f"{prompt}\n出力は{lang_choice}で。コードだけを出力してください。"
    code_raw = generate_code(prompt_with_lang, model_choice)
    code = extract_code(code_raw)

    filename = f"generated_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{ 'js' if 'java' in lang_choice else 'py'}"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(code)

    document = FSInputFile(filename)
    await message.reply_document(document, caption=f"✅ 生成コードです\nモデル: {model_choice}\n言語: {lang_choice}")

# ----------------------------
# 通常メッセージ（コード生成）
# ----------------------------
@dp.message()
async def handle_message(message: types.Message):
    user_text = message.text.strip()
    model_choice = user_model_choice.get(message.from_user.id, "deepseek")
    lang_choice = user_lang_choice.get(message.from_user.id, "python")

    await message.answer(f"🧠 コード生成中...（{model_choice}, 言語: {lang_choice})")

    prompt_with_lang = f"{user_text}\n出力は{lang_choice}で。コードだけを出力してください。"
    code_raw = generate_code(prompt_with_lang, model_choice)
    code = extract_code(code_raw)

    try:
        await message.answer(f"✅ 結果:\n```\n{code}\n```")
    except Exception:
        await message.answer("✅ 結果:\n" + code)

# ----------------------------
# メイン実行
# ----------------------------
async def main():
    print("🤖 Telegram Bot (DeepSeek↔OpenAI + /lang + /explain + /help強化) 起動中...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
