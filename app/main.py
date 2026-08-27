from fastapi import FastAPI
from sqlalchemy import text

from app.db.database import AsyncSessionLocal


app = FastAPI()


@app.get("/health")
async def health():
    async with AsyncSessionLocal() as session:
        result = await session.execute(text("SELECT 1"))
        return {
            "status": "ok",
            "database": result.scalar(),
        }