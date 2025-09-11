#!/usr/bin/env python3
"""
Client script to interact with the F1 Data Ingestion API.
"""

import requests
import json
import time
import sys
from typing import List, Optional

API_BASE_URL = "http://localhost:8000"


class F1IngestionClient:
    """Client for interacting with the F1 Data Ingestion API."""

    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url

    def start_full_ingestion(self, years: Optional[List[int]] = None, sessions: Optional[List[str]] = None):
        """Start ingestion for all years (2014-2025) or specified years."""
        if years is None:
            years = list(range(2014, 2026))

        if sessions is None:
            sessions = ["R", "Q", "FP1", "FP2", "FP3"]

        print(
            f"🚀 Starting ingestion for years {years} with sessions {sessions}")

        response = requests.post(
            f"{self.base_url}/ingest/races",
            json={"years": years, "sessions": sessions}
        )

        if response.status_code == 200:
            result = response.json()
            print(f"✅ Ingestion started with task ID: {result['task_id']}")
            return result['task_id']
        else:
            print(f"❌ Failed to start ingestion: {response.text}")
            return None

    def start_year_ingestion(self, year: int, sessions: Optional[List[str]] = None):
        """Start ingestion for a specific year."""
        if sessions is None:
            sessions = ["R", "Q", "FP1", "FP2", "FP3"]

        print(f"🚀 Starting ingestion for year {year} with sessions {sessions}")

        response = requests.post(
            f"{self.base_url}/ingest/year/{year}",
            json={"sessions": sessions}
        )

        if response.status_code == 200:
            result = response.json()
            print(f"✅ Ingestion started with task ID: {result['task_id']}")
            return result['task_id']
        else:
            print(f"❌ Failed to start ingestion: {response.text}")
            return None

    def get_task_status(self, task_id: str):
        """Get the status of an ingestion task."""
        response = requests.get(f"{self.base_url}/status/{task_id}")

        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Failed to get task status: {response.text}")
            return None

    def wait_for_completion(self, task_id: str, check_interval: int = 30):
        """Wait for a task to complete and show progress."""
        print(f"⏳ Waiting for task {task_id} to complete...")

        while True:
            status = self.get_task_status(task_id)
            if not status:
                break

            print(f"📊 Status: {status['status']} | "
                  f"Progress: {status['processed_items']}/{status['total_items']} "
                  f"({status['progress_percentage']:.1f}%) | "
                  f"Failed: {status['failed_items']}")

            if status['status'] in ['completed', 'failed']:
                if status['status'] == 'completed':
                    print("✅ Task completed successfully!")
                else:
                    print(
                        f"❌ Task failed: {status.get('error_message', 'Unknown error')}")
                break

            time.sleep(check_interval)

    def get_ingestion_stats(self):
        """Get statistics about ingested data."""
        response = requests.get(f"{self.base_url}/stats")

        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Failed to get stats: {response.text}")
            return None

    def get_races(self, year: Optional[int] = None, limit: int = 100):
        """Get list of ingested races."""
        params = {"limit": limit}
        if year:
            params["year"] = year

        response = requests.get(f"{self.base_url}/races", params=params)

        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Failed to get races: {response.text}")
            return None


def main():
    """Main function for command-line usage."""
    client = F1IngestionClient()

    if len(sys.argv) < 2:
        print("Usage:")
        print("  python ingest_client.py full [years] [sessions]")
        print("  python ingest_client.py year <year> [sessions]")
        print("  python ingest_client.py status <task_id>")
        print("  python ingest_client.py stats")
        print("  python ingest_client.py races [year]")
        print()
        print("Examples:")
        print("  python ingest_client.py full")
        print("  python ingest_client.py full 2023,2024 R,Q")
        print("  python ingest_client.py year 2024")
        print("  python ingest_client.py status task_123")
        return

    command = sys.argv[1]

    if command == "full":
        years = None
        sessions = None

        if len(sys.argv) > 2:
            years = [int(y) for y in sys.argv[2].split(',')]
        if len(sys.argv) > 3:
            sessions = sys.argv[3].split(',')

        task_id = client.start_full_ingestion(years, sessions)
        if task_id:
            client.wait_for_completion(task_id)

    elif command == "year":
        if len(sys.argv) < 3:
            print("❌ Please specify a year")
            return

        year = int(sys.argv[2])
        sessions = None

        if len(sys.argv) > 3:
            sessions = sys.argv[3].split(',')

        task_id = client.start_year_ingestion(year, sessions)
        if task_id:
            client.wait_for_completion(task_id)

    elif command == "status":
        if len(sys.argv) < 3:
            print("❌ Please specify a task ID")
            return

        task_id = sys.argv[2]
        status = client.get_task_status(task_id)
        if status:
            print(json.dumps(status, indent=2))

    elif command == "stats":
        stats = client.get_ingestion_stats()
        if stats:
            print("📊 Ingestion Statistics:")
            print(f"  Total Sessions: {stats['total_sessions']}")
            print(f"  Years Covered: {stats['years_covered']}")
            print(f"  Unique Grand Prix: {stats['unique_grand_prix']}")
            print(
                f"  Year Range: {stats['earliest_year']}-{stats['latest_year']}")
            print()
            print("Sessions by Year:")
            for year_stat in stats['sessions_by_year']:
                print(f"  {year_stat['year']}: {year_stat['count']} sessions")
            print()
            print("Sessions by Type:")
            for session_stat in stats['sessions_by_type']:
                print(
                    f"  {session_stat['session']}: {session_stat['count']} sessions")

    elif command == "races":
        year = None
        if len(sys.argv) > 2:
            year = int(sys.argv[2])

        races = client.get_races(year)
        if races:
            print(f"📋 Ingested Races ({len(races)} total):")
            for race in races[:20]:  # Show first 20
                print(f"  {race['year']} {race['grand_prix']} {race['session']} "
                      f"({race['race_laps']} laps)")
            if len(races) > 20:
                print(f"  ... and {len(races) - 20} more")

    else:
        print(f"❌ Unknown command: {command}")


if __name__ == "__main__":
    main()
