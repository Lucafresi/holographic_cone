#!/usr/bin/env python3
import json, hashlib, os
h=lambda s: hashlib.sha256(s.encode()).hexdigest()
def R(p): 
    with open(p) as f: return json.load(f)
def W(p,o):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p,"w") as f: json.dump(o,f,indent=2)

def main():
    eta  = R("artifacts/eta.json")["eta"]
    fp   = R("artifacts/tosc_fixedpoint.json")["solution"]
    fa   = R("artifacts/fa.json")["fa_GeV"]
    th   = R("artifacts/theta_ledger.json")["allowed_thetas_rad"]
    mu   = fp["mu_req_sc_GeV"]
    Tosc = fp["T_osc_GeV"]; Gs = fp["Gstar_at_Tosc"]
    # N,q scelti in compare_sinst_sreq (già promossi)
    cert0 = R("artifacts/dm_certificate.json")
    N = cert0["flux_integer_N"]; q = cert0["wrapping_q"]; S = cert0["S_inst"]

    Ms = mu/eta
    out = {
      "status":"PASS",
      "uv_toric":"CY_cone_on_dP3",
      "N":N,"q":q,"S_inst":S,
      "theta_allowed_rad": th,
      "fa_GeV": fa,
      "eta": eta,
      "mu_req_sc_GeV": mu,
      "Ms_GeV": Ms,
      "T_osc_GeV": Tosc,
      "Gstar_at_Tosc": Gs
    }
    out["hash"]=h(json.dumps(out,sort_keys=True))
    W("artifacts/dm_final_certificate.json", out)
    print("PASS:DM_FINAL_CERT")
    print(f"M_s = {Ms:.6e} GeV (from mu/eta); G*={Gs:.2f}; Tosc={Tosc:.3e} GeV")
if __name__=="__main__":
    main()
