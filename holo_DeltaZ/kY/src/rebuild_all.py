import os, sys, subprocess, json
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CASES = ["sigma1","sigma2","sigma3","sigma4"]

def run(py):
    print(">>", os.path.basename(py))
    subprocess.check_call([sys.executable, py], cwd=os.path.dirname(py))

def main():
    for s in ["snf_hnf.py","cs_integrality.py","orbifold_check.py"]:
        run(os.path.join(ROOT,"src",s))
    # riepilogo
    for c in CASES:
        base = os.path.join(ROOT,"certs","kY",c)
        cs = json.load(open(os.path.join(base,"cs_integrality.json")))
        ob = json.load(open(os.path.join(base,"orbifold_check.json")))
        print(f"=== {c} === kY={cs['kY']} | CS_PASS={cs['PASS']} | ORB_PASS={ob['PASS']}")
    print("ALL kY CERTS REBUILT.")
if __name__=="__main__": main()
