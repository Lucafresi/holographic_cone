import numpy as np

def pick_value_at_brane(arr, z, z_brane):
    return arr[np.argmin(np.abs(z - z_brane))]

def y4D_brane(lambda_B, Lscale, z_brane, f_s_chir, g_L_chir, h0=1.0):
    # Yukawa 4D da operatore di brana: y4 = λ_B * e^{3A} * f_s * g_L * h0, con e^{3A}=(L/z)^3
    return float(lambda_B) * ((Lscale / z_brane)**3) * f_s_chir * g_L_chir * h0

def sin2_2theta(m_s, y4d, v=246.0):
    m_D = y4d * v
    val = (4.0*m_D*m_D) / (m_s*m_s + 4.0*m_D*m_D)
    return 0.0 if val<0 else (1.0 if val>1 else float(val))
