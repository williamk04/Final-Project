from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional

@dataclass
class Vehicle:
    license_plate: str
    image_url: str
    entry_time: datetime
    status: str = "in"
    fee: int = 0
    duration_minutes: float = 0.0
    exit_time: Optional[datetime] = None
    exit_image_url: Optional[str] = None

    def to_dict(self):
        """Chuyển object thành dict để lưu Firestore"""
        data = asdict(self)
        # convert datetime -> iso string
        data["entry_time"] = self.entry_time.isoformat()
        if self.exit_time:
            data["exit_time"] = self.exit_time.isoformat()
        return data
