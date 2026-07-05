import logging

from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.scheduler import scheduler

from app.routers.monitor import router as monitor_router

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting API Monitor...")
    scheduler.start()
    logger.info("Scheduler started...")
    yield
    scheduler.shutdown()
    logger.info("Scheduler stopped...")
    logger.info("Shutting down API Monitor...")


app = FastAPI(
    title= "API Monitor",
    version= "1.0.0",
    lifespan=lifespan
)

app.include_router(monitor_router)