# services/payments.py
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram.constants import ParseMode
from datetime import datetime
import pytz
import logging
from utils.files import save_bot_data
from services.users import USERS, save_users
from services.receipt import create_invoice_image, create_receipt_image

logger = logging.getLogger(__name__)

GROUP_ID = -4979712337


def create_click_url(order_id, amount):
    return f"https://my.click.uz/pay/?service_id=999999999&merchant_id=398062629&amount={amount}&transaction_param={order_id}"


async def send_invoice(user_id, order, amount, context):
    text = (
        f"👋 <b>Hurmatli mijoz,</b>\n\n"
        f"Quyidagi xizmat uchun to‘lovni amalga oshiring:\n\n"
        f"🧾 Buyurtma: #{order['order_id']}\n"
        f"📌 Xizmat: {order['service_name']}\n"
        f"💰 Narxi: {amount} so‘m\n"
        f"🕒 Sana: {order['timestamp']}\n\n"
        f"💳 To‘lov kartasi: <code>8600 3104 7319 9081</code>\n"
        f"💬 To‘lovdan so‘ng chekni yuboring.\n"
    )

    markup = InlineKeyboardMarkup([
        [InlineKeyboardButton(
            "📤 Chekni yuborish", callback_data=f"send_receipt_{order['order_id']}")]
    ])

    try:
        image = create_invoice_image(order, amount)
        await context.bot.send_photo(chat_id=user_id, photo=image, caption=text, parse_mode=ParseMode.HTML, reply_markup=markup)
    except:
        await context.bot.send_message(chat_id=user_id, text=text, parse_mode=ParseMode.HTML, reply_markup=markup)

    order['payment_status'] = 'pending'
    context.bot_data[f"payment_{order['order_id']}"] = {
        'user_id': user_id,
        'amount': amount,
        'order_id': order['order_id'],
        'thread_id': context.bot_data.get(f"user_{user_id}", {}).get("thread_id"),
        'status': 'pending'
    }
    save_users(USERS)
    save_bot_data(context)
    logger.info(f"✅ Invoys yuborildi: #{order['order_id']}, user_id={user_id}")


async def confirm_payment(order_id: int, context):
    payment_info = context.bot_data.get(f"payment_{order_id}")
    if not payment_info:
        return False

    user_id = payment_info['user_id']
    user_id_str = str(user_id)
    order = next((o for o in USERS.get(user_id_str, {}).get(
        'orders', []) if o['order_id'] == order_id), None)
    if not order:
        return False

    confirm_time = datetime.now(pytz.timezone(
        'Asia/Tashkent')).strftime('%Y-%m-%d %H:%M:%S')
    payment_info['status'] = 'confirmed'
    payment_info['confirmation_time'] = confirm_time
    order['payment_status'] = 'confirmed'

    save_users(USERS)
    save_bot_data(context)

    try:
        receipt_image = create_receipt_image(
            order, payment_info['amount'], confirm_time)
        await context.bot.send_photo(
            chat_id=user_id,
            photo=receipt_image,
            caption=(
                f"✅ <b>To‘lovingiz tasdiqlandi!</b>\n\n"
                f"🧾 Buyurtma: #{order_id}\n"
                f"📌 Xizmat: {order['service_name']}\n"
                f"💰 Summa: {payment_info['amount']} so‘m\n"
                f"🕒 Vaqt: {confirm_time}\n"
                f"🙏 Rahmat! Xizmat ko‘rsatishga tayyormiz."
            ),
            parse_mode=ParseMode.HTML
        )
    except:
        await context.bot.send_message(
            chat_id=user_id,
            text=f"✅ To‘lovingiz tasdiqlandi! Buyurtma #{order_id}"
        )

    logger.info(f"✅ To‘lov tasdiqlandi: #{order_id}, user_id={user_id}")
    return True
