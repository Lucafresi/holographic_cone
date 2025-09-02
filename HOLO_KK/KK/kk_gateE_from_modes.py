#!/usr/bin/env python3
import json, argparse, csv
import mpmath as mp

def load_modes(path):
    data = json.load(open(path,"r"))
    L = mp.mpf(data["L"])
    m2 = [ mp.mpf(m["m2"]) for m in data["modes"] ]
    g  = [ mp.mpf(m["g"])  for m in data["modes"] ]
    return L, m2, g

def PiKK_factory(m2, g):
    def Pi(s):
        return mp.fsum([(gi*gi)/(s+mi2) for gi,mi2 in zip(g,m2)])
    return Pi

def Pi_tail_factory(L):
    # C_log^th = -(L^3)/8  ⇒ Π_tail(s) = C_log^th * s^2 log s
    Clog_th = -(L**3)/8
    def Pi_tail(s):
        return Clog_th * (s*s) * mp.log(s)  # s>0 in UV
    return Pi_tail

def second_derivative_5pt(F, sk, h):
    s = [sk-2*h, sk-h, sk, sk+h, sk+2*h]
    vals = [F(si) for si in s]
    return (-vals[4] + 16*vals[3] - 30*vals[2] + 16*vals[1] - vals[0]) / (12*h*h)

def fit_alpha_log(s_list, y_list):
    X = [mp.log(s) for s in s_list]
    n = len(X); SX = mp.fsum(X); SY = mp.fsum(y_list)
    SXX = mp.fsum([x*x for x in X]); SXY = mp.fsum([x*y for x,y in zip(X,y_list)])
    den = n*SXX - SX*SX
    alpha = (n*SXY - SX*SY)/den
    beta  = (SY*SXX - SX*SXY)/den
    return alpha, beta

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--modes", default="cert/kk/modes_analytic.json")
    ap.add_argument("--smin", type=float, default=1e-14)
    ap.add_argument("--smax", type=float, default=1e-8)
    ap.add_argument("--K", type=int, default=9)
    ap.add_argument("--eta", type=float, default=0.1)
    ap.add_argument("--prec", type=int, default=160)
    ap.add_argument("--csv", default="cert/kk/pi.csv")
    ap.add_argument("--out", default="cert/kk/fit_gateE.json")
    args = ap.parse_args()

    mp.mp.dps = args.prec
    L, m2, g = load_modes(args.modes)
    Pi_sum  = PiKK_factory(m2, g)
    Pi_tail = Pi_tail_factory(L)

    def Pi(s):
        # Gate-E: somma parziale + coda UV universale
        return Pi_sum(s) + Pi_tail(s)

    # griglia log-spaziata per s e dump audit CSV
    log_smin, log_smax = mp.log(args.smin), mp.log(args.smax)
    s_macro = [ mp.e**(log_smin + i*(log_smax-log_smin)/(args.K-1)) for i in range(args.K) ]
    with open(args.csv,"w",newline="") as f:
        w=csv.writer(f); w.writerow(["s","Pi"])
        for sk in s_macro:
            h = args.eta * sk
            for j in [-2,-1,0,1,2]:
                sj = sk + j*h
                w.writerow([float(sj), float(Pi(sj))])

    # seconda derivata e fit Y = alpha log s + beta
    Y=[]; S=[]
    for sk in s_macro:
        h = args.eta * sk
        Yk = second_derivative_5pt(Pi, sk, h)
        Y.append(Yk); S.append(sk)
    alpha, beta = fit_alpha_log(S, Y)
    Clog = alpha/2

    out = {
        "alpha": float(alpha),
        "C_log": float(Clog),
        "alpha_th": float(-(L**3)/4),
        "C_log_th": float(-(L**3)/8),
        "K": args.K, "eta": args.eta, "s_window":[float(args.smin), float(args.smax)],
        "modes_used": len(m2), "prec": args.prec,
        "used_tail": True
    }
    json.dump(out, open(args.out,"w"), indent=2)

    # stampa robusta per mpf
    print("[KK Gate-E] alpha =",
          mp.nstr(alpha, 15),
          " (th =",
          mp.nstr(-(L**3)/4, 15),
          ")")
    print("[KK Gate-E] C_log =",
          mp.nstr(Clog, 15),
          " (th =",
          mp.nstr(-(L**3)/8, 15),
          ")")
    print(f"[KK Gate-E] wrote {args.csv} and {args.out}")
if __name__=="__main__": main()
