import os, sys, subprocess
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CASES = ["sigma1","sigma2","sigma3","sigma4"]
SCRIPTS = ["snf_hnf.py","cs_integrality.py","orbifold_check.py"]
def run_case(case):
    print(f"\n=== CASE {case} ===")
    for s in SCRIPTS:
        p = os.path.join(ROOT,"src",s)
        print(">>", s)
        subprocess.check_call([sys.executable, p, case])
    # echo summary
    import json
    cert_dir = os.path.join(ROOT,"certs","kY",case)
    cs = json.load(open(os.path.join(cert_dir,"cs_integrality.json")))
    ob = json.load(open(os.path.join(cert_dir,"orbifold_check.json")))
    print(f"SUMMARY {case}: kY={cs['kY']} | CS_PASS={cs['PASS']} | ORB_PASS={ob['PASS']}" + ("" if ob.get("PASS") else f" | reasons={ob.get('reasons')}"))
if __name__=="__main__":
    for c in CASES: run_case(c)
    print("\nALL CASES REBUILT.")
