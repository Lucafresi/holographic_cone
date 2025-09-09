from math import isclose
from cosxi.io import GlobalInput, Coeff
from cosxi.sequester import compute_xi
def test_regression_numbers():
    g = GlobalInput(Mpl=2.435e18, t0=4.35e17, Leff=1.0,
                    Aprime_UV=-0.300000000, Aprime_IR=-0.299999998,
                    Tbar=1.0e-12, coeff=Coeff(cB=1.0, cT=1.0))
    xi = compute_xi(g)
    assert isclose(xi, 2.0e-9, rel_tol=1e-9, abs_tol=0.0)
