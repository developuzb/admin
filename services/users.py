# services/users.py
import json
import logging

logger = logging.getLogger(__name__)

USERS_FILE = "users.json"

# Global USERS dict
USERS = {}


def get_user(user_id):
    return USERS.get(str(user_id), None)


def update_user(user_id, data: dict):
    user = USERS.setdefault(str(user_id), {
                            'name': None, 'phone': None, 'orders': [], 'rated_identifiers': []})
    user.update(data)
    save_users(USERS)


def load_users():
    global USERS
    try:
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            USERS = json.load(f)
            for user_id, data in USERS.items():
                if isinstance(data, str):
                    USERS[user_id] = {
                        'name': data,
                        'phone': None,
                        'orders': [],
                        'rated_identifiers': []
                    }
                for order in USERS[user_id].get('orders', []):
                    if 'payment_status' not in order:
                        order['payment_status'] = 'pending'
        logger.info("✅ USERS loaded from users.json")
    except FileNotFoundError:
        logger.warning("users.json not found, initializing empty USERS")
        USERS = {}
    except Exception as e:
        logger.error(f"❌ Error loading users.json: {e}")
        USERS = {}


def save_users(data):
    try:
        with open(USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info("✅ USERS saved to users.json")
    except Exception as e:
        logger.error(f"❌ Error saving users.json: {e}")


def list_users():
    return list(USERS.keys())
