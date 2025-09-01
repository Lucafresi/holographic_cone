#!/usr/bin/env python3
import json, math, argparse, os, csv
from fractions import Fraction

HBAR_GEV_S = 6.582119569e-25
T_UNIV_S   = 4.354e17
PI = math.pi

def load_json(p):
    with open(p) as f: return json.load(f)

def get_couplings_map(d):
    for k in ('C_integer','C_hat','C','couplings','C_int'):
        if k in d and isinstance(d[k], dict): return d[k]
    for k,v in d.items():
        if isinstance(v, dict) and 'integer' in k.lower():
            return v
    raise KeyError("Couplings map non trovata nel JSON di input.")

def parse_num(x):
    if isinstance(x,(int,float)): return float(x)
    if isinstance(x,str):
        return float(Fraction(x)) if '/' in x else float(x)
    return float(x)

def compute_constants(coup_map, met):
    s2 = met.get('sin2_thetaW', 0.23122); sW = math.sqrt(s2); cW = math.sqrt(1.0 - s2)
    a_em = met.get('alpha_em', 1/137.035999084)
    a_s  = met.get('alpha_s', 0.1181)

    C = {k: parse_num(v) for k,v in coup_map.items()}
    C_WW = C.get('aWW', C.get('C_aWW', C.get('WW')))
    C_YY = C.get('aYY', C.get('C_aYY', C.get('YY')))
    C_GG = C.get('aGG', C.get('C_aGG', C.get('GG')))
    if C_WW is None or C_YY is None or C_GG is None:
        raise KeyError("Mancano aWW/aYY/aGG nella mappa dei coefficienti.")

    C_agamma = sW*sW*C_WW + cW*cW*C_YY
    K = ((a_em*C_agamma/(2*PI))**2)/(64*PI) + ((a_s*C_GG/(2*PI))**2)/(8*PI)

    return {
        'alpha_em': a_em, 'alpha_s': a_s, 'sin2_thetaW': s2,
        'C_WW': C_WW, 'C_YY': C_YY, 'C_GG': C_GG, 'C_agamma': C_agamma, 'K': K
    }

def widths_and_tau(m, fa, const):
    a_em = const['alpha_em']; a_s = const['alpha_s']
    C_ag = const['C_agamma']; C_GG = const['C_GG']
    g_agamma = a_em/(2*PI*fa) * C_ag
    g_agg    = a_s /(2*PI*fa) * C_GG
    G_aa = (g_agamma**2) * (m**3) / (64*PI)
    G_gg = (g_agg**2)    * (m**3) / (8*PI)
    Gtot = G_aa + G_gg
    tau  = HBAR_GEV_S / Gtot if Gtot>0 else float('inf')
    BRa  = G_aa/Gtot if Gtot>0 else 0.0
    BRg  = G_gg/Gtot if Gtot>0 else 0.0
    return Gtot, tau, BRa, BRg, g_agamma, g_agg

def logspace(a,b,n):
    la, lb = math.log10(a), math.log10(b)
    return [10**(la + i*(lb-la)/(n-1)) for i in range(n)]

def main():
    ap = argparse.ArgumentParser(description="Scan (f_a, m_a) per τ e BR; ledger-only, nessun fit.")
    ap.add_argument('--couplings', default='cert/DM/axion/axion_couplings_norm.json')
    ap.add_argument('--met', default='cert/DM/metrology.json')
    ap.add_argument('--mmin', type=float, default=1e-12)
    ap.add_argument('--mmax', type=float, default=1e-1)
    ap.add_argument('--nm', type=int, default=61)
    ap.add_argument('--fmin', type=float, default=1e8)
    ap.add_argument('--fmax', type=float, default=1e16)
    ap.add_argument('--nf', type=int, default=65)
    ap.add_argument('--tau_target', type=float, default=T_UNIV_S)
    ap.add_argument('--out_csv', default='cert/DM/axion/scan/scan_grid.csv')
    ap.add_argument('--out_iso', default='cert/DM/axion/scan/iso_tau.json')
    ap.add_argument('--plot', action='store_true')
    args=ap.parse_args()

    os.makedirs(os.path.dirname(args.out_csv), exist_ok=True)

    coup_map  = get_couplings_map(load_json(args.couplings))
    const     = compute_constants(coup_map, load_json(args.met))

    Ms = logspace(args.mmin, args.mmax, args.nm)
    Fs = logspace(args.fmin, args.fmax, args.nf)

    with open(args.out_csv,'w',newline='') as f:
        w=csv.writer(f)
        w.writerow(['m_GeV','fa_GeV','Gamma_GeV','tau_s','BR_gg','BR_aa','g_agg_GeV^-1','g_agamma_GeV^-1'])
        for m in Ms:
            for fa in Fs:
                G, tau, BRa, BRg, gA, gG = widths_and_tau(m, fa, const)
                w.writerow([m, fa, G, tau, BRg, BRa, gG, gA])

    K = const['K']
    iso = []
    for m in Ms:
        fa_min = math.sqrt((K * (m**3) * args.tau_target) / HBAR_GEV_S)
        iso.append({'m_GeV': m, 'fa_min_GeV': fa_min})

    with open(args.out_iso,'w') as f:
        json.dump({
            'tau_target_s': args.tau_target,
            'K_const': K,
            'metrology': {k: const[k] for k in ('alpha_em','alpha_s','sin2_thetaW')},
            'couplings': {k: const[k] for k in ('C_WW','C_YY','C_GG','C_agamma')},
            'iso_curve': iso
        }, f, indent=2)

    if args.plot:
        try:
            import matplotlib.pyplot as plt
            import numpy as np
            grid = np.genfromtxt(args.out_csv, delimiter=',', names=True)
            iso_arr = load_json(args.out_iso)['iso_curve']
            m_line  = np.array([p['m_GeV'] for p in iso_arr])
            fa_line = np.array([p['fa_min_GeV'] for p in iso_arr])

            plt.figure()
            sc = plt.tricontourf(np.log10(grid['m_GeV']),
                                 np.log10(grid['fa_GeV']),
                                 np.log10(grid['tau_s']),
                                 levels=20)
            plt.colorbar(sc, label='log10 τ [s]')
            plt.plot(np.log10(m_line), np.log10(fa_line), 'k--', label=f'τ = {args.tau_target:.2e} s')
            plt.xlabel('log10 m_a [GeV]'); plt.ylabel('log10 f_a [GeV]')
            plt.legend()
            out_png = os.path.join(os.path.dirname(args.out_iso),'scan_plot.png')
            plt.savefig(out_png, dpi=200, bbox_inches='tight')
        except Exception as e:
            print("[WARN] plot skipped:", e)

    print(f"[SCAN] wrote {args.out_csv}")
    print(f"[ISO ] wrote {args.out_iso}")
    print("[INFO] K =", const['K'], " C_agamma=", const['C_agamma'], " C_GG=", const['C_GG'])
    print("[INFO] PASS region = above the iso curve (τ ≥ target).")

if __name__=='__main__':
    main()
