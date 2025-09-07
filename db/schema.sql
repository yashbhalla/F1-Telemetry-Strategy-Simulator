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