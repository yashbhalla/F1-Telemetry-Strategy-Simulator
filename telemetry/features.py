import pandas as pd

def stint_summary(laps: pd.DataFrame):
    g = laps.groupby('Stint')
    return g.agg(
        compound=('Compound','first'),
        laps=('LapNumber','count'),
        avg_laptime_s=('LapTimeSec','mean'),
        tyre_life_end=('TyreLife','max')
    ).reset_index()
