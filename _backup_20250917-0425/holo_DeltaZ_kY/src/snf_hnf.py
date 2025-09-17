import json, os, sys
from sympy import Matrix
from sympy.matrices.normalforms import smith_normal_form

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

def run(case):
    base = os.path.join(ROOT, "cases", case, "data")
    A = Matrix(json.load(open(os.path.join(base, "charges_matrix.json")))["A"])
    ret = smith_normal_form(A)
    if not isinstance(ret, tuple):
        raise RuntimeError("smith_normal_form: unexpected return type")
    if len(ret) == 3:
        D, U, V = ret
    elif len(ret) == 4:
        D, U, V, _ = ret
    else:
        raise RuntimeError(f"smith_normal_form: unexpected tuple length {len(ret)}")
    inv = []
    m, n = D.shape
    for i in range(min(m,n)):
        d = D[i,i]
        inv.append(int(d) if d.is_Integer else int(d))
    rank = sum(1 for d in inv if d!=0)
    out_dir = os.path.join(ROOT, "certs", "kY", case)
    os.makedirs(out_dir, exist_ok=True)
    json.dump({"invariants": inv, "rank": rank}, open(os.path.join(out_dir,"snf.json"),"w"), indent=2)
    open(os.path.join(out_dir,"rank.txt"),"w").write(str(rank))
    print(f"[SNF] {case}: rank={rank} invariants={inv}")

if __name__=="__main__":
    run(sys.argv[1] if len(sys.argv)>1 else "sigma3")
