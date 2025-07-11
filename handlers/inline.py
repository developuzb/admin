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
)