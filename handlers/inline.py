from SQlite2.SQlite2.loader import dp
from aiogram import types
import asyncio
from aiogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent
from uuid import uuid4
import aiohttp

API_URL = "http://localhost:8000/api/services/"
DEFAULT_IMAGE = "https://i.ibb.co/4w8mVTyH/Chat-GPT-Image-Jul-9-2025-04-30-59-AM.png"


async def fetch_services():
    async with aiohttp.ClientSession() as session:
        async with session.get(API_URL) as response:
            if response.status == 200:
                return await response.json()
            return []


async def inline_query_handler(inline_query: InlineQuery):
    query = inline_query.query.lower().strip()
    services = await fetch_services()

    results = []

    for service in services:
        name = service.get("name", "").lower()

        # Filtrlash (query bo‘yicha)
        if query in name or query == "":
            duration = service.get("duration", "—")
            cashback = service.get("cashback", 0)
            image_url = service.get("image_url") or DEFAULT_IMAGE

            message_text = (
                f"<b>✅ Tanlangan xizmat:</b>\n"
                f"📌 <b>{service['name']}</b>\n"
                f"⏱ <b>{duration} daqiqa</b>\n"
                f"💸 <b>{cashback}% cashback</b>\n\n"
                f"📞 <i>Iltimos, aloqa vaqtini yozing:</i>"
            )

            results.append(
                InlineQueryResultArticle(
                    id=str(uuid4()),
                    title=service["name"],
                    description=f"⏱ {duration} daqiqa | 💸 Cashback: {cashback}%",
                    thumb_url=image_url,
                    input_message_content=InputTextMessageContent(
                        message_text=message_text,
                        parse_mode="HTML"
                    )
                )
            )

    await inline_query.answer(results=results[:50], cache_time=1, is_personal=True)


@dp.message(lambda message: message.text.startswith("#XIZMAT#"))
async def send_service_details(message: types.Message):
    try:
        service_id = message.text.replace("#XIZMAT#", "").strip()

        # API orqali xizmat ma'lumotini olish
        async with aiohttp.ClientSession() as session:
            async with session.get(f"http://localhost:8000/api/services/{service_id}") as resp:
                if resp.status != 200:
                    await message.answer("❌ Xizmat topilmadi.")
                    return
                service = await resp.json()

        # Narxlar (demo ma'lumotlar)
        eski_narx = 12550
        chegirma_narx = 11500
        cashback = service.get("cashback", 0)

        # Asosiy tafsilotlar xabari
        caption = (
            f"<b>✅ Tanlangan xizmat:</b> {service['name']}\n\n"
            f"<b>⏱ Bajarilish vaqti:</b> atigi <b>{service['duration']} daqiqa</b>da tayyor!\n\n"
            f"<b>💸 Narx:</b> <s>{eski_narx:,} so‘m</s> → <b><u>{chegirma_narx:,} so‘m</u></b>\n"
            f"<b>🎁 Cashback:</b> <b>{cashback}%</b> — xizmat tugagach bonus tarzida qaytariladi\n\n"
            f"<b>🔥 Qulay narx + tezkor xizmat = to‘g‘ri tanlov</b>\n\n"
            f"Quyidagilardan birini tanlang:"
        )

        # Tugmalarni qo‘shamiz
        keyboard = get_confirmation_keyboard(service_id)

        # Xizmat rasmi bilan yuborish
        await message.answer_photo(
            photo=service.get("image_url"),
            caption=caption,
            reply_markup=keyboard,
            parse_mode="HTML"
        )

        # 🔁 2 sekunddan keyin foyda haqida motivatsion xabar
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
