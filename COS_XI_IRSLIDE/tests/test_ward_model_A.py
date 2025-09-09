from math import isclose
from cosxi_ir import (
    Coeff, xi_from_state, ward_rhs,
    model_A_Aprime, model_A_Aprime_dot,
    model_A_Tbar, model_A_T,
)

def _richardson_deriv(f, t, h0, levels=3):
    # centrale + Richardson triangolare (ordine ~ O(h^(2*levels)))
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

def test_ward_identity_model_A():
    Mpl = 1.0
    coeff = Coeff(cB=1.0, cT=1.0)
    a0, a1, tau = 0.2, 0.3, 5.0
    T0 = 3.0

    tUV = 0.0
    tIR = 10.0
    h0  = 1e-3 * tIR  # base più grande per ridurre round-off; Richardson farà il resto

    Apr_UV = model_A_Aprime(tUV, a0, a1, tau)
    Tbar   = model_A_Tbar(tIR, T0)

    def xi_at(tt):
        Apr_IR = model_A_Aprime(tt, a0, a1, tau)
        Tbar_  = model_A_Tbar(tt, T0)
        return xi_from_state(Mpl, tt, Apr_UV, Apr_IR, Tbar_, coeff)

    lhs = _richardson_deriv(xi_at, tIR, h0, levels=3)
    rhs = ward_rhs(
        Mpl, tIR,
        model_A_Aprime_dot(tIR, a1, tau),
        model_A_T(tIR, T0),
        Tbar,
        coeff,
    )
    assert isclose(lhs, rhs, rel_tol=1e-12, abs_tol=1e-13)
