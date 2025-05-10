from fastapi import FastAPI
from app.api.v1.router import api_router
from app.core.scheduler import setup_scheduler
from app.services.lol_store import LoLStoreService

app = FastAPI(
    title="LoL Store Scraper API",
    description="API for scraping League of Legends store discounts",
    version="1.0.0"
)

# Include API router
app.include_router(api_router, prefix="/api/v1")

# Initialize services
lol_store_service = LoLStoreService()

@app.on_event("startup")
async def startup_event():
    """Initialize scheduler and run initial scraping on startup"""
    setup_scheduler()
    # Run initial scraping
    await lol_store_service.update_discounts()

@app.get("/")
async def root():
    """Root endpoint returning basic API information"""
    return {
        "name": "LoL Store Scraper API",
        "description": "API for scraping League of Legends store discounts",
        "version": "1.0.0",
        "endpoints": {
            "/api/v1/lol-store/discounts": "Get current discount information",
            "/api/v1/lol-store/last-update": "Get last scraping timestamp"
        }
    } 

@app.get("/discounts")
async def get_discounts():
    """Get current discount information"""
    discounts = await lol_store_service.update_discounts()
    return discounts 