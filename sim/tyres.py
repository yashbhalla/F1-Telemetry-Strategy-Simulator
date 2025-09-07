import numpy as np

COMPOUNDS = {"SOFT": 0, "MED": 1, "HARD": 2}


class TyreModel:
    def __init__(self, params):
        self.params = params

    def lap_time(self, compound, tyre_life, fuel_mass):
        p = self.params[compound]
        lt = p["base"] + p["k"]*tyre_life - 0.04*fuel_mass
        if tyre_life > p.get("cliff_at", 10**9):
            lt += p.get("cliff_penalty", 0.0) * (tyre_life - p["cliff_at"] + 1)
        return lt
