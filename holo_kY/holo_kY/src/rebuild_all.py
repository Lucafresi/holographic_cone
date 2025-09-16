import os, sys, subprocess, json, hashlib
ROOT = os.path.dirname(os.path.dirname(__file__))
def run(py):
    print(">>", py); subprocess.check_call([sys.executable, os.path.join(ROOT, "src", py)])
def sha(path):
    h=hashlib.sha256(); 
    with open(path,'rb') as f:
        for b in iter(lambda: f.read(1<<16), b''): h.update(b)
    return h.hexdigest()
if __name__=="__main__":
    os.makedirs(os.path.join(ROOT,"certs","kY"), exist_ok=True)
    inputs=[os.path.join(ROOT,"data","charges_matrix.json"),
            os.path.join(ROOT,"data","su5_mixed_cs.json"),
            os.path.join(ROOT,"data","orbifold_parities.csv")]
    audit={"inputs":{os.path.basename(p): (sha(p) if os.path.exists(p) else None) for p in inputs}}
    with open(os.path.join(ROOT,"certs","kY","input_hashes.json"),"w") as f: json.dump(audit,f,indent=2)
    run("snf_hnf.py"); run("cs_integrality.py"); run("orbifold_check.py")
    print("All certificates rebuilt.")
