# handlers/help.py
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
import logging
from utils.files import save_bot_data

logger = logging.getLogger(__name__)

GROUP_ID = -4979712337


async def help_request_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    name = query.from_user.full_name or f"ID {user_id}"

    user_key = f"user_{user_id}"
    existing = context.bot_data.get(user_key)

    if existing and existing.get("thread_id") and existing.get("is_operator_started"):
        thread_id = existing["thread_id"]
        await query.message.edit_text(
            "🆘 Operator bilan suhbat allaqachon ochilgan. Savolingizni yozing.",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("🔁 Qayta boshlash", callback_data="restart")]])
        )
        return

    topic = await context.bot.create_forum_topic(
        chat_id=GROUP_ID,
        name=f"🦸 Yordam — {name[:50]}"
    )

    await context.bot.send_message(
        chat_id=GROUP_ID,
        message_thread_id=topic.message_thread_id,
        text=(
            f"🆘 <b>Yordam so‘rovi</b>\n\n"
            f"👤 Mijoz: {name}\n"
            f"📩 Iltimos, savolni kuting yoki qabul qiling."
        ),
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton(
                "✅ Qabul qilish", callback_data=f"accept_help_{user_id}")]
        ])
    )

    context.bot_data[user_key] = {
        "thread_id": topic.message_thread_id,
        "help_question": True,
        "is_operator_started": False
    }
    context.bot_data[f"thread_{topic.message_thread_id}"] = {
        "user_id": user_id,
        "order_id": None
    }
    save_bot_data(context)

    await query.message.edit_text(
        "✅ Yordam so‘rovingiz qabul qilindi! Savolingizni yozing.",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("🔁 Qayta boshlash", callback_data="restart")]])
    )
    context.user_data["step"] = "waiting_for_help_question"


async def accept_help_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    if not data.startswith("accept_help_"):
        return

    user_id = int(data.replace("accept_help_", ""))
    user_key = f"user_{user_id}"

    await query.message.reply_text("✅ Operator so‘rovni qabul qildi.")
    try:
        await context.bot.send_message(
            chat_id=user_id,
            text="👨‍💻 Operator ulandi. Savolingizni yozishingiz mumkin."
        )
        if user_key in context.bot_data:
            context.bot_data[user_key]['is_operator_started'] = True
            save_bot_data(context)
    except Exception as e:
        logger.error(f"❌ Mijozga yozishda xato: {e}")
