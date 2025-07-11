from aiogram import Dispatcher
from handlers import admin, users

async def register_handlers(dp: Dispatcher):
    dp.include_router(admin.router)
    dp.include_router(users.router)
