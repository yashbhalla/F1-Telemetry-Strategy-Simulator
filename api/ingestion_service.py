from api.schemas import RaceInfo, TaskStatus
from api.models import RaceData, IngestionTask, DriverData, LapData, WeatherData, SafetyCarData, IngestionStatus
from db.database import DatabaseManager
import asyncio
import fastf1
from fastf1 import plotting
import pandas as pd
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
import logging
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, text
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import sys
from pathlib import Path

# Add project root to path
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RaceIngestionService:
    """Service for ingesting F1 race data from FastF1."""

    def __init__(self, database_url: str = "postgresql://postgres:password@localhost:5432/f1_strategy"):
        self.db_manager = DatabaseManager(database_url)
        self.engine = create_engine(database_url)
        self.SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine)

        # Task tracking
        self.tasks: Dict[str, TaskStatus] = {}

        # Configure FastF1 cache
        cache_dir = ROOT / "data" / "cache"
        cache_dir.mkdir(parents=True, exist_ok=True)
        fastf1.Cache.enable_cache(str(cache_dir))

        # Grand Prix names mapping (common variations)
        self.gp_name_mapping = {
            "bahrain": "Bahrain",
            "saudi": "Saudi Arabia",
            "australia": "Australia",
            "japan": "Japan",
            "china": "China",
            "miami": "Miami",
            "emilia": "Emilia Romagna",
            "monaco": "Monaco",
            "canada": "Canada",
            "spain": "Spain",
            "austria": "Austria",
            "britain": "Great Britain",
            "hungary": "Hungary",
            "belgium": "Belgium",
            "netherlands": "Netherlands",
            "italy": "Italy",
            "azerbaijan": "Azerbaijan",
            "singapore": "Singapore",
            "united": "United States",
            "mexico": "Mexico",
            "brazil": "Brazil",
            "abu": "Abu Dhabi",
            "qatar": "Qatar",
            "vegas": "Las Vegas"
        }

    def get_task_status(self, task_id: str) -> Optional[TaskStatus]:
        """Get the status of a specific task."""
        return self.tasks.get(task_id)

    def get_all_status(self) -> Dict[str, TaskStatus]:
        """Get status of all tasks."""
        return self.tasks

    def _update_task_status(self, task_id: str, **kwargs):
        """Update task status."""
        if task_id in self.tasks:
            task = self.tasks[task_id]
            for key, value in kwargs.items():
                if hasattr(task, key):
                    setattr(task, key, value)

            # Calculate progress percentage
            if task.total_items > 0:
                task.progress_percentage = (
                    task.processed_items / task.total_items) * 100

            # Estimate completion time
            if task.status == IngestionStatus.RUNNING and task.processed_items > 0:
                elapsed = time.time() - task.started_at.timestamp()
                rate = task.processed_items / elapsed
                remaining = task.total_items - task.processed_items
                if rate > 0:
                    eta_seconds = remaining / rate
                    task.estimated_completion = datetime.now() + timedelta(seconds=eta_seconds)

    async def ingest_multiple_years(
        self,
        years: List[int],
        sessions: List[str],
        task_id: str
    ):
        """Ingest data for multiple years."""
        logger.info(
            f"Starting ingestion for years {years} with sessions {sessions}")

        # Initialize task
        self.tasks[task_id] = TaskStatus(
            task_id=task_id,
            status=IngestionStatus.RUNNING,
            started_at=datetime.now(),
            total_items=len(years) * len(sessions) * 10,  # Estimate
            processed_items=0,
            failed_items=0
        )

        try:
            for year in years:
                await self.ingest_year(year, sessions, f"{task_id}_year_{year}")

            self._update_task_status(
                task_id, status=IngestionStatus.COMPLETED, completed_at=datetime.now())
            logger.info(f"Completed ingestion for years {years}")

        except Exception as e:
            logger.error(f"Failed to ingest years {years}: {e}")
            self._update_task_status(
                task_id, status=IngestionStatus.FAILED, error_message=str(e))

    async def ingest_year(
        self,
        year: int,
        sessions: List[str],
        task_id: str
    ):
        """Ingest data for a specific year."""
        logger.info(f"Starting ingestion for year {year}")

        # Get available Grand Prix for the year
        try:
            available_gps = self._get_available_grand_prix(year)
            logger.info(
                f"Found {len(available_gps)} Grand Prix for {year}: {available_gps}")

            total_sessions = len(available_gps) * len(sessions)

            # Update task with more accurate total
            if task_id in self.tasks:
                self._update_task_status(task_id, total_items=total_sessions)

            # Process each Grand Prix
            for gp in available_gps:
                for session in sessions:
                    try:
                        await self._ingest_session(year, gp, session)
                        self._update_task_status(
                            task_id, processed_items=self.tasks[task_id].processed_items + 1)
                    except Exception as e:
                        logger.error(
                            f"Failed to ingest {year} {gp} {session}: {e}")
                        self._update_task_status(
                            task_id, failed_items=self.tasks[task_id].failed_items + 1)

            logger.info(f"Completed ingestion for year {year}")

        except Exception as e:
            logger.error(f"Failed to get Grand Prix for year {year}: {e}")
            raise

    async def ingest_specific_races(self, races: List[RaceInfo], task_id: str):
        """Ingest specific races."""
        logger.info(f"Starting ingestion for {len(races)} specific races")

        self.tasks[task_id] = TaskStatus(
            task_id=task_id,
            status=IngestionStatus.RUNNING,
            started_at=datetime.now(),
            total_items=len(races),
            processed_items=0,
            failed_items=0
        )

        try:
            for race in races:
                try:
                    await self._ingest_session(race.year, race.grand_prix, race.session)
                    self._update_task_status(
                        task_id, processed_items=self.tasks[task_id].processed_items + 1)
                except Exception as e:
                    logger.error(
                        f"Failed to ingest {race.year} {race.grand_prix} {race.session}: {e}")
                    self._update_task_status(
                        task_id, failed_items=self.tasks[task_id].failed_items + 1)

            self._update_task_status(
                task_id, status=IngestionStatus.COMPLETED, completed_at=datetime.now())
            logger.info(f"Completed ingestion for {len(races)} specific races")

        except Exception as e:
            logger.error(f"Failed to ingest specific races: {e}")
            self._update_task_status(
                task_id, status=IngestionStatus.FAILED, error_message=str(e))

    def _get_available_grand_prix(self, year: int) -> List[str]:
        """Get list of available Grand Prix for a given year."""
        # This is a simplified approach - in practice, you'd want to query FastF1
        # or maintain a mapping of available GPs per year

        # Common Grand Prix names (this would ideally be dynamic)
        common_gps = [
            "Bahrain", "Saudi Arabia", "Australia", "Japan", "China", "Miami",
            "Emilia Romagna", "Monaco", "Canada", "Spain", "Austria",
            "Great Britain", "Hungary", "Belgium", "Netherlands", "Italy",
            "Azerbaijan", "Singapore", "United States", "Mexico", "Brazil",
            "Abu Dhabi", "Qatar", "Las Vegas"
        ]

        # Filter based on year (some GPs didn't exist in certain years)
        if year < 2016:
            common_gps = [gp for gp in common_gps if gp not in [
                "Azerbaijan", "Miami", "Las Vegas"]]
        if year < 2018:
            common_gps = [gp for gp in common_gps if gp not in ["Qatar"]]
        if year < 2021:
            common_gps = [
                gp for gp in common_gps if gp not in ["Saudi Arabia"]]
        if year < 2022:
            common_gps = [gp for gp in common_gps if gp not in ["Miami"]]
        if year < 2023:
            common_gps = [gp for gp in common_gps if gp not in ["Las Vegas"]]

        return common_gps

    async def _ingest_session(self, year: int, grand_prix: str, session: str):
        """Ingest data for a specific session."""
        logger.info(f"Ingesting {year} {grand_prix} {session}")

        try:
            # Load session data
            session_obj = fastf1.get_session(year, grand_prix, session)
            session_obj.load(telemetry=True, laps=True, weather=True)

            # Save to database
            await self._save_session_to_db(session_obj, year, grand_prix, session)

        except Exception as e:
            logger.error(
                f"Failed to load session {year} {grand_prix} {session}: {e}")
            raise

    async def _save_session_to_db(self, session_obj, year: int, grand_prix: str, session: str):
        """Save session data to database."""
        db = self.SessionLocal()
        try:
            # Check if session already exists
            existing = db.query(RaceData).filter(
                RaceData.year == year,
                RaceData.grand_prix == grand_prix,
                RaceData.session_code == session
            ).first()

            if existing:
                logger.info(
                    f"Session {year} {grand_prix} {session} already exists, skipping")
                return

            # Create session record
            race_data = RaceData(
                year=year,
                grand_prix=grand_prix,
                session_code=session,
                race_laps=session_obj.total_laps if hasattr(
                    session_obj, 'total_laps') else None,
                track_name=getattr(session_obj, 'track_name', None),
                country=getattr(session_obj, 'country', None),
                circuit_length=getattr(session_obj, 'circuit_length', None),
                total_drivers=len(session_obj.drivers) if hasattr(
                    session_obj, 'drivers') else None
            )

            db.add(race_data)
            db.commit()
            db.refresh(race_data)

            # Save driver data
            if hasattr(session_obj, 'drivers') and session_obj.drivers is not None:
                for driver_code in session_obj.drivers:
                    try:
                        driver_info = session_obj.get_driver(driver_code)
                        driver_data = DriverData(
                            session_id=race_data.id,
                            driver_number=str(driver_info['DriverNumber']),
                            driver_code=driver_code,
                            driver_name=driver_info['FullName'],
                            team=driver_info.get('TeamName', None)
                        )
                        db.add(driver_data)
                    except Exception as e:
                        logger.warning(
                            f"Failed to save driver {driver_code}: {e}")

            # Save lap data
            if hasattr(session_obj, 'laps') and session_obj.laps is not None:
                laps_df = session_obj.laps
                for _, lap in laps_df.iterrows():
                    try:
                        lap_data = LapData(
                            session_id=race_data.id,
                            driver_id=1,  # This would need proper driver mapping
                            lap_number=int(lap['LapNumber']),
                            lap_time=lap['LapTime'].total_seconds(
                            ) if pd.notna(lap['LapTime']) else None,
                            compound=lap.get('Compound', None),
                            tyre_life=int(lap['TyreLife']) if pd.notna(
                                lap['TyreLife']) else None,
                            stint=int(lap['Stint']) if pd.notna(
                                lap['Stint']) else None,
                            position=int(lap['Position']) if pd.notna(
                                lap['Position']) else None
                        )
                        db.add(lap_data)
                    except Exception as e:
                        logger.warning(f"Failed to save lap data: {e}")

            # Save weather data
            if hasattr(session_obj, 'weather_data') and session_obj.weather_data is not None:
                weather_df = session_obj.weather_data
                for _, weather in weather_df.iterrows():
                    try:
                        weather_data = WeatherData(
                            session_id=race_data.id,
                            lap_number=int(weather['LapNumber']),
                            air_temp=weather.get('AirTemp', None),
                            track_temp=weather.get('TrackTemp', None),
                            humidity=weather.get('Humidity', None),
                            pressure=weather.get('Pressure', None),
                            wind_speed=weather.get('WindSpeed', None),
                            wind_direction=weather.get('WindDirection', None),
                            rainfall=weather.get('Rainfall', None)
                        )
                        db.add(weather_data)
                    except Exception as e:
                        logger.warning(f"Failed to save weather data: {e}")

            db.commit()
            logger.info(f"Successfully saved {year} {grand_prix} {session}")

        except Exception as e:
            db.rollback()
            logger.error(f"Failed to save session to database: {e}")
            raise
        finally:
            db.close()
