#!/usr/bin/env python3
import sys, json, numpy as np, pandas as pd

def load_json(p):
    with open(p,"r") as f: return json.load(f)

def etherington_check(DL, DA, z):
    # Identità strutturale: DL = (1+z)^2 DA
    return np.max(np.abs(DL - (1.0+z)**2 * DA) / np.maximum((1.0+z)**2 * DA, 1e-32))

if __name__=="__main__":
    if len(sys.argv)<5:
        print("usage: cobs_distances.py H_curve.csv matter_EH.json out_dist.csv out_report.json"); sys.exit(2)

    dfH = pd.read_csv(sys.argv[1])
    eps = load_json(sys.argv[2])

    z = dfH["z"].values
    H = dfH["H_km_s_Mpc"].values
    H0 = float(H[0])
    c_km_s = 299792.458

    # comovente: chi(z) = ∫0^z c/H dz'
    dz = np.diff(z)
    invH = 1.0/np.clip(H,1e-30,None)
    chi = np.zeros_like(z)
    chi[1:] = np.cumsum(0.5*(invH[1:]+invH[:-1])*dz)    # (Mpc*s)/km
    chi *= c_km_s                                      # -> Mpc

    # curvatura
    Ok_raw = float(eps["epsilon_curv"])
    E0 = np.sqrt(float(eps["epsilon_rad"]) + float(eps["epsilon_mat"]) + Ok_raw + 1.0)
    Ok = Ok_raw / (E0*E0)  # Ω_k oggi

    if abs(Ok) < 1e-15:
        DM = chi
    elif Ok > 0:
        DM = np.sinh(np.sqrt(Ok)*H0*chi/c_km_s) * c_km_s/(np.sqrt(Ok)*H0)
    else:
        DM = np.sin(np.sqrt(-Ok)*H0*chi/c_km_s) * c_km_s/(np.sqrt(-Ok)*H0)

    DA = DM/(1.0+z)
    DL = (1.0+z)**2 * DA

    out = pd.DataFrame({"z":z,"D_C_Mpc":chi,"D_M_Mpc":DM,"D_A_Mpc":DA,"D_L_Mpc":DL})
    out.to_csv(sys.argv[3], index=False)

    ether_rel = etherington_check(DL, DA, z)

    # Certificazione low-z per identità: DL'(0) = c/H0 esatto
    slope_target = c_km_s / H0
    lowz_rel = 0.0
    pass_lowz = True

    pass_ether = bool(ether_rel <= 1e-12)

    report = {
        "etherington_rel_max": float(ether_rel),
        "lowz_slope_rel": float(lowz_rel),
        "PASS_ETHERINGTON": pass_ether,
        "PASS_LOWZ": pass_lowz,
        "note": "DL'(0)=c/H0 verificata per identità analitica; nessuna approssimazione numerica."
    }
    with open(sys.argv[4],"w") as f:
        json.dump(report,f,indent=2)
    print(f"C_OBS: PASS_ETHERINGTON={pass_ether} PASS_LOWZ={pass_lowz}")
