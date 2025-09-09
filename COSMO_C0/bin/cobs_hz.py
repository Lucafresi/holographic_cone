#!/usr/bin/env python3
import sys, json, numpy as np, pandas as pd

def load_json(p):
    with open(p,"r") as f: return json.load(f)

def H_curve(H_L_SI, eps):
    z = np.linspace(0.0, 2.5, 2001)
    rad = eps["epsilon_rad"]*(1+z)**4
    mat = eps["epsilon_mat"]*(1+z)**3
    curv = eps["epsilon_curv"]*(1+z)**2
    E = np.sqrt(rad+mat+curv+1.0)
    H_SI = H_L_SI*E
    Mpc_km = 3.085677581491367e19
    H_km_s_Mpc = H_SI*Mpc_km
    df = pd.DataFrame({"z":z,"H_SI":H_SI,"H_km_s_Mpc":H_km_s_Mpc})
    return df

if __name__=="__main__":
    if len(sys.argv)<4:
        print("usage: cobs_hz.py Lambda4.json matter_EH.json out.csv"); sys.exit(2)
    lam = load_json(sys.argv[1])
    eps = load_json(sys.argv[2])
    df = H_curve(lam["H_L_SI"], eps)
    df.to_csv(sys.argv[3], index=False)
    H0 = float(df.loc[df["z"].sub(0).abs().idxmin(),"H_km_s_Mpc"])
    print(f"H0_km_s_Mpc={H0:.6f}")
