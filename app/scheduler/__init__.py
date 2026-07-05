from apscheduler.schedulers.background import BackgroundScheduler
from app.scheduler.jobs import run_scheduled_checks

scheduler = BackgroundScheduler()

scheduler.add_job(run_scheduled_checks,
                  "interval",
                  minutes=1,
                  id="monitor_checks")