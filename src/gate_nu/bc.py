import numpy as np
from .fermion_bessel import J, Y, nu_from_c

def _alpha_val(alpha):
    # Consente "inf" in JSON
    if isinstance(alpha, str) and alpha.lower() in ("inf", "+inf", "infty", "infinite", "infinity"):
        return np.inf
    return float(alpha)

def r_uv(m, c, alpha_uv, z_uv):
    """
    r_UV(m) = - [ J_{nu-1}(x_uv) + alpha_uv J_{nu}(x_uv) ] / [ Y_{nu-1}(x_uv) + alpha_uv Y_{nu}(x_uv) ]
    Casi:
      alpha_uv = 0   -> P_- (impone f_R=0 su UV)
      alpha_uv = inf -> P_+ (impone f_L=0 su UV) => r = - J_nu / Y_nu
    """
    alpha = _alpha_val(alpha_uv)
    nu = nu_from_c(c)
    x = m * z_uv
    if np.isinf(alpha):
        num = J(nu, x)
        den = Y(nu, x)
    else:
        num = J(nu-1.0, x) + alpha * J(nu, x)
        den = Y(nu-1.0, x) + alpha * Y(nu, x)
    return - num / den

def phi_ir(m, c, alpha_uv, alpha_ir, z_uv, z_ir):
    """
    Funzione secolare:
      Phi_IR(m) = f_R(z_IR;m) + alpha_IR f_L(z_IR;m) = 0
    con f_{L,R} costruite con r_UV(m).
    """
    from .fermion_bessel import fL_fR_point
    r = r_uv(m, c, alpha_uv, z_uv)
    fL_IR, fR_IR = fL_fR_point(z_ir, m, c, r)
    alpha_ir_val = _alpha_val(alpha_ir)
    if np.isinf(alpha_ir_val):
        # P_+ su IR => f_L(z_IR)=0 come condizione: Phi ≡ f_L
        return fL_IR
    else:
        # Robin generica e caso P_- (alpha=0) inclusi: Phi ≡ f_R + alpha_IR f_L
        return fR_IR + alpha_ir_val * fL_IR
