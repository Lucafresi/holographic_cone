#!/usr/bin/env python3
import json, math, os, hashlib
def h(s): import hashlib; return hashlib.sha256(s.encode()).hexdigest()
def rj(p): 
    with open(p,"r") as f: return json.load(f)
def wj(x,p):
    with open(p,"w") as f: json.dump(x,f,indent=2)
def main():
    os.makedirs("artifacts", exist_ok=True)
    rs = rj("sources/rs_ledger.json")
    hp = rj("sources/hodge_pao.json")
    L   = float(rs["L"]); zUV = float(rs["zUV_GeV^-1"]); zIR = float(rs["zIR_GeV^-1"])
    J = 0.5*(L**3)*(zUV**-2 - zIR**-2)  # GeV^2
    uTu = float(hp["uT_kappa_u"])
    fa  = math.sqrt(uTu*J)              # GeV
    payload = {"status":"PASS","J_GeV^2":J,"uT_kappa_u":uTu,"fa_GeV":fa,
               "hash":h(f"{L}|{zUV}|{zIR}|{uTu}") }
    wj(payload,"artifacts/fa.json")
    print("PASS:FA_BUILT"); print(f"J={J:.6e} GeV^2 ; f_a={fa:.6e} GeV")
if __name__=="__main__": main()
