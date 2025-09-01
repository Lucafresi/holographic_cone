import numpy as np

def cheb_lobatto(a, b, N):
    """
    N nodi di Chebyshev-Lobatto su [a,b].
    Ritorna (z, w_trap): nodi crescenti e pesi tipo trapezoidali adattati ai nodi non-uniformi.
    """
    k = np.arange(N)
    x = np.cos(np.pi * k / (N-1))  # in [-1,1], da 1 a -1
    z = 0.5*(b+a) + 0.5*(b-a)*x
    # ordina crescente in z
    idx = np.argsort(z)
    z = z[idx]
    # pesi trapezoidali adattati a griglia non uniforme
    w = np.zeros_like(z)
    w[0]  = 0.5*(z[1]-z[0])
    w[-1] = 0.5*(z[-1]-z[-2])
    for i in range(1, N-1):
        w[i] = 0.5*(z[i+1]-z[i-1])
    return z, w

def B_weights(z, L):
    return (L / z)**3

def normalize_mode(fL, fR, z, w, L):
    B = B_weights(z, L)
    dens = (fL**2 + fR**2) * B
    norm2 = np.sum(dens * w)
    if norm2 <= 0:
        raise RuntimeError("Norma non positiva.")
    scale = 1.0 / np.sqrt(norm2)
    return fL*scale, fR*scale, norm2
