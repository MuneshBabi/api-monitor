from sqlalchemy import Integer, String, text, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

from app.db.base import Base

class Monitor(Base):
    __tablename__ = "monitors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    url: Mapped[str] = mapped_column(String(500))
    status: Mapped[str] = mapped_column(String(20), default= "ACTIVE", server_default=text("'ACTIVE'"))

    interval_minutes: Mapped[int] = mapped_column(Integer, default=5, server_default="5")

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    last_checked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    checks = relationship("MonitorCheck", back_populates="monitor", cascade="all, delete-orphan") 