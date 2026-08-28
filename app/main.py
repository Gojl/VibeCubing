from fastapi import FastAPI
from sqlalchemy import text
from app.api.rooms import router as rooms_router
from app.db.models import User, Room, RoomMember, Round, Solve
from app.db.database import AsyncSessionLocal


app = FastAPI()

app.include_router(rooms_router)

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