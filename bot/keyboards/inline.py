from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_main_menu():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🛍️ Do'kon", callback_data="shop")],
            [InlineKeyboardButton(text="🎒 Inventory", callback_data="inventory")],
            [InlineKeyboardButton(text="🔥 Streak", callback_data="streak")],
            [InlineKeyboardButton(text="⚡ Energiya", callback_data="energy")],
            [InlineKeyboardButton(text="👥 Community", callback_data="community")],
            [InlineKeyboardButton(text="📢 Yangiliklar", callback_data="news")]
        ]
    )
    return keyboard

def get_shop_keyboard():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🌿 Kiyimlar", callback_data="shop_clothes")],
            [InlineKeyboardButton(text="👜 Aksessuarlar", callback_data="shop_accessories")],
            [InlineKeyboardButton(text="🖼️ Fonlar", callback_data="shop_backgrounds")],
            [InlineKeyboardButton(text="🔙 Orqaga", callback_data="main_menu")]
        ]
    )
    return keyboard