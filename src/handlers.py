from aiogram import types, Router, F
from aiogram.filters import Command
from src.deepseek_api import generate_code
from src.utils import get_user_setting, set_user_setting, save_code_to_file
from src.keyboards import get_continue_keyboard

router = Router()

def register_handlers(dp):
    dp.include_router(router)

@router.message(Command("start"))
async def cmd_start(msg: types.Message):
    await msg.answer("💡 コード生成Botです！\n`/help`でコマンド一覧を確認できます。")

@router.message(Command("help"))
async def cmd_help(msg: types.Message):
    await msg.answer(
        "🧠 **CodeWriter v2.0 コマンド一覧**\n\n"
        "/lang <言語> — 出力言語設定（例: /lang Python）\n"
        "/length <short|medium|long> — コードの長さ設定\n"
        "/file <説明> — コードをファイルで生成\n"
        "/file_structure — 生成コードの構成を表示\n"
        "/help — この説明を表示"
    )

@router.message(Command("lang"))
async def cmd_lang(msg: types.Message):
    lang = msg.text.replace("/lang", "").strip()
    if not lang:
        await msg.answer("⚠️ 例: /lang Python")
        return
    set_user_setting(msg.from_user.id, "lang", lang)
    await msg.answer(f"✅ 言語を `{lang}` に設定しました。")

@router.message(Command("length"))
async def cmd_length(msg: types.Message):
    length = msg.text.replace("/length", "").strip().lower()
    if length not in ["short", "medium", "long"]:
        await msg.answer("⚠️ 例: /length short | medium | long")
        return
    set_user_setting(msg.from_user.id, "length", length)
    await msg.answer(f"✅ コード長を `{length}` に設定しました。")

@router.message(Command("file"))
async def cmd_file(msg: types.Message):
    prompt = msg.text.replace("/file", "").strip()
    if not prompt:
        await msg.answer("⚠️ 例: /file PythonでQRコードを作るコード")
        return

    await msg.answer("🧠 コード生成中...")

    lang = get_user_setting(msg.from_user.id, "lang", "Python")
    length = get_user_setting(msg.from_user.id, "length", "medium")
    code = generate_code(prompt, length, lang)

    filename = save_code_to_file(code)
    await msg.reply_document(types.FSInputFile(filename), caption="✅ コード生成完了", reply_markup=get_continue_keyboard())

@router.message(Command("file_structure"))
async def cmd_structure(msg: types.Message):
    await msg.answer(
        "📂 一般的なPythonプロジェクト構成:\n"
        "├── main.py\n"
        "├── src/\n"
        "│   ├── __init__.py\n"
        "│   ├── handlers.py\n"
        "│   ├── utils.py\n"
        "└── requirements.txt"
    )

@router.callback_query(F.data == "continue_code")
async def cb_continue(callback: types.CallbackQuery):
    await callback.message.answer("🔁 続きのコードを生成したい内容を入力してください！")

@router.callback_query(F.data == "new_code")
async def cb_new(callback: types.CallbackQuery):
    await callback.message.answer("🆕 新しいテーマのコード説明を入力してください！")
