from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class SessionType(str, Enum):
    RACE = "R"
    QUALIFYING = "Q"
    PRACTICE_1 = "FP1"
    PRACTICE_2 = "FP2"
    PRACTICE_3 = "FP3"
    SPRINT_QUALIFYING = "SQ"
    SPRINT = "S"


class RaceInfo(BaseModel):
    """Information about a specific race session."""
    year: int = Field(..., ge=2014, le=2025, description="Year of the race")
    grand_prix: str = Field(..., min_length=1,
                            description="Name of the Grand Prix")
    session: str = Field(..., description="Session type (R, Q, FP1, etc.)")
    race_laps: Optional[int] = Field(None, description="Number of race laps")
    created_at: Optional[datetime] = Field(
        None, description="When the data was ingested")


class IngestionRequest(BaseModel):
    """Request model for ingesting specific races."""
    races: List[RaceInfo] = Field(..., min_items=1,
                                  description="List of races to ingest")


class IngestionResponse(BaseModel):
    """Response model for ingestion requests."""
    task_id: str = Field(...,
                         description="Unique identifier for the ingestion task")
    message: str = Field(..., description="Status message")
    years: Optional[List[int]] = Field(
        None, description="Years being ingested")
    sessions: Optional[List[str]] = Field(
        None, description="Session types being ingested")
    races: Optional[List[RaceInfo]] = Field(
        None, description="Specific races being ingested")
    status: str = Field(..., description="Current status of the task")


class TaskStatus(BaseModel):
    """Status information for an ingestion task."""
    task_id: str = Field(..., description="Task identifier")
    status: str = Field(..., description="Current status")
    started_at: Optional[datetime] = Field(
        None, description="When the task started")
    completed_at: Optional[datetime] = Field(
        None, description="When the task completed")
    total_items: int = Field(0, description="Total number of items to process")
    processed_items: int = Field(0, description="Number of items processed")
    failed_items: int = Field(0, description="Number of items that failed")
    progress_percentage: float = Field(0.0, description="Progress percentage")
    error_message: Optional[str] = Field(
        None, description="Error message if failed")
    estimated_completion: Optional[datetime] = Field(
        None, description="Estimated completion time")


class IngestionStats(BaseModel):
    """Statistics about ingested data."""
    total_sessions: int = Field(...,
                                description="Total number of sessions ingested")
    years_covered: int = Field(..., description="Number of years covered")
    unique_grand_prix: int = Field(...,
                                   description="Number of unique Grand Prix")
    earliest_year: Optional[int] = Field(
        None, description="Earliest year in dataset")
    latest_year: Optional[int] = Field(
        None, description="Latest year in dataset")
    sessions_by_year: List[Dict[str, Any]
                           ] = Field(..., description="Session count by year")
    sessions_by_type: List[Dict[str, Any]
                           ] = Field(..., description="Session count by type")


class DriverInfo(BaseModel):
    """Driver information."""
    driver_number: str = Field(..., description="Driver number")
    driver_code: str = Field(..., description="Driver code")
    driver_name: str = Field(..., description="Driver full name")
    team: Optional[str] = Field(None, description="Team name")
    position: Optional[int] = Field(None, description="Final position")
    points: Optional[float] = Field(None, description="Points scored")


class LapInfo(BaseModel):
    """Lap information."""
    lap_number: int = Field(..., description="Lap number")
    lap_time: Optional[float] = Field(None, description="Lap time in seconds")
    sector_1_time: Optional[float] = Field(None, description="Sector 1 time")
    sector_2_time: Optional[float] = Field(None, description="Sector 2 time")
    sector_3_time: Optional[float] = Field(None, description="Sector 3 time")
    compound: Optional[str] = Field(None, description="Tire compound")
    tyre_life: Optional[int] = Field(None, description="Tire life in laps")
    position: Optional[int] = Field(None, description="Position at end of lap")


class WeatherInfo(BaseModel):
    """Weather information."""
    lap_number: int = Field(..., description="Lap number")
    air_temp: Optional[float] = Field(
        None, description="Air temperature in Celsius")
    track_temp: Optional[float] = Field(
        None, description="Track temperature in Celsius")
    humidity: Optional[float] = Field(None, description="Humidity percentage")
    pressure: Optional[float] = Field(None, description="Atmospheric pressure")
    wind_speed: Optional[float] = Field(None, description="Wind speed")
    wind_direction: Optional[float] = Field(None, description="Wind direction")
    rainfall: Optional[float] = Field(None, description="Rainfall amount")


class SafetyCarEvent(BaseModel):
    """Safety car event information."""
    start_lap: int = Field(..., description="Lap when SC started")
    end_lap: int = Field(..., description="Lap when SC ended")
    duration_laps: int = Field(..., description="Duration in laps")
    event_type: str = Field(..., description="Type of event")
    reason: Optional[str] = Field(None, description="Reason for the event")


class SessionDetails(BaseModel):
    """Detailed session information."""
    race_info: RaceInfo = Field(..., description="Basic race information")
    drivers: List[DriverInfo] = Field(..., description="List of drivers")
    laps: List[LapInfo] = Field(..., description="Lap data")
    weather: List[WeatherInfo] = Field(..., description="Weather data")
    safety_car_events: List[SafetyCarEvent] = Field(
        ..., description="Safety car events")
    total_laps: int = Field(..., description="Total number of laps")
    fastest_lap: Optional[float] = Field(None, description="Fastest lap time")


class BulkIngestionRequest(BaseModel):
    """Request for bulk ingestion with advanced options."""
    years: List[int] = Field(..., min_items=1, description="Years to ingest")
    sessions: List[str] = Field(
        default=["R", "Q", "FP1", "FP2", "FP3"], description="Session types")
    grand_prix_filter: Optional[List[str]] = Field(
        None, description="Specific Grand Prix to include")
    exclude_grand_prix: Optional[List[str]] = Field(
        None, description="Grand Prix to exclude")
    include_weather: bool = Field(True, description="Include weather data")
    include_safety_car: bool = Field(
        True, description="Include safety car events")
    include_lap_data: bool = Field(
        True, description="Include detailed lap data")
    max_concurrent: int = Field(
        5, ge=1, le=10, description="Maximum concurrent downloads")
