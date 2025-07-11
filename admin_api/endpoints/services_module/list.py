from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from db.models import get_db
import sqlite3

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
def service_list(request: Request, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM services ORDER BY id DESC")
    services = cursor.fetchall()
    return templates.TemplateResponse("services.html", {
        "request": request,
        "services": services
    })
