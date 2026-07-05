from pydantic import BaseModel

class DashboardResponse(BaseModel):
    total_monitors: int
    active_monitors: int
    total_checks: int
    successful_checks: int
    failed_checks: int
    overall_uptime_percentage: float
    average_response_time_ms: float