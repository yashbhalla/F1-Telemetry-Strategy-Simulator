import numpy as np
from typing import List, Dict, Tuple
import random


class SafetyCarModel:
    """Model safety car events and their effects on race strategy."""

    def __init__(self):
        # Safety car probability factors
        self.base_sc_probability = 0.15  # 15% chance per race
        self.lap_sc_probability = 0.002  # 0.2% chance per lap

        # Safety car duration parameters (laps)
        self.sc_duration_min = 2
        self.sc_duration_max = 8
        self.sc_duration_mean = 4

        # Pit stop time reduction under SC
        self.sc_pit_time_reduction = 8.0  # seconds

        # Field compression effect
        self.field_compression = 0.8  # 80% of original gaps maintained

    def generate_safety_car_events(self, race_laps: int,
                                   weather_conditions: List[Dict] = None) -> List[Dict]:
        """
        Generate safety car events for a race.

        Args:
            race_laps: Total number of race laps
            weather_conditions: Weather forecast (affects SC probability)

        Returns:
            List of safety car events with start/end laps
        """
        sc_events = []

        # Calculate base probability
        total_sc_prob = self.base_sc_probability + \
            (race_laps * self.lap_sc_probability)

        # Weather effect on SC probability
        if weather_conditions:
            weather_factor = self._calculate_weather_sc_factor(
                weather_conditions)
            total_sc_prob *= weather_factor

        # Determine if SC occurs
        if random.random() < total_sc_prob:
            # Generate SC start lap (avoid first/last few laps)
            start_lap = random.randint(5, race_laps - 10)

            # Generate SC duration
            duration = max(self.sc_duration_min,
                           min(self.sc_duration_max,
                               int(np.random.normal(self.sc_duration_mean, 1.5))))

            end_lap = min(start_lap + duration, race_laps - 2)

            sc_events.append({
                "start_lap": start_lap,
                "end_lap": end_lap,
                "duration": end_lap - start_lap,
                "type": "SAFETY_CAR"
            })

        return sc_events

    def _calculate_weather_sc_factor(self, weather_conditions: List[Dict]) -> float:
        """Calculate weather effect on safety car probability."""
        # Count wet laps
        wet_laps = sum(1 for w in weather_conditions
                       if w.get("rain_intensity", "DRY") != "DRY")

        if wet_laps == 0:
            return 1.0  # No weather effect
        elif wet_laps < len(weather_conditions) * 0.3:
            return 1.2  # 20% increase for light rain
        elif wet_laps < len(weather_conditions) * 0.7:
            return 1.5  # 50% increase for moderate rain
        else:
            return 2.0  # 100% increase for heavy rain

    def get_pit_stop_time(self, base_pit_time: float, lap: int,
                          sc_events: List[Dict]) -> float:
        """
        Calculate pit stop time considering safety car effects.

        Args:
            base_pit_time: Normal pit stop time
            lap: Current lap number
            sc_events: List of safety car events

        Returns:
            Adjusted pit stop time
        """
        # Check if pit stop is under safety car
        is_under_sc = any(event["start_lap"] <= lap <= event["end_lap"]
                          for event in sc_events)

        if is_under_sc:
            return max(base_pit_time - self.sc_pit_time_reduction, 5.0)
        else:
            return base_pit_time

    def apply_field_compression(self, lap_times: List[float],
                                sc_events: List[Dict]) -> List[float]:
        """
        Apply field compression effect during safety car periods.

        Args:
            lap_times: List of lap times
            sc_events: List of safety car events

        Returns:
            Adjusted lap times with compression effects
        """
        compressed_times = lap_times.copy()

        for event in sc_events:
            start_lap = event["start_lap"]
            end_lap = event["end_lap"]

            # Apply compression during SC period
            for lap in range(start_lap, end_lap + 1):
                if lap < len(compressed_times):
                    # Reduce lap time variation during SC
                    base_time = compressed_times[lap]
                    compressed_times[lap] = base_time * self.field_compression

        return compressed_times

    def calculate_strategy_advantage(self, pit_lap: int,
                                     sc_events: List[Dict]) -> Dict:
        """
        Calculate strategic advantage of pitting under safety car.

        Args:
            pit_lap: Lap when pit stop occurs
            sc_events: List of safety car events

        Returns:
            Dictionary with advantage details
        """
        advantage = {
            "is_under_sc": False,
            "time_saved": 0.0,
            "position_gained": 0,
            "field_compression": 0.0
        }

        # Check if pit stop is under SC
        for event in sc_events:
            if event["start_lap"] <= pit_lap <= event["end_lap"]:
                advantage["is_under_sc"] = True
                advantage["time_saved"] = self.sc_pit_time_reduction
                advantage["position_gained"] = 2  # Typical positions gained
                advantage["field_compression"] = 1.0 - self.field_compression
                break

        return advantage


def sample_sc_events(race_laps=60, lam=0.6):
    """Legacy function for backward compatibility."""
    model = SafetyCarModel()
    events = model.generate_safety_car_events(race_laps)
    return [event["start_lap"] for event in events]


def sc_effect(pit_loss, is_under_sc):
    """Legacy function for backward compatibility."""
    model = SafetyCarModel()
    return model.get_pit_stop_time(pit_loss, 0, []) if is_under_sc else pit_loss
