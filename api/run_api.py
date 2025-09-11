#!/usr/bin/env python3
"""
Script to run the F1 Data Ingestion API.
"""

import uvicorn
import sys
from pathlib import Path

# Add project root to path
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

if __name__ == "__main__":
    print("🚀 Starting F1 Data Ingestion API...")
    print("📊 API Documentation: http://localhost:8000/docs")
    print("🔧 Interactive API: http://localhost:8000/redoc")
    print("📋 API Root: http://localhost:8000/")
    print()

    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
