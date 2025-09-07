import numpy as np
from sim.tyres import TyreModel
from sim.sc_models import sample_sc_events, sc_effect


def simulate_plan(race_laps, start_compound, plan, tyre_model: TyreModel,
                  base_pit_loss=21.0, fuel_start=100.0, sc_laps=None):
    plan_idx = 0
    curr_comp = start_compound
    tyre_life = 1
    fuel = fuel_start
    total_time = 0.0
    p_stops = []
    sc_laps = set(sc_laps or [])

    for lap in range(1, race_laps+1):
        # pit stop?
        if plan_idx < len(plan) and lap == plan[plan_idx][0]:
            under_sc = lap in sc_laps or (lap-1) in sc_laps
            loss = sc_effect(base_pit_loss, under_sc)
            total_time += loss
            curr_comp = plan[plan_idx][1]
            tyre_life = 1
            p_stops.append((lap, curr_comp, loss))
            plan_idx += 1

        # lap time
        total_time += tyre_model.lap_time(curr_comp, tyre_life, fuel)
        tyre_life += 1
        fuel = max(0.0, fuel - (fuel_start / race_laps))
    return total_time, p_stops
