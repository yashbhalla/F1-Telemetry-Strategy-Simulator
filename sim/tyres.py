# sim_tyres.py
class TyreModel:
    def __init__(self, params):
        """
        params example:
        {
          "SOFT": {"base": 75.0, "k": 0.08},  # seconds
          "MED":  {"base": 76.0, "k": 0.05},
          "HARD": {"base": 77.0, "k": 0.03}
        }
        """
        self.params = params

    def lap_time(self, compound, tyre_life):
        p = self.params[compound]
        return p["base"] + p["k"] * tyre_life
