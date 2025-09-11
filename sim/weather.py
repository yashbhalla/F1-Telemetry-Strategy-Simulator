import numpy as np
from typing import Dict, List, Tuple


class WeatherModel:
    """Model weather effects on F1 race strategy."""

    def __init__(self):
        self.rain_intensity_levels = {
            "DRY": 0.0,
            "LIGHT_RAIN": 0.3,
            "MODERATE_RAIN": 0.6,
            "HEAVY_RAIN": 1.0
        }

        # Rain tire performance multipliers
        self.rain_tire_performance = {
            "INTERMEDIATE": {
                "DRY": 0.95,      # 5% slower on dry
                "LIGHT_RAIN": 1.0,  # Optimal
                "MODERATE_RAIN": 1.05,  # 5% slower
                "HEAVY_RAIN": 1.15   # 15% slower
            },
            "WET": {
                "DRY": 0.85,      # 15% slower on dry
                "LIGHT_RAIN": 0.95,  # 5% slower
                "MODERATE_RAIN": 1.0,  # Optimal
                "HEAVY_RAIN": 1.05   # 5% slower
            }
        }

    def get_track_temperature(self, air_temp: float, humidity: float,
                              cloud_cover: float, time_of_day: str = "afternoon") -> float:
        """
        Calculate track temperature based on weather conditions.

        Args:
            air_temp: Air temperature in Celsius
            humidity: Humidity percentage (0-100)
            cloud_cover: Cloud cover percentage (0-100)
            time_of_day: "morning", "afternoon", "evening"
        """
        # Base track temp is typically 10-15°C higher than air temp
        base_track_temp = air_temp + 12.0

        # Humidity effect (higher humidity = cooler track)
        humidity_effect = -humidity * 0.05

        # Cloud cover effect (more clouds = cooler track)
        cloud_effect = -cloud_cover * 0.08

        # Time of day effect
        time_effects = {
            "morning": -5.0,
            "afternoon": 0.0,
            "evening": -3.0
        }
        time_effect = time_effects.get(time_of_day, 0.0)

        track_temp = base_track_temp + humidity_effect + cloud_effect + time_effect
        return max(track_temp, 15.0)  # Minimum track temp

    def get_rain_intensity(self, precipitation: float) -> str:
        """Convert precipitation value to rain intensity level."""
        if precipitation < 0.1:
            return "DRY"
        elif precipitation < 0.5:
            return "LIGHT_RAIN"
        elif precipitation < 1.0:
            return "MODERATE_RAIN"
        else:
            return "HEAVY_RAIN"

    def get_optimal_tire_compound(self, rain_intensity: str, track_temp: float) -> str:
        """
        Determine optimal tire compound based on weather conditions.

        Args:
            rain_intensity: Rain intensity level
            track_temp: Track temperature in Celsius

        Returns:
            Recommended tire compound
        """
        if rain_intensity == "DRY":
            if track_temp > 35:
                return "SOFT"  # Hot track favors soft tires
            elif track_temp > 25:
                return "MED"   # Moderate temp
            else:
                return "HARD"  # Cool track favors hard tires
        elif rain_intensity in ["LIGHT_RAIN", "MODERATE_RAIN"]:
            return "INTERMEDIATE"
        else:  # HEAVY_RAIN
            return "WET"

    def get_tire_performance_multiplier(self, tire_compound: str,
                                        rain_intensity: str) -> float:
        """
        Get performance multiplier for tire compound in given conditions.

        Returns:
            Multiplier (1.0 = normal performance, >1.0 = slower, <1.0 = faster)
        """
        if tire_compound in ["SOFT", "MED", "HARD"]:
            # Dry tires get slower in wet conditions
            if rain_intensity == "DRY":
                return 1.0
            elif rain_intensity == "LIGHT_RAIN":
                return 1.1  # 10% slower
            elif rain_intensity == "MODERATE_RAIN":
                return 1.25  # 25% slower
            else:  # HEAVY_RAIN
                return 1.5   # 50% slower
        else:
            # Rain tires
            return self.rain_tire_performance.get(tire_compound, {}).get(rain_intensity, 1.0)

    def simulate_weather_forecast(self, race_laps: int,
                                  initial_conditions: Dict) -> List[Dict]:
        """
        Simulate weather changes during the race.

        Args:
            race_laps: Total number of race laps
            initial_conditions: Starting weather conditions

        Returns:
            List of weather conditions for each lap
        """
        forecast = []
        current_conditions = initial_conditions.copy()

        for lap in range(1, race_laps + 1):
            # Simulate gradual weather changes
            if np.random.random() < 0.1:  # 10% chance of weather change per lap
                current_conditions = self._simulate_weather_change(
                    current_conditions)

            # Calculate track temperature for this lap
            track_temp = self.get_track_temperature(
                current_conditions["air_temp"],
                current_conditions["humidity"],
                current_conditions["cloud_cover"]
            )

            rain_intensity = self.get_rain_intensity(
                current_conditions["precipitation"])

            forecast.append({
                "lap": lap,
                "air_temp": current_conditions["air_temp"],
                "track_temp": track_temp,
                "humidity": current_conditions["humidity"],
                "precipitation": current_conditions["precipitation"],
                "rain_intensity": rain_intensity,
                "cloud_cover": current_conditions["cloud_cover"]
            })

        return forecast

    def _simulate_weather_change(self, current_conditions: Dict) -> Dict:
        """Simulate gradual weather changes during the race."""
        new_conditions = current_conditions.copy()

        # Temperature changes (±2°C per change)
        temp_change = np.random.normal(0, 1.0)
        new_conditions["air_temp"] = max(15, min(40,
                                                 new_conditions["air_temp"] + temp_change))

        # Humidity changes (±5% per change)
        humidity_change = np.random.normal(0, 3.0)
        new_conditions["humidity"] = max(20, min(90,
                                                 new_conditions["humidity"] + humidity_change))

        # Precipitation changes (can increase or decrease)
        precip_change = np.random.normal(0, 0.1)
        new_conditions["precipitation"] = max(0,
                                              new_conditions["precipitation"] + precip_change)

        # Cloud cover changes
        cloud_change = np.random.normal(0, 5.0)
        new_conditions["cloud_cover"] = max(0, min(100,
                                                   new_conditions["cloud_cover"] + cloud_change))

        return new_conditions


def get_default_weather_conditions() -> Dict:
    """Get typical weather conditions for F1 race."""
    return {
        "air_temp": 25.0,      # Celsius
        "humidity": 60.0,      # Percentage
        "precipitation": 0.0,  # mm/h
        "cloud_cover": 30.0    # Percentage
    }
