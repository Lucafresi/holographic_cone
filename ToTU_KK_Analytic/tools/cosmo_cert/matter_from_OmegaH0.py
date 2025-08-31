#!/usr/bin/env python3
import json, argparse

def jload(p): 
    with open(p,"r") as f: return json.load(f)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--met", required=True, help="cert/obs/metrology_cosmo.json")
    ap.add_argument("--omega", required=True, help="cert/obs/OmegaH0.json")
    ap.add_argument("--out", required=True, help="cert/obs/matter_EH.json")
    args = ap.parse_args()

    met   = jload(args.met)
    omega = jload(args.omega)

    H0_km_s_Mpc = float(omega["H0_km_s_Mpc"])
    Om          = float(omega.get("Omega_m0", 0.0))
    Ok          = float(omega.get("Omega_k0", 0.0))

    Mpc_km      = float(met["Mpc_km"])
    hbar_GeVs   = float(met["hbar_GeVs"])

    H0_sinv  = H0_km_s_Mpc / Mpc_km   # s^-1
    H0_GeV   = H0_sinv * hbar_GeVs    # GeV

    rho_m0_EH = 3.0 * Om * (H0_GeV**2)
    rho_k0_EH = 3.0 * Ok * (H0_GeV**2)

    out = {
        "schema_version": 1,
        "inputs": { "Omega_m0": Om, "Omega_k0": Ok, "H0_km_s_Mpc": H0_km_s_Mpc },
        "conversions": { "H0_s^-1": H0_sinv, "H0_GeV": H0_GeV },
        "rho_m0_EH": rho_m0_EH,
        "rho_k0_EH": rho_k0_EH
    }
    with open(args.out,"w") as f: json.dump(out,f,indent=2)
    print(f"[OK] wrote {args.out}")
    print(f"[OK] rho_m0_EH = {rho_m0_EH:.6e} ; rho_k0_EH = {rho_k0_EH:.6e}")

if __name__ == "__main__":
    main()
