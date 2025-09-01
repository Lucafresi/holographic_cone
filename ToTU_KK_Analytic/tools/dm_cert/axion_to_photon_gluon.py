#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
axion_to_photon_gluon.py
- Legge i coefficienti C in base (aGG, aWW, aYY, aXXX, agrav) dal ledger.
- Esegue la rotazione EWSB: (aγγ, aγZ, aZZ).
- Se è noto f_a (via --fa_GeV o --fa_file) calcola g_{aγγ} e g_{agg}.
Formule:
  C_{aγγ} =  C_{aYY} cos^2θ_W + C_{aWW} sin^2θ_W
  C_{aγZ} = 2 sinθ_W cosθ_W ( C_{aWW} - C_{aYY} )
  C_{aZZ} =  C_{aYY} sin^2θ_W + C_{aWW} cos^2θ_W
Coupling fisici:
  g_{aγγ} = (α_EM / (2π f_a)) * C_{aγγ}
  g_{agg} = (α_s  / (2π f_a)) * C_{aGG}
"""
from __future__ import annotations
import json, argparse, math, sys
from fractions import Fraction

def load_json(p: str):
    with open(p, "r") as f:
        return json.load(f)

def rational_str_to_float(s: str) -> float:
    s = str(s).strip()
    if "/" in s:
        num, den = s.split("/", 1)
        return float(Fraction(int(num), int(den)))
    return float(s)

def ensure_C_integer(d: dict) -> dict:
    """
    Ritorna un dict con chiave 'C_integer' (stringhe razionali "num/den").
    Se manca, prova fallback su 'g_hat', 'C', 'C_hat'.
    """
    if "C_integer" in d:
        return d
    src = None
    for k in ("g_hat", "C", "C_hat"):
        if k in d:
            src = d[k]
            break
    if src is None:
        print("[ERR] Nessuna delle chiavi {C_integer, g_hat, C, C_hat} presente nel file input.", file=sys.stderr)
        sys.exit(1)
    C_int = {}
    for ch, val in src.items():
        try:
            f = float(val)
            frac = Fraction(f).limit_denominator(10**6)
            C_int[ch] = f"{frac.numerator}/{frac.denominator}"
        except Exception:
            s = str(val).strip()
            if "/" in s:
                C_int[ch] = s
            else:
                raise
    d["C_integer"] = C_int
    return d

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True, help="JSON: couplings dal ledger (C_integer o fallback)")
    ap.add_argument("--met", required=True, help="JSON metrologia (alphaEM_inv, alpha_s_mZ, sin2thetaW_mZ)")
    ap.add_argument("--fa_GeV", type=float, default=None, help="Valore f_a in GeV (opz.)")
    ap.add_argument("--fa_file", default=None, help="JSON con chiave f_a_GeV (opz.)")
    ap.add_argument("--out", required=True, help="Output JSON ruotato")
    args = ap.parse_args()

    coup = ensure_C_integer(load_json(args.inp))
    met  = load_json(args.met)

    C = coup["C_integer"]
    def getC(key: str) -> float:
        s = C.get(key, "0/1")
        return rational_str_to_float(s)

    C_aGG  = getC("aGG")
    C_aWW  = getC("aWW")
    C_aYY  = getC("aYY")
    C_aXXX = getC("aXXX")
    C_agrav= getC("agrav")

    alphaEM_inv = float(met.get("alphaEM_inv", 137.035999084))
    alpha_s     = float(met.get("alpha_s_mZ", 0.1181))
    sin2W       = float(met.get("sin2thetaW_mZ", 0.23122))
    alphaEM     = 1.0 / alphaEM_inv
    sW = math.sqrt(sin2W)
    cW = math.sqrt(max(0.0, 1.0 - sin2W))

    C_agamma = C_aYY*(cW**2) + C_aWW*(sW**2)
    C_agZ    = 2.0*sW*cW*(C_aWW - C_aYY)
    C_aZZ    = C_aYY*(sW**2) + C_aWW*(cW**2)

    f_a = None
    if args.fa_GeV is not None:
        f_a = float(args.fa_GeV)
    elif args.fa_file:
        fobj = load_json(args.fa_file)
        if "f_a_GeV" not in fobj:
            print("[ERR] fa_file non contiene 'f_a_GeV'", file=sys.stderr); sys.exit(1)
        f_a = float(fobj["f_a_GeV"])

    out = {
        "schema_version": 1,
        "inputs": {
            "source": args.inp,
            "metrology": args.met,
            "alphaEM_inv": alphaEM_inv,
            "alpha_s_mZ": alpha_s,
            "sin2thetaW_mZ": sin2W
        },
        "C_integer": coup["C_integer"],
        "C_rot": {
            "aGG": C_aGG,
            "aγγ": C_agamma,
            "aγZ": C_agZ,
            "aZZ": C_aZZ,
            "aWW": C_aWW,
            "aYY": C_aYY,
            "aXXX": C_aXXX,
            "agrav": C_agrav
        }
    }

    if f_a is not None:
        two_pi_f = 2.0*math.pi*f_a
        g_agamma = (alphaEM * C_agamma) / two_pi_f
        g_agg    = (alpha_s  * C_aGG)   / two_pi_f
        out["fa_GeV"] = f_a
        out["g_phys_GeV^-1"] = {"g_agamma": g_agamma, "g_agg": g_agg}

    with open(args.out, "w") as f:
        json.dump(out, f, indent=2)

    print(f"[D3] wrote {args.out}")
    print(f"[D3] C_rot: C_agamma={C_agamma:.6g}, C_aGG={C_aGG:g}")
    if f_a is not None:
        print(f"[D3] g_agamma={g_agamma:.6e} GeV^-1  (fa={f_a:.3e} GeV)")
        print(f"[D3] g_agg   ={g_agg:.6e} GeV^-1")

if __name__ == "__main__":
    main()
