from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from app.api.websocket import router as websocket_router
from app.api.rooms import router as rooms_router
from app.db.models import User, Room, RoomMember, Round, Solve
from app.db.database import AsyncSessionLocal


app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"

app.mount(
    "/static",
    StaticFiles(directory=STATIC_DIR),
    name="static",
)


@app.get("/")
async def index():
    return FileResponse(STATIC_DIR / "index.html")


app.include_router(rooms_router)
app.include_router(websocket_router)


@app.get("/health")
async def health():
    async with AsyncSessionLocal() as session:
        result = await session.execute(text("SELECT 1"))

        return {
            "status": "ok",
            "database": result.scalar(),
        }
    
# uvicorn app.main:app --reload
#psql -U postgres -h localhost -d cube_race