import numpy as np

def zero_mode_profile_L(z_grid, c, Lscale, kind="L"):
    """
    Restituisce (fL, fR) per lo zero-mode analitico:
      kind="L": f_L ~ z^{2-c}, f_R = 0
      kind="R": f_R ~ z^{2+c}, f_L = 0
    Poi normalizza con peso B=(L/z)^3 sulla griglia discreta (trapezi).
    """
    z = z_grid
    if kind.upper()=="L":
        fL = z**(2.0 - c); fR = np.zeros_like(z)
    else:
        fL = np.zeros_like(z); fR = z**(2.0 + c)
    # pesi trapezoidali per z non uniforme (già costruiti altrove, qui stimiamo)
    w = np.zeros_like(z)
    w[0]  = 0.5*(z[1]-z[0])
    w[-1] = 0.5*(z[-1]-z[-2])
    for i in range(1,len(z)-1):
        w[i] = 0.5*(z[i+1]-z[i-1])
    B = (Lscale / z)**3
    norm2 = np.sum((fL**2 + fR**2)*B*w)
    scale = 1.0/np.sqrt(norm2)
    return fL*scale, fR*scale, norm2
