from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_continue_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔁 続きのコードを生成", callback_data="continue_code")],
        [InlineKeyboardButton(text="🆕 別のテーマで作る", callback_data="new_code")]
    ])
