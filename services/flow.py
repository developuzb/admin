# services/flow.py
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.constants import ParseMode
from datetime import datetime
import re
import pytz
import json
from services.orders import send_order_to_group
from services.users import save_users
from services.users import USERS
from utils.files import get_next_order_number
from utils.misc import get_services, create_click_url
from aiogram.types import Message

GROUP_ID = -4979712337

WAIT_PHONE, WAIT_CONTACT_METHOD, WAIT_CONTACT_TIME = range(3)


async def trigger_inline_handler(update, context):
    try:
        text = update.message.text.strip()
        service_id = int(text.replace("#XIZMAT#", ""))
    except:
        await update.message.reply_text("❌ Xizmat topilmadi.")
        return

    services = get_services()
    service = next((s for s in services if s['id'] == service_id), None)
    if not service:
        await update.message.reply_text("❌ Bunday xizmat topilmadi.")
        return

    order_id = get_next_order_number()
    context.user_data.update({
        'selected_service': service,
        'order_id': order_id,
        'user_id': update.effective_user.id,
        'step': 'waiting_for_phone'
    })

    caption = (
        f"📌 <b>{service['name']}</b>\n"
        f"💰 {service['price']} so‘m\n"
        f"💳 To‘lov: {', '.join(service['payment_methods'])}\n"
        f"🧾 Buyurtma raqami: <b>#{order_id}</b>\n\n"
        "❗ Agar rozimisiz, pastdagi tugmani bosing."
    )
    buttons = [[InlineKeyboardButton(
        "✅ Roziman", callback_data="confirm_service")]]
    if 'Click' in service['payment_methods']:
        buttons.insert(0, [InlineKeyboardButton(
            "💳 Click orqali to‘lash", url=create_click_url(order_id, service['price']))])

    markup = InlineKeyboardMarkup(buttons)
    await update.message.reply_photo(photo=service['image'], caption=caption, parse_mode=ParseMode.HTML, reply_markup=markup) if service.get('image') else await update.message.reply_text(caption, parse_mode=ParseMode.HTML, reply_markup=markup)
    return WAIT_PHONE


async def roziman_handler(update, context):
    query = update.callback_query
    await query.answer()

    markup = ReplyKeyboardMarkup([[KeyboardButton(
        "📱 Telefon raqamni yuborish", request_contact=True)]], resize_keyboard=True)
    await query.message.reply_text("📞 Telefon raqamingizni yuboring:", reply_markup=markup)
    context.user_data['step'] = 'waiting_for_phone'
    return WAIT_PHONE


async def phone_handler(message: Message, **kwargs):
    if message.contact:
        phone = message.contact.phone_number
        await message.answer(f"📱 Sizning raqamingiz: {phone}")
    else:
        await message.answer("📱 Iltimos, telefon raqamingizni yuboring.")


async def contact_method_handler(update, context):
    query = update.callback_query
    await query.answer()

    method_map = {
        "contact_bot": "📱 Shu bot orqali",
        "contact_call": "☎️ Qo‘ng‘iroq orqali",
        "contact_sms": "📩 SMS orqali",
        "contact_other": "🔄 Boshqa usul"
    }
    selected = method_map.get(query.data)
    if not selected:
        await query.message.reply_text("❌ Noma'lum aloqa usuli.")
        return WAIT_CONTACT_METHOD

    context.user_data['contact_method'] = selected
    context.user_data['step'] = 'waiting_for_time'
    await query.message.reply_text("🕒 Siz bilan qachon bog‘lanishimizni xohlaysiz?")
    return WAIT_CONTACT_TIME


async def contact_time_handler(update, context):
    contact_time = update.message.text.strip()
    user_id = context.user_data.get('user_id')
    order_id = context.user_data.get('order_id')
    service = context.user_data.get('selected_service')
    phone = context.user_data.get('phone')
    contact_method = context.user_data.get('contact_method')

    if not all([user_id, order_id, service, phone, contact_method, contact_time]):
        await update.message.reply_text("⚠️ Jarayonda xatolik. /start bilan qaytadan urinib ko‘ring.")
        return

    timestamp = datetime.now(pytz.timezone(
        'Asia/Tashkent')).strftime('%Y-%m-%d %H:%M:%S')
    user_str = str(user_id)
    if user_str not in USERS:
        USERS[user_str] = {'name': None, 'phone': phone,
                           'orders': [], 'rated_identifiers': []}
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

    # Topic ochish
    topic = await context.bot.create_forum_topic(chat_id=GROUP_ID, name=f"#{order_id} - {service['name']}")
    text = (
        f"🧾 Buyurtma raqami: <b>#{order_id}</b>\n"
        f"🆔 Xizmat ID: <code>{service['id']}</code>\n"
        f"📌 Nomi: <b>{service['name']}</b>\n"
        f"📞 Raqam: <code>{phone}</code>\n"
        f"📱 Aloqa usuli: <i>{contact_method}</i>\n"
        f"⏰ Aloqa vaqti: <i>{contact_time}</i>"
    )
    await send_order_to_group(context, order_id, service, phone, contact_method, contact_time, text, topic.message_thread_id, user_id)

    await update.message.reply_text("✅ Buyurtmangiz qabul qilindi!", reply_markup=ReplyKeyboardRemove())
    context.user_data.clear()
    return
