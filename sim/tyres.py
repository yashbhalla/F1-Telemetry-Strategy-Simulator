# sim_tyres.py
import numpy as np


class TyreModel:
    def __init__(self, params):
        self.params = params

    def lap_time(self, compound, tyre_life, track_temp=25.0, fuel_load=0.0):
        p = self.params[compound]

        # Base degradation (linear)
        base_time = p["base"] + p["k"] * tyre_life

        # Cliff effect - sudden performance drop
        if "cliff_at" in p and "cliff_penalty" in p:
            if tyre_life > p["cliff_at"]:
                cliff_factor = min(
                    (tyre_life - p["cliff_at"]) / 5.0, 2.0)  # Gradual cliff
                base_time += p["cliff_penalty"] * cliff_factor

        # Temperature effects
        temp_effect = self._temperature_effect(compound, track_temp)
        base_time += temp_effect

        # Fuel load effect (lighter = faster)
        fuel_effect = fuel_load * 0.1  # 0.1s per lap when full tank
        base_time += fuel_effect

        return base_time

    def _temperature_effect(self, compound, track_temp):
        # Optimal temperature ranges for each compound
        optimal_temps = {
            "SOFT": 30.0,
            "MED": 25.0,
            "HARD": 20.0,
            "INTER": 22.0,
            "WET": 18.0
        }

        optimal = optimal_temps.get(compound, 25.0)
        temp_diff = track_temp - optimal

        # Temperature sensitivity (seconds per degree)
        sensitivity = {
            "SOFT": 0.02,
            "MED": 0.015,
            "HARD": 0.01,
            "INTER": 0.008,
            "WET": 0.005
        }

        sens = sensitivity.get(compound, 0.015)
        return sens * temp_diff

    def get_optimal_life(self, compound):
        p = self.params[compound]
        return p.get("cliff_at", 20)

    def get_max_life(self, compound):
        p = self.params[compound]
        return p.get("max_life", 30)

    def is_tire_dead(self, compound, tyre_life):
        return tyre_life > self.get_max_life(compound)


def get_default_tire_params():
    return {
        "SOFT": {
            "base": 75.0,
            "k": 0.10,
            "cliff_at": 18,
            "cliff_penalty": 0.30,
            "max_life": 25
        },
        "MED": {
            "base": 75.7,
            "k": 0.07,
            "cliff_at": 24,
            "cliff_penalty": 0.20,
            "max_life": 35
        },
        "HARD": {
            "base": 76.3,
            "k": 0.05,
            "cliff_at": 999,
            "cliff_penalty": 0.0,
            "max_life": 50
        },
        "INTER": {
            "base": 78.5,
            "k": 0.08,
            "cliff_at": 30,
            "cliff_penalty": 0.25,
            "max_life": 40
        },
        "WET": {
            "base": 81.0,
            "k": 0.10,
            "cliff_at": 25,
            "cliff_penalty": 0.40,
            "max_life": 35
        }
    }
