from aiogram import Router, F
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from aiogram.filters import Command
# from services.users import update_user, get_user
from services.order_counter import get_next_order_number
from config import ADMIN_ID

router = Router()


@router.message(Command("start"))
async def start_handler(message: Message):
    update_user(message.from_user.id, name=message.from_user.full_name)
    await message.answer(
        f"Assalomu alaykum, {message.from_user.full_name}! 😊\n"
        f"Buyurtma berish uchun telefon raqamingizni yuboring:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="📞 Raqamni yuborish", request_contact=True)]],
            resize_keyboard=True
        )
    )


@router.message(F.contact)
async def handle_contact(message: Message):
    phone = message.contact.phone_number
    update_user(message.from_user.id, phone=phone)
    await message.answer("☎️ Raqamingiz qabul qilindi.\nQaysi vaqtda bog‘lansak bo‘ladi?", reply_markup=ReplyKeyboardRemove())


@router.message(F.text)
async def handle_time(message: Message):
    user_data = get_user(message.from_user.id)
    if not user_data or "phone" not in user_data:
        await message.answer("Iltimos, /start buyrug‘i orqali qaytadan boshlang.")
        return

    contact_time = message.text
    order_id = get_next_order_number()
    user_name = user_data.get("name")
    phone = user_data.get("phone")

    order_text = (
        f"🆕 <b>Yangi buyurtma</b> #{order_id}\n\n"
        f"👤 {user_name}\n"
        f"📞 {phone}\n"
        f"🕒 Bog‘lanish vaqti: {contact_time}"
    )

    await message.answer("✅ Buyurtmangiz qabul qilindi!")
    await message.bot.send_message(chat_id=ADMIN_ID, text=order_text)
