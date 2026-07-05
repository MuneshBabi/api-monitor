from fastapi import APIRouter, Depends, HTTPException, status, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.monitor import Monitor
from app.schemas.monitor import MonitorCreate, MonitorResponse, MonitorUpdate
from app.models.monitor_check import MonitorCheck
from app.schemas.monitor_check import MonitorCheckResponse, MonitorCheckHistoryResponse, MonitorStatsResponse
from app.services.monitor_service import run_monitor_check, get_monitor_stats
from app.schemas.dashboard import DashboardResponse
from app.services.monitor_service import get_dashboard_stats
from app.schemas.health import MonitorHealthResponse
from app.services.monitor_service import get_monitor_health

router = APIRouter(prefix="/monitors",
                   tags=["Monitors"])

@router.get("/dashboard", response_model=DashboardResponse)
def dashboard(db: Session = Depends(get_db)):
    return get_dashboard_stats(db)

@router.post("/", response_model=MonitorResponse)
def create_monitor(monitor: MonitorCreate, db: Session = Depends(get_db)):
    new_monitor = Monitor(name=monitor.name,
                          url=str(monitor.url),
                          interval_minutes=monitor.interval_minutes)
    db.add(new_monitor)
    db.commit()
    db.refresh(new_monitor)
    return new_monitor

@router.get("/", response_model=list[MonitorResponse])
def get_monitors(skip: int = Query(0, ge=0), 
                 limit: int = Query(10, ge=1, le=100),
                 name: str | None = None,
                 db: Session = Depends(get_db)):
    query = select(Monitor)
    if name: 
        query = query.where(Monitor.name.ilike(f"%{name}%"))
    
    query = query.offset(skip).limit(limit)
    monitors = db.execute(query).scalars().all()
    return monitors

@router.get("/{monitor_id}", response_model=MonitorResponse)
def get_monitor(monitor_id: int, db: Session= Depends(get_db)):
    monitor = db.execute(select(Monitor).where(Monitor.id == monitor_id)).scalar_one_or_none()
    if monitor is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= "Monitor not found")
    return monitor

@router.put("/{monitor_id}", response_model=MonitorResponse)
def update_monitor(monitor_id: int,
                   monitor: MonitorUpdate,
                   db: Session = Depends(get_db)):
    existing_monitor = db.execute(select(Monitor).where(
        Monitor.id == monitor_id
        )).scalar_one_or_none()
    
    if existing_monitor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Monitor not found"
        )
    
    if monitor.name is not None:
        existing_monitor.name = monitor.name

    if monitor.url is not None:
        existing_monitor.url = str(monitor.url)

    if monitor.interval_minutes is not None:
        existing_monitor.interval_minutes = monitor.interval_minutes

    db.commit()
    db.refresh(existing_monitor)
    return existing_monitor

@router.delete("/{monitor_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_monitor(monitor_id: int,
                   db: Session= Depends(get_db)):
    monitor = db.execute(select(Monitor).where(
        Monitor.id == monitor_id
    )).scalar_one_or_none()
    
    if monitor is None:
        raise HTTPException(
            status_code= status.HTTP_404_NOT_FOUND,
            detail= "Monitor not found"
        )
    db.delete(monitor)
    db.commit()

@router.post("/{monitor_id}/check", response_model= MonitorCheckResponse)
def check_monitor(monitor_id: int,
                  db: Session = Depends(get_db)):
    monitor = db.get(Monitor, monitor_id)

    if monitor is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Monitor not found")
    
    return run_monitor_check(monitor=monitor, db=db)

@router.get("/{monitor_id}/health", response_model=MonitorHealthResponse)
def monitor_health(monitor_id: int,
                    db: Session = Depends(get_db)):
    return get_monitor_health(monitor_id=monitor_id,
                              db=db)

@router.get("/{monitor_id}/checks", response_model=list[MonitorCheckHistoryResponse])
def get_monitor_checks(monitor_id: int,
                       skip: int = 0,
                       limit: int = 10,
                       db: Session = Depends(get_db)):
    monitor = db.get(Monitor, monitor_id)

    if monitor is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Monitor not found")
    
    checks = db.execute(select(MonitorCheck)
                        .where(MonitorCheck.monitor_id == monitor_id)
                               .order_by(MonitorCheck.id.desc())
                               .offset(skip)
                               .limit(limit)).scalars().all()
    return checks

@router.get("/{monitor_id}/stats", response_model=MonitorStatsResponse)
def get_monitor_stats_endpoint(monitor_id: int,
                      db: Session = Depends(get_db)):
    
    return get_monitor_stats(monitor_id=monitor_id,
                             db=db)

