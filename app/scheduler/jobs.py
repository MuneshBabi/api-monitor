import logging

from datetime import datetime, timezone
from sqlalchemy import select

from app.db.database import SessionLocal
from app.models.monitor import Monitor
from app.services.monitor_service import run_monitor_check

logger = logging.getLogger(__name__)

def run_scheduled_checks():
    logger.info("Running scheduled monitor checks")

    db = SessionLocal()

    try:
        monitors = db.execute(select(Monitor)).scalars().all()

        now = datetime.now(timezone.utc)

        for monitor in monitors:
            if monitor.last_checked_at is None:
                logger.info(f"Scheduler checking monitor {monitor.id}")
                run_monitor_check(monitor=monitor, db=db)
                continue

            elapsed_minutes = (now - monitor.last_checked_at).total_seconds()/60

            if elapsed_minutes >= monitor.interval_minutes:
                logger.info(f"Scheduler checking monitor {monitor.id}")
                run_monitor_check(monitor=monitor, db=db)
            
    finally:
        db.close()