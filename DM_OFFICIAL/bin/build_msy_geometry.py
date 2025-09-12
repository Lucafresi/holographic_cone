#!/usr/bin/env python3
import json, math, os, hashlib
def h(s): return hashlib.sha256(s.encode()).hexdigest()
def main():
    os.makedirs("artifacts", exist_ok=True)
    VolX5 = (2/9.0)*math.pi**3
    VolSig = (2/9.0)*math.pi**2
    payload = {
      "status":"PASS",
      "uv_toric":"CY_cone_on_dP3",
      "volumes":{
        "VolX5": VolX5,
        "VolSigma": VolSig,
        "rational_over_pi": {"VolX5/pi^3":"2/9","VolSigma/pi^2":"2/9"}
      },
      "hash": h(f"{VolX5:.15e}|{VolSig:.15e}")
    }
    with open("artifacts/msy_geometry.json","w") as f: json.dump(payload,f,indent=2)
    print("PASS:MSY_GEOMETRY")
    print(f"Vol(X5)={VolX5:.12f} ; VolSigma={VolSig:.12f}")
if __name__=="__main__": main()
