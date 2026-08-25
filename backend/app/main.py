from fastapi import FastAPI
import uvicorn

from sqlalchemy import text

from app.core.config import settings
from app.core.database import engine
from app.api.auth import auth_router
from app.api.procurement.procurement_api import procurement_router
from app.api.dev_auth_check import test_auth_router


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    debug=settings.debug,
)


app.include_router(auth_router)
app.include_router(procurement_router)
app.include_router(test_auth_router)


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


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )