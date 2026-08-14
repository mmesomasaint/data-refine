# app/api/v1/router.py
from fastapi import APIRouter
from app.api.v1.endpoints import router as imports_router

api_router = APIRouter()
api_router.include_router(imports_router, prefix="/imports", tags=["CSV Ingestion & Cleaning"])
