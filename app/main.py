from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.router import api_router
from app.core.scheduler import setup_scheduler
from app.services.lol_store import LoLStoreService
import os
import re
import json

app = FastAPI(
    title="Honken Mini Hub",
    description="Honken's Server in Mini PC",
    version="1.0.0"
)

# CORS 설정 (HTTP/HTTPS 모두 허용 가능)
cors_origins_env = os.getenv("CORS_ORIGINS", "*")
if cors_origins_env == "*":
    allow_origins = ["*"]
else:
    allow_origins = [o.strip() for o in cors_origins_env.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API 라우터는 /api/v1 아래에 마운트
app.include_router(api_router, prefix="/api/v1")

# Initialize services
lol_store_service = LoLStoreService()

@app.on_event("startup")
async def startup_event():
    """Initialize scheduler on startup"""
    setup_scheduler()

# 루트 페이지 - 커스텀 인덱스 제공
@app.get("/")
async def root_index():
    return FileResponse("app/templates/index.html")

# API 엔드포인트들...
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

@app.get("/lime-voca/word-bank")
async def list_word_bank_files():
    """List available word bank JSON base names."""
    base_dir = os.path.join("data", "lime_voca", "word_bank")
    try:
        filenames = [
            os.path.splitext(name)[0]
            for name in os.listdir(base_dir)
            if name.endswith(".json") and os.path.isfile(os.path.join(base_dir, name))
        ]
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="Word bank directory not found")
    return JSONResponse(content={"available": sorted(filenames)})

@app.get("/lime-voca/word-bank/{name}")
async def get_word_bank_file(name: str):
    """Return JSON content for a specific word bank by base name.
    Validates name to prevent path traversal and only allows simple filenames.
    """
    if not re.fullmatch(r"[A-Za-z0-9_.\-]+", name):
        raise HTTPException(status_code=400, detail="Invalid file name")
    base_dir = os.path.join("data", "lime_voca", "word_bank")
    file_path = os.path.join(base_dir, f"{name}.json")
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Invalid JSON content")
    return JSONResponse(content=data)

@app.get("/lol-back-play/privacy")
async def get_privacy_policy():
    """Get privacy policy page"""
    return FileResponse("policy/lol_back_play/privacy.html")

@app.get("/lol-back-play/privacy/")
async def get_privacy_policy_trailing():
    return FileResponse("policy/lol_back_play/privacy.html")

@app.get("/lol-back-play/terms")
async def get_terms_conditions():
    """Get terms and conditions page"""
    return FileResponse("policy/lol_back_play/terms.html")

@app.get("/lol-back-play/terms/")
async def get_terms_conditions_trailing():
    return FileResponse("policy/lol_back_play/terms.html")

# React 빌드 결과물 마운트 (마지막에 배치하여 API 라우트가 우선 매칭되도록 함)
app.mount("/", StaticFiles(directory="app/static", html=True), name="static")