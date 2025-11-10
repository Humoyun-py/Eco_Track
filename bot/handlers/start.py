from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from utils.database import Database

start_router = Router()
db = Database()

@start_router.message(Command("start"))
async def start_handler(message: Message):
    user = message.from_user
    
    # Foydalanuvchini tekshirish va ro'yxatdan o'tkazish
    existing_user = db.get_user_by_telegram_id(user.id)
    
    if not existing_user:
        # Ro'yxatdan o'tkazish
        success = db.create_telegram_user({
            'id': user.id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name
        })
        
        if success:
            welcome_text = f"""
🌍 *EcoVerse Botiga Xush Kelibsiz!*

Salom {user.first_name}! Siz muvaffaqiyatli ro'yxatdan o'tdingiz.

💰 *Boshlang'ich bonus:* 0 coin
⚡ *Energiya:* 100
🔥 *Streak:* 0 kun

📊 *Mavjud komandalar:*
/shop - Do'kondan buyumlar xarid qiling
/inventory - Sotib olgan buyumlaringizni ko'ring  
/streak - Kunlik ketma-ketligingizni ko'ring
/energy - Energiya miqdoringiz
/community - Jamoa postlari
/news - Ekologik yangiliklar
/profile - Profilingiz

💡 *Eslatma:* Coinslarni topshiriqlarni bajarish orqali yig'ishingiz mumkin!
            """
        else:
            welcome_text = "❌ Ro'yxatdan o'tishda xatolik yuz berdi. Iltimos, qayta urinib ko'ring."
    else:
        # Mavjud foydalanuvchi
        user_id, username, email, password_hash, role, coins, energy, streak, last_login, created_at = existing_user
        
        welcome_text = f"""
🌍 *EcoVerse ga Xush Kelibsiz!*

Salom {user.first_name}! Sizning profilingiz:

💰 *Coins:* {coins}
⚡ *Energiya:* {energy}
🔥 *Streak:* {streak} kun

📊 *Mavjud komandalar:*
/shop - Do'kon
/inventory - Inventory  
/streak - Streak
/energy - Energiya
/community - Community
/news - Yangiliklar
/profile - Profil
        """
    
    await message.answer(welcome_text, parse_mode="Markdown")