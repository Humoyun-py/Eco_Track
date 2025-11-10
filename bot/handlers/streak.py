from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from utils.database import Database

streak_router = Router()
db = Database()

@streak_router.message(Command("streak"))
async def streak_handler(message: Message):
    user = message.from_user
    
    # Foydalanuvchi ma'lumotlarini olish
    user_data = db.get_user_by_telegram_id(user.id)
    
    if not user_data:
        await message.answer("❌ Siz hali ro'yxatdan o'tmagansiz. /start ni bosing.")
        return
    
    streak = user_data[7]  # streak indeksi
    coins = user_data[5]   # coins indeksi
    
    # Level hisoblash
    level = (streak // 7) + 1
    
    streak_info = f"""
🔥 *Kunlik Streak*

Sizning ketma-ketligingiz: *{streak} kun*
🎯 *Daraja:* {level}

💰 *Joriy coins:* {coins}

🎯 *Keyingi maqsadlar:*
{'✅' if streak >= 7 else '🎯'} 7 kun - 50 coin bonus
{'✅' if streak >= 14 else '🎯'} 14 kun - 100 coin + maxsus nishon
{'✅' if streak >= 30 else '🎯'} 30 kun - 200 coin + "Eco Legend" unvoni

📅 *Streakni saqlash:*
Har kuni botga kirishingiz kifoya!

💡 *Maslahat:* Har kuni kirish va topshiriqlarni bajarish orqali coins yig'ing!
    """
    
    await message.answer(streak_info, parse_mode="Markdown")