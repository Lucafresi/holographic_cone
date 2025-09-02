import yaml, json, sympy as sp, os
from math import gcd

def primitive_integer(vec):
    v = sp.Matrix(vec)
    den = 1
    for x in v:
        xn = sp.nsimplify(x); _, d = xn.as_numer_denom()
        den = sp.ilcm(den, int(d))
    v = (den*v).applyfunc(lambda x: int(sp.Integer(x)))
    g = 0
    for x in v: g = gcd(g, abs(x))
    g = max(g,1)
    v = v.applyfunc(lambda x: x//g)
    for i in range(v.rows):
        if v[i]!=0:
            if v[i]<0: v = -v
            break
    return v

def egcd_int(a,b):
    a0, b0 = int(a), int(b)
    if b0 == 0:
        s = 1 if a0>=0 else -1
        return s, 0, abs(a0)
    x, y, g = egcd_int(b0, a0 % b0)
    return y, x - (a0//b0)*y, g

def bezout_vector_for_dot1(k):
    k = [int(sp.Integer(x)) for x in list(k)]
    n = len(k); coeffs = [0]*n
    j0 = next((j for j,x in enumerate(k) if x!=0), None)
    if j0 is None: raise ValueError("k nullo.")
    g = abs(k[j0]); coeffs[j0] = 1 if k[j0]>0 else -1
    for i in range(n):
        if i==j0: continue
        x,y,g2 = egcd_int(g, k[i])
        coeffs = [x*c for c in coeffs]; coeffs[i] += y; g = abs(g2)
    s = sum(k[t]*coeffs[t] for t in range(n))
    if s not in (1,-1): raise RuntimeError("Bezout failure.")
    if s == -1: coeffs = [-c for c in coeffs]
    return sp.Matrix(coeffs)

def build_A(cfg, fields):
    idx = {f:i for i,f in enumerate(fields)}
    rows=[]
    Y={"QuH":["Q","uR","H"],"QdH":["Q","dR","H"],"LeH":["L","eR","H"]}
    for y in cfg.get("yukawa_active",[]):
        r=[0]*len(fields)
        for f in Y[y]: r[idx[f]]+=1
        rows.append(r)
    for m in cfg.get("majorana",[]):
        r=[0]*len(fields); r[idx[m]] = 2; rows.append(r)
    return sp.Matrix(rows) if rows else sp.zeros(0,len(fields))

def load_CL(cfg):
    C = cfg.get("CdotGG", [])
    L = cfg.get("L", [])
    C = sp.Matrix(C) if C else sp.zeros(0,0)
    L = sp.Matrix(L) if L else sp.zeros(0,0)
    if C.rows==0 and L.rows==0:
        raise ValueError("CdotGG e L assenti/vuoti.")
    b2 = C.rows if C.rows>0 else L.rows
    if C.rows not in (0,b2) or L.rows not in (0,b2):
        raise ValueError("Righe di C o L non coerenti con b2.")
    return C, L, b2

def hstack_CL(C,L):
    if C.cols==0 and L.cols==0: raise ValueError("C e L hanno 0 colonne.")
    if C.cols==0: return L
    if L.cols==0: return C
    return sp.Matrix.hstack(C,L)

def integer_kernel_BT(B):
    NS = B.T.nullspace()
    return [primitive_integer(v) for v in NS]

def orth_to_k(M, k, w):
    if M.cols==0: return M
    out = M.copy()
    for j in range(M.cols):
        c = out[:,j]; s = int((k.T*c)[0])
        if s!=0: out[:,j] = c - s*w
    return out

def q_basis_from_A(A, nfields):
    if A.rows==0: return sp.eye(nfields)
    NS = A.nullspace()
    if not NS: return sp.zeros(nfields,0)
    cols = [primitive_integer(v) for v in NS]
    return sp.Matrix.hstack(*cols)

def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--coeffs", nargs="+", type=int, required=True)
    ap.add_argument("--out", dest="out", required=True)
    ap.add_argument("--pretty", action="store_true")
    ap.add_argument("--echo", action="store_true")
    args = ap.parse_args()

    with open(args.inp,"r") as f: cfg = yaml.safe_load(f)
    fields = cfg["field_order"]
    A = build_A(cfg, fields)
    C,L,b2 = load_CL(cfg)
    B = hstack_CL(C,L)
    K = integer_kernel_BT(B)
    if len(args.coeffs) != len(K):
        raise SystemExit(f"coeffs forniti = {len(args.coeffs)}, dim ker(B^T) = {len(K)}.")
    k = sp.zeros(b2,1)
    for ci,Ki in zip(args.coeffs, K): k += int(ci)*Ki
    k = primitive_integer(k)
    w = bezout_vector_for_dot1(list(k))
    C2 = orth_to_k(C, k, w)
    L2 = orth_to_k(L, k, w)
    B2 = hstack_CL(C2,L2)
    if (B2.T * k) != sp.zeros(B2.cols,1):
        raise RuntimeError("k non è nel nuovo ker(B^T).")
    q_basis = q_basis_from_A(A, len(fields))
    qDM = primitive_integer(q_basis*k)
    ok_yuk = (A*qDM) == sp.zeros(A.rows,1) if A.rows>0 else True
    outcfg = dict(cfg)
    outcfg["CdotGG"] = [[int(C2[i,j]) for j in range(C2.cols)] for i in range(C2.rows)]
    if L2.cols>0:
        outcfg["L"] = [[int(L2[i,j]) for j in range(L2.cols)] for i in range(L2.rows)]
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out,"w") as f:
        if args.pretty: yaml.safe_dump(outcfg,f,sort_keys=False)
        else: yaml.safe_dump(outcfg,f,sort_keys=False)
    if args.echo:
        print("b2 =", b2)
        print("k =", list(map(int,k)))
        print("w =", list(map(int,w)))
        print("C (out) ="); sp.pprint(C2)
        print("L (out) ="); sp.pprint(L2)
        print("Yukawa invariant =", ok_yuk)
    print(f"[OK] scritto -> {args.out}")

if __name__ == "__main__":
    main()
