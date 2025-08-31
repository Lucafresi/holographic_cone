#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse, csv, json, math, os
from typing import List, Tuple

HBAR_GeVs = 6.582119569e-25      # ħ [GeV·s]
MPC_KM    = 3.085677581491367e19 # 1 Mpc in km
C_KM_S    = 299792.458

def loadj(p): 
    with open(p,"r") as f: 
        return json.load(f)

def _pick_z_col(cols):
    if "z" in cols: return "z"
    for c in cols:
        if c.strip().lower() == "z": return c
    return cols[0]

def _pick_H_mode(cols):
    if "H_km_s_Mpc" in cols: return ("H_km_s_Mpc", "km")
    if "H_GeV"      in cols: return ("H_GeV", "GeV")
    if "E"          in cols: return ("E", "E")
    raise KeyError(f"Nessuna colonna H riconosciuta. Header={cols}")

def read_Hcurve_csv(path_csv: str):
    with open(path_csv, "r") as f:
        r = csv.DictReader(f)
        cols = r.fieldnames or []
        zc = _pick_z_col(cols)
        hc, mode = _pick_H_mode(cols)
        z, H_km = [], []
        rows = list(r)
        if len(rows) == 0:
            raise ValueError("CSV vuoto.")
        # Se serve H0, prendilo da JSON (se presente), altrimenti dallo stesso CSV (z≈0)
        # qui lasciamo la conversione a dopo
        return rows, zc, hc, mode

def H_to_km_per_s_Mpc(value, mode, H0_km=None, H0_GeV=None):
    if mode == "km":
        return float(value)
    elif mode == "GeV":
        # H[GeV] -> s^-1 -> km/s/Mpc
        H_s = float(value) / HBAR_GeVs
        return H_s * MPC_KM
    elif mode == "E":
        if H0_km is not None:
            return float(value) * H0_km
        elif H0_GeV is not None:
            H0_s = H0_GeV / HBAR_GeVs
            return float(value) * (H0_s * MPC_KM)
        else:
            raise ValueError("Serve H0 (km/s/Mpc o GeV) per convertire E(z).")
    else:
        raise ValueError("Modo H sconosciuto.")

