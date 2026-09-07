from fastapi import FastAPI
import uvicorn

from sqlalchemy import text

from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import engine

from app.api.users.auth import auth_router
from app.api.procurement.procurement_api import procurement_router
from app.api.approval.approval import approval_router
from app.api.audit.audit import audit_router
from app.api.vendor.vendor_api import vendor_router
from app.api.vendor.vendor_auth import vendor_auth_router
from app.api.ai.ai_chat import ai_router
from app.api.dashboard.dashboard_api import dashboard_router
from app.api.quotation.quotation_api import quotation_router
from app.api.rfq.rfq_api import rfq_router
from app.api.users.user_management import admin_user_router
from app.api.vendor.vendor_rfq import vendor_rfq_router
from app.api.vendor.vendor_quotations import vendor_quotation_router


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    debug=settings.debug,
)


# ==========================================================
# CORS
# ==========================================================

if settings.CORS_ORIGINS.strip() == "*":
    origins = ["*"]
else:
    origins = [
        origin.strip()
        for origin in settings.CORS_ORIGINS.split(",")
        if origin.strip()
    ]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==========================================================
# ROUTERS
# ==========================================================

app.include_router(auth_router)
app.include_router(admin_user_router)
app.include_router(procurement_router)
app.include_router(approval_router)
app.include_router(audit_router)
app.include_router(vendor_router)
app.include_router(vendor_auth_router)
app.include_router(ai_router)
app.include_router(dashboard_router)
app.include_router(quotation_router)
app.include_router(rfq_router)
app.include_router(vendor_rfq_router)
app.include_router(vendor_quotation_router)




# ==========================================================
# HEALTH CHECK
# ==========================================================

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": settings.app_name,
    }


@app.get("/health/database")
def database_health_check():
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        value = result.scalar()

    return {
        "status": "healthy",
        "database": "postgresql",
        "result": value,
    }


# ==========================================================
# APPLICATION START
# ==========================================================

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=8000,
        reload=False,
    )