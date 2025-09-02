#!/usr/bin/env python3
import yaml, sympy as sp, json, argparse, math

def mat_from_yaml(path):
    with open(path,"r") as f: cfg=yaml.safe_load(f)
    C=sp.Matrix(cfg["CdotGG"])
    b2=C.shape[0]
    L_list=cfg.get("L",[])
    L = sp.Matrix.zeros(b2,0) if not L_list else sp.Matrix(L_list)
    if L.shape[0]!=b2: raise ValueError(f"L ha {L.shape[0]} righe, b2={b2}")
    return C.row_join(L)

def primitive_int(vec):
    nums=[int(x) for x in vec]
    g=0
    for a in nums: g=math.gcd(g,abs(a))
    if g==0: return nums
    nums=[a//g for a in nums]
    # segno canonico: primo elemento non nullo >0
    for a in nums:
        if a<0: nums=[-x for x in nums]; break
        if a>0: break
    return nums

def integerize(v):
    den_lcm=1
    for x in v:
        q=sp.Rational(x)
        den_lcm=sp.ilcm(den_lcm, q.q)
    ints=[int(sp.Rational(x)*den_lcm) for x in v]
    return primitive_int(ints)

def kernel_basis_integer(B):
    N = (B.T).nullspace()
    cols=[]
    for w in N:
        cols.append(integerize(list(w)))
    # deduplica colonne
    uniq=[]
    for c in cols:
        if c not in uniq: uniq.append(c)
    return uniq

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--in",dest="inp",required=True)
    ap.add_argument("--out",dest="out",required=True)
    args=ap.parse_args()
    B=mat_from_yaml(args.inp)
    K=kernel_basis_integer(B)
    print("B ="); sp.pprint(B)
    print("\n--> base intera ker(B^T):")
    for i,c in enumerate(K):
        print(f"v[{i}] =", c)
    payload={"input_yaml":args.inp,"kernel_generators":K}
    with open(args.out,"w") as f: json.dump(payload,f,indent=2)
    print(f"\n[OK] scritto → {args.out}")
