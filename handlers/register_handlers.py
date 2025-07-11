# handlers/register_handlers.py
from services.service_details import (
    send_service_details,
    handle_confirm_service,
    handle_contact
)
from aiogram import types
from aiogram import Dispatcher, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from handlers.inline import inline_query_handler
from aiogram import F

from SQlite2.SQlite2.services.keraksiz import (
    trigger_inline_handler, roziman_handler,
    phone_handler, contact_method_handler, contact_time_handler
)
# from services.orders import command_in_topic_handler
from handlers.help import help_request_handler, accept_help_button_handler

# /start buyruq


async def start(message: Message):
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📩 Buyurtma berish",
                              switch_inline_query_current_chat="")],
        [InlineKeyboardButton(text="💬 Yordam", callback_data="help_request")],
        [InlineKeyboardButton(text="🧾 Mening buyurtmalarim",
                              callback_data="my_orders")],
        [InlineKeyboardButton(text="💰 Cashback", callback_data="cashback")],
    ])
    await message.answer(
        "👋 Assalomu alaykum! Xush kelibsiz.\nQuyidagilardan birini tanlang:",
        reply_markup=markup
    )

# Baholash callback


async def test_send_photo(message: Message):
    await message.answer_photo(
        photo="https://via.placeholder.com/600x400.png?text=AVTO+SUGURTA",
        caption="🚗 AVTO SUG'URTA\n⏱ 1 soat\n💰 Cashback: 5000 so'm"
    )


async def rating_callback(call: CallbackQuery):
    await call.answer()
    await call.message.answer("⭐ Reyting uchun rahmat!")


def register_handlers(dp):
    dp.message.register(send_service_details,
                        lambda msg: msg.text.startswith("#XIZMAT#"))
    dp.callback_query.register(
        handle_confirm_service, lambda c: c.data.startswith("confirm_service"))
    dp.message.register(handle_contact, lambda msg: msg.contact)

    # Aloqa usuli
    dp.callback_query.register(
        contact_method_handler, F.data.startswith("contact_"))

    # Aloqa vaqti
    dp.message.register(contact_time_handler, F.text & ~F.text.startswith("/"))

    # Yordam so‘rovi
    dp.callback_query.register(help_request_handler, F.data == "help_request")
    dp.callback_query.register(
        accept_help_button_handler, F.data.startswith("accept_help_"))

    # Guruhdagi komandalar
    dp.message.register(command_in_topic_handler, F.text.startswith(
        "/bajarildi") | F.text.startswith("/bekor"))

    # Reyting tugmalari
    dp.callback_query.register(rating_callback, F.data.startswith("rate_"))

    # Inline so‘rovlar
    dp.inline_query.register(inline_query_handler)

    # Test tugmasi
    dp.message.register(test_send_photo, F.text == "/test")

    # Telefon qabul qilish
    dp.message.register(phone_handler, F.contact | F.text)
