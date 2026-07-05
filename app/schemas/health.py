from datetime import datetime
from pydantic import BaseModel

class MonitorHealthResponse(BaseModel):
    monitor_id: int
    status: str
    last_status_code: int
    last_response_time_ms: int
    last_checked_at: datetime