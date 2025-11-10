from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from datetime import datetime

community_router = Router()

@community_router.message(Command("community"))
async def community_handler(message: Message):
    community_text = """
👥 *So'nggi Community Postlari*

*📝 Plastikni qayta ishlash bo'yicha maslahat*
"Har kuni 3 ta plastik idishni qayta ishlash markaziga olib boring"
👤 **Ali** | 📅 Bugun | 💬 5 ta izoh

*🌳 Daraxt ekish aksiyasi*
"Yakshanba kuni shahar bog'ida daraxt ekamiz. Hammingizni taklif qilamiz!"
👤 **Malika** | 📅 Kecha | 💬 12 ta izoh  

*💡 Energiya tejash*
"Uyda energiya tejash bo'yicha 10 ta oddiy maslahat"
👤 **Sardor** | 📅 2 kun oldin | 💬 8 ta izoh

Batafsil ma'lumot va yangi postlar uchun web ilovamizga kiring!
    """
    
    await message.answer(community_text, parse_mode="Markdown")