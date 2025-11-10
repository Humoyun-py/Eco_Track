import asyncio
import logging
from aiogram import Bot, Dispatcher


from handlers.start import start_router
from handlers.shop import shop_router
from handlers.inventory import inventory_router
from handlers.community import community_router
from handlers.news import news_router
from handlers.streak import streak_router
from handlers.energy import energy_router
from handlers.profile import profile_router

# Logging sozlash
logging.basicConfig(level=logging.INFO)

# Bot token
BOT_TOKEN = ("8257163432:AAFmWvYNGMJhi3Ja7bpxKJvukOTkgPBj6oQ")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Routerlarni qo'shish
dp.include_router(start_router)
dp.include_router(shop_router)
dp.include_router(inventory_router)
dp.include_router(community_router)
dp.include_router(news_router)
dp.include_router(streak_router)
dp.include_router(energy_router)
dp.include_router(profile_router)

async def main():
    logging.info("Bot ishga tushdi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())