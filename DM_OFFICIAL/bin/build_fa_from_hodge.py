#!/usr/bin/env python3
import json, os, math, hashlib, sys
def h(s): import hashlib; return hashlib.sha256(s.encode()).hexdigest()
def rj(p): 
    with open(p,"r") as f: return json.load(f)
def wj(x,p):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p,"w") as f: json.dump(x,f,indent=2)

def main():
    if len(sys.argv)!=3:
        print("usage: build_fa_from_hodge.py <sources/hodge_pao.json> <artifacts/fa.json>")
        sys.exit(2)
    src,out = sys.argv[1], sys.argv[2]
    try:
        dat = rj(src)
    except Exception as e:
        print(f"NO-GO: cannot_read_hodge ({e})"); sys.exit(1)
    # attesi: {"uTkappaU": ..., "J": ..., "units":"GeV"}
    if any(k not in dat for k in ("uTkappaU","J")):
        wj({"status":"NO-GO","reason":"missing_uTkappaU_or_J"},out)
        print("NO-GO: missing_uTkappaU_or_J"); sys.exit(1)
    uTu = float(dat["uTkappaU"]); J = float(dat["J"])
    if uTu<=0 or J<=0:
        wj({"status":"NO-GO","reason":"nonpositive_inputs"},out)
        print("NO-GO: nonpositive_inputs"); sys.exit(1)
    fa = math.sqrt(uTu*J)
    payload = {"status":"PASS","fa_GeV":fa,"hash":h(json.dumps({"fa":fa}))}
    wj(payload,out)
    print("PASS:FA_BUILT")
    print(f"fa = {fa:.6e} GeV")
if __name__=="__main__":
    main()
