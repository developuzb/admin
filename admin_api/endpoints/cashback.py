from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from db.models import get_db
import sqlite3
from utils.cashback import add_cashback  # ⚠️ bu fayl mavjud bo‘lishi kerak
from datetime import date

router = APIRouter()
templates = Jinja2Templates(directory="templates")


    
@router.get("/admin/cashback")
def cashback_page(request: Request, db: sqlite3.Connection = Depends(get_db)):
    users = db.execute("""
        SELECT id, name, phone, cashback_balance,
        (SELECT COUNT(*) FROM cashback_history WHERE user_id = users.id) as operations
        FROM users
    """).fetchall()
    return templates.TemplateResponse("cashback_monitor.html", {"request": request, "users": users})
    
@router.get("/admin/cashback/stats")
def cashback_stats(db: sqlite3.Connection = Depends(get_db)):
    today = date.today().isoformat()

    total = db.execute("SELECT SUM(amount) FROM cashback_history").fetchone()[0] or 0
    today_in = db.execute("SELECT SUM(amount) FROM cashback_history WHERE direction='in' AND DATE(timestamp)=?", (today,)).fetchone()[0] or 0
    today_out = db.execute("SELECT SUM(amount) FROM cashback_history WHERE direction='out' AND DATE(timestamp)=?", (today,)).fetchone()[0] or 0

    return {"total": total, "today_in": today_in, "today_out": today_out}

@router.post("/admin/cashback/adjust")
def adjust_cashback(
    user_id: int = Form(...),
    amount: int = Form(...),
    direction: str = Form(...),
    note: str = Form(""),
    db: sqlite3.Connection = Depends(get_db)
):
    signed_amount = amount if direction == "in" else -amount
    db.execute("UPDATE users SET cashback_balance = cashback_balance + ? WHERE id = ?", (signed_amount, user_id))
    db.execute("""
        INSERT INTO cashback_history (user_id, amount, direction, note, timestamp)
        VALUES (?, ?, ?, ?, datetime('now'))
    """, (user_id, signed_amount, direction, note))
    db.commit()
    return {"success": True}

@router.get("/admin/cashback/history/{user_id}", response_class=HTMLResponse)
def cashback_history(request: Request, user_id: int, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()

    user = cursor.execute("SELECT id, name FROM users WHERE id = ?", (user_id,)).fetchone()
    if not user:
        return HTMLResponse(content="Foydalanuvchi topilmadi", status_code=404)

    rows = cursor.execute("""
        SELECT amount, direction, note, timestamp
        FROM cashback_history
        WHERE user_id = ?
        ORDER BY timestamp DESC
        LIMIT 50
    """, (user_id,)).fetchall()

    return templates.TemplateResponse("cashback_history.html", {
        "request": request,
        "user": user,
        "history": rows
    })
