# __init__.py ichida
from fastapi import APIRouter

router = APIRouter()


# misol uchun

@router.get("/json")
def get_services_json():
    return {"msg": "ok"}
