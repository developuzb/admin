from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import sqlite3
from db.models import get_db
from db.queries import get_dashboard_stats

router = APIRouter()
templates = Jinja2Templates(directory="templates")


router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
def dashboard(request: Request, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()

    # Bugungi sana (YYYY-MM-DD)
    cursor.execute("SELECT DATE('now')")
    today = cursor.fetchone()[0]

    # 1. Bugungi buyurtmalar soni
    cursor.execute("SELECT COUNT(*) FROM orders WHERE DATE(created_at) = DATE('now')")
    today_orders = cursor.fetchone()[0]

    # 2. Bugungi tushum (price - cashback)
    cursor.execute("""
        SELECT SUM(s.price - o.used_cashback)
        FROM orders o
        JOIN services s ON o.service_id = s.id
        WHERE DATE(o.created_at) = DATE('now')
    """)
    today_revenue = cursor.fetchone()[0] or 0

    # 3. Oylik buyurtmalar soni va tushum
    cursor.execute("""
        SELECT COUNT(*), SUM(s.price - o.used_cashback)
        FROM orders o
        JOIN services s ON o.service_id = s.id
        WHERE strftime('%Y-%m', o.created_at) = strftime('%Y-%m', 'now')
    """)
    month_data = cursor.fetchone()
    month_orders = month_data[0]
    month_revenue = month_data[1] or 0

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "today_orders": today_orders,
        "today_revenue": today_revenue,
        "month_orders": month_orders,
        "month_revenue": month_revenue
    })

@router.get("/admin/dashboard/data")
def dashboard_data(db: sqlite3.Connection = Depends(get_db)):
    stats = get_dashboard_stats(db)
    return JSONResponse(content=stats)