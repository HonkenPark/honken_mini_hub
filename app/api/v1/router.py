from fastapi import APIRouter
from app.api.v1.endpoints import lol_store

api_router = APIRouter()
api_router.include_router(lol_store.router, prefix="/lol-store", tags=["lol-store"]) 