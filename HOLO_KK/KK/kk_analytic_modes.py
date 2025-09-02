#!/usr/bin/env python3
import json, argparse
import mpmath as mp

# Bessel helpers (ordine intero)
def J(n,x): return mp.besselj(n,x)
def Y(n,x): return mp.bessely(n,x)
def Jp(n,x): return 0.5*(mp.besselj(n-1,x)-mp.besselj(n+1,x))
def Yp(n,x): return 0.5*(mp.bessely(n-1,x)-mp.bessely(n+1,x))

def beta_of_x(x, zUV):
    # UV Dirichlet: J2 + beta Y2 = 0  at tUV = x zUV
    tUV = x*zUV
    return -J(2,tUV)/Y(2,tUV)

def fprime_IR(x, zIR, zUV):
    # f'(z) = 2 z (J2 + beta Y2) + z^2 x (J2'+beta Y2')
    tIR = x*zIR
    b = beta_of_x(x, zUV)
    return 2*zIR*(J(2,tIR)+b*Y(2,tIR)) + zIR**2 * x * (Jp(2,tIR) + b*Yp(2,tIR))

def find_roots_IR_neumann(N, zIR, zUV):
    roots = []
    x = mp.mpf('1e-6')
    dx = mp.pi  # passo robusto
    s0 = mp.sign(fprime_IR(x, zIR, zUV))
    while len(roots) < N:
        x2 = x + dx
        s1 = mp.sign(fprime_IR(x2, zIR, zUV))
        if s0 == 0:
            roots.append(x); s0 = mp.sign(fprime_IR(x2, zIR, zUV)); x = x2; continue
        if s1 == 0 or s1 != s0:
            a,b = x,x2
            fa,fb = fprime_IR(a,zIR,zUV), fprime_IR(b,zIR,zUV)
            for _ in range(80):
                c = 0.5*(a+b)
                fc = fprime_IR(c,zIR,zUV)
                if mp.sign(fc) == 0: a=b=c; break
                if mp.sign(fa)*mp.sign(fc) < 0:
                    b,fb = c,fc
                else:
                    a,fa = c,fc
            roots.append(0.5*(a+b))
            s0 = mp.sign(fprime_IR(x2, zIR, zUV))
        x = x2
    return roots

def lommel_S(t, beta):
    # S(t) = (t^2/2)[ (J2^2 - J1 J3) + 2β (J2 Y2 - J1 Y3) + β^2 (Y2^2 - Y1 Y3) ]
    J1,J2,J3 = J(1,t), J(2,t), J(3,t)
    Y1,Y2,Y3 = Y(1,t), Y(2,t), Y(3,t)
    JJ = J2*J2 - J1*J3
    JY = J2*Y2 - J1*Y3
    YY = Y2*Y2 - Y1*Y3
    return 0.5 * t*t * ( JJ + 2*beta*JY + (beta*beta)*YY )

def I_analytic(x, L, zUV, zIR):
    b = beta_of_x(x, zUV)
    tUV, tIR = x*zUV, x*zIR
    return (L**3)/(x*x) * ( lommel_S(tIR,b) - lommel_S(tUV,b) )

def g_from_mode(x, L, zUV, zIR):
    # f'(zUV) simplifies because J2+beta Y2=0 at tUV
    b = beta_of_x(x, zUV)
    tUV = x*zUV
    fprimeUV = (zUV*zUV*x/2) * ( (J(1,tUV)-J(3,tUV)) + b*(Y(1,tUV)-Y(3,tUV)) )
    I = I_analytic(x, L, zUV, zIR)
    g = (L**3)/(zUV**3) * ( fprimeUV / mp.sqrt(I) )
    return g, I

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--L", type=float, default=1.0)
    ap.add_argument("--zUV", type=float, default=1e-4)
    ap.add_argument("--zIR", type=float, default=1.0)
    ap.add_argument("--N", type=int, default=150)
    ap.add_argument("--prec", type=int, default=120)
    ap.add_argument("--out", default="cert/kk/modes_analytic.json")
    args = ap.parse_args()

    mp.mp.dps = args.prec
    L = mp.mpf(args.L); zUV = mp.mpf(args.zUV); zIR = mp.mpf(args.zIR)

    xs = find_roots_IR_neumann(args.N, zIR, zUV)
    modes = []
    for x in xs:
        b = beta_of_x(x, zUV)
        g,I = g_from_mode(x, L, zUV, zIR)
        modes.append({
            "x": float(x),
            "m2": float(x*x),
            "beta": float(b),
            "I_analytic": float(I),
            "g": float(g)
        })
    out = {
        "L": float(L), "zUV": float(zUV), "zIR": float(zIR),
        "prec": args.prec, "N": args.N,
        "modes": modes
    }
    with open(args.out,"w") as f: json.dump(out,f,indent=2)
    print(f"[KK-AN] wrote {args.out}  | modes: {len(modes)}")
    # stampa rapido dei primi 3 per controllo
    for i,m in enumerate(modes[:3],1):
        print(f"  n={i:3d}  x≈{m['x']:.6e}  g≈{m['g']:.6e}  I≈{m['I_analytic']:.6e}")
if __name__=="__main__": main()
