# admin_api/endpoints/services_module/json_api.py

from fastapi import APIRouter, Depends
from db.models import get_db
import sqlite3

router = APIRouter()


@router.get("/api/services/")
def get_services_json(db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute(
        "SELECT id, name, duration, cashback, image_url FROM services")
    rows = cursor.fetchall()

    services = []
    for row in rows:
        services.append({
            "id": row[0],
            "name": row[1],
            "duration": row[2],
            "cashback": row[3],
            "image_url": row[4] or "",
        })
    return services