def trapz(x: List[float], y: List[float]) -> float:
    s = 0.0
    for i in range(len(x)-1):
        dx = x[i+1]-x[i]
        s += 0.5*dx*(y[i]+y[i+1])
    return s

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--Hcurve_json", default="cert/cosmo/C_obs/H_curve.json")
    ap.add_argument("--Hcurve_csv",  default="cert/cosmo/C_obs/H_curve.csv")
    ap.add_argument("--out_json",    default="cert/cosmo/C_obs/distances.json")
    ap.add_argument("--out_csv",     default="cert/cosmo/C_obs/distances.csv")
    args = ap.parse_args()

    meta = loadj(args.Hcurve_json)
    met  = meta.get("metrology", {})
    c_km_s = float(met.get("c_km_s", C_KM_S))

    # Prova a leggere H0 dal JSON in varie forme
    H0_km = meta.get("H0_km_s_Mpc", None)
    H0_GeV = meta.get("H0_GeV", None)
    if H0_km is not None: H0_km = float(H0_km)
    if H0_GeV is not None: H0_GeV = float(H0_GeV)

    # Leggi CSV e autodetect colonne
    rows, zc, hc, mode = read_Hcurve_csv(args.Hcurve_csv)
    # Se manca H0 e il CSV ha z=0 e una colonna H (GeV o km/s/Mpc), stimiamo da lì
    if H0_km is None and H0_GeV is None:
        # cerca la riga con z più vicino a 0
        z0row = min(rows, key=lambda r: abs(float(r[zc])))
        z0 = float(z0row[zc])
        if abs(z0) < 1e-9:
            v = float(z0row[hc])
            if mode == "km":
                H0_km = v
            elif mode == "GeV":
                H0_km = H_to_km_per_s_Mpc(v, "GeV")
            # se mode == "E" e z=0 ⇒ E(0)=1, ma senza H0 non risolviamo: lasciamo None
        # se ancora None, pace: gestiremo caso E con errore più sotto

    # Converte tutta la curva H(z) in km/s/Mpc
    z, H = [], []
    for r in rows:
        zi = float(r[zc])
        Hi = H_to_km_per_s_Mpc(r[hc], mode, H0_km=H0_km, H0_GeV=H0_GeV)
        z.append(zi); H.append(Hi)
    assert all(z[i] <= z[i+1] for i in range(len(z)-1)), "z non monotono"

    # Se H0 resta ignoto ed eravamo nel mode=E, ora possiamo fissarlo da z=0 (E(0)=1)
    if H0_km is None and mode == "E":
        # cerca la riga con z ~ 0 e E ~ 1 e usa H(z=0) come H0
        i0 = min(range(len(z)), key=lambda i: abs(z[i]))
        H0_km = H[i0]

    # Distanze (flat o curvo) — prendi Ω_k da meta se presente
    eps  = meta.get("eps", {})
    Omk  = float(eps.get("curv", 0.0))
    # comoving integral: D_C(z) = c ∫ dz'/H(z') (in Mpc se H in km/s/Mpc e c in km/s)
    DC = [0.0]
    for i in range(1, len(z)):
        zseg = z[:i+1]
        yseg = [1.0/Hi for Hi in H[:i+1]]
        integ = trapz(zseg, yseg)
        DC.append(c_km_s * integ)

    if abs(Omk) < 1e-15:
        DM = DC[:]
    else:
        DM = []
        for Dc in DC:
            chi = math.sqrt(abs(Omk)) * (H0_km * Dc / c_km_s)
            if Omk > 0:
                DM.append((c_km_s/H0_km) * math.sinh(chi)/math.sqrt(Omk))
            else:
                DM.append((c_km_s/H0_km) * math.sin(chi)/math.sqrt(abs(Omk)))

    DA, DL, MU = [], [], []
    for zi, DMi in zip(z, DM):
        DAi = DMi / (1.0 + zi)
        DLi = DMi * (1.0 + zi)
        DA.append(DAi); DL.append(DLi)
        MU.append(5.0*math.log10(max(DLi, 1e-300)) + 25.0)

    # Etherington
    max_rel_err = 0.0
    for zi, DAi, DLi in zip(z, DA, DL):
        lhs = DLi
        rhs = (1.0+zi)**2 * DAi
        rel = abs(lhs - rhs)/max(1.0, abs(lhs), abs(rhs))
        if rel > max_rel_err: max_rel_err = rel
    reciprocity_pass = (max_rel_err < 1e-10)

    # low-z check: D_L ~ (c/H0) z
    idx = next((i for i,zi in enumerate(z) if zi>0), 1 if len(z)>1 else 0)
    z1 = z[idx]
    slope_est = DL[idx] / z1 if z1 != 0 else float("nan")
    slope_th  = c_km_s / H0_km if H0_km else float("nan")
    slope_rel = abs(slope_est - slope_th)/slope_th if math.isfinite(slope_est) else float("inf")
    lowz_pass = (slope_rel < 1e-3) if math.isfinite(slope_rel) else False

    os.makedirs(os.path.dirname(args.out_csv), exist_ok=True)
    with open(args.out_csv, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["z","H_km_s_Mpc","D_C_Mpc","D_M_Mpc","D_A_Mpc","D_L_Mpc","mu_mag"])
        for zi, Hi, DCi, DMi, DAi, DLi, mui in zip(z, H, DC, DM, DA, DL, MU):
            w.writerow([f"{zi:.12g}", f"{Hi:.12g}", f"{DCi:.12g}", f"{DMi:.12g}",
                        f"{DAi:.12g}", f"{DLi:.12g}", f"{mui:.12g}"])

    out = {
        "schema_version": 1,
        "inputs": {"Hcurve_json": args.Hcurve_json, "Hcurve_csv": args.Hcurve_csv},
        "H0_km_s_Mpc": H0_km, 
        "eps": meta.get("eps", {}),
        "metrology": { "c_km_s": c_km_s },
        "checks": {
            "etherington_max_rel_err": max_rel_err,
            "etherington_pass": reciprocity_pass,
            "lowz_slope_rel_err": slope_rel,
            "lowz_pass": lowz_pass
        },
        "pass": reciprocity_pass and lowz_pass
    }
    os.makedirs(os.path.dirname(args.out_json), exist_ok=True)
    with open(args.out_json, "w") as f:
        json.dump(out, f, indent=2)

    print(f"[C_obs/dist] wrote {args.out_csv} and {args.out_json}")
    print(f"[C_obs/dist] Etherington pass={reciprocity_pass} (max_rel_err={max_rel_err:.3e}); "
          f"low-z slope rel.err={slope_rel:.3e} (pass={lowz_pass})")

if __name__ == "__main__":
    main()
