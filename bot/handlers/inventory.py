from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

inventory_router = Router()

@inventory_router.message(Command("inventory"))
async def inventory_handler(message: Message):
    inventory_text = """
🎒 *Sizning Inventoryingiz*

*Kiyimlar:*
✅ Yashil Kepka (Faol)
✅ Ekologik Futbolka

*Aksessuarlar:*
✅ Eco Sumka
⛔ Daraxt Nishoni (Faol emas)

*Fonlar:*
⛔ O'simlik Fon (Faol emas)

*Umumiy: 4 ta buyum*

Buyumni faollashtirish uchun web ilovamizdan foydalaning!
    """
    
    await message.answer(inventory_text, parse_mode="Markdown")