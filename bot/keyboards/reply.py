from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_main_reply_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🛍️ Do'kon"), KeyboardButton(text="🎒 Inventory")],
            [KeyboardButton(text="🔥 Streak"), KeyboardButton(text="⚡ Energiya")],
            [KeyboardButton(text="👥 Community"), KeyboardButton(text="📢 Yangiliklar")]
        ],
        resize_keyboard=True,
        input_field_placeholder="Buyruq tanlang..."
    )
    return keyboard