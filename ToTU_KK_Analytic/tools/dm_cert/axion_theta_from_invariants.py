#!/usr/bin/env python3
import json, argparse, math

def load(p):
    with open(p,"r") as f: return json.load(f)

def as_int(x):
    if isinstance(x, bool): return int(x)
    if isinstance(x, (int,)): return int(x)
    if isinstance(x, (float,)): return int(round(x))
    if isinstance(x, str):
        s = x.strip()
        if '/' in s:
            num, den = s.split('/',1)
            return int(round(float(num)/float(den)))
        return int(round(float(s)))
    raise TypeError(f"Valore non interpretabile come intero: {x!r}")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--Lambda4", required=True, help="cert/cosmo/Lambda4.json (deve contenere Q_inv)")
    ap.add_argument("--coup",    required=True, help="cert/DM/axion/axion_couplings.json (C_integer.aGG)")
    ap.add_argument("--out",     required=True, help="output JSON")
    args = ap.parse_args()

    Lam = load(args.Lambda4)
    C   = load(args.coup)

    Qin = Lam.get("Q_inv", Lam.get("Q_inv_float"))
    if Qin is None:
        raise KeyError("Lambda4.json non contiene Q_inv/Q_inv_float; rigenera con lambda4_from_discrete.py")
    Qin = as_int(Qin)

    Cin = C.get("C_integer", C.get("C_hat"))
    if Cin is None or "aGG" not in Cin:
        raise KeyError("Couplings non contiene 'C_integer.aGG' (rigenera axion_couplings.json)")
    Ndw = abs(as_int(Cin["aGG"]))
    if Ndw <= 0: raise ValueError("N_dw=|C_aGG| deve essere > 0.")

    theta_i = 2*math.pi*((Qin % Ndw)/Ndw)

    out = {
        "schema_version": 1,
        "inputs": { "Q_inv": Qin, "N_dw": Ndw },
        "theta_i_rad": theta_i,
        "theta_i_over_pi": theta_i/math.pi,
        "mapping_note": "theta_i = 2π*(Q_inv mod N_dw)/N_dw; N_dw=|C_aGG|."
    }
    with open(args.out,"w") as f: json.dump(out, f, indent=2)
    print(f"[D5] wrote {args.out}")
    print(f"[D5] theta_i = {theta_i:.6e} rad  (= {theta_i/math.pi:.6e} * pi);  N_dw={Ndw}, Q_inv={Qin}")

if __name__=="__main__":
    main()
