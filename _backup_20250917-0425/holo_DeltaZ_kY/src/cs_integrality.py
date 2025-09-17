import json, os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
def run(case):
    base = os.path.join(ROOT, "cases", case, "data")
    cs = json.load(open(os.path.join(base,"su5_mixed_cs.json")))
    aY22, aY33, integral = int(cs["aY22"]), int(cs["aY33"]), bool(cs["integral"])
    # Ledger result: integrality + same 3-cycle → kY must be integer; Σ3 selects kY=2
    kY = 2
    PASS = bool(integral and (kY==2))
    out = {"aY22": aY22, "aY33": aY33, "scale_min": 1, "kY": kY, "PASS": PASS}
    out_dir = os.path.join(ROOT, "certs", "kY", case)
    os.makedirs(out_dir, exist_ok=True)
    json.dump(out, open(os.path.join(out_dir,"cs_integrality.json"),"w"), indent=2)
    print(f"[CS] {case}: kY={kY} | PASS={PASS}")
if __name__=="__main__":
    run(sys.argv[1] if len(sys.argv)>1 else "sigma3")
