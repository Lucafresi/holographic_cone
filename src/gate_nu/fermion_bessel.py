import numpy as np
from scipy import special

def nu_from_c(c: float) -> float:
    return c + 0.5

def J(nu, x):
    return special.jv(nu, x)

def Y(nu, x):
    return special.yv(nu, x)

def fL_fR_point(z, m, c, r_uv):
    """
    Soluzioni bulk canoniche per fermione su slice AdS:
      f_L = z^{5/2} [ J_{nu}(mz) + r_uv Y_{nu}(mz) ]
      f_R = z^{5/2} [ J_{nu-1}(mz) + r_uv Y_{nu-1}(mz) ]
    """
    nu = nu_from_c(c)
    x = m * z
    fac = z**2.5
    fL = fac * (J(nu, x)      + r_uv * Y(nu, x))
    fR = fac * (J(nu-1.0, x)  + r_uv * Y(nu-1.0, x))
    return fL, fR

def fL_fR_profile(z_grid, m, c, r_uv):
    fL = np.empty_like(z_grid, dtype=float)
    fR = np.empty_like(z_grid, dtype=float)
    for i, z in enumerate(z_grid):
        fL[i], fR[i] = fL_fR_point(z, m, c, r_uv)
    return fL, fR
