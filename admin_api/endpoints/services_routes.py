import os
import sqlite3
from fastapi import APIRouter, Request, Depends, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from db.models import get_db
from db.queries import get_services_with_stats_from_db

router = APIRouter()
templates = Jinja2Templates(directory="templates")

UPLOAD_DIR = "static/images"
os.makedirs(UPLOAD_DIR, exist_ok=True)  # katalog mavjud bo'lmasa yaratadi

@router.get("/", response_class=HTMLResponse)
def service_list(request: Request, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM services")
    services = cursor.fetchall()
    return templates.TemplateResponse("services.html", {
        "request": request,
        "services": services
    })

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

@router.get("/add", response_class=HTMLResponse)
def add_service_form(request: Request):
    return templates.TemplateResponse("add_service.html", {"request": request})

@router.post("/add")
def add_service(
    name: str = Form(...),
    description: str = Form(...),
    price: int = Form(...),
    original_price: int = Form(...),
    cost_price: int = Form(...),
    cashback: int = Form(...),
    payment_options: str = Form(...),
    image: UploadFile = File(...),
    db: sqlite3.Connection = Depends(get_db)
):
    image_filename = image.filename
    file_path = os.path.join(UPLOAD_DIR, image_filename)
    with open(file_path, "wb") as f:
        f.write(image.file.read())

    cursor = db.cursor()
    cursor.execute("""
        INSERT INTO services (
            name, description, price, original_price, cost_price,
            cashback, payment_options, image, active
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)
    """, (
        name,
        description,
        price,
        original_price,
        cost_price,
        cashback,
        payment_options,
        image_filename
    ))
    db.commit()
    return RedirectResponse("/admin/services", status_code=302)

@router.get("/edit/{service_id}", response_class=HTMLResponse)
def edit_service_form(request: Request, service_id: int, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM services WHERE id = ?", (service_id,))
    service = cursor.fetchone()
    if not service:
        return HTMLResponse("Xizmat topilmadi", status_code=404)
    return templates.TemplateResponse("edit_service.html", {
        "request": request,
        "service": service
    })

@router.post("/edit/{service_id}")
def update_service(
    service_id: int,
    name: str = Form(...),
    description: str = Form(...),
    price: int = Form(...),
    original_price: int = Form(...),
    cost_price: int = Form(...),
    cashback: int = Form(...),
    payment_options: str = Form(...),
    image: UploadFile = File(...),
    db: sqlite3.Connection = Depends(get_db)
):
    image_filename = image.filename
    file_path = os.path.join(UPLOAD_DIR, image_filename)
    with open(file_path, "wb") as f:
        f.write(image.file.read())

    cursor = db.cursor()
    cursor.execute("""
        UPDATE services SET
            name = ?, description = ?, price = ?, original_price = ?,
            cost_price = ?, cashback = ?, payment_options = ?, image = ?
        WHERE id = ?
    """, (
        name,
        description,
        price,
        original_price,
        cost_price,
        cashback,
        payment_options,
        image_filename,
        service_id
    ))
    db.commit()
    return RedirectResponse("/admin/services", status_code=302)

@router.get("/json")
def get_services_json(db: sqlite3.Connection = Depends(get_db)):
    services = get_services_with_stats_from_db(db)
    return JSONResponse(content=services)

# Router ro'yxati
routers = [router]
