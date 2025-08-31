import math
from .coeffs import COEFFS
from .sm_counts import SM_DOFS, pair_weight_same_category

def C_eff(spin_X: str, include_S=True, include_F=True, include_V=True):
    """
    Costruisce C_eff^(X) = sum_{cats} c_{cat,cat->X} * [0.5 * g_cat^2]
    (somma solo su coppie omogenee S/S, F/F, V/V: contributo dominante e rigoroso
     per coeff. universali di gravità; nessun cross-term ad hoc).
    """
    if spin_X not in COEFFS:
        raise ValueError(f"spin_X non valido: {spin_X}")
    ctab = COEFFS[spin_X]
    C = 0.0
    if include_S and ("S","S") in ctab:
        C += ctab[("S","S")] * pair_weight_same_category(SM_DOFS["S"])
    if include_F and ("F","F") in ctab:
        C += ctab[("F","F")] * pair_weight_same_category(SM_DOFS["F"])
    if include_V and ("V","V") in ctab:
        C += ctab[("V","V")] * pair_weight_same_category(SM_DOFS["V"])
    return C

def Y_infinity(TR, Mpl, gstar, gstars, Ceff):
    """
    Y_inf = [135*sqrt(10)/(2*pi^8)] * (Ceff/(gstars*sqrt(gstar))) * (TR/Mpl)^3
    (freeze-in UV-dominated dal bagno termico, MB/BE-FD al LO)
    """
    K = (135.0 * math.sqrt(10.0)) / (2.0 * (math.pi**8))
    return K * (Ceff / (gstars * math.sqrt(gstar))) * ((TR / Mpl) ** 3)

def Omega_h2(m_GeV, Y):
    # Omega h^2 = (m s0)/(rho_c/h^2) * Y  con s0=2891.2 cm^-3, rho_c/h^2=1.0537e-5 GeV cm^-3
    s0 = 2891.2
    rho_over_h2 = 1.0537e-5
    return (m_GeV * s0 / rho_over_h2) * Y

def TR_required(target_Omega, m_GeV, Mpl, gstar, gstars, Ceff):
    K = (135.0 * math.sqrt(10.0)) / (2.0 * (math.pi**8))
    if target_Omega <= 0 or m_GeV <= 0 or Ceff <= 0 or gstar <= 0 or gstars <= 0:
        return float("nan")
    Y_req = target_Omega / ( (m_GeV * 2891.2) / 1.0537e-5 )
    X = (Y_req * gstars * math.sqrt(gstar)) / (K * Ceff)
    return (X ** (1.0/3.0)) * Mpl
