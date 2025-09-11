from sqlalchemy import Column, Integer, String, DateTime, Float, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime
from typing import Dict, List, Optional
from enum import Enum

Base = declarative_base()


class IngestionStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class RaceData(Base):
    """Model for storing race session data."""
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    year = Column(Integer, nullable=False, index=True)
    grand_prix = Column(String(100), nullable=False, index=True)
    session_code = Column(String(10), nullable=False, index=True)
    race_laps = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Additional metadata
    track_name = Column(String(200))
    country = Column(String(100))
    circuit_length = Column(Float)
    weather_conditions = Column(JSON)
    total_drivers = Column(Integer)

    def __repr__(self):
        return f"<RaceData(year={self.year}, gp={self.grand_prix}, session={self.session_code})>"


class IngestionTask(Base):
    """Model for tracking ingestion tasks."""
    __tablename__ = "ingestion_tasks"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String(100), unique=True, index=True)
    status = Column(String(20), default=IngestionStatus.PENDING)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    total_items = Column(Integer, default=0)
    processed_items = Column(Integer, default=0)
    failed_items = Column(Integer, default=0)
    error_message = Column(Text)
    task_config = Column(JSON)

    def __repr__(self):
        return f"<IngestionTask(id={self.task_id}, status={self.status})>"


class DriverData(Base):
    """Model for storing driver information."""
    __tablename__ = "drivers"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, nullable=False, index=True)
    driver_number = Column(String(10), nullable=False)
    driver_code = Column(String(10), nullable=False, index=True)
    driver_name = Column(String(100), nullable=False)
    team = Column(String(100))
    position = Column(Integer)
    points = Column(Float)
    fastest_lap = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<DriverData(session={self.session_id}, driver={self.driver_code})>"


class LapData(Base):
    """Model for storing lap-by-lap data."""
    __tablename__ = "lap_data"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, nullable=False, index=True)
    driver_id = Column(Integer, nullable=False, index=True)
    lap_number = Column(Integer, nullable=False)
    lap_time = Column(Float)
    sector_1_time = Column(Float)
    sector_2_time = Column(Float)
    sector_3_time = Column(Float)
    compound = Column(String(20))
    tyre_life = Column(Integer)
    stint = Column(Integer)
    position = Column(Integer)
    gap_to_leader = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<LapData(session={self.session_id}, driver={self.driver_id}, lap={self.lap_number})>"


class WeatherData(Base):
    """Model for storing weather data."""
    __tablename__ = "weather_data"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, nullable=False, index=True)
    lap_number = Column(Integer, nullable=False)
    air_temp = Column(Float)
    track_temp = Column(Float)
    humidity = Column(Float)
    pressure = Column(Float)
    wind_speed = Column(Float)
    wind_direction = Column(Float)
    rainfall = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<WeatherData(session={self.session_id}, lap={self.lap_number})>"


class SafetyCarData(Base):
    """Model for storing safety car events."""
    __tablename__ = "safety_car_events"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, nullable=False, index=True)
    start_lap = Column(Integer, nullable=False)
    end_lap = Column(Integer, nullable=False)
    duration_laps = Column(Integer)
    event_type = Column(String(50))  # SAFETY_CAR, VIRTUAL_SAFETY_CAR, RED_FLAG
    reason = Column(String(200))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<SafetyCarData(session={self.session_id}, laps={self.start_lap}-{self.end_lap})>"
