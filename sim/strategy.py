from .tyres import TyreModel


def simulate_plan(race_laps, start_compound, pit_plan, tyre_model, pit_loss=20.0):
    stints = []
    current_lap = 1
    current_compound = start_compound
    total_time = 0.0

    # Sort pit stops by lap number
    pit_plan = sorted(pit_plan, key=lambda x: x[0])

    for pit_lap, new_compound in pit_plan:
        # Calculate stint from current lap to pit lap
        stint_laps = pit_lap - current_lap
        stint_time = 0.0

        for lap in range(stint_laps):
            tyre_life = lap + 1  # Tyre life starts at 1
            lap_time = tyre_model.lap_time(current_compound, tyre_life)
            stint_time += lap_time

        stints.append({
            'compound': current_compound,
            'start_lap': current_lap,
            'end_lap': pit_lap - 1,
            'laps': stint_laps,
            'total_time': stint_time,
            'avg_lap_time': stint_time / stint_laps if stint_laps > 0 else 0
        })

        total_time += stint_time + pit_loss
        current_lap = pit_lap
        current_compound = new_compound

    # Final stint to end of race
    final_stint_laps = race_laps - current_lap + 1
    final_stint_time = 0.0

    for lap in range(final_stint_laps):
        tyre_life = lap + 1
        lap_time = tyre_model.lap_time(current_compound, tyre_life)
        final_stint_time += lap_time

    stints.append({
        'compound': current_compound,
        'start_lap': current_lap,
        'end_lap': race_laps,
        'laps': final_stint_laps,
        'total_time': final_stint_time,
        'avg_lap_time': final_stint_time / final_stint_laps if final_stint_laps > 0 else 0
    })

    total_time += final_stint_time

    return total_time, stints


# Example usage (commented out to avoid circular imports)
if __name__ == "__main__":
    # Toy tyre performance assumptions
    params = {
        "SOFT": {"base": 75.0, "k": 0.08},
        "MED":  {"base": 76.0, "k": 0.05},
        "HARD": {"base": 77.0, "k": 0.03}
    }
    tyre_model = TyreModel(params)

    race_laps = 78  # Monaco GP length

    # 1-stop: Start SOFT, pit lap 25 → HARD
    plan1 = [(25, "HARD")]
    t1, stints1 = simulate_plan(race_laps, "SOFT", plan1, tyre_model)

    # 2-stop: Start SOFT, pit lap 18 → MED, pit lap 50 → HARD
    plan2 = [(18, "MED"), (50, "HARD")]
    t2, stints2 = simulate_plan(race_laps, "SOFT", plan2, tyre_model)

    print(f"1-stop SOFT→HARD: {t1:.1f} sec")
    print(f"2-stop SOFT→MED→HARD: {t2:.1f} sec")
    print("Best strategy:", "1-stop" if t1 < t2 else "2-stop")
