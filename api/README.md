# 🏎️ F1 Data Ingestion API

A FastAPI-based service for ingesting F1 race data from 2014-2025 using FastF1.

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r api/requirements.txt
```

### 2. Start the API Server
```bash
python api/run_api.py
```

The API will be available at:
- **API Documentation**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **API Root**: http://localhost:8000/

### 3. Start Data Ingestion

#### Using the Client Script (Recommended)
```bash
# Ingest all years (2014-2025)
python api/ingest_client.py full

# Ingest specific years
python api/ingest_client.py full 2023,2024

# Ingest specific year
python api/ingest_client.py year 2024

# Check status
python api/ingest_client.py status <task_id>

# View statistics
python api/ingest_client.py stats

# List ingested races
python api/ingest_client.py races
```

#### Using HTTP Requests
```bash
# Start full ingestion
curl -X POST "http://localhost:8000/ingest/races" \
     -H "Content-Type: application/json" \
     -d '{"years": [2023, 2024], "sessions": ["R", "Q", "FP1"]}'

# Check status
curl "http://localhost:8000/status/<task_id>"

# Get statistics
curl "http://localhost:8000/stats"
```

## 📊 API Endpoints

### Core Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API information and available endpoints |
| `/ingest/races` | POST | Start ingestion for multiple years |
| `/ingest/year/{year}` | POST | Start ingestion for specific year |
| `/ingest/specific` | POST | Ingest specific races |
| `/status/{task_id}` | GET | Get task status |
| `/status` | GET | Get all task statuses |
| `/races` | GET | List ingested races |
| `/stats` | GET | Get ingestion statistics |

### Query Parameters

#### `/races` endpoint:
- `year`: Filter by year
- `grand_prix`: Filter by Grand Prix name
- `session`: Filter by session type
- `limit`: Limit number of results (default: 100)

## 🗄️ Database Schema

The API creates and manages the following tables:

- **sessions**: Race session information
- **drivers**: Driver data for each session
- **lap_data**: Lap-by-lap timing data
- **weather_data**: Weather conditions per lap
- **safety_car_events**: Safety car periods
- **ingestion_tasks**: Task tracking and progress
- **strategies**: Strategy simulation results
- **tyre_params**: Tire model parameters

## 📈 Data Coverage

### Years: 2014-2025
### Sessions:
- **R**: Race
- **Q**: Qualifying
- **FP1**: Free Practice 1
- **FP2**: Free Practice 2
- **FP3**: Free Practice 3
- **SQ**: Sprint Qualifying (2021+)
- **S**: Sprint (2021+)

### Data Types:
- Session metadata (track, laps, drivers)
- Driver information (teams, positions, points)
- Lap-by-lap timing data
- Tire compound and life
- Weather conditions
- Safety car events
- Sector times

## 🔧 Configuration

### Environment Variables
- `DATABASE_URL`: PostgreSQL connection string
- `FASTF1_CACHE`: Cache directory for FastF1 data

### Default Settings
- **Cache Directory**: `data/cache/`
- **Database**: PostgreSQL on localhost:5432
- **Concurrent Downloads**: 5 (configurable)

## 📊 Monitoring

### Task Status
Tasks can have the following statuses:
- `pending`: Task queued
- `running`: Task in progress
- `completed`: Task finished successfully
- `failed`: Task failed with error

### Progress Tracking
Each task tracks:
- Total items to process
- Items processed
- Items failed
- Progress percentage
- Estimated completion time

## 🚨 Error Handling

The API includes comprehensive error handling:
- Database connection errors
- FastF1 API failures
- Invalid race/session combinations
- Network timeouts
- Data parsing errors

Failed sessions are logged but don't stop the overall ingestion process.

## 🔍 Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Ensure PostgreSQL is running
   - Check database credentials
   - Verify database exists

2. **FastF1 Cache Issues**
   - Clear cache: `rm -rf data/cache/*`
   - Check internet connection
   - Verify FastF1 API access

3. **Memory Issues**
   - Reduce concurrent downloads
   - Process smaller year ranges
   - Monitor system resources

### Logs
Check the console output for detailed logging information including:
- Ingestion progress
- Error messages
- Performance metrics

## 🎯 Usage Examples

### Ingest Recent Seasons
```bash
python api/ingest_client.py full 2022,2023,2024
```

### Ingest Only Races and Qualifying
```bash
python api/ingest_client.py full 2024 R,Q
```

### Monitor Progress
```bash
# Start ingestion
task_id=$(python api/ingest_client.py year 2024 | grep "task ID" | cut -d: -f2)

# Check status
python api/ingest_client.py status $task_id
```

## 🔗 Integration

The ingested data can be used with:
- **Streamlit App**: `streamlit run app/Home.py`
- **Strategy Simulator**: All simulation modules
- **Database Queries**: Direct PostgreSQL access
- **External Tools**: Via API endpoints

---

**Built with ❤️ for F1 data analysis**
