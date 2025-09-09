from math import isclose
from cosxi.io import GlobalInput, Coeff
from cosxi.sequester import compute_xi

def test_sign_convention():
    g = GlobalInput(Mpl=1.0, t0=1.0, Leff=1.0,
                    Aprime_UV=-1.0, Aprime_IR=+1.0,
                    Tbar=0.0, coeff=Coeff(cB=1.0, cT=0.0))
    assert isclose(compute_xi(g), 2.0, rel_tol=0.0, abs_tol=0.0)
    g2 = GlobalInput(Mpl=1.0, t0=1.0, Leff=1.0,
                     Aprime_UV=+1.0, Aprime_IR=-1.0,
                     Tbar=0.0, coeff=Coeff(cB=1.0, cT=0.0))
    assert isclose(compute_xi(g2), -2.0, rel_tol=0.0, abs_tol=0.0)

def test_u1_term_units():
    g = GlobalInput(Mpl=10.0, t0=1.0, Leff=1.0,
                    Aprime_UV=0.0, Aprime_IR=0.0,
                    Tbar=1.0, coeff=Coeff(cB=0.0, cT=1.0))
    assert abs(compute_xi(g) - 10.0**-4) < 1e-18
