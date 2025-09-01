#!/usr/bin/env python3
import json, argparse
def jload(p): 
    with open(p,"r") as f: return json.load(f)
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--met", required=True)    # cert/obs/metrology_cosmo.json
    ap.add_argument("--omega", required=True)  # cert/obs/OmegaH0.json
    ap.add_argument("--out", required=True)    # cert/cosmo/Lambda4_obs.json
    args = ap.parse_args()

    met   = jload(args.met)
    omega = jload(args.omega)

    H0_km_s_Mpc = float(omega["H0_km_s_Mpc"])
    Om          = float(omega.get("Omega_m0", 0.0))
    Ok          = float(omega.get("Omega_k0", 0.0))
    Ol          = 1.0 - Om - Ok

    Mpc_km      = float(met["Mpc_km"])
    hbar_GeVs   = float(met["hbar_GeVs"])

    H0_sinv  = H0_km_s_Mpc / Mpc_km
    H0_GeV   = H0_sinv * hbar_GeVs
    Lambda4_EH = 3.0 * Ol * (H0_GeV**2)

    out = {
      "schema_version": 1,
      "inputs": {"Omega_m0": Om, "Omega_k0": Ok, "Omega_L0": Ol, "H0_km_s_Mpc": H0_km_s_Mpc},
      "conversions": {"H0_s^-1": H0_sinv, "H0_GeV": H0_GeV},
      "Lambda4_EH": Lambda4_EH
    }
    with open(args.out,"w") as f: json.dump(out,f,indent=2)
    print(f"[OK] wrote {args.out}")
    print(f"[OK] Λ4_EH = {Lambda4_EH:.6e}")
if __name__=="__main__": main()
