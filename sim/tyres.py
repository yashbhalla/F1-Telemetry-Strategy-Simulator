# sim_tyres.py
import numpy as np


class TyreModel:
    def __init__(self, params):
        """
        Enhanced tire model with realistic degradation curves.

        params example:
        {
          "SOFT": {
            "base": 75.0,           # Base lap time in seconds
            "k": 0.08,              # Linear degradation rate
            "cliff_at": 18,         # Lap when cliff effect starts
            "cliff_penalty": 0.30,  # Additional time penalty after cliff
            "max_life": 25          # Maximum useful tire life
          },
          "MED": {"base": 75.7, "k": 0.05, "cliff_at": 24, "cliff_penalty": 0.20, "max_life": 35},
          "HARD": {"base": 76.3, "k": 0.03, "cliff_at": 999, "cliff_penalty": 0.0, "max_life": 50}
        }
        """
        self.params = params

    def lap_time(self, compound, tyre_life, track_temp=25.0, fuel_load=0.0):
        """
        Calculate lap time based on tire compound, life, and conditions.

        Args:
            compound (str): Tire compound ("SOFT", "MED", "HARD")
            tyre_life (int): Number of laps on current tires
            track_temp (float): Track temperature in Celsius
            fuel_load (float): Fuel load effect (0.0 = full tank, 1.0 = empty)
        """
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
        """Calculate temperature effect on tire performance."""
        # Optimal temperature ranges for each compound
        optimal_temps = {
            "SOFT": 30.0,
            "MED": 25.0,
            "HARD": 20.0
        }

        optimal = optimal_temps.get(compound, 25.0)
        temp_diff = track_temp - optimal

        # Temperature sensitivity (seconds per degree)
        sensitivity = {
            "SOFT": 0.02,  # Most sensitive
            "MED": 0.015,
            "HARD": 0.01   # Least sensitive
        }

        sens = sensitivity.get(compound, 0.015)
        return sens * temp_diff

    def get_optimal_life(self, compound):
        """Get optimal tire life before significant degradation."""
        p = self.params[compound]
        return p.get("cliff_at", 20)

    def get_max_life(self, compound):
        """Get maximum useful tire life."""
        p = self.params[compound]
        return p.get("max_life", 30)

    def is_tire_dead(self, compound, tyre_life):
        """Check if tire is beyond useful life."""
        return tyre_life > self.get_max_life(compound)


def get_default_tire_params():
    """Get realistic default tire parameters for F1 2024."""
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
        }
    }
