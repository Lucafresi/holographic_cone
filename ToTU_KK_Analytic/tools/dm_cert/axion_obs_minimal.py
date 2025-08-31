#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json, argparse, math, os, sys

HBAR_GEV_S = 6.582119569e-25  # ħ in GeV*s

def load_json(p):
    with open(p,"r") as f: return json.load(f)

def pick_float(d, *paths):
    """Ritorna il primo valore float trovato tra più path candidati (annidati)."""
    for path in paths:
        cur = d; ok = True
        for k in path:
            if isinstance(cur, dict) and k in cur:
                cur = cur[k]
            else:
                ok = False; break
        if ok:
            try: return float(cur)
            except: pass
    raise KeyError(str(paths))

def compute_couplings_from_Crot(ew, met, fa_GeV):
    # Costanti
    alpha_em = pick_float(met, ("couplings","alpha_em"), ("alpha_em",))
    alpha_s  = pick_float(met, ("couplings","alpha_s"),  ("alpha_s",))
    # C_rot
    C_agamma = pick_float(ew, ("C_rot","agamma"), ("C_rot","C_agamma"), ("C_rot","aγ"), ("C_rot","aA"))
    C_aGG    = pick_float(ew, ("C_rot","aGG"),    ("C_rot","C_aGG"))
    # Convenzioni: g_{aγγ} = (α_em / 2π) * C_agamma / f_a, g_{agg} = (α_s / 2π) * C_aGG / f_a
    two_pi = 2.0*math.pi
    g_agamma = (alpha_em / two_pi) * C_agamma / fa_GeV
    g_agg    = (alpha_s  / two_pi) * C_aGG    / fa_GeV
    return g_agamma, g_agg, C_agamma, C_aGG

def main():
    ap = argparse.ArgumentParser(description="Osservabili minimi axion: Γ(a→γγ), Γ(a→gg) con soglia hadron.")
    ap.add_argument("--ew", required=True, help="JSON couplings (da axion_to_photon_gluon.py).")
    ap.add_argument("--ma_GeV", type=float, required=True, help="Massa axion in GeV.")
    ap.add_argument("--met", default="cert/DM/metrology.json", help="Metrologia (α_em, α_s, m_pi0).")
    ap.add_argument("--fa_file", default=None, help="(fallback) JSON con {f_a_GeV}.")
    ap.add_argument("--out", default="cert/DM/axion/axion_obs_min.json")
    args = ap.parse_args()

    # Carica input
    ew  = load_json(args.ew)
    met = load_json(args.met) if os.path.exists(args.met) else {}

    # 1) Prova a leggere direttamente g_agamma/g_agg in tutti i formati comuni
    g_agamma = None; g_agg = None; note_build = []
    try:
        g_agamma = pick_float(ew, ("g","agamma_GeV^-1"), ("g_agamma_GeV^-1",), ("g","agamma"), ("g_agamma",))
        g_agg    = pick_float(ew, ("g","agg_GeV^-1"),    ("g_agg_GeV^-1",),   ("g","agg"),    ("g_agg",))
        note_build.append("g presi direttamente da file EW")
    except KeyError:
        # 2) Ricostruisci da C_rot + f_a
        fa_GeV = None
        # prova dentro ew
        try: fa_GeV = pick_float(ew, ("inputs","fa_GeV"), ("fa_GeV",))
        except KeyError:
            # prova da --fa_file
            if args.fa_file and os.path.exists(args.fa_file):
                fa = load_json(args.fa_file)
                fa_GeV = pick_float(fa, ("f_a_GeV",),)
        if fa_GeV is None:
            print("[ERR] Couplings g non presenti e f_a non disponibile per ricostruirli.", file=sys.stderr)
            sys.exit(2)
        g_agamma, g_agg, C_agamma, C_aGG = compute_couplings_from_Crot(ew, met, fa_GeV)
        note_build.append("g ricostruiti da C_rot + f_a")

    # Parametri di massa e soglia adronica
    m_a = float(args.ma_GeV)
    m_pi0 = 0.1349768
    if met:
        try: m_pi0 = pick_float(met, ("masses","m_pi0_GeV"), ("m_pi0_GeV",))
        except KeyError: pass
    m_thr_gg = 2.0 * m_pi0

    # Larghezze
    Gamma_aa = (g_agamma**2) * (m_a**3) / (64.0 * math.pi)
    Gamma_gg = (g_agg**2)    * (m_a**3) / (64.0 * math.pi) if m_a >= m_thr_gg else 0.0

    Gamma_tot = Gamma_aa + Gamma_gg
    tau_s = (HBAR_GEV_S / Gamma_tot) if Gamma_tot > 0 else float("inf")
    BR_aa = Gamma_aa / Gamma_tot if Gamma_tot>0 else 1.0
    BR_gg = Gamma_gg / Gamma_tot if Gamma_tot>0 else 0.0

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    out = {
        "schema_version": 1,
        "inputs": {
            "ma_GeV": m_a,
            "metrology_file": args.met if os.path.exists(args.met) else None,
            "fa_file": args.fa_file if args.fa_file else None
        },
        "couplings": {"g_agamma_GeV^-1": g_agamma, "g_agg_GeV^-1": g_agg},
        "widths_GeV": {"Gamma_aa": Gamma_aa, "Gamma_gg": Gamma_gg, "Gamma_tot": Gamma_tot},
        "branchings": {"BR_aa": BR_aa, "BR_gg": BR_gg},
        "lifetime_s": tau_s,
        "thresholds": {"m_pi0_GeV": m_pi0, "m_thr_gg_GeV": m_thr_gg, "gg_open": (m_a>=m_thr_gg)},
        "notes": "; ".join(note_build) + ". Soglia gg: Γ_gg=0 per m_a<2m_pi0."
    }
    with open(args.out,"w") as f: json.dump(out, f, indent=2)

    print(f"[D3-OBS] wrote {args.out}")
    print(f"  Gamma_tot = {Gamma_tot:.6e} GeV  | BR(γγ)={BR_aa:.3f}, BR(gg)={BR_gg:.3f}")
