from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from utils.database import Database

shop_router = Router()
db = Database()

@shop_router.message(Command("shop"))
async def shop_handler(message: Message):
    user = message.from_user
    
    # Foydalanuvchi coins larini olish
    user_data = db.get_user_by_telegram_id(user.id)
    
    if not user_data:
        await message.answer("❌ Siz hali ro'yxatdan o'tmagansiz. /start ni bosing.")
        return
    
    coins = user_data[5]  # coins indeksi
    
    shop_text = f"""
🛍️ *EcoVerse Do'koni*

💰 *Sizning coinslaringiz:* {coins}

*Top mahsulotlar:*

🌿 *Yashil Kepka* - 30 coin
   Ekologik uslubdagi maxsus kepka

👜 *Eco Sumka* - 50 coin  
   Qayta ishlangan materialdan tayyorlangan

🖼️ *O'simlik Fon* - 100 coin
   Profil uchun maxsus fon

🌳 *Daraxt Nishoni* - 75 coin
   Maxsus ekologik nishon

💧 *Suv Idishi* - 40 coin
   Qayta ishlatiladigan idish

📚 *Kitob: Ekologiya Asoslari* - 60 coin
   Bilimingizni oshiring

🔋 *Quyosh Batareyasi* - 150 coin
   Maxsus energiya manbai

⚠️ *Eslatma:* Coinslarni topshiriqlarni bajarish orqali yig'ishingiz mumkin!
Web ilovamizda barcha mahsulotlarni ko'rishingiz va sotib olishingiz mumkin!
    """
    
    await message.answer(shop_text, parse_mode="Markdown")