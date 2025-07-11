from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse
from db.models import get_db
import sqlite3

router = APIRouter()

@router.post("/{service_id}/toggle")
def toggle_service(service_id: int, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("SELECT active FROM services WHERE id = ?", (service_id,))
    service = cursor.fetchone()
    if not service:
        return RedirectResponse("/admin/services", status_code=302)

    new_status = 0 if service["active"] else 1
    cursor.execute("UPDATE services SET active = ? WHERE id = ?", (new_status, service_id))
    db.commit()
    return RedirectResponse("/admin/services", status_code=302)
