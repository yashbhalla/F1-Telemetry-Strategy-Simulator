import itertools
import numpy as np
from sim.strategy import simulate_plan


def brute_force_best(race_laps, start_comp, compounds, tyre_model):
    best = (9e9, None)
    # try 1-2 stops, windows spaced 8–20 laps
    for nstops in [1, 2]:
        for pivots in itertools.combinations(range(12, race_laps-8, 4), nstops):
            for afters in itertools.product(compounds, repeat=nstops):
                plan = list(zip(pivots, afters))
                tt, _ = simulate_plan(race_laps, start_comp, plan, tyre_model)
                if tt < best[0]:
                    best = (tt, plan)
    return best
