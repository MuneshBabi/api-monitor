from pydantic import BaseModel
from datetime import datetime

class MonitorCheckResponse(BaseModel):
    monitor_id: int
    status_code: int
    response_time_ms: int
    is_up: bool

class MonitorCheckHistoryResponse(BaseModel):
    id: int
    status_code: int
    response_time_ms: int
    is_up: bool
    created_at: datetime

    class config:
        from_attributes: True

class MonitorStatsResponse(BaseModel):
    monitor_id: int
    total_checks: int
    successful_checks: int
    failed_checks: int
    uptime_percentage: float
    average_response_time_ms: float
