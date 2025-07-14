
from fastapi import FastAPI, APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
import sqlite3
from datetime import datetime

app = FastAPI()
router = APIRouter()


def get_db():
    db = sqlite3.connect("bot.db")
    db.row_factory = sqlite3.Row
    return db


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


@router.get("/api/services/")
def get_services(db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM services")
    rows = cursor.fetchall()
    services = [dict(row) for row in rows]
    return services


@router.get("/api/services/{service_id}")
def get_service_by_id(service_id: int, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()

    # Xizmat ma’lumotlari
    cursor.execute("SELECT * FROM services WHERE id = ?", (service_id,))
    service = cursor.fetchone()
    if not service:
        raise HTTPException(status_code=404, detail="Xizmat topilmadi")

    service_data = dict(service)

    # So‘nggi buyurtma (agar mavjud bo‘lsa)
    cursor.execute(
        "SELECT id, user_id, contact, created_at FROM orders WHERE service_id = ? ORDER BY id DESC LIMIT 1",
        (service_id,)
    )
    last_order = cursor.fetchone()
    service_data["last_order"] = dict(last_order) if last_order else None

    return service_data


@router.patch("/api/services/{service_id}/stats")
def update_service_stats(service_id: int, data: ServiceStatUpdate, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute(
        "SELECT price, cashback, original_price FROM services WHERE id = ?", (service_id,))
    row = cursor.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Xizmat topilmadi")
    price, cashback, original_price = row
    foyda = (original_price or 0 - price or 0) + data.cashback_given
    cursor.execute("""
        UPDATE services
        SET orders = COALESCE(orders, 0) + 1,
            profit = COALESCE(profit, 0) + ?
        WHERE id = ?
    """, (foyda, service_id))
    db.commit()
    return {"status": "success", "foyda": foyda}


class MetricLog(BaseModel):
    event: str
    date: str
    group: str | None = None


@router.post("/api/metrics/")
def log_metric(metric: MetricLog):
    # Bu yerda faqat xotirada saqlaymiz yoki logga yozamiz
    print(f"📊 METRIKA: {metric.event} ({metric.date})", "group:", metric.group)
    return {"status": "ok"}


class TrackUserSchema(BaseModel):
    user_id: int
    name: str
    phone: str


@router.post("/api/services/users/track")
def track_user(data: TrackUserSchema, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("INSERT OR IGNORE INTO users (id, name, phone) VALUES (?, ?, ?)",
                   (data.user_id, data.name, data.phone))
    db.commit()
    return {"status": "tracked"}


class OrderCreateSchema(BaseModel):
    order_id: int
    service_id: int
    service_name: str
    user_id: int
    phone: str
    contact_method: str
    contact_time: str
    name: str


@router.post("/api/orders/")
def create_order(data: OrderCreateSchema, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("""
        INSERT INTO orders (id, service_id, service_name, user_id, phone, contact_method, contact_time, name)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (data.order_id, data.service_id, data.service_name, data.user_id, data.phone, data.contact_method, data.contact_time, data.name))
    db.commit()
    return {"status": "order_created"}


@router.get("/ api/users/{user_id}")
def get_user_profile(user_id: int, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute(
        "SELECT name, phone, balance, actions_count FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Foydalanuvchi topilmadi")
    badge = "🥉 Bronze"
    count = row["actions_count"] or 0
    if count >= 10:
        badge = "🥇 Gold"
    elif count >= 5:
        badge = "🥈 Silver"
    return {
        "ism": row["name"],
        "telefon": row["phone"],
        "balans": row["balance"],
        "amallar_soni": count,
        "badge": badge
    }


@router.post("/api/cashback-log/")
def add_cashback_log(log: CashbackLog, db: sqlite3.Connection = Depends(get_db)):
    if log.direction not in ("plus", "minus"):
        raise HTTPException(
            status_code=400, detail="direction faqat 'plus' yoki 'minus' bo'lishi mumkin")
    cursor = db.cursor()
    cursor.execute("""
        INSERT INTO cashback_log (user_id, service_id, amount, direction)
        VALUES (?, ?, ?, ?)
    """, (log.user_id, log.service_id, log.amount, log.direction))
    cursor.execute(
        "SELECT balance, actions_count FROM users WHERE id = ?", (log.user_id,))
    user = cursor.fetchone()
    if not user:
        raise HTTPException(status_code=404, detail="Foydalanuvchi topilmadi")
    balance = user["balance"] or 0
    actions = user["actions_count"] or 0
    if log.direction == "plus":
        balance += log.amount
        actions += 1
    else:
        if log.amount > balance:
            raise HTTPException(status_code=400, detail="Balans yetarli emas")
        balance -= log.amount
    cursor.execute("UPDATE users SET balance = ?, actions_count = ? WHERE id = ?",
                   (balance, actions, log.user_id))
    db.commit()
    return {"status": "success", "balance": balance}


@router.delete("/api/cashback-log/{log_id}")
def delete_cashback_log(log_id: int, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("DELETE FROM cashback_log WHERE id = ?", (log_id,))
    db.commit()
    return {"status": "deleted"}


@router.post("/api/webhook/send-report")
def send_report(report: WebhookReport):
    return {"status": "report received", "type": report.type}


app.include_router(router)


class ServicePartialUpdate(BaseModel):
    last_order: int | None = None


@router.patch("/api/services/{service_id}")
def update_service_partial(service_id: int, data: ServicePartialUpdate, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    fields = []
    values = []

    if data.last_order is not None:
        fields.append("last_order = ?")
        values.append(data.last_order)

    if not fields:
        raise HTTPException(
            status_code=400, detail="Hech narsa o‘zgartirilmadi")

    values.append(service_id)
    sql = f"UPDATE services SET {', '.join(fields)} WHERE id = ?"
    cursor.execute(sql, values)
    db.commit()
    return {"status": "updated"}


def ensure_last_order_column_exists():
    db = sqlite3.connect("bot.db")
    cursor = db.cursor()
    cursor.execute("PRAGMA table_info(services);")
    columns = [row[1] for row in cursor.fetchall()]
    if "last_order" not in columns:
        cursor.execute("ALTER TABLE services ADD COLUMN last_order INTEGER;")
        db.commit()
        print("✅ 'last_order' ustuni qo‘shildi.")
    else:
        print("ℹ️ 'last_order' ustuni allaqachon mavjud.")
    db.close()


# ⏳ Dastur ishga tushganda chaqiriladi
ensure_last_order_column_exists()


class UserUpdate(BaseModel):
    name: str | None = None
    phone: str | None = None
    balance: int | None = None
    actions_count: int | None = None


@router.put("/api/users/{user_id}")
def update_user(user_id: int, update: UserUpdate, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()

    fields = []
    values = []

    if update.name is not None:
        fields.append("name = ?")
        values.append(update.name)
    if update.phone is not None:
        fields.append("phone = ?")
        values.append(update.phone)
    if update.balance is not None:
        fields.append("balance = ?")
        values.append(update.balance)
    if update.actions_count is not None:
        fields.append("actions_count = ?")
        values.append(update.actions_count)

    if not fields:
        raise HTTPException(
            status_code=400, detail="Yangilanish uchun ma'lumot yo‘q")

    values.append(user_id)
    sql = f"UPDATE users SET {', '.join(fields)} WHERE id = ?"
    cursor.execute(sql, values)
    db.commit()
    return {"status": "updated"}
