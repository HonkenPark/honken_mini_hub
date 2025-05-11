from fastapi import APIRouter, HTTPException
from app.models.lol_store import DiscountResponse, LastUpdateResponse
from app.services.lol_store import LoLStoreService

router = APIRouter()
lol_store_service = LoLStoreService()

@router.get("/discounts", response_model=DiscountResponse)
async def get_discounts():
    """Get the latest scraping results"""
    results = await lol_store_service.get_discounts()
    if not results["discounts"]:
        raise HTTPException(status_code=404, detail="No scraping results available yet")
    return results

@router.get("/last-update", response_model=LastUpdateResponse)
async def get_last_update():
    """Get the timestamp of the last successful scraping"""
    result = lol_store_service.get_last_update()
    if not result["last_update"]:
        raise HTTPException(status_code=404, detail="No scraping has been performed yet")
    return result 