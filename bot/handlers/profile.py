from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from utils.database import Database

profile_router = Router()
db = Database()

@profile_router.message(Command("profile"))
async def profile_handler(message: Message):
    user = message.from_user
    
    user_data = db.get_user_by_telegram_id(user.id)
    
    if not user_data:
        await message.answer("❌ Siz hali ro'yxatdan o'tmagansiz. /start ni bosing.")
        return
    
    user_id, username, email, password_hash, role, coins, energy, streak, last_login, created_at = user_data
    
    profile_text = (
        f"👤 *Sizning Profilingiz*\n\n"
        f"📛 *Ism:* {user.first_name} {user.last_name or ''}\n"
        f"👤 *Username:* @{user.username or 'Yoq'}\n"
        f"🎮 *Rol:* {role.capitalize()}\n\n"
        f"💰 *Coins:* {coins}\n"
        f"⚡ *Energiya:* {energy}\n"
        f"🔥 *Streak:* {streak} kun\n\n"
        f"📅 *Ro'yxatdan o'tgan sana:* {created_at.split()[0] if created_at else 'Nomanium'}\n\n"
        f"💡 *Coins yigish uchun:*\n"
        f"- Topshiriqlarni bajarish\n"
        f"- Kunlik kirish\n"
        f"- Streak bonuslari"
    )
    
    await message.answer(profile_text, parse_mode="Markdown")