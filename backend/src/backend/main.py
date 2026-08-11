import logging
import time
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

from backend.api.v1.category import router as category_router
from backend.api.v1.event import router as event_router
from backend.api.v1.review import router as review_router
from backend.api.v1.search import router as search_router
from backend.api.v1.tag import router as tag_router
from backend.api.v1.ticket import router as ticket_router
from backend.api.v1.user_auth import router as auth_router
from backend.core.config import settings

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Подготовка директорий
UPLOAD_DIR = Path("static/avatars")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Инициализация приложения
app = FastAPI(
    title=settings.app_name,
    description="Event Ticket API",
    version="0.1.0",
)

# 1. CORS Middleware (всегда подключается первым)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 2. Logging Middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000

    logger.info(
        f"Method: {request.method} | Path: {request.url.path} | "
        f"Status: {response.status_code} | Duration: {process_time:.2f}ms"
    )
    return response


# 3. Глобальные обработчики ошибок (Exception Handlers)
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "error": "validation_error",
            "message": "Invalid request parameters",
            "details": exc.errors(),
        },
    )


@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "http_error",
            "message": str(exc.detail),
        },
    )


# Базовые эндпоинты
@app.get("/")
async def root():
    return {"message": "Event Ticket API"}


@app.get("/health")
async def health():
    return {"status": "ok", "version": "0.1.0"}


# Подключение статики и роутеров
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(auth_router, prefix="/api/v1")
app.include_router(ticket_router, prefix="/api/v1")
app.include_router(tag_router, prefix="/api/v1")
app.include_router(review_router, prefix="/api/v1")
app.include_router(event_router, prefix="/api/v1")
app.include_router(category_router, prefix="/api/v1")
app.include_router(search_router, prefix="/api/v1")