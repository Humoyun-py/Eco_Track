from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
import requests

news_router = Router()

@news_router.message(Command("news"))
async def news_handler(message: Message):
    news_text = """
📢 *So'nggi Ekologik Yangiliklar*

*🌍 Global Isish Darajasi*
Yangi hisobotga ko'ra, global isish darajasi rekord darajaga chiqdi.

*🌳 O'rmonlarni qayta tiklash*
Yil davomida 1 million gektar maydonda o'rmonlar qayta tiklandi.

*♻️ Qayta ishlash yangiliklari*
Yangi qayta ishlash texnologiyasi chiqdi - 90% samaradorlik.

*💧 Suv muammosi*
Suv resurslarini tejash bo'yicha yangi dastur ishga tushirildi.

*Yangiliklar har soat yangilanadi!*
    """
    
    await message.answer(news_text, parse_mode="Markdown")