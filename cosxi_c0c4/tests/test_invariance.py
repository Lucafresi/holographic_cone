from math import isclose
from cosxi.io import GlobalInput, Coeff
from cosxi.sequester import compute_xi, compute_rho_Lambda_t0
def test_global_rescaling_invariance():
    base = GlobalInput(Mpl=2.435e18, t0=4.35e17, Leff=1.0,
                       Aprime_UV=-0.3, Aprime_IR=-0.299999998,
                       Tbar=1e-12, coeff=Coeff(cB=1.0,cT=1.0))
    xi = compute_xi(base)
    rho = compute_rho_Lambda_t0(base, xi)
    lam = 3.7
    scaled = GlobalInput(Mpl=lam*base.Mpl, t0=lam*base.t0, Leff=base.Leff,
                         Aprime_UV=base.Aprime_UV, Aprime_IR=base.Aprime_IR,
                         Tbar=base.Tbar, coeff=base.coeff)
    rho2 = compute_rho_Lambda_t0(scaled, compute_xi(scaled))
    assert isclose(rho2, rho, rel_tol=1e-12, abs_tol=0.0)
