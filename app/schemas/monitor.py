from datetime import datetime

from pydantic import BaseModel, HttpUrl, ConfigDict

class MonitorCreate(BaseModel):
    name: str
    url: HttpUrl
    interval_minutes: int = 5

class MonitorResponse(BaseModel):
    id: int
    name: str
    url: str
    status: str
    interval_minutes: int
    created_at: datetime

    model_config = ConfigDict(
        from_attributes= True
    )

class MonitorUpdate(BaseModel):
    name: str | None = None
    url: HttpUrl | None = None
    interval_minutes: int | None = None