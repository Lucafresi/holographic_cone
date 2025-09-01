import numpy as np
from scipy.optimize import brentq

from .bc import phi_ir

def scan_brackets(fun, m_min, m_max, n_samples):
    xs = np.linspace(m_min, m_max, n_samples)
    vals = fun(xs)
    brackets = []
    for i in range(len(xs)-1):
        a, b = xs[i], xs[i+1]
        fa, fb = vals[i], vals[i+1]
        if np.sign(fa) == 0:
            brackets.append((a*(1-1e-6), a*(1+1e-6)))
        elif np.sign(fa) != np.sign(fb):
            brackets.append((a, b))
    return brackets

def find_roots_phi(c, alpha_uv, alpha_ir, z_uv, z_ir,
                   m_min, m_max, n_samples=20000, max_roots=6, tol=1e-14):
    def f(m):
        return phi_ir(m, c, alpha_uv, alpha_ir, z_uv, z_ir)
    def f_vec(ms):
        return np.array([f(m) for m in ms], dtype=float)

    br = scan_brackets(f_vec, m_min, m_max, n_samples)
    roots = []
    for (a,b) in br:
        try:
            r = brentq(f, a, b, xtol=tol, rtol=tol, maxiter=200)
            if r>0:
                # evita duplicati vicini
                if all(abs(r - rr) > 1e-9 for rr in roots):
                    roots.append(r)
                    if len(roots) >= max_roots:
                        break
        except ValueError:
            pass
    roots.sort()
    return roots
