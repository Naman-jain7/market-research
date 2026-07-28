from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.api.research import limiter
from app.api.router import api_router
from app.db.manager import db_manager
from configs.core_config import settings
from src.utils.exception import AppException
from src.utils.logger import APP_LOGGER


@asynccontextmanager  # type: ignore
async def lifespan(app: FastAPI):
    """Handles FastAPI application startup and shutdown events."""
    await db_manager.connect()
    try:
        await db_manager.execute_command("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                full_name VARCHAR(100) NOT NULL,
                age INT,
                email VARCHAR(255) UNIQUE NOT NULL,
                hashed_password VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        APP_LOGGER.info("Base database tables verified.")
    except Exception as e:  # noqa: BLE001
        APP_LOGGER.error(f"Failed to create base tables: {e}")
    yield
    await db_manager.disconnect()


app = FastAPI(
    title=settings.app.APP_NAME,
    version=settings.app.APP_VERSION,
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler) # type: ignore


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.message,
            **exc.to_dict(),
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    first = errors[0] if errors else {}
    field = (
        ".".join(str(loc) for loc in first.get("loc", []))
        if first.get("loc")
        else "body"
    )
    msg = first.get("msg", "Invalid input")
    return JSONResponse(
        status_code=422,
        content={"detail": f"'{field}': {msg}"},
    )

app.include_router(api_router, prefix="/api/v1")
