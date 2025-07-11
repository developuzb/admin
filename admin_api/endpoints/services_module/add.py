from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from db.models import get_db
import sqlite3

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/add", response_class=HTMLResponse)
def show_form(request: Request):
    return templates.TemplateResponse("service_add.html", {"request": request})

@router.post("/add")
def add_service(
    name: str = Form(...),
    description: str = Form(""),
    price: int = Form(...),
    original_price: int = Form(...),
    cost_price: int = Form(...),
    cashback: int = Form(...),
    payment_options: str = Form(""),
    image: str = Form(""),
    db: sqlite3.Connection = Depends(get_db)
):
    cursor = db.cursor()
    cursor.execute("""
        INSERT INTO services (
            name, description, price, original_price, cost_price,
            cashback, payment_options, image, active
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)
    """, (
        name, description, price, original_price, cost_price,
        cashback, payment_options, image
    ))
    db.commit()
    return RedirectResponse("/admin/services", status_code=302)
