from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from uuid import uuid4
import asyncio
import aiohttp
from datetime import datetime
import pytz
from services.users import USERS, save_users
from utils.misc import create_click_url
from utils.files import get_next_order_number
from services.orders import send_order_to_group

API_URL = "http://localhost:8000/api/services/"
DEFAULT_IMAGE = "https://cdn-icons-png.flaticon.com/512/9068/9068756.png"
GROUP_ID = -4979712337

WAIT_PHONE = 0


def get_confirmation_keyboard(service_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Qabul qilish",
                                 callback_data=f"confirm_service:{service_id}"),
            InlineKeyboardButton(
                text="🔙 Orqaga", callback_data="cancel_service")
        ]
    ])


async def send_service_details(message: types.Message):
    try:
        service_id = message.text.replace("#XIZMAT#", "").strip()
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{API_URL}{service_id}") as resp:
                if resp.status != 200:
                    await message.answer("❌ Xizmat topilmadi.")
                    return
                service = await resp.json()

        order_id = get_next_order_number()
        message.bot['user_data'] = {
            'selected_service': service,
            'order_id': order_id,
            'user_id': message.from_user.id,
            'step': 'waiting_for_phone'
        }

        eski_narx = 12550
        chegirma_narx = 11500
        cashback = service.get("cashback", 0)
        duration = service.get("duration", "—")
        image_url = service.get("image_url") or DEFAULT_IMAGE

        caption = (
            f"<b>✅ Tanlangan xizmat:</b> {service['name']}\n\n"
            f"<b>⏱ Bajarilish vaqti:</b> atigi <b>{duration} daqiqa</b>da tayyor!\n\n"
            f"<b>💸 Narx:</b> <s>{eski_narx:,} so‘m</s> → <b><u>{chegirma_narx:,} so‘m</u></b>\n"
            f"<b>🎁 Cashback:</b> <b>{cashback}%</b> — xizmat tugagach qaytariladi\n\n"
            f"<b>🔥 Qulay narx + tezkor xizmat = to‘g‘ri tanlov</b>\n\n"
            f"Quyidagilardan birini tanlang:"
        )

        keyboard = get_confirmation_keyboard(service_id)
        await message.answer_photo(
            photo=image_url,
            caption=caption,
            reply_markup=keyboard,
            parse_mode="HTML"
        )

        await asyncio.sleep(2)
        tafovut = eski_narx - chegirma_narx
        cashback_sum = int(chegirma_narx * cashback / 100)
        jami_foyda = tafovut + cashback_sum

        await message.answer(
            f"🎯 Siz jami <b>{jami_foyda:,} so‘m</b> foyda qilasiz! 💰",
            parse_mode="HTML"
        )

    except Exception as e:
        print("Xatolik:", e)
        await message.answer("⚠️ Xizmatni ko‘rsatishda xatolik yuz berdi.")


async def handle_confirm_service(callback_query: types.CallbackQuery):
    await callback_query.answer()
    markup = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📱 Telefon raqamni yuborish", request_contact=True)]],
        resize_keyboard=True
    )
    await callback_query.message.answer("📞 Telefon raqamingizni yuboring:", reply_markup=markup)


async def handle_contact(message: types.Message):
    if message.contact:
        phone = message.contact.phone_number
        await message.answer(f"📱 Sizning raqamingiz: {phone}")
        # Bu yerda user_data dan ma'lumotlar olinadi
        user_data = message.bot.get('user_data', {})
        service = user_data.get('selected_service')
        order_id = user_data.get('order_id')
        contact_method = "Bot orqali"
        contact_time = datetime.now().strftime("%H:%M")
        user_id = message.from_user.id
        timestamp = datetime.now(pytz.timezone(
            'Asia/Tashkent')).strftime('%Y-%m-%d %H:%M:%S')

        user_str = str(user_id)
        USERS.setdefault(
            user_str, {'name': None, 'phone': phone, 'orders': [], 'rated_identifiers': []})
        USERS[user_str]['orders'].append({
            'order_id': order_id,
            'service_id': service['id'],
            'service_name': service['name'],
            'contact_method': contact_method,
            'contact_time': contact_time,
            'status': 'pending',
            'timestamp': timestamp
        })
        save_users(USERS)

        topic = await message.bot.create_forum_topic(chat_id=GROUP_ID, name=f"#{order_id} - {service['name']}")
        text = (
            f"🧾 Buyurtma raqami: <b>#{order_id}</b>\n"
            f"🆔 Xizmat ID: <code>{service['id']}</code>\n"
            f"📌 Nomi: <b>{service['name']}</b>\n"
            f"📞 Raqam: <code>{phone}</code>\n"
            f"📱 Aloqa usuli: <i>{contact_method}</i>\n"
            f"⏰ Aloqa vaqti: <i>{contact_time}</i>"
        )
