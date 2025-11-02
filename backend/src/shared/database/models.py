"""Database models."""

from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String, UniqueConstraint

from .database import Base


class ScheduleDB(Base):
    """SQLAlchemy model for schedules - simplified for single cluster"""

    __tablename__ = "schedules"

    id = Column(Integer, primary_key=True, index=True)
    namespace = Column(String, nullable=False, index=True)
    deployment_name = Column(String, nullable=False, index=True)
    scale_down_time = Column(String, nullable=False)  # Format: "HH:MM"
    scale_up_time = Column(String, nullable=False)  # Format: "HH:MM"
    original_replicas = Column(Integer, nullable=True)  # Null until first scale down
    enabled = Column(Boolean, default=True, nullable=False)
    is_scaled_down = Column(Boolean, default=False, nullable=False)
    last_scaled_at = Column(DateTime, nullable=True)  # Last time scaled up or down
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    __table_args__ = (UniqueConstraint("namespace", "deployment_name", name="uix_namespace_deployment"),)
