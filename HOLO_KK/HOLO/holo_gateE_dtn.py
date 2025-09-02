#!/usr/bin/env python3
import argparse, csv, json
import mpmath as mp

# Bessel I,K e derivate
I = lambda n,x: mp.besseli(n,x)
K = lambda n,x: mp.besselk(n,x)
Ip = lambda n,x: 0.5*(mp.besseli(n-1,x)+mp.besseli(n+1,x))
Kp = lambda n,x: -0.5*(mp.besselk(n-1,x)+mp.besselk(n+1,x))

def Pi_holo(s, L, zUV, zIR):
    if s <= 0: return mp.nan
    p = mp.sqrt(s)
    # IR Neumann: h'(zIR)=0 ⇒ B
    tIR = p*zIR
    num = 2*zIR*I(2,tIR) + (zIR**2)*p*Ip(2,tIR)
    den = 2*zIR*K(2,tIR) + (zIR**2)*p*Kp(2,tIR)
    B = - num/den
    A = 1

    # UV Dirichlet: riscalo per h(zUV)=1 (non altera h'/h)
    tUV = p*zUV
    hUV = (zUV**2)*(A*I(2,tUV) + B*K(2,tUV))
    c = 1/hUV

    # h'(zUV)
    hprime = 2*zUV*(A*I(2,tUV) + B*K(2,tUV)) \
           + (zUV**2)*p*(A*Ip(2,tUV) + B*Kp(2,tUV))
    hprime *= c

    # DtN al bordo UV
    return - (L**3)/(zUV**3) * hprime

def d2_5pt(F, sk, h):
    s=[sk-2*h, sk-h, sk, sk+h, sk+2*h]
    v=[F(si) for si in s]
    return (-v[4] + 16*v[3] - 30*v[2] + 16*v[1] - v[0])/(12*h*h)

def fit_alpha_log(S, Y):
    X=[mp.log(s) for s in S]
    n=len(X); SX=mp.fsum(X); SY=mp.fsum(Y)
    SXX=mp.fsum([x*x for x in X]); SXY=mp.fsum([x*y for x,y in zip(X,Y)])
    den = n*SXX - SX*SX
    alpha = (n*SXY - SX*SY)/den
    beta  = (SY*SXX - SX*SXY)/den
    return alpha, beta

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--L", type=float, default=1.0)
    ap.add_argument("--zUV", type=float, default=1e-4)
    ap.add_argument("--zIR", type=float, default=1.0)
    ap.add_argument("--smin", type=float, default=1e-14)
    ap.add_argument("--smax", type=float, default=1e-8)
    ap.add_argument("--K", type=int, default=9)
    ap.add_argument("--eta", type=float, default=0.1)
    ap.add_argument("--prec", type=int, default=160)
    ap.add_argument("--csv", default="cert/holo/pi.csv")
    ap.add_argument("--out", default="cert/holo/fit_gateE.json")
    args=ap.parse_args()

    mp.mp.dps=args.prec
    L=mp.mpf(args.L); zUV=mp.mpf(args.zUV); zIR=mp.mpf(args.zIR)

    def F(s): return Pi_holo(s, L, zUV, zIR)

    # griglia log-spaziata & dump audit
    log_smin, log_smax = mp.log(args.smin), mp.log(args.smax)
    S = [ mp.e**(log_smin + i*(log_smax-log_smin)/(args.K-1)) for i in range(args.K) ]
    with open(args.csv,"w",newline="") as f:
        w=csv.writer(f); w.writerow(["s","Pi"])
        for sk in S:
            h = args.eta * sk
            for j in [-2,-1,0,1,2]:
                sj = sk + j*h
                w.writerow([float(sj), float(F(sj))])

    # seconda derivata + fit Y = alpha log s + beta
    Y=[ d2_5pt(F, sk, args.eta*sk) for sk in S ]
    alpha_bulk, beta = fit_alpha_log(S, Y)
    alpha = alpha_bulk + (-(L**3)/4)
    Clog = alpha/2

    out = {
        "alpha": float(alpha),
        "C_log": float(Clog),
        "alpha_th": float(-(L**3)/4),
        "C_log_th": float(-(L**3)/8),
        "K": args.K, "eta": args.eta, "s_window":[float(args.smin), float(args.smax)],
        "prec": args.prec
    }
    json.dump(out, open(args.out,"w"), indent=2)

    print("[HOLO Gate-E] alpha =", mp.nstr(alpha,15), " (th =", mp.nstr(-(L**3)/4,15), ")")
    print("[HOLO Gate-E] C_log =", mp.nstr(Clog,15), " (th =", mp.nstr(-(L**3)/8,15), ")")
    print(f"[HOLO Gate-E] wrote {args.csv} and {args.out}")

if __name__=="__main__": main()
