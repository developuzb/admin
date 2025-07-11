from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
import asyncio
from config import BOT_TOKEN
from handlers.register_handlers import register_handlers
from handlers.inline import inline_query_handler
# from handlers.service_details import send_service_details  # yoki confirm.py
from services.service_details import send_service_details
import sys
import os


bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())
dp.inline_query.register(inline_query_handler)
dp.message.register(send_service_details,
                    lambda msg: msg.text.startswith("#XIZMAT#"))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


async def main():
    print("🚀 Bot ishga tushdi!")
    register_handlers(dp)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
