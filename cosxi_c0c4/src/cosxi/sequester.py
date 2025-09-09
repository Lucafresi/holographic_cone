from __future__ import annotations
from .io import GlobalInput

def compute_xi(g: GlobalInput) -> float:
    # B_IR = A'|IR - A'|UV  (dimensionless, globale)
    B_IR = g.Aprime_IR - g.Aprime_UV
    xi_B = g.coeff.cB * B_IR
    xi_T = g.coeff.cT * (g.Tbar / (g.Mpl ** 4))
    return float(xi_B + xi_T)

def compute_rho_Lambda_t0(g: GlobalInput, xi: float) -> float:
    # ρ_Λ(t0) = (Mpl^2 / t0^2) * ξ
    return float((g.Mpl ** 2 / g.t0 ** 2) * xi)
