from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

energy_router = Router()

@energy_router.message(Command("energy"))
async def energy_handler(message: Message):
    energy_info = """
⚡ *Energiya Tizimi*

Joriy energiya: *75/100*

📊 *Energiya sarflash:*
• Topshiriq bajarish - 10 energiya
• Post yozish - 5 energiya  
• Izoh yozish - 2 energiya

🔄 *Energiya to'ldirish:*
• Kunlik kirish - +10 energiya
• Streak bonus - +5-20 energiya
• Vazifa bonuslari - +5-15 energiya

⏰ *Keyingi to'ldirish:* 8 soat

Energiya har kun soat 00:00 da to'liq to'lanadi!
    """
    
    await message.answer(energy_info, parse_mode="Markdown")