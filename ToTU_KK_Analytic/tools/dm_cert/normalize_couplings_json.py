#!/usr/bin/env python3
import json, sys
from fractions import Fraction

def as_rat_str(x):
    # converte 36 -> "36/1", 10.0 -> rationals "10/1"
    if isinstance(x,(int,float)):
        f = Fraction(x).limit_denominator()
        return f"{f.numerator}/{f.denominator}"
    if isinstance(x,str):
        s = x.strip()
        if "/" in s: return s
        try:
            f = Fraction(float(s)).limit_denominator()
            return f"{f.numerator}/{f.denominator}"
        except Exception:
            pass
    raise ValueError(f"valore non interpretabile: {x!r}")

def main(path):
    with open(path,"r") as f: d = json.load(f)
    C = d.get("C_integer")
    if C is None:
        # fallback da chiavi alternative
        src = None
        for k in ("g_hat","C","C_hat"):
            if k in d:
                src = d[k]; break
        if src is None:
            print("[ERR] nessuna tra C_integer / g_hat / C / C_hat", file=sys.stderr)
            sys.exit(1)
        C = {ch: as_rat_str(val) for ch,val in src.items()}
        d["C_integer"] = C
    with open(path,"w") as f: json.dump(d,f,indent=2)
    print(f"[OK] normalized {path}: C_integer present with keys {sorted(d['C_integer'].keys())}")

if __name__=="__main__":
    if len(sys.argv)!=2:
        print("usage: normalize_couplings_json.py <path.json>", file=sys.stderr); sys.exit(2)
    main(sys.argv[1])
