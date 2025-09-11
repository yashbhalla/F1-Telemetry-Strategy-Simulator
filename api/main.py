from api.schemas import IngestionRequest, IngestionResponse, RaceInfo
from api.ingestion_service import RaceIngestionService
from api.models import RaceData, IngestionStatus
from db.database import DatabaseManager
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import asyncio
from typing import List, Dict, Optional
import sys
from pathlib import Path

# Add project root to path
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


app = FastAPI(
    title="F1 Data Ingestion API",
    description="API for ingesting F1 race data from 2014-2025",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup
DATABASE_URL = "postgresql://postgres:password@localhost:5432/f1_strategy"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Global ingestion service
ingestion_service = RaceIngestionService()


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    try:
        db_manager = DatabaseManager(DATABASE_URL)
        db_manager.create_tables()
        print("✅ Database initialized successfully")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "F1 Data Ingestion API",
        "version": "1.0.0",
        "endpoints": {
            "ingest_races": "/ingest/races",
            "ingest_year": "/ingest/year/{year}",
            "ingest_specific": "/ingest/specific",
            "status": "/status",
            "races": "/races"
        }
    }


@app.post("/ingest/races", response_model=IngestionResponse)
async def ingest_all_races(
    background_tasks: BackgroundTasks,
    years: Optional[List[int]] = None,
    sessions: Optional[List[str]] = None
):
    """
    Ingest F1 race data for specified years and sessions.

    Args:
        years: List of years to ingest (default: 2014-2025)
        sessions: List of sessions to ingest (default: ["R", "Q", "FP1", "FP2", "FP3"])
    """
    if years is None:
        years = list(range(2014, 2026))

    if sessions is None:
        sessions = ["R", "Q", "FP1", "FP2", "FP3"]

    # Start background ingestion
    task_id = f"ingest_{len(years)}_years"
    background_tasks.add_task(
        ingestion_service.ingest_multiple_years,
        years=years,
        sessions=sessions,
        task_id=task_id
    )

    return IngestionResponse(
        task_id=task_id,
        message=f"Started ingestion for {len(years)} years",
        years=years,
        sessions=sessions,
        status="started"
    )


@app.post("/ingest/year/{year}", response_model=IngestionResponse)
async def ingest_year(
    year: int,
    background_tasks: BackgroundTasks,
    sessions: Optional[List[str]] = None
):
    """
    Ingest F1 race data for a specific year.

    Args:
        year: Year to ingest (2014-2025)
        sessions: List of sessions to ingest
    """
    if year < 2014 or year > 2025:
        raise HTTPException(
            status_code=400, detail="Year must be between 2014 and 2025")

    if sessions is None:
        sessions = ["R", "Q", "FP1", "FP2", "FP3"]

    task_id = f"ingest_year_{year}"
    background_tasks.add_task(
        ingestion_service.ingest_year,
        year=year,
        sessions=sessions,
        task_id=task_id
    )

    return IngestionResponse(
        task_id=task_id,
        message=f"Started ingestion for year {year}",
        years=[year],
        sessions=sessions,
        status="started"
    )


@app.post("/ingest/specific", response_model=IngestionResponse)
async def ingest_specific_races(
    request: IngestionRequest,
    background_tasks: BackgroundTasks
):
    """
    Ingest specific races based on year, grand prix, and session.

    Args:
        request: IngestionRequest with specific race details
    """
    task_id = f"ingest_specific_{len(request.races)}"
    background_tasks.add_task(
        ingestion_service.ingest_specific_races,
        races=request.races,
        task_id=task_id
    )

    return IngestionResponse(
        task_id=task_id,
        message=f"Started ingestion for {len(request.races)} specific races",
        races=request.races,
        status="started"
    )


@app.get("/status/{task_id}")
async def get_ingestion_status(task_id: str):
    """Get the status of an ingestion task."""
    status = ingestion_service.get_task_status(task_id)
    if status is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return status


@app.get("/status")
async def get_all_status():
    """Get status of all ingestion tasks."""
    return ingestion_service.get_all_status()


@app.get("/races", response_model=List[RaceInfo])
async def get_ingested_races(
    year: Optional[int] = None,
    grand_prix: Optional[str] = None,
    session: Optional[str] = None,
    limit: int = 100
):
    """Get list of ingested races with optional filters."""
    db = SessionLocal()
    try:
        query = text("""
            SELECT DISTINCT year, grand_prix, session_code, race_laps, created_at
            FROM sessions
            WHERE 1=1
        """)

        params = {}
        if year:
            query += " AND year = :year"
            params["year"] = year
        if grand_prix:
            query += " AND grand_prix ILIKE :grand_prix"
            params["grand_prix"] = f"%{grand_prix}%"
        if session:
            query += " AND session_code = :session"
            params["session"] = session

        query += " ORDER BY year DESC, grand_prix, session_code LIMIT :limit"
        params["limit"] = limit

        result = db.execute(query, params)
        races = []

        for row in result:
            races.append(RaceInfo(
                year=row.year,
                grand_prix=row.grand_prix,
                session=row.session_code,
                race_laps=row.race_laps,
                created_at=row.created_at
            ))

        return races

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@app.get("/stats")
async def get_ingestion_stats():
    """Get statistics about ingested data."""
    db = SessionLocal()
    try:
        # Get basic stats
        stats_query = text("""
            SELECT 
                COUNT(*) as total_sessions,
                COUNT(DISTINCT year) as years_covered,
                COUNT(DISTINCT grand_prix) as unique_gps,
                MIN(year) as earliest_year,
                MAX(year) as latest_year
            FROM sessions
        """)

        stats_result = db.execute(stats_query).fetchone()

        # Get sessions by year
        year_stats_query = text("""
            SELECT year, COUNT(*) as session_count
            FROM sessions
            GROUP BY year
            ORDER BY year
        """)

        year_stats = db.execute(year_stats_query).fetchall()

        # Get sessions by type
        session_stats_query = text("""
            SELECT session_code, COUNT(*) as count
            FROM sessions
            GROUP BY session_code
            ORDER BY count DESC
        """)

        session_stats = db.execute(session_stats_query).fetchall()

        return {
            "total_sessions": stats_result.total_sessions,
            "years_covered": stats_result.years_covered,
            "unique_grand_prix": stats_result.unique_gps,
            "earliest_year": stats_result.earliest_year,
            "latest_year": stats_result.latest_year,
            "sessions_by_year": [{"year": row.year, "count": row.session_count} for row in year_stats],
            "sessions_by_type": [{"session": row.session_code, "count": row.count} for row in session_stats]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
