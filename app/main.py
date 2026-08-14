# app/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.config import settings
from app.core.database import engine, Base
import app.models  # Registers all ORM models to Base metadata
from app.api.v1.router import api_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Auto-initialize database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()

app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan, version="1.0.0")
app.include_router(api_router, prefix="/api/v1")

@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy", "service": settings.PROJECT_NAME}
