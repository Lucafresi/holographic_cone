import csv, os, json, hashlib
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CASES = ["sigma1","sigma2","sigma3","sigma4"]

def sha256_of(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        while True:
            b=f.read(8192)
            if not b: break
            h.update(b)
    return h.hexdigest()

for case in CASES:
    base = os.path.join(ROOT,"cases",case,"data")
    path = os.path.join(base,"orbifold_parities.csv")
    par = {}
    with open(path,newline='') as f:
        r=csv.reader(f)
        for row in r:
            if not row or row[0].startswith("#"): continue
            name = row[0].strip()
            sign = row[1].strip().replace(" ","")
            par[name]=sign
    fails=[]
    # regole minime: solo Σ3 deve passare
    if par.get("H_triplet_1","--") == "++":
        fails.append("Triplet not projected: H_triplet_1 ++")
    if par.get("U1prime_field","--") == "++":
        fails.append("Unwanted U(1)' survives: U1prime_field ++")
    if par.get("H_doublet_1","--") != "++":
        fails.append("Doublet wrongly projected: H_doublet_1")
    PASS = (len(fails)==0)
    outdir = os.path.join(ROOT,"certs","kY",case)
    os.makedirs(outdir, exist_ok=True)
    out = {
      "PASS": bool(PASS),
      "fails": fails,
      "inputs_sha256": {"orbifold_parities.csv": sha256_of(path)}
    }
    with open(os.path.join(outdir,"orbifold_check.json"),"w") as f: json.dump(out,f,indent=2)
    print(f"[ORB] {case}: PASS={PASS}" + ("" if PASS else f" | FAILS={fails}"))
