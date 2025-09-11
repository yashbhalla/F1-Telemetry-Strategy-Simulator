CREATE TABLE
    sessions (
        id SERIAL PRIMARY KEY,
        year INT,
        grand_prix TEXT,
        session_code TEXT,
        race_laps INT,
        created_at TIMESTAMPTZ DEFAULT now ()
    );

CREATE TABLE
    stints (
        id SERIAL PRIMARY KEY,
        session_id INT REFERENCES sessions (id),
        driver TEXT,
        stint INT,
        compound TEXT,
        laps INT,
        avg_laptime_s REAL,
        start_lap INT,
        end_lap INT
    );

CREATE TABLE
    tyre_params (
        id SERIAL PRIMARY KEY,
        track TEXT,
        compound TEXT,
        base REAL,
        k REAL,
        cliff_at INT,
        cliff_penalty REAL,
        fitted_from_session INT REFERENCES sessions (id)
    );

CREATE TABLE
    strategies (
        id SERIAL PRIMARY KEY,
        session_id INT REFERENCES sessions (id),
        start_compound TEXT,
        plan JSONB,
        total_time_s REAL,
        sim_config JSONB,
        created_at TIMESTAMPTZ DEFAULT now ()
    );

-- Enhanced sessions table with additional metadata
ALTER TABLE sessions
ADD COLUMN IF NOT EXISTS track_name TEXT;

ALTER TABLE sessions
ADD COLUMN IF NOT EXISTS country TEXT;

ALTER TABLE sessions
ADD COLUMN IF NOT EXISTS circuit_length REAL;

ALTER TABLE sessions
ADD COLUMN IF NOT EXISTS weather_conditions JSONB;

ALTER TABLE sessions
ADD COLUMN IF NOT EXISTS total_drivers INT;

ALTER TABLE sessions
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ DEFAULT now ();

-- Ingestion tasks tracking
CREATE TABLE
    IF NOT EXISTS ingestion_tasks (
        id SERIAL PRIMARY KEY,
        task_id TEXT UNIQUE NOT NULL,
        status TEXT DEFAULT 'pending',
        started_at TIMESTAMPTZ DEFAULT now (),
        completed_at TIMESTAMPTZ,
        total_items INT DEFAULT 0,
        processed_items INT DEFAULT 0,
        failed_items INT DEFAULT 0,
        error_message TEXT,
        task_config JSONB
    );

-- Driver information
CREATE TABLE
    IF NOT EXISTS drivers (
        id SERIAL PRIMARY KEY,
        session_id INT REFERENCES sessions (id),
        driver_number TEXT NOT NULL,
        driver_code TEXT NOT NULL,
        driver_name TEXT NOT NULL,
        team TEXT,
        position INT,
        points REAL,
        fastest_lap REAL,
        created_at TIMESTAMPTZ DEFAULT now ()
    );

-- Lap-by-lap data
CREATE TABLE
    IF NOT EXISTS lap_data (
        id SERIAL PRIMARY KEY,
        session_id INT REFERENCES sessions (id),
        driver_id INT REFERENCES drivers (id),
        lap_number INT NOT NULL,
        lap_time REAL,
        sector_1_time REAL,
        sector_2_time REAL,
        sector_3_time REAL,
        compound TEXT,
        tyre_life INT,
        stint INT,
        position INT,
        gap_to_leader REAL,
        created_at TIMESTAMPTZ DEFAULT now ()
    );

-- Weather data
CREATE TABLE
    IF NOT EXISTS weather_data (
        id SERIAL PRIMARY KEY,
        session_id INT REFERENCES sessions (id),
        lap_number INT NOT NULL,
        air_temp REAL,
        track_temp REAL,
        humidity REAL,
        pressure REAL,
        wind_speed REAL,
        wind_direction REAL,
        rainfall REAL,
        created_at TIMESTAMPTZ DEFAULT now ()
    );

-- Safety car events
CREATE TABLE
    IF NOT EXISTS safety_car_events (
        id SERIAL PRIMARY KEY,
        session_id INT REFERENCES sessions (id),
        start_lap INT NOT NULL,
        end_lap INT NOT NULL,
        duration_laps INT,
        event_type TEXT,
        reason TEXT,
        created_at TIMESTAMPTZ DEFAULT now ()
    );

-- Indexes for better performance
CREATE INDEX IF NOT EXISTS idx_sessions_year ON sessions (year);

CREATE INDEX IF NOT EXISTS idx_sessions_gp ON sessions (grand_prix);

CREATE INDEX IF NOT EXISTS idx_sessions_session ON sessions (session_code);

CREATE INDEX IF NOT EXISTS idx_drivers_session ON drivers (session_id);

CREATE INDEX IF NOT EXISTS idx_drivers_code ON drivers (driver_code);

CREATE INDEX IF NOT EXISTS idx_lap_data_session ON lap_data (session_id);

CREATE INDEX IF NOT EXISTS idx_lap_data_driver ON lap_data (driver_id);

CREATE INDEX IF NOT EXISTS idx_lap_data_lap ON lap_data (lap_number);

CREATE INDEX IF NOT EXISTS idx_weather_session ON weather_data (session_id);

CREATE INDEX IF NOT EXISTS idx_weather_lap ON weather_data (lap_number);

CREATE INDEX IF NOT EXISTS idx_sc_events_session ON safety_car_events (session_id);

CREATE INDEX IF NOT EXISTS idx_ingestion_tasks_status ON ingestion_tasks (status);