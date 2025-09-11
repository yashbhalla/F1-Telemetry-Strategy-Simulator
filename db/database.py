import os
import json
from typing import Dict, List, Optional
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
import pandas as pd


class DatabaseManager:
    """Manage database operations for F1 strategy simulator."""

    def __init__(self, database_url: str = None):
        """
        Initialize database connection.

        Args:
            database_url: PostgreSQL connection string
        """
        if database_url is None:
            # Default to environment variable or local PostgreSQL
            database_url = os.getenv(
                'DATABASE_URL',
                'postgresql://postgres:password@localhost:5432/f1_strategy'
            )

        self.engine = create_engine(database_url)
        self.SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine)

    def create_tables(self):
        """Create database tables from schema."""
        try:
            with open('db/schema.sql', 'r') as f:
                schema_sql = f.read()

            with self.engine.connect() as conn:
                conn.execute(text(schema_sql))
                conn.commit()

            print("Database tables created successfully")
        except SQLAlchemyError as e:
            print(f"Error creating tables: {e}")

    def save_session(self, year: int, grand_prix: str, session_code: str,
                     race_laps: int) -> int:
        """
        Save session information to database.

        Returns:
            Session ID
        """
        try:
            with self.SessionLocal() as session:
                result = session.execute(text("""
                    INSERT INTO sessions (year, grand_prix, session_code, race_laps)
                    VALUES (:year, :grand_prix, :session_code, :race_laps)
                    RETURNING id
                """), {
                    'year': year,
                    'grand_prix': grand_prix,
                    'session_code': session_code,
                    'race_laps': race_laps
                })

                session_id = result.fetchone()[0]
                session.commit()
                return session_id

        except SQLAlchemyError as e:
            print(f"Error saving session: {e}")
            return None

    def save_stints(self, session_id: int, stints: List[Dict]):
        """Save stint information to database."""
        try:
            with self.SessionLocal() as session:
                for stint in stints:
                    session.execute(text("""
                        INSERT INTO stints (session_id, driver, stint, compound, laps, 
                                          avg_laptime_s, start_lap, end_lap)
                        VALUES (:session_id, :driver, :stint, :compound, :laps,
                                :avg_laptime_s, :start_lap, :end_lap)
                    """), {
                        'session_id': session_id,
                        'driver': stint.get('driver', 'UNKNOWN'),
                        'stint': stint.get('stint', 1),
                        'compound': stint['compound'],
                        'laps': stint['laps'],
                        'avg_laptime_s': stint['avg_lap_time'],
                        'start_lap': stint['start_lap'],
                        'end_lap': stint['end_lap']
                    })

                session.commit()

        except SQLAlchemyError as e:
            print(f"Error saving stints: {e}")

    def save_tire_params(self, track: str, compound: str, params: Dict,
                         fitted_from_session: int = None):
        """Save tire parameters to database."""
        try:
            with self.SessionLocal() as session:
                session.execute(text("""
                    INSERT INTO tyre_params (track, compound, base, k, cliff_at, 
                                           cliff_penalty, fitted_from_session)
                    VALUES (:track, :compound, :base, :k, :cliff_at, 
                            :cliff_penalty, :fitted_from_session)
                """), {
                    'track': track,
                    'compound': compound,
                    'base': params['base'],
                    'k': params['k'],
                    'cliff_at': params.get('cliff_at', 999),
                    'cliff_penalty': params.get('cliff_penalty', 0.0),
                    'fitted_from_session': fitted_from_session
                })

                session.commit()

        except SQLAlchemyError as e:
            print(f"Error saving tire params: {e}")

    def save_strategy(self, session_id: int, start_compound: str, plan: List,
                      total_time: float, sim_config: Dict):
        """Save strategy simulation results to database."""
        try:
            with self.SessionLocal() as session:
                session.execute(text("""
                    INSERT INTO strategies (session_id, start_compound, plan, 
                                          total_time_s, sim_config)
                    VALUES (:session_id, :start_compound, :plan, :total_time_s, :sim_config)
                """), {
                    'session_id': session_id,
                    'start_compound': start_compound,
                    'plan': json.dumps(plan),
                    'total_time_s': total_time,
                    'sim_config': json.dumps(sim_config)
                })

                session.commit()

        except SQLAlchemyError as e:
            print(f"Error saving strategy: {e}")

    def get_session_strategies(self, session_id: int) -> pd.DataFrame:
        """Get all strategies for a session."""
        try:
            query = """
                SELECT s.*, se.year, se.grand_prix, se.session_code
                FROM strategies s
                JOIN sessions se ON s.session_id = se.id
                WHERE s.session_id = :session_id
                ORDER BY s.total_time_s
            """

            return pd.read_sql(query, self.engine, params={'session_id': session_id})

        except SQLAlchemyError as e:
            print(f"Error getting strategies: {e}")
            return pd.DataFrame()

    def get_tire_params(self, track: str = None) -> pd.DataFrame:
        """Get tire parameters for a track or all tracks."""
        try:
            if track:
                query = """
                    SELECT * FROM tyre_params 
                    WHERE track = :track
                    ORDER BY compound
                """
                return pd.read_sql(query, self.engine, params={'track': track})
            else:
                query = "SELECT * FROM tyre_params ORDER BY track, compound"
                return pd.read_sql(query, self.engine)

        except SQLAlchemyError as e:
            print(f"Error getting tire params: {e}")
            return pd.DataFrame()

    def get_best_strategies(self, limit: int = 10) -> pd.DataFrame:
        """Get best strategies across all sessions."""
        try:
            query = """
                SELECT s.*, se.year, se.grand_prix, se.session_code
                FROM strategies s
                JOIN sessions se ON s.session_id = se.id
                ORDER BY s.total_time_s
                LIMIT :limit
            """

            return pd.read_sql(query, self.engine, params={'limit': limit})

        except SQLAlchemyError as e:
            print(f"Error getting best strategies: {e}")
            return pd.DataFrame()

    def close(self):
        """Close database connection."""
        self.engine.dispose()


def get_database_manager() -> DatabaseManager:
    """Get database manager instance."""
    return DatabaseManager()
