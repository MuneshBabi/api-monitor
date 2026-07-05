import time 
import httpx
import logging
from sqlalchemy import select, func
from fastapi import HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from app.models.monitor import Monitor
from app.models.monitor_check import MonitorCheck

logger = logging.getLogger(__name__)

def run_monitor_check(monitor: Monitor, db: Session):
    logger.info(f"Running check for monitor {monitor.id} ({monitor.name})")

    start_time = time.perf_counter()

    try:
        response = httpx.get(monitor.url, follow_redirects=True, timeout=5)
        end_time = time.perf_counter()
        response_time_ms = int((end_time - start_time)*1000)
        status_code = response.status_code
        is_up = status_code < 400

        logger.info(f"Monitor {monitor.id} ({monitor.name}) responded with status {status_code}")

    except httpx.RequestError:
        end_time = time.perf_counter()
        response_time_ms = int((end_time-start_time)*1000)
        status_code = 0
        is_up = False

        logger.warning(f"Monitor {monitor.id} ({monitor.name}) is unreachable")

    new_check = MonitorCheck(monitor_id = monitor.id,
                             status_code = status_code,
                             response_time_ms = response_time_ms, 
                             is_up = is_up)
    
    db.add(new_check)
    monitor.last_checked_at = datetime.now()
    db.commit()
    db.refresh(new_check)

    return {
        "monitor_id": monitor.id,
        "status_code": status_code,
        "response_time_ms": response_time_ms,
        "is_up": is_up
    }   

def get_monitor_stats(monitor_id: int, db: Session):
    monitor = db.get(Monitor, monitor_id)

    if monitor is None:
        raise HTTPException(status_code=404, detail="Monitor not found")
    
    total_checks = db.scalar(select(func.count())
                             .select_from(MonitorCheck)
                             .where(MonitorCheck.monitor_id == monitor_id))
    
    successful_checks = db.scalar(select(func.count())
                                  .select_from(MonitorCheck)
                                  .where(MonitorCheck.monitor_id == monitor_id,
                                         MonitorCheck.is_up.is_(True)))
    
    failed_checks = total_checks - successful_checks

    average_response_time_ms = db.scalar(select(func.avg(MonitorCheck.response_time_ms))
                                         .where(MonitorCheck.monitor_id == monitor_id))
    
    if average_response_time_ms is None:
        average_response_time_ms = 0

    if total_checks == 0:
        uptime_percentage = 0
    else: 
        uptime_percentage = (successful_checks/total_checks)*100

    return {
        "monitor_id": monitor.id,
        "total_checks": total_checks,
        "successful_checks": successful_checks,
        "failed_checks": failed_checks,
        "uptime_percentage": round(uptime_percentage, 2),
        "average_response_time_ms": round(average_response_time_ms, 2)
    }

def get_dashboard_stats(db: Session):
    total_monitors = db.scalar(select(func.count())
                              .select_from(Monitor))
    
    active_monitors = db.scalar(select(func.count())
                                .select_from(Monitor)
                                .where(Monitor.status == "ACTIVE"))
    
    total_checks = db.scalar(select(func.count())
                             .select_from(MonitorCheck))
    
    successful_checks = db.scalar(select(func.count())
                                  .select_from(MonitorCheck)
                                  .where(MonitorCheck.is_up.is_(True)))
    
    failed_checks = total_checks - successful_checks

    average_response_time_ms = db.scalar(select(func.avg(MonitorCheck.response_time_ms)))

    if average_response_time_ms is None:
        average_response_time_ms = 0
    
    if total_checks == 0:
        overall_uptime_percentage = 0
    else: 
        overall_uptime_percentage = (successful_checks/total_checks)*100

    return {
        "total_monitors": total_monitors,
        "active_monitors": active_monitors,
        "total_checks": total_checks,
        "successful_checks": successful_checks,
        "failed_checks": failed_checks,
        "overall_uptime_percentage": round(overall_uptime_percentage,2),
        "average_response_time_ms": round(average_response_time_ms,2)
    }

def get_monitor_health(monitor_id: int, db: Session):
    monitor = db.get(Monitor, monitor_id)

    if monitor is None:
        raise HTTPException(status_code=404, detail="Monitor not found")
    
    latest_check = db.execute(select(MonitorCheck)
                              .where(MonitorCheck.monitor_id == monitor_id)
                              .order_by(MonitorCheck.created_at.desc())).scalars().first()
    
    if latest_check is None:
        raise HTTPException(status_code=404, detail="No checks found for monitor")
    
    return {
        "monitor_id": monitor.id,
        "status": "UP" if latest_check.is_up else "DOWN",
        "last_status_code": latest_check.status_code,
        "last_response_time_ms": latest_check.response_time_ms,
        "last_checked_at": latest_check.created_at
    }
    
