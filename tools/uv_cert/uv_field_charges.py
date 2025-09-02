#!/usr/bin/env python3
import argparse, json, yaml
import sympy as sp

def mat_from_rows(rows):
    if rows is None: return sp.Matrix(0,0,[])
    return sp.Matrix(rows) if len(rows)>0 else sp.Matrix(0,0,[])

def is_empty(M): return M.shape==(0,0)

def integerize_vector(vec):
    rr = [sp.Rational(x) for x in list(vec)]
    if len(rr)==0: return sp.Matrix([])
    L = rr[0].q
    for r in rr[1:]: L = sp.ilcm(L, r.q)
    ints = [int(sp.Integer(r*L)) for r in rr]
    g = 0
    for z in ints: g = sp.igcd(g, abs(z))
    g = max(g,1)
    return sp.Matrix([z//g for z in ints])

def integer_kernel_BT(B):
    NS = (B.T).nullspace()
    return [integerize_vector(v) for v in NS]

def build_A(field_order, yukawas):
    idx = {f:i for i,f in enumerate(field_order)}
    rows = []
    if "LeH" in yukawas:
        r=[0]*len(field_order); r[idx["L"]]=1; r[idx["eR"]]=1; r[idx["H"]]=1; rows.append(r)
    if "QdH" in yukawas:
        r=[0]*len(field_order); r[idx["Q"]]=1; r[idx["dR"]]=1; r[idx["H"]]=1; rows.append(r)
    if "QuH" in yukawas:
        r=[0]*len(field_order); r[idx["Q"]]=1; r[idx["uR"]]=1; r[idx["H"]]=1; rows.append(r)
    return sp.Matrix(rows)

def integer_nullspace_right(A):
    NS = A.nullspace()
    if not NS: return sp.Matrix.zeros(A.shape[1],0)
    cols = [integerize_vector(v) for v in NS]
    return sp.Matrix.hstack(*cols)

def load_B(cfg):
    C = mat_from_rows(cfg.get("CdotGG", []))
    L = mat_from_rows(cfg.get("L", []))
    b2 = max(C.rows if not is_empty(C) else 0, L.rows if not is_empty(L) else 0)
    if b2==0: raise ValueError("b2=0: C e L sono entrambe vuote.")
    if is_empty(C): C = sp.zeros(b2, 0)
    if is_empty(L): L = sp.zeros(b2, 0)
    if C.rows!=b2 or L.rows!=b2: raise ValueError("C e L devono avere lo stesso numero di righe (b2).")
    return C.row_join(L), b2

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--out", dest="out", required=True)
    ap.add_argument("--pretty", action="store_true")
    ap.add_argument("--echo", action="store_true")
    args = ap.parse_args()

    with open(args.inp,"r") as f: cfg = yaml.safe_load(f)
    fields = cfg["field_order"]
    A = build_A(fields, cfg.get("yukawa_active", []))
    Q = integer_nullspace_right(A)
    B, b2 = load_B(cfg)
    K = integer_kernel_BT(B)

    if args.echo:
        print(f"FIELD_ORDER = {fields}")
        print("A ="); sp.pprint(A)
        print("q_basis (colonne) ="); sp.pprint(Q)
        print("B ="); sp.pprint(B)
        print(f"--> dim ker(B^T) = {len(K)}")

    gens=[]
    for i,k in enumerate(K):
        qv = Q*k
        charges = {f:int(qv[j]) for j,f in enumerate(fields)}
        gens.append({"k":[int(x) for x in list(k)], "charges":charges})

    payload={"input_yaml":args.inp,"field_order":fields,"generators":gens}
    with open(args.out,"w") as f:
        if args.pretty: json.dump(payload,f,indent=2,ensure_ascii=False)
        else: json.dump(payload,f,separators=(",",":"),ensure_ascii=False)
    print(f"[OK] scritto -> {args.out}")

if __name__ == "__main__":
    main()
