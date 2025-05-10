from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class DiscountedSkin(BaseModel):
    url: str
    name: str
    price: str
    discount: str

class DiscountResponse(BaseModel):
    last_update: datetime
    count: int
    results: List[DiscountedSkin]

class LastUpdateResponse(BaseModel):
    last_update: datetime 