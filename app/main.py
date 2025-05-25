from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from app.api.v1.router import api_router
from app.core.scheduler import setup_scheduler
from app.services.lol_store import LoLStoreService
import os

app = FastAPI(
    title="Honken Mini Hub",
    description="Honken's Server in Mini PC",
    version="1.0.0"
)

# 정적 파일 마운트
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Include API router
app.include_router(api_router, prefix="/api/v1")

# Initialize services
lol_store_service = LoLStoreService()

@app.on_event("startup")
async def startup_event():
    """Initialize scheduler on startup"""
    setup_scheduler()

@app.get("/")
async def root():
    """Root endpoint returning HTML page"""
    return FileResponse("app/templates/index.html")

@app.get("/discounts")
async def get_discounts():
    """Get current discount information"""
    return await lol_store_service.get_discounts()

@app.get("/skin_discount")
async def get_latest_video():
    """Get the latest skin discount video URL"""
    try:
        with open("data/lol_store/latest_video_id.txt", "r") as f:
            video_url = f.read().strip()
        return JSONResponse(content={"video_url": video_url})
    except FileNotFoundError:
        return JSONResponse(
            status_code=404,
            content={"error": "Latest video information not found"}
        ) 