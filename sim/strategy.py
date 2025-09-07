from sim_tyres import TyreModel
from sim_strategy import simulate_plan

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
t1 = simulate_plan(race_laps, "SOFT", plan1, tyre_model)

# 2-stop: Start SOFT, pit lap 18 → MED, pit lap 50 → HARD
plan2 = [(18, "MED"), (50, "HARD")]
t2 = simulate_plan(race_laps, "SOFT", plan2, tyre_model)

print(f"1-stop SOFT→HARD: {t1:.1f} sec")
print(f"2-stop SOFT→MED→HARD: {t2:.1f} sec")
print("Best strategy:", "1-stop" if t1 < t2 else "2-stop")
