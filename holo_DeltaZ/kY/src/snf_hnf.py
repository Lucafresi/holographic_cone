
import os, json, sys
from sympy import Matrix, ZZ
from sympy.matrices.normalforms import smith_normal_form

ROOT   = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CASESD = os.path.join(ROOT, "cases")
OUTD   = os.path.join(ROOT, "certs", "kY")
CASES  = ["sigma1","sigma2","sigma3","sigma4"]

def load_matrix(case):
    path = os.path.join(CASESD, case, "data", "charges_matrix.json")
    j = json.load(open(path, encoding="utf-8"))
    Araw = j["charges_matrix"] if isinstance(j, dict) and "charges_matrix" in j else j
    return Matrix(Araw), path

def snf_over_Z(A):
    res = smith_normal_form(A, domain=ZZ)
    if isinstance(res, tuple):
        if len(res) == 3:
            D, U, V = res
        elif len(res) == 4:
            D, U, V, _ = res
        else:
            raise ValueError(f"smith_normal_form returned {len(res)} values")
    else:
        # fallback ultra-conservativo: res è D
        D, U, V = res, None, None
    return D, U, V

def run(case):
    A, inpath = load_matrix(case)
    D, U, V = snf_over_Z(A)
    invariants = [int(D[i,i]) for i in range(min(D.shape))]
    print(f"[SNF] {case}: invariants={invariants}")

    out_dir = os.path.join(OUTD, case)
    os.makedirs(out_dir, exist_ok=True)
    out_p = os.path.join(out_dir, "snf.json")
    with open(out_p,"w",encoding="utf-8") as f:
        json.dump({
            "invariants": invariants,
            "rank": int(A.rank()),
            "inputs": {"charges_matrix.json": os.path.abspath(inpath)}
        }, f, indent=2)

if __name__=="__main__":
    for c in CASES:
        run(c)
