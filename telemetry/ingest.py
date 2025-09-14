import fastf1
from fastf1 import plotting
import pandas as pd

fastf1.Cache.enable_cache("data/cache")  # creates local cache


def load_session(year, gp, session):
    ses = fastf1.get_session(year, gp, session)
    ses.load(telemetry=True, laps=True, weather=True)
    return ses


def driver_laps(session, driver_code):
    laps = session.laps.pick_driver(driver_code).copy()
    laps = laps[laps['LapTime'].notna()]
    laps['LapTimeSec'] = laps['LapTime'].dt.total_seconds()
    return laps[['LapNumber', 'LapTime', 'LapTimeSec', 'Compound', 'TyreLife', 'Stint']]
