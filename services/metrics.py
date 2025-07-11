import json
from datetime import datetime
from pathlib import Path

METRICS_PATH = Path("metrics.json")

def load_metrics():
    if not METRICS_PATH.exists():
        return {}
    with open(METRICS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_metrics(data):
    with open(METRICS_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def mark_first_visit(user_id):
    data = load_metrics()
    uid = str(user_id)
    if uid not in data:
        data[uid] = {"first_visit": datetime.now().isoformat()}
        save_metrics(data)

def get_segment(user_id):
    uid = str(user_id)
    data = load_metrics()
    return data.get(uid, {}).get("segment", "A")

def set_segment(user_id, segment):
    data = load_metrics()
    uid = str(user_id)
    if uid not in data:
        data[uid] = {}
    data[uid]["segment"] = segment
    save_metrics(data)

def mark_loyal(user_id):
    data = load_metrics()
    uid = str(user_id)
    if uid not in data:
        data[uid] = {}
    data[uid]["loyal"] = True
    save_metrics(data)

def is_loyal(user_id):
    return load_metrics().get(str(user_id), {}).get("loyal", False)
