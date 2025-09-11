# 🏎️ F1 Telemetry Strategy Simulator

A comprehensive Formula 1 race strategy simulation and telemetry analysis tool that combines real F1 data with advanced mathematical modeling to optimize pit stop strategies.

## ✨ Features

### 🛞 **Advanced Tire Modeling**
- Realistic tire degradation curves with cliff effects
- Temperature and fuel load effects on performance
- Support for SOFT, MEDIUM, HARD, INTERMEDIATE, and WET compounds
- Configurable parameters for different tracks and conditions

### 🌤️ **Weather Integration**
- Dynamic weather simulation during races
- Track temperature calculation based on air temp, humidity, and cloud cover
- Rain intensity modeling affecting tire choice and performance
- Weather-based safety car probability adjustments

### 🚨 **Safety Car Effects**
- Realistic safety car event generation
- Pit stop time reduction under safety car conditions
- Field compression effects on lap times
- Strategic advantage calculations for SC pit stops

### 📊 **Strategy Optimization**
- Brute force optimization for 1-stop and 2-stop strategies
- Multiple tire compound combinations
- Detailed stint analysis and timing
- Strategy comparison and visualization

### 🎯 **Interactive Web Interface**
- Modern Streamlit-based dashboard
- Real-time strategy optimization
- Interactive charts and visualizations
- Weather and safety car configuration
- Database integration for saving results

### 🗄️ **Database Integration**
- PostgreSQL backend for storing strategies and results
- Session management and historical data
- Tire parameter storage and retrieval
- Performance analytics and comparisons

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL (for database features)
- Docker (optional, for containerized deployment)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/F1-Telemetry-Strategy-Simulator.git
cd F1-Telemetry-Strategy-Simulator
```

2. **Install dependencies**
```bash
pip install -r infra/requirements.txt
```

3. **Set up database (optional)**
```bash
# Using Docker
docker-compose -f infra/docker-compose.yml up -d db

# Or install PostgreSQL locally and create database
create db f1_strategy
```

4. **Run the application**
```bash
streamlit run app/Home.py
```

The application will be available at `http://localhost:8501`

### Docker Deployment

```bash
# Build and run with Docker Compose
cd infra
docker-compose up --build

# Access the application at http://localhost:8501
```

## 📁 Project Structure

```
F1-Telemetry-Strategy-Simulator/
├── app/                    # Streamlit web application
│   └── Home.py            # Main dashboard
├── sim/                   # Simulation engine
│   ├── tyres.py          # Tire degradation models
│   ├── strategy.py       # Strategy simulation
│   ├── optimiser.py      # Strategy optimization
│   ├── weather.py        # Weather modeling
│   └── sc_models.py      # Safety car modeling
├── telemetry/            # F1 data handling
│   ├── ingest.py         # Data loading
│   ├── features.py       # Feature extraction
│   └── plots.py          # Visualization utilities
├── db/                   # Database layer
│   ├── schema.sql        # Database schema
│   └── database.py       # Database operations
├── notebooks/            # Jupyter notebooks for analysis
├── infra/               # Infrastructure and deployment
│   ├── Dockerfile       # Container configuration
│   ├── docker-compose.yml
│   └── requirements.txt
└── data/                # Cached F1 data
```

## 🎮 Usage

### Basic Strategy Analysis

1. **Select Race Parameters**
   - Choose year, Grand Prix, and session type
   - Configure weather conditions
   - Enable/disable safety car simulation

2. **Run Optimization**
   - Click "Load Session & Optimize Strategy"
   - View optimal pit stop strategy
   - Analyze tire degradation curves

3. **Compare Strategies**
   - See multiple strategy options
   - Compare total race times
   - Analyze stint details

### Advanced Features

- **Weather Simulation**: Adjust temperature, humidity, and precipitation
- **Safety Car Events**: Enable realistic SC scenarios
- **Database Storage**: Save and retrieve strategy results
- **Historical Analysis**: Compare strategies across different races

## 🔧 Configuration

### Tire Parameters
Customize tire performance in `sim/tyres.py`:
```python
tire_params = {
    "SOFT": {
        "base": 75.0,           # Base lap time (seconds)
        "k": 0.10,              # Degradation rate
        "cliff_at": 18,         # Cliff effect start lap
        "cliff_penalty": 0.30,  # Cliff penalty (seconds)
        "max_life": 25          # Maximum useful life
    }
}
```

### Weather Conditions
Adjust weather parameters in the Streamlit sidebar or modify defaults in `sim/weather.py`.

### Safety Car Probability
Configure SC likelihood in `sim/sc_models.py`:
```python
self.base_sc_probability = 0.15  # 15% chance per race
self.lap_sc_probability = 0.002  # 0.2% chance per lap
```

## 📊 API Reference

### Core Classes

#### `TyreModel`
```python
tm = TyreModel(tire_params)
lap_time = tm.lap_time(compound, tyre_life, track_temp, fuel_load)
```

#### `WeatherModel`
```python
weather = WeatherModel()
forecast = weather.simulate_weather_forecast(race_laps, conditions)
```

#### `SafetyCarModel`
```python
sc = SafetyCarModel()
events = sc.generate_safety_car_events(race_laps, weather_forecast)
```

#### `simulate_plan`
```python
total_time, stints = simulate_plan(race_laps, start_compound, pit_plan, tyre_model)
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 🙏 Acknowledgments

- [FastF1](https://github.com/theOehrly/Fast-F1) for F1 data access
- [Streamlit](https://streamlit.io/) for the web interface
- [Plotly](https://plotly.com/) for interactive visualizations
- Formula 1 for the amazing sport and data

---

**Built with ❤️ for F1 by Yash Bhalla**
