MPL_GEV = 2.435e18
HBAR_GEV_S = 6.582119569e-25

def seconds_to_GeVinv(t_s: float) -> float:
    return t_s / HBAR_GEV_S
