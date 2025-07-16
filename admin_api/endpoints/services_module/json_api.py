from fastapi import FastAPI, APIRouter, Depends, HTTPException, Request, Query
from pydantic import BaseModel
import sqlite3
from datetime import datetime
import logging
import traceback

logger = logging.getLogger(__name__)


app = FastAPI()
router = APIRouter()


def get_db():
    db = sqlite3.connect("bot.db")
    db.row_factory = sqlite3.Row
    return db


class OrderCreateSchema(BaseModel):
    order_id: int
    service_id: int
    service_name: str
    user_id: int
    phone: str
    contact_method: str
    contact_time: str
    name: str


class OrderUpdateSchema(BaseModel):
    service_id: int
    service_name: str
    user_id: int
    phone: str
    contact_method: str
    contact_time: str
    name: str


class ServiceStatUpdate(BaseModel):
    cashback_given: int = 0


class CashbackLog(BaseModel):
    user_id: int
    service_id: int
    amount: int
    direction: str


class UserTrack(BaseModel):
    id: int
    name: str
    phone: str


class WebhookReport(BaseModel):
    type: str
    user_id: int
    service_id: int


class MetricLog(BaseModel):
    event: str
    date: str
    group: str | None = None


class TrackUserSchema(BaseModel):
    user_id: int
    name: str
    phone: str


class ServicePartialUpdate(BaseModel):
    last_order: int | None = None


class UserUpdate(BaseModel):
    name: str | None = None
    phone: str | None = None
    balance: int | None = None
    actions_count: int | None = None


@router.get("/api/services/")
def get_services(db: sqlite3.Connection = Depends(get_db)):
    try:
        cursor = db.cursor()
        cursor.execute("SELECT * FROM services")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.get("/api/services/{service_id}")
