import csv, os, sys, json
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
def run(case):
    base = os.path.join(ROOT, "cases", case, "data")
    rows = list(csv.DictReader(open(os.path.join(base,"orbifold_parities.csv"))))
    def par(name):
        for r in rows:
            if r["field"]==name: return r["UV"].strip()+r["IR"].strip()
        return None
    fail_reasons=[]
    # Conditions:
    # 1) Doublet survives: H_doublet_1 must be "++"
    if par("H_doublet_1")!="++": fail_reasons.append("Doublet wrongly projected: H_doublet_1")
    # 2) Triplet removed: H_triplet_1 must NOT be '++'
    if par("H_triplet_1")=="++": fail_reasons.append("Triplet not projected: H_triplet_1 ++")
    # 3) No extra U(1)': U1prime_field must NOT be '++'
    if par("U1prime_field")=="++": fail_reasons.append("Unwanted U(1)' survives: U1prime_field ++")
    PASS = (len(fail_reasons)==0)
    out = {"PASS": PASS}
    if not PASS: out["reasons"]=fail_reasons
    out_dir = os.path.join(ROOT, "certs", "kY", case)
    os.makedirs(out_dir, exist_ok=True)
    json.dump(out, open(os.path.join(out_dir,"orbifold_check.json"),"w"), indent=2)
    print(f"[ORB] {case}: PASS={PASS}" + ("" if PASS else f" | {fail_reasons}"))
if __name__=="__main__":
    run(sys.argv[1] if len(sys.argv)>1 else "sigma3")
