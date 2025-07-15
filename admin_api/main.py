from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from admin_api.endpoints import dashboard
from admin_api.endpoints import dashboard
from admin_api.endpoints import cashback
from admin_api.endpoints.services_module import json_api

# 🔌 To‘g‘ri router importlari
# ✅ ro‘yxatdagi routerlar
from admin_api.endpoints.services_routes import routers as service_routers
from admin_api.endpoints.dashboard import router as dashboard_router
from admin_api.endpoints.cashback import router as cashback_router
from admin_api.endpoints.abtest import router as abtest_router

app = FastAPI()

# 🔌 Dashboard, cashback, A/B test bo‘limlari
app.include_router(dashboard_router, prefix="/admin")
app.include_router(cashback_router, prefix="/admin")
app.include_router(abtest_router, prefix="/admin")
app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(dashboard.router)
app.include_router(cashback.router)
app.include_router(json_api.router)


# 🔌 Xizmatlar (services) bo‘limi — bir nechta routerni ulaymiz
for r in service_routers:
    app.include_router(r, prefix="/admin/services")


@app.on_event("startup")
async def show_routes():
    print("📍 Routerlar ro'yxati:")
    for route in app.routes:
        print(f"{route.path} → {route.name}")


print("✅ Server ishga tushdi")

if __name__ == "__main__":
    import os
    import uvicorn
    uvicorn.run(
        "admin_api.main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=False
    )