def get_service_by_id(service_id: int, db: sqlite3.Connection = Depends(get_db)):
    try:
        cursor = db.cursor()
        cursor.execute("SELECT * FROM services WHERE id = ?", (service_id,))
        service = cursor.fetchone()
        if not service:
            raise HTTPException(status_code=404, detail="Xizmat topilmadi")

        service_data = dict(service)

        cursor.execute(
            "SELECT id, user_id, contact, created_at FROM orders WHERE service_id = ? ORDER BY id DESC LIMIT 1",
            (service_id,)
        )
        last_order = cursor.fetchone()
        service_data["last_order"] = dict(last_order) if last_order else None

        return service_data
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.post("/api/services/users/track")
def track_user(data: TrackUserSchema, db: sqlite3.Connection = Depends(get_db)):
    try:
        cursor = db.cursor()
        cursor.execute("INSERT OR IGNORE INTO users (id, name, phone) VALUES (?, ?, ?)",
                       (data.user_id, data.name, data.phone))
        db.commit()
        return {"status": "tracked"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.post("/api/orders/")
def create_order(data: OrderCreateSchema, db: sqlite3.Connection = Depends(get_db)):
    try:
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO orders (id, service_id, service_name, user_id, phone, contact_method, contact_time, name)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (data.order_id, data.service_id, data.service_name, data.user_id, data.phone,
              data.contact_method, data.contact_time, data.name))
        db.commit()
        return {"status": "order_created"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.put("/api/orders/{order_id}")
def update_order(order_id: int, data: OrderUpdateSchema, db: sqlite3.Connection = Depends(get_db)):
    try:
        cursor = db.cursor()
        cursor.execute("""
            UPDATE orders SET
            service_id = ?, service_name = ?, user_id = ?, phone = ?, contact_method = ?, contact_time = ?, name = ?
            WHERE id = ?
        """, (data.service_id, data.service_name, data.user_id, data.phone, data.contact_method,
              data.contact_time, data.name, order_id))
        db.commit()
        return {"status": "order_updated"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.get("/api/orders/{order_id}")
def get_order(order_id: int, user_id: int = Query(...), db: sqlite3.Connection = Depends(get_db)):
    try:
        cursor = db.cursor()
        cursor.execute(
            "SELECT * FROM orders WHERE id = ? AND user_id = ?", (order_id, user_id))
        order = cursor.fetchone()

        if not order:
            # bu 404 ni alohida qaytaramiz
            raise HTTPException(status_code=404, detail="Order not found")

        return dict(order)

    except HTTPException as he:
        raise he  # 👈 bu joyda 404 ni 500 ga o‘zgartirmay, shunchaki uzatamiz

    except Exception as e:
        print("XATOLIK:", e)
        traceback.print_exc()
        raise HTTPException(
            status_code=500, detail="Buyurtmani olishda xatolik yuz berdi.")


@router.put("/api/services/{service_id}")
def partial_update_service(service_id: int, data: ServiceStatUpdate, db: sqlite3.Connection = Depends(get_db)):
    try:
        cursor = db.cursor()
        cursor.execute("UPDATE services SET cashback_given = cashback_given + ? WHERE id = ?",
                       (data.cashback_given, service_id))
        db.commit()
        return {"status": "updated"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.patch("/api/services/{service_id}")
def patch_service(service_id: int, data: ServiceStatUpdate, db: sqlite3.Connection = Depends(get_db)):
    try:
        cursor = db.cursor()
        cursor.execute("UPDATE services SET cashback_given = cashback_given + ? WHERE id = ?",
                       (data.cashback_given, service_id))
        db.commit()
        return {"status": "updated"}
    except Exception as e:
        import traceback
        print("PATCH xatolik:", e)
        traceback.print_exc()
        raise HTTPException(
            status_code=500, detail="PATCH orqali yangilashda xatolik.")


@router.put("/api/services/update_last/{service_id}")
def update_last_order(service_id: int, data: dict, db: sqlite3.Connection = Depends(get_db)):
    last_order = data.get("last_order")
    if last_order is None:
        raise HTTPException(status_code=400, detail="last_order is required")

    cursor = db.cursor()
    cursor.execute(
        "UPDATE services SET last_order = ? WHERE id = ?", (last_order, service_id))
    db.commit()
    return {"status": "updated"}


@router.get("/api/services/users/{user_id}")
def get_user(user_id: int, db: sqlite3.Connection = Depends(get_db)):
    try:
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE telegram_id = ?", (user_id,))
        user = cursor.fetchone()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return {
            "user_id": user[1],
            "name": user[2],
            "phone": user[3],
            "cashback": user[5],
            "segment": user[6],
            "balance": user[9],
            "actions": user[10],
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.post("/api/services/cashback")
def log_cashback(data: CashbackLog, db: sqlite3.Connection = Depends(get_db)):
    try:
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO cashback_log (user_id, service_id, amount, direction, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (data.user_id, data.service_id, data.amount, data.direction, datetime.utcnow().isoformat()))
        db.commit()
        return {"status": "cashback_logged"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.put("/api/services/users/{user_id}")
def update_user(user_id: int, data: UserUpdate, db: sqlite3.Connection = Depends(get_db)):
    try:
        fields = []
        values = []
        for key, value in data.dict(exclude_unset=True).items():
            fields.append(f"{key} = ?")
            values.append(value)
        values.append(user_id)
        cursor = db.cursor()
        cursor.execute(
            f"UPDATE users SET {', '.join(fields)} WHERE telegram_id = ?", values)
        db.commit()
        return {"status": "user_updated"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.post("/api/metrics")
def log_metric(data: MetricLog, db: sqlite3.Connection = Depends(get_db)):
    try:
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO metrics (event, date, segment)
            VALUES (?, ?, ?)
        """, (data.event, data.date, data.group))
        db.commit()
        return {"status": "metric_logged"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.post("/api/webhook")
def webhook_report(data: WebhookReport, db: sqlite3.Connection = Depends(get_db)):
    try:
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO webhook_log (type, user_id, service_id, created_at)
            VALUES (?, ?, ?, ?)
        """, (data.type, data.user_id, data.service_id, datetime.utcnow().isoformat()))
        db.commit()
        return {"status": "webhook_logged"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))
