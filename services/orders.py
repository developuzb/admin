# services/orders.py
import logging
from datetime import datetime
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from utils.files import save_bot_data
from services.users import save_users
from services.users import USERS

logger = logging.getLogger(__name__)

GROUP_ID = -4979712337  # Group ID where topics are created


async def send_order_to_group(context, order_id, service, phone, contact_method, contact_time, text, thread_id, user_id):
    buttons = [[
        InlineKeyboardButton(
            "✅ Qabul qilindi", callback_data=f"group_accept_{order_id}"),
        InlineKeyboardButton(
            "❌ Bekor qilindi", callback_data=f"group_cancel_{order_id}")
    ]]
    reply_markup = InlineKeyboardMarkup(buttons)

    msg = await context.bot.send_message(
        chat_id=GROUP_ID,
        message_thread_id=thread_id,
        text=(f"📥 <b>Yangi buyurtma qabul qilindi!</b>\n\n{text}\n"
              f"📌 <b>Buyurtmani qabul qilish yoki bekor qilish uchun tugmalardan foydalaning.</b>"),
        reply_markup=reply_markup,
        parse_mode=ParseMode.HTML
    )

    context.bot_data[f"msg_{msg.message_id}"] = {
        'user_id': user_id,
        'order_id': order_id,
        'thread_id': thread_id
    }
    context.bot_data[f"user_{user_id}"] = {
        'order_id': order_id,
        'thread_id': thread_id,
        'is_operator_started': False
    }
    context.bot_data[f"thread_{thread_id}"] = {
        'user_id': user_id,
        'order_id': order_id
    }
    logger.info(
        f"✅ Buyurtma guruhga yuborildi: #{order_id}, thread={thread_id}")


async def command_in_topic_handler(update, context):
    message = update.message
    thread_id = message.message_thread_id
    info = context.bot_data.get(f"thread_{thread_id}")

    if not info:
        await message.reply_text("❌ Foydalanuvchi topilmadi.")
        return

    user_id = info.get("user_id")
    order_id = info.get("order_id")
    user_id_str = str(user_id)

    if message.text.startswith("/bekor"):
        reason = message.text.replace(
            "/bekor", "").strip() or "Sababsiz bekor qilindi"
        for order in USERS.get(user_id_str, {}).get("orders", []):
            if order['order_id'] == order_id:
                order['status'] = 'cancelled'
                break
        save_users(USERS)

        await context.bot.send_message(chat_id=user_id, text=f"❌ Buyurtmangiz bekor qilindi.\n📄 Sabab: {reason}")

    elif message.text.startswith("/bajarildi"):
        for order in USERS.get(user_id_str, {}).get("orders", []):
            if order['order_id'] == order_id:
                order['status'] = 'completed'
                break
        save_users(USERS)

        await context.bot.send_message(chat_id=user_id, text="✅ Buyurtmangiz muvaffaqiyatli bajarildi!")

    await send_rating_request(user_id, str(order_id), context)
    await context.bot.delete_forum_topic(chat_id=GROUP_ID, message_thread_id=thread_id)

    context.bot_data.pop(f"user_{user_id}", None)
    context.bot_data.pop(f"thread_{thread_id}", None)
    for key in list(context.bot_data):
        if key.startswith("msg_") and context.bot_data[key].get("thread_id") == thread_id:
            context.bot_data.pop(key, None)


async def send_rating_request(user_id: int, identifier: str, context, is_help_request: bool = False):
    markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("1 😞", callback_data=f"rate_{identifier}_1"),
         InlineKeyboardButton("2 😕", callback_data=f"rate_{identifier}_2"),
         InlineKeyboardButton("3 😐", callback_data=f"rate_{identifier}_3"),
         InlineKeyboardButton("4 🙂", callback_data=f"rate_{identifier}_4"),
         InlineKeyboardButton("5 🤩", callback_data=f"rate_{identifier}_5")]
    ])
    text = f"📝 {'Yordam so‘rovingiz' if is_help_request else f'Buyurtma #{identifier}'} uchun xizmat sifatini baholang:"

    await context.bot.send_message(
        chat_id=user_id,
        text=text,
        reply_markup=markup
    )
    logger.info(
        f"✅ Baholash so‘rovi yuborildi: user_id={user_id}, identifier={identifier}")
