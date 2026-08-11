from fastapi import FastAPI
from backend.api.v1.user_auth import router as auth_router
from backend.api.v1.ticket import router as ticket_router
from backend.api.v1.tag import router as tag_router
from backend.api.v1.review import router as review_router
from backend.api.v1.event import router as event_router
from backend.api.v1.category import router as category_router
from backend.api.v1.search import router as search_router
from fastapi.staticfiles import StaticFiles
from pathlib import Path

UPLOAD_DIR = Path("static/avatars")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
app = FastAPI(
    title = "Event Ticket",
    description = "Event Ticket API",
    version = "0.1.0",
)
@app.get("/")
async def root():
    return {"message": "Event Ticket API"}

@app.get("/health")
async def health():
    return {"status": "ok" , "version": "0.1.0"}
app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(auth_router, prefix="/api/v1")
app.include_router(ticket_router, prefix="/api/v1")
app.include_router(tag_router, prefix="/api/v1")
app.include_router(review_router, prefix="/api/v1")
app.include_router(event_router, prefix="/api/v1")
app.include_router(category_router, prefix="/api/v1")
app.include_router(search_router, prefix="/api/v1")
