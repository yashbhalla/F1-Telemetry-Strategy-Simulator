import numpy as np


def sample_sc_events(race_laps=60, lam=0.6):
    n = np.random.poisson(lam)
    laps = np.random.choice(np.arange(5, race_laps-5), size=n, replace=False)
    return sorted(int(x) for x in laps)  # SC start laps


def sc_effect(pit_loss, is_under_sc):
    return pit_loss - 8.0 if is_under_sc else pit_loss  # example
