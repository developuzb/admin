from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from services.metrics import get_segment, set_segment, mark_loyal, is_loyal, load_metrics
# from services.users import list_users
from config import ADMIN_ID

router = Router()


@router.message(Command("panel"), F.from_user.id == ADMIN_ID)
async def admin_panel(message: Message):
    users = list_users()
    metrics = load_metrics()

    total = len(users)
    loyal = sum(1 for u in metrics.values() if u.get("loyal"))
    a_users = sum(1 for u in metrics.values() if u.get("segment") == "A")
    b_users = sum(1 for u in metrics.values() if u.get("segment") == "B")

    await message.answer(
        f"📊 <b>Admin panel</b>\n\n"
        f"👥 Jami foydalanuvchilar: <b>{total}</b>\n"
        f"🅰️ Segment A: <b>{a_users}</b>\n"
        f"🅱️ Segment B: <b>{b_users}</b>\n"
        f"💎 Sodiq mijozlar: <b>{loyal}</b>"
    )


@router.message(Command("abtest"), F.from_user.id == ADMIN_ID)
async def abtest_change(message: Message):
    try:
        _, user_id_str, segment = message.text.split()
        user_id = int(user_id_str)
        segment = segment.upper()

        if segment not in ["A", "B"]:
            raise ValueError("Segment faqat A yoki B bo‘lishi mumkin")

        set_segment(user_id, segment)
        await message.answer(f"✅ {user_id} foydalanuvchi {segment} segmentga o‘tkazildi")
    except Exception as e:
        await message.answer("❌ Format: <code>/abtest USER_ID A/B</code>")


@router.message(Command("report"), F.from_user.id == ADMIN_ID)
async def send_report(message: Message):
    users = list_users()
    metrics = load_metrics()

    total = len(users)
    loyal = sum(1 for u in metrics.values() if u.get("loyal"))
    a_users = sum(1 for u in metrics.values() if u.get("segment") == "A")
    b_users = sum(1 for u in metrics.values() if u.get("segment") == "B")

    await message.answer(
        f"📈 <b>Bugungi hisobot:</b>\n"
        f"👥 Jami foydalanuvchilar: {total}\n"
        f"🅰️ A segment: {a_users}\n"
        f"🅱️ B segment: {b_users}\n"
        f"💎 Sodiq mijozlar: {loyal}"
    )
