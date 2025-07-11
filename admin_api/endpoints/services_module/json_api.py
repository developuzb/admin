# admin_api/endpoints/services_module/json_api.py

from fastapi import APIRouter, Depends
from db.models import get_db
import sqlite3

router = APIRouter()

# faqat .py faylga yoziladi
NGROK_BASE = "https://38ede9b87b92.ngrok-free.app"


@router.get("/api/services/")
def get_services_json(db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute(
        "SELECT id, name, duration, cashback, image_url FROM services")
    rows = cursor.fetchall()

    services = []
    for row in rows:
        image_url = row[4] or ""

        if image_url and not image_url.startswith("http"):
            image_url = f"{NGROK_BASE}/static/{image_url.lstrip('/')}"

        services.append({
            "id": row[0],
            "name": row[1],
            "duration": row[2],
            "cashback": row[3],
            "image_url": image_url,
        })

    return services
