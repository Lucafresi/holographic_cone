from math import isclose
from cosxi_ir import (
    Coeff, xi_from_state, ward_rhs
)

def test_zero_derivative_when_constants():
    Mpl = 1.0
    coeff = Coeff(cB=1.0, cT=1.0)
    Apr_UV = 0.0
    Apr_IR = 0.0
    Tbar   = 5.0
    tIR    = 10.0
    dt     = 1e-3

    xi1 = xi_from_state(Mpl, tIR, Apr_UV, Apr_IR, Tbar, coeff)
    xi2 = xi_from_state(Mpl, tIR+dt, Apr_UV, Apr_IR, Tbar, coeff)

    lhs = (xi2 - xi1) / dt
    rhs = ward_rhs(Mpl, tIR, 0.0, Tbar, Tbar, coeff)
    assert isclose(lhs, 0.0, abs_tol=1e-15)
    assert isclose(rhs, 0.0, abs_tol=1e-15)
