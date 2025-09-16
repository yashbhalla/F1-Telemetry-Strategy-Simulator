from .tyres import TyreModel


def simulate_plan(race_laps, start_compound, pit_plan, tyre_model, pit_loss=20.0, weather_forecast=None):
    stints = []
    current_lap = 1
    current_compound = start_compound
    total_time = 0.0

    pit_plan = sorted(pit_plan, key=lambda x: x[0])

    while current_lap <= race_laps:
        # Check if there is a scheduled pit stop at this lap
        if pit_plan and current_lap == pit_plan[0][0]:
            _, new_compound = pit_plan.pop(0)
            # End previous stint before pit stop
            if stints and stints[-1]['end_lap'] < current_lap - 1:
                stints[-1]['end_lap'] = current_lap - 1
            current_compound = new_compound
            total_time += pit_loss  # add pit loss

        # Weather check: rain forecast triggers forced pit stop if >=5 laps rain
        if weather_forecast:
            rain = weather_forecast[current_lap -
                                    1].get("rain_intensity", "DRY")
            if rain in ("LIGHT_RAIN", "HEAVY_RAIN"):
                # Look ahead for 5 laps
                end_idx = min(current_lap + 4, race_laps)
                upcoming = [weather_forecast[i].get("rain_intensity", "DRY")
                            for i in range(current_lap - 1, end_idx)]
                if all(r == rain for r in upcoming):
                    forced_compound = "INTER" if rain == "LIGHT_RAIN" else "WET"
                    if current_compound not in ("INTER", "WET"):
                        # Insert pit stop now
                        if stints:
                            stints[-1]['end_lap'] = current_lap - 1
                        current_compound = forced_compound
                        total_time += pit_loss

        # Lap time calculation
        tyre_life = 1 if not stints else (
            current_lap - stints[-1]['start_lap'] + 1)
        lap_time = tyre_model.lap_time(current_compound, tyre_life)
        total_time += lap_time

        # Record stint info
        if not stints or stints[-1]['compound'] != current_compound:
            # New stint
            stints.append({
                'compound': current_compound,
                'start_lap': current_lap,
                'end_lap': current_lap,
                'laps': 1,
                'total_time': lap_time,
                'avg_lap_time': lap_time
            })
        else:
            # Extend current stint
            stints[-1]['end_lap'] = current_lap
            stints[-1]['laps'] += 1
            stints[-1]['total_time'] += lap_time
            stints[-1]['avg_lap_time'] = stints[-1]['total_time'] / \
                stints[-1]['laps']

        current_lap += 1

    return total_time, stints


# Example usage (run directly)
if __name__ == "__main__":
    params = {
        "SOFT": {"base": 75.0, "k": 0.08, "cliff_at": 20, "cliff_penalty": 0.3, "max_life": 30},
        "MED": {"base": 76.0, "k": 0.05, "cliff_at": 28, "cliff_penalty": 0.2, "max_life": 40},
        "HARD": {"base": 77.0, "k": 0.03, "cliff_at": 999, "cliff_penalty": 0.0, "max_life": 60},
        "INTER": {"base": 78.5, "k": 0.04, "cliff_at": 25, "cliff_penalty": 0.2, "max_life": 30},
        "WET": {"base": 80.0, "k": 0.05, "cliff_at": 20, "cliff_penalty": 0.3, "max_life": 25}
    }
    tyre_model = TyreModel(params)

    # Dummy rain forecast: dry until lap 15, then heavy rain 10 laps
    forecast = [{"lap": i + 1, "rain_intensity": "DRY"} for i in range(30)]
    for i in range(15, 25):
        forecast[i]["rain_intensity"] = "HEAVY_RAIN"

    total_time, stints = simulate_plan(
        race_laps=30,
        start_compound="SOFT",
        pit_plan=[(12, "MED"), (22, "HARD")],
        tyre_model=tyre_model,
        weather_forecast=forecast
    )

    print(f"Total time: {total_time:.1f} sec")
    for stint in stints:
        print(stint)
