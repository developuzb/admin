# utils/files.py
import json
import os
import logging

logger = logging.getLogger(__name__)

BOT_DATA_FILE = "bot_data.json"
ORDER_COUNTER_FILE = "./database/order_counter.json"


def save_bot_data(context):
    try:
        with open(BOT_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(context.bot_data, f, ensure_ascii=False, indent=2)
        logger.info("✅ bot_data.json saqlandi")
    except Exception as e:
        logger.error(f"❌ bot_data.json saqlashda xato: {e}")


def load_bot_data(context):
    try:
        with open(BOT_DATA_FILE, 'r', encoding='utf-8') as f:
            context.bot_data.update(json.load(f))
        logger.info("✅ bot_data.json dan yuklandi")
    except FileNotFoundError:
        logger.info("ℹ bot_data.json topilmadi, yangi yaratiladi")
    except Exception as e:
        logger.error(f"❌ bot_data.json dan o‘qishda xato: {e}")


def get_next_order_number():
    os.makedirs('./database', exist_ok=True)
    try:
        with open(ORDER_COUNTER_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if 'order_id' not in data:
            data['order_id'] = 172999
        data['order_id'] += 1
        with open(ORDER_COUNTER_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        return data['order_id']
    except (FileNotFoundError, json.JSONDecodeError):
        with open(ORDER_COUNTER_FILE, 'w', encoding='utf-8') as f:
            json.dump({"order_id": 172999}, f, indent=2)
        return 172999
