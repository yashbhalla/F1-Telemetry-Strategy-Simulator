import streamlit as st
from telemetry.ingest import load_session, driver_laps
from sim.optimiser import brute_force_best
from sim.tyres import TyreModel

st.title("F1 Telemetry & Strategy Lab")

year = st.selectbox("Year", [2022, 2023, 2024])
gp = st.text_input("Grand Prix", "Monaco")
ses = st.selectbox("Session", ["R", "Q", "FP1"])

if st.button("Load"):
    session = load_session(year, gp, ses)
    st.success(f"Loaded {gp} {year} {ses}")

    # quick demo model (replace with fitted params)
    tm = TyreModel({
        "SOFT": {"base": 75.0, "k": 0.10, "cliff_at": 18, "cliff_penalty": 0.30},
        "MED": {"base": 75.7, "k": 0.07, "cliff_at": 24, "cliff_penalty": 0.20},
        "HARD": {"base": 76.3, "k": 0.05, "cliff_at": 999, "cliff_penalty": 0.0},
    })
    best = brute_force_best(session.total_laps, "SOFT", ["MED", "HARD"], tm)
    st.write("Best (toy model):", best)
