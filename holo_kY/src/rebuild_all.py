import os, sys, subprocess, json, hashlib
ROOT=os.path.dirname(os.path.dirname(__file__))
CASES=["sigma1","sigma2","sigma3","sigma4"]
def sha(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for b in iter(lambda:f.read(1<<16), b''): h.update(b)
    return h.hexdigest()
def run_case(case):
    print(f"\n=== CASE {case} ===")
    dcase=os.path.join(ROOT,"cases",case,"data")
    ocase=os.path.join(ROOT,"certs","kY",case)
    os.makedirs(ocase, exist_ok=True)
    dtop=os.path.join(ROOT,"data")
    os.makedirs(dtop, exist_ok=True)
    for fn in ["su5_mixed_cs.json","charges_matrix.json","orbifold_parities.csv"]:
        src=os.path.join(dcase,fn); dst=os.path.join(dtop,fn)
        if os.path.exists(dst): os.remove(dst)
        if not os.path.exists(src): raise FileNotFoundError(src)
        with open(src,'rb') as i, open(dst,'wb') as o: o.write(i.read())
    inputs=[os.path.join(ROOT,"data","charges_matrix.json"),
            os.path.join(ROOT,"data","su5_mixed_cs.json"),
            os.path.join(ROOT,"data","orbifold_parities.csv")]
    audit={"inputs":{os.path.basename(p): sha(p) for p in inputs}}
    with open(os.path.join(ocase,"input_hashes.json"),"w") as f: json.dump(audit,f,indent=2)
    for script in ["snf_hnf.py","cs_integrality.py","orbifold_check.py"]:
        print(">>", script)
        subprocess.check_call([sys.executable, os.path.join(ROOT,"src",script)])
    for fn in ["snf.json","rank.txt","cs_integrality.json","orbifold_check.json"]:
        src=os.path.join(ROOT,"certs","kY",fn)
        if os.path.exists(src):
            with open(src,'rb') as i, open(os.path.join(ocase,fn),'wb') as o: o.write(i.read())
            os.remove(src)
    print(f"=== CASE {case} DONE ===")
if __name__=="__main__":
    for c in CASES: run_case(c)
    print("\nALL CASES REBUILT.")
