from math import isclose
from cosxi_ir import (
    Coeff, xi_from_state, ward_rhs,
    model_B_Aprime, model_B_Aprime_dot,
    model_B_Tbar, model_B_T,
)

def _richardson_deriv(f, t, h0, levels=3):
    D = []
    h = h0
    for _ in range(levels):
        D.append((f(t + h) - f(t - h)) / (2.0*h))
        h *= 0.5
    for k in range(1, levels):
        factor = 4**k
        for i in range(levels - k):
            D[i] = (factor * D[i+1] - D[i]) / (factor - 1.0)
    return D[0]

def test_ward_identity_model_B():
    Mpl = 1.0
    coeff = Coeff(cB=1.0, cT=1.0)
    a0 = 0.7
    T0, q = 2.5, 0.02

    tUV = 0.0
    tIR = 20.0
    h0  = 1e-3 * tIR

    Apr_UV = model_B_Aprime(tUV, a0)
    Tbar   = model_B_Tbar(tIR, T0, q)

    def xi_at(tt):
        Apr_IR = model_B_Aprime(tt, a0)
        Tbar_  = model_B_Tbar(tt, T0, q)
        return xi_from_state(Mpl, tt, Apr_UV, Apr_IR, Tbar_, coeff)

    lhs = _richardson_deriv(xi_at, tIR, h0, levels=3)
    rhs = ward_rhs(
        Mpl, tIR,
        model_B_Aprime_dot(tIR),
        model_B_T(tIR, T0, q),
        Tbar,
        coeff,
    )
    assert isclose(lhs, rhs, rel_tol=1e-12, abs_tol=1e-13)
