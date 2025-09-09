from dataclasses import dataclass
from math import exp

@dataclass(frozen=True)
class Coeff:
    cB: float = 1.0
    cT: float = 1.0

def xi_from_state(Mpl: float, tIR: float, Aprime_UV: float, Aprime_IR: float,
                  Tbar: float, coeff: Coeff = Coeff()) -> float:
    return coeff.cB * (Aprime_IR - Aprime_UV) + coeff.cT * (Tbar / (Mpl**4))

def ward_rhs(Mpl: float, tIR: float, Aprime_dot_IR: float, T_at_IR: float,
             Tbar: float, coeff: Coeff = Coeff()) -> float:
    return coeff.cB * Aprime_dot_IR + coeff.cT * ((T_at_IR - Tbar) / (tIR * (Mpl**4)))

# ---------- Analytic models for tests ----------

def model_A_Aprime(t: float, a0: float, a1: float, tau: float) -> float:
    return a0 + a1 * exp(-t / tau)

def model_A_Aprime_dot(t: float, a1: float, tau: float) -> float:
    return -(a1 / tau) * exp(-t / tau)

def model_A_T(t: float, T0: float) -> float:
    return T0

def model_A_Tbar(t: float, T0: float) -> float:
    return T0

def model_B_Aprime(t: float, a0: float) -> float:
    return a0

def model_B_Aprime_dot(t: float) -> float:
    return 0.0

def model_B_T(t: float, T0: float, q: float) -> float:
    return T0 + q * t

def model_B_Tbar(t: float, T0: float, q: float) -> float:
    return T0 + 0.5 * q * t
