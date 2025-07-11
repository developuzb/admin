# handlers/
from telegram.ext import CommandHandler, CallbackQueryHandler, MessageHandler, InlineQueryHandler, ConversationHandler, filters
from aiogram import Dispatcher, F
from aiogram.types import Message, CallbackQuery

# Import handlers
from services.flow import (
    trigger_inline_handler, roziman_handler,
    phone_handler, contact_method_handler,
    contact_time_handler, WAIT_PHONE, WAIT_CONTACT_METHOD, WAIT_CONTACT_TIME
)
from handlers.help import help_request_handler, accept_help_button_handler
from services.orders import command_in_topic_handler, send_rating_request

# Example start handler (placeholder)


async def start(update, context):
    await update.message.reply_text("👋 Assalomu alaykum! Xush kelibsiz.")


# Rating handler (stub)
async def rating_callback_handler(update, context):
    query = update.callback_query
    await query.answer()
    await query.message.reply_text("⭐ Reyting qabul qilindi. Rahmat!")


def setup_handlers(app):
    # /start
    app.add_handler(CommandHandler("start", start))

    # Inline handler: #XIZMAT#123
    app.add_handler(MessageHandler(filters.Regex(
        r"^#XIZMAT#\d+$"), trigger_inline_handler))

    # Roziman
    app.add_handler(CallbackQueryHandler(
        roziman_handler, pattern="^confirm_service$"))

    # Telefon
    app.add_handler(MessageHandler(
        filters.CONTACT | filters.TEXT, phone_handler))

    # Aloqa usuli
    app.add_handler(CallbackQueryHandler(contact_method_handler,
                    pattern="^contact_(bot|call|sms|other)$"))

    # Aloqa vaqti
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, contact_time_handler))

    # Yordam
    app.add_handler(CallbackQueryHandler(
        help_request_handler, pattern="^help_request$"))
    app.add_handler(CallbackQueryHandler(
        accept_help_button_handler, pattern="^accept_help_"))

    # Guruhdan /bajarildi va /bekor
    app.add_handler(MessageHandler(filters.Regex(
        r"^/(bajarildi|bekor)"), command_in_topic_handler))

    # Baholash callback
    app.add_handler(CallbackQueryHandler(
        rating_callback_handler, pattern="^rate_"))
