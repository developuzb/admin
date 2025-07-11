from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from db.models import get_db
import sqlite3

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/edit/{service_id}", response_class=HTMLResponse)
def edit_form(service_id: int, request: Request, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM services WHERE id = ?", (service_id,))
    service = cursor.fetchone()
    return templates.TemplateResponse("service_edit.html", {
        "request": request,
        "service": service
    })

@router.post("/edit/{service_id}")
def update_service(
    service_id: int,
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
        UPDATE services
        SET name = ?, description = ?, price = ?, original_price = ?, cost_price = ?,
            cashback = ?, payment_options = ?, image = ?
        WHERE id = ?
    """, (
        name, description, price, original_price, cost_price,
        cashback, payment_options, image, service_id
    ))
    db.commit()
    return RedirectResponse("/admin/services", status_code=302)
