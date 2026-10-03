import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from app.api.v1 import admin, auth, menu, orders
from app.core.config import get_settings
from app.core.logging import setup_logging
from app.db.session import engine

settings = get_settings()
setup_logging(settings.LOG_LEVEL)
log = logging.getLogger("dragonwok")

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    docs_url=None if settings.is_production else "/docs",
    redoc_url=None,
    openapi_url=None if settings.is_production else "/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

API_PREFIX = "/api/v1"
for r in (auth.router, menu.router, orders.router, admin.router):
    app.include_router(r, prefix=API_PREFIX)


@app.get("/health", tags=["health"])
def health():
    """Liveness check (ALB / ECS container health check)."""
    return {"status": "ok"}


@app.get(f"{API_PREFIX}/health", tags=["health"])
def health_db():
    """Readiness check: also confirms the database answers."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception:
        log.exception("database health check failed")
        return JSONResponse(status_code=503, content={"status": "unavailable"})
    return {"status": "ok", "database": "ok"}


@app.exception_handler(RequestValidationError)
async def validation_handler(request: Request, exc: RequestValidationError):
    errors = [{"field": ".".join(str(p) for p in e["loc"][1:]), "message": e["msg"]} for e in exc.errors()]
    return JSONResponse(status_code=422, content={"detail": "Invalid request", "errors": errors})


@app.exception_handler(IntegrityError)
async def integrity_handler(request: Request, exc: IntegrityError):
    log.warning("integrity error", extra={"path": request.url.path})
    return JSONResponse(status_code=409, content={"detail": "This change conflicts with existing data"})


@app.exception_handler(Exception)
async def unhandled_handler(request: Request, exc: Exception):
    # Full details go to the logs only. The client gets a safe message.
    log.exception("unhandled error", extra={"path": request.url.path})
    return JSONResponse(status_code=500, content={"detail": "Something went wrong. Please try again."})
