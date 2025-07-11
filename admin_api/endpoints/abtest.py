from fastapi import Request, Depends, APIRouter
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from db.models import get_db
import sqlite3

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/abtest", response_class=HTMLResponse)
def ab_test_view(request: Request, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    q = request.query_params

    from_date = q.get("from", "2000-01-01")
    to_date = q.get("to", "2100-01-01")

    # Guruh A
    cursor.execute("""
        SELECT COUNT(*) FROM users WHERE user_segment = 'A'
    """)
    group_a_users = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*) FROM orders
        WHERE user_id IN (SELECT id FROM users WHERE user_segment = 'A')
        AND DATE(created_at) BETWEEN DATE(?) AND DATE(?)
    """, (from_date, to_date))
    group_a_orders = cursor.fetchone()[0]

    # Guruh B
    cursor.execute("""
        SELECT COUNT(*) FROM users WHERE user_segment = 'B'
    """)
    group_b_users = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*) FROM orders
        WHERE user_id IN (SELECT id FROM users WHERE user_segment = 'B')
        AND DATE(created_at) BETWEEN DATE(?) AND DATE(?)
    """, (from_date, to_date))
    group_b_orders = cursor.fetchone()[0]

    return templates.TemplateResponse("ab_test_results.html", {
        "request": request,
        "group_a_users": group_a_users,
        "group_b_users": group_b_users,
        "group_a_orders": group_a_orders,
        "group_b_orders": group_b_orders,
        "from_date": from_date,
        "to_date": to_date
    })
