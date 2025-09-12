#!/usr/bin/env python3
import json, math, os, hashlib
def h(s): return hashlib.sha256(s.encode()).hexdigest()
def R(p): 
    with open(p,"r") as f: return json.load(f)
def W(x,p):
    with open(p,"w") as f: json.dump(x,f,indent=2)

def main():
    os.makedirs("artifacts", exist_ok=True)
    th = R("artifacts/theta_ledger.json")["allowed_thetas_rad"]
    fa = R("artifacts/fa.json")["fa_GeV"]
    S  = R("artifacts/sinst_vs_sreq.json")["chosen"]["S_inst"]
    K  = R("artifacts/cosmo_kernel.json")["cosmo_kernel"]["constants"]["Kmis_numeric"]
    Om = R("sources/omega_target.json")["Omega_target"]

    # griglia discreta di G* (SM puro, finestra ragionevole intorno alla soglia d'oscillazione)
    Gstars = [20,30,40,50,60,70,80,90]
    out = {"status":"PASS","inputs":{"fa_GeV":fa,"S_inst":S,"Kmis":K,"Omega_target":Om},
           "grid":[]}
    for g in Gstars:
        for t in th:
            if t==0.0: 
                out["grid"].append({"G*":g,"theta":t,"mu_required_GeV": None,"reason":"theta_zero_leads_to_Omega_zero"})
                continue
            mu = Om / (K * g * (t**2) * (fa**1.5) * math.exp(-S/4.0))
            out["grid"].append({"G*":g,"theta":t,"mu_required_GeV": mu})
    out["hash"]=h(json.dumps(out,sort_keys=True))
    W(out,"artifacts/mu_required.json")
    print("PASS:MU_REQUIRED")
    print(f"grid entries: {len(out['grid'])}  (|theta|={len(th)}, |G*|={len(Gstars)})")
if __name__=="__main__": main()
