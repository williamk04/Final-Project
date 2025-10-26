# backend/models/vehicle_model.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class VehicleSchema(BaseModel):
    license_plate: str
    image_url: str
    entry_time: datetime
    exit_time: Optional[datetime] = None
    status: str
    fee: Optional[int] = 0
