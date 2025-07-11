from fastapi import APIRouter, Depends
from db.models import get_db
import sqlite3

router = APIRouter()

@router.get("/api/services/")
def get_services_json(db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()

    cursor.execute("""
        SELECT 
            name,
            description,
            price,
            original_price,
            pre_discount_price,
            cashback,
            orders,
            is_active,
            image_url
        FROM services
    """)
    rows = cursor.fetchall()

    services = []
    for row in rows:
        (
            name,
            description,
            price,
            original_price,
            pre_discount_price,
            cashback,
            orders,
            is_active,
            image_filename
        ) = row

        cashback_sum = int((price or 0) * (cashback or 0) / 100)
        foyda = (original_price or 0 - price or 0) + cashback_sum

        services.append({
            "xizmat_nomi": name,
            "tavsifi": description,
            "narx": price,
            "asl_narx": original_price,
            "chegirma_oldi_narx": pre_discount_price,
            "cashback": cashback,
            "buyurtmalar": orders,
            "foyda": foyda,
            "holati": "aktiv" if is_active else "passiv",
            "image": image_filename or "no-image.png"  # 🔥 frontend talabiga mos
        })

    return services
