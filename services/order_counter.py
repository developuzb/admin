import json
from pathlib import Path

COUNTER_PATH = Path("order_counter.json")
DEFAULT_START = 173000

def load_counter():
    if not COUNTER_PATH.exists():
        return {"last": DEFAULT_START - 1}
    with open(COUNTER_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_counter(data):
    with open(COUNTER_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def get_next_order_number():
    data = load_counter()
    data["last"] += 1
    save_counter(data)
    return data["last"]
