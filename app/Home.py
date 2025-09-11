from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import streamlit as st
from telemetry.ingest import load_session, driver_laps
from sim.optimiser import brute_force_best
from sim.tyres import TyreModel, get_default_tire_params
from sim.weather import WeatherModel, get_default_weather_conditions
from sim.sc_models import SafetyCarModel
from sim.strategy import simulate_plan
from db.database import get_database_manager
import sys
from pathlib import Path

# --- Ensure project root is on sys.path ---
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# --- Now imports will work ---


# Page configuration
st.set_page_config(
    page_title="F1 Strategy Simulator",
    page_icon="🏎️",
    layout="wide"
)

st.title("F1 Telemetry & Strategy Lab")
st.markdown("---")

# Sidebar for configuration
st.sidebar.header("Race Configuration")

# Session selection
col1, col2, col3 = st.sidebar.columns(3)
with col1:
    year = st.selectbox("Year", [2022, 2023, 2024])
with col2:
    gp = st.text_input("Grand Prix", "Monaco")
with col3:
    ses = st.selectbox("Session", ["R", "Q", "FP1"])

# Weather configuration
st.sidebar.subheader("Weather Conditions")
weather_model = WeatherModel()
weather_conditions = get_default_weather_conditions()

weather_conditions["air_temp"] = st.sidebar.slider(
    "Air Temperature (°C)", 15, 40, 25
)
weather_conditions["humidity"] = st.sidebar.slider(
    "Humidity (%)", 20, 90, 60
)
weather_conditions["precipitation"] = st.sidebar.slider(
    "Precipitation (mm/h)", 0.0, 2.0, 0.0
)
weather_conditions["cloud_cover"] = st.sidebar.slider(
    "Cloud Cover (%)", 0, 100, 30
)

# Safety car configuration
st.sidebar.subheader("Safety Car")
sc_model = SafetyCarModel()
enable_sc = st.sidebar.checkbox("Enable Safety Car Simulation", True)

