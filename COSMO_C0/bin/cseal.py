#!/usr/bin/env python3
import json, hashlib, platform, sys, time, os, pandas as pd
from mpmath import gammainc, gamma
def sha256(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for b in iter(lambda:f.read(65536), b''): h.update(b)
    return h.hexdigest()
obs=json.load(open("artifacts/C_obs_report.json"))
fit=json.load(open("artifacts/C_fit_report.json"))
N_SNe=len(pd.read_csv("data/sne.csv")) if os.path.exists("data/sne.csv") else 0
k=fit.get("dof_total",0); x=fit.get("chi2_total",0.0)
p=float(gammainc(k/2, x/2, float('inf'))/gamma(k/2)) if k>0 else None
files=["artifacts/H_curve.csv","artifacts/distances.csv","artifacts/C_obs_report.json","artifacts/C_fit_report.json"]
hashes={p:sha256(p) for p in files if os.path.exists(p)}
seal={
 "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
 "python": sys.version.split()[0],
 "packages": {
  "numpy": __import__('numpy').__version__,
  "pandas": __import__('pandas').__version__,
  "scipy": __import__('importlib').import_module('scipy').__version__ if __import__('importlib').util.find_spec('scipy') else None,
  "mpmath": __import__('mpmath').__version__
 },
 "C_OBS": obs, "C_FIT": fit, "p_value": p, "N_SNe": N_SNe,
 "hashes": hashes,
 "PASS_ALL": bool(obs.get("PASS_ETHERINGTON") and obs.get("PASS_LOWZ") and fit.get("PASS", False))
}
with open("artifacts/SEAL.json","w") as f: json.dump(seal,f,indent=2)
print(f"SEAL: PASS_ALL={seal['PASS_ALL']} p_value={seal['p_value']} N_SNe={seal['N_SNe']}")