# Main content
if st.button("Load Session & Optimize Strategy", type="primary"):
    with st.spinner("Loading session data..."):
        try:
            session = load_session(year, gp, ses)
            st.success(
                f"Loaded {gp} {year} {ses} - {session.total_laps} laps")

            # Get tire parameters
            tire_params = get_default_tire_params()
            tm = TyreModel(tire_params)

            # Generate weather forecast
            weather_forecast = weather_model.simulate_weather_forecast(
                session.total_laps, weather_conditions
            )

            # Generate safety car events
            sc_events = []
            if enable_sc:
                sc_events = sc_model.generate_safety_car_events(
                    session.total_laps, weather_forecast
                )

            # Strategy optimization
            with st.spinner("Optimizing strategy..."):
                best_time, best_plan = brute_force_best(
                    session.total_laps, "SOFT", ["MED", "HARD"], tm
                )

            # Display results
            st.header("Strategy Analysis")

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Best Strategy Time",
                          f"{best_time:.1f}s", "Optimized")
            with col2:
                st.metric("Race Laps", session.total_laps)
            with col3:
                st.metric("Pit Stops", len(best_plan))

            # Strategy details
            st.subheader("Optimal Strategy")
            if best_plan:
                strategy_text = f"Start: SOFT"
                for i, (lap, compound) in enumerate(best_plan):
                    strategy_text += f" → Pit Lap {lap}: {compound}"
                st.write(strategy_text)

                # Detailed simulation
                total_time, stints = simulate_plan(
                    session.total_laps, "SOFT", best_plan, tm
                )

                # Create stint visualization
                stint_data = []
                for stint in stints:
                    stint_data.append({
                        'Stint': f"Stint {len(stint_data) + 1}",
                        'Compound': stint['compound'],
                        'Laps': stint['laps'],
                        'Start Lap': stint['start_lap'],
                        'End Lap': stint['end_lap'],
                        'Avg Lap Time': f"{stint['avg_lap_time']:.2f}s",
                        'Total Time': f"{stint['total_time']:.1f}s"
                    })

                stint_df = pd.DataFrame(stint_data)
                st.dataframe(stint_df, use_container_width=True)

                # Tire degradation chart
                st.subheader("Tire Degradation Analysis")

                # Create degradation curves for each compound
                compounds = ["SOFT", "MED", "HARD"]
                fig = go.Figure()

                for compound in compounds:
                    lap_times = []
                    for lap in range(1, 31):  # Show first 30 laps
                        lap_time = tm.lap_time(compound, lap)
                        lap_times.append(lap_time)

                    fig.add_trace(go.Scatter(
                        x=list(range(1, 31)),
                        y=lap_times,
                        mode='lines+markers',
                        name=compound,
                        line=dict(width=3)
                    ))

                fig.update_layout(
                    title="Tire Degradation Curves",
                    xaxis_title="Tire Life (laps)",
                    yaxis_title="Lap Time (seconds)",
                    hovermode='x unified'
                )

                st.plotly_chart(fig, use_container_width=True)

                # Weather forecast
                if weather_forecast:
                    st.subheader("Weather Forecast")

                    weather_df = pd.DataFrame(weather_forecast)

                    fig_weather = make_subplots(
                        rows=2, cols=2,
                        subplot_titles=('Track Temperature', 'Precipitation',
                                        'Humidity', 'Rain Intensity'),
                        specs=[[{"secondary_y": False}, {"secondary_y": False}],
                               [{"secondary_y": False}, {"secondary_y": False}]]
                    )

                    # Track temperature
                    fig_weather.add_trace(
                        go.Scatter(x=weather_df['lap'], y=weather_df['track_temp'],
                                   mode='lines', name='Track Temp', line=dict(color='red')),
                        row=1, col=1
                    )

                    # Precipitation
                    fig_weather.add_trace(
                        go.Scatter(x=weather_df['lap'], y=weather_df['precipitation'],
                                   mode='lines', name='Precipitation', line=dict(color='blue')),
                        row=1, col=2
                    )

                    # Humidity
                    fig_weather.add_trace(
                        go.Scatter(x=weather_df['lap'], y=weather_df['humidity'],
                                   mode='lines', name='Humidity', line=dict(color='green')),
                        row=2, col=1
                    )

                    # Rain intensity (categorical)
                    rain_colors = {'DRY': 'yellow', 'LIGHT_RAIN': 'lightblue',
                                   'MODERATE_RAIN': 'blue', 'HEAVY_RAIN': 'darkblue'}
                    for intensity in weather_df['rain_intensity'].unique():
                        mask = weather_df['rain_intensity'] == intensity
                        fig_weather.add_trace(
                            go.Scatter(x=weather_df[mask]['lap'],
                                       y=[intensity] * mask.sum(),
                                       mode='markers', name=intensity,
                                       marker=dict(color=rain_colors.get(intensity, 'gray'))),
                            row=2, col=2
                        )

                    fig_weather.update_layout(height=600, showlegend=True)
                    st.plotly_chart(fig_weather, use_container_width=True)

                # Safety car events
                if sc_events:
                    st.subheader("Safety Car Events")
                    for event in sc_events:
                        st.info(f"Safety Car: Laps {event['start_lap']}-{event['end_lap']} "
                                f"({event['duration']} laps)")

                # Strategy comparison
                st.subheader("Strategy Comparison")

                # Test different strategies
                strategies = [
                    ("1-Stop SOFT→HARD", [(25, "HARD")]),
                    ("2-Stop SOFT→MED→HARD", [(18, "MED"), (50, "HARD")]),
                    ("Optimal Strategy", best_plan)
                ]

                comparison_data = []
                for name, plan in strategies:
                    time, _ = simulate_plan(
                        session.total_laps, "SOFT", plan, tm)
                    comparison_data.append({
                        'Strategy': name,
                        'Total Time (s)': time,
                        'Pit Stops': len(plan),
                        'Time vs Optimal': time - best_time
                    })

                comparison_df = pd.DataFrame(comparison_data)
                st.dataframe(comparison_df, use_container_width=True)

                # Bar chart comparison
                fig_comparison = px.bar(
                    comparison_df,
                    x='Strategy',
                    y='Total Time (s)',
                    title='Strategy Time Comparison',
                    color='Total Time (s)',
                    color_continuous_scale='RdYlGn_r'
                )
                st.plotly_chart(fig_comparison, use_container_width=True)

        except Exception as e:
            st.error(f"Error loading session: {str(e)}")
            st.exception(e)

# Database integration section
st.sidebar.markdown("---")
st.sidebar.subheader("Database")
if st.sidebar.button("View Saved Strategies"):
    try:
        db = get_database_manager()
        strategies = db.get_best_strategies(10)
        if not strategies.empty:
            st.subheader("Best Saved Strategies")
            st.dataframe(strategies[['year', 'grand_prix', 'start_compound',
                                     'total_time_s', 'created_at']],
                         use_container_width=True)
        else:
            st.info("No saved strategies found. Run some simulations to save data!")
    except Exception as e:
        st.error(f"Database error: {str(e)}")
