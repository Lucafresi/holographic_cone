#!/usr/bin/env python3
import argparse, json, os
import sympy as sp
import yaml

def to_int_primitive(col):
    nums = [sp.Rational(x) for x in col]
    den_lcm = 1
    for r in nums:
        den_lcm = sp.ilcm(den_lcm, r.q)
    ints = [int((r*den_lcm)) for r in nums]
    g = 0
    for x in ints:
        g = sp.igcd(g, abs(x))
    g = max(1, g)
    return [x//g for x in ints]

def integer_nullspace_right(M):
    M = sp.Matrix(M)
    ns = M.nullspace()
    if not ns:
        return sp.Matrix.zeros(M.shape[1], 0)
    cols = []
    for v in ns:
        cols.append(to_int_primitive(list(v)))
    return sp.Matrix(cols).T

def build_A(field_order, yukawa_active, majorana_terms=None):
    idx = {name: i for i, name in enumerate(field_order)}
    rows = []
    if 'QuH' in yukawa_active:
        r = [0]*len(field_order); r[idx['Q']]+=1; r[idx['uR']]+=1; r[idx['H']]+=1; rows.append(r)
    if 'QdH' in yukawa_active:
        r = [0]*len(field_order); r[idx['Q']]+=1; r[idx['dR']]+=1; r[idx['H']]+=1; rows.append(r)
    if 'LeH' in yukawa_active:
        r = [0]*len(field_order); r[idx['L']]+=1; r[idx['eR']]+=1; r[idx['H']]+=1; rows.append(r)
    if majorana_terms and 'NN' in majorana_terms:
        r = [0]*len(field_order); r[idx['NR']]+=2; rows.append(r)
    if not rows:
        raise ValueError("Nessuna equazione Yukawa/Majorana attiva.")
    return sp.Matrix(rows)

def as_int_matrix(lst, name):
    if lst is None:
        return None
    try:
        return sp.Matrix([[int(x) for x in row] for row in lst])
    except Exception:
        raise ValueError(f"{name}: elementi non interi.")

def load_mat(name, cfg, b2):
    raw = cfg.get(name, None)
    if raw in (None, [], ()):
        return sp.Matrix.zeros(b2, 0)
    M = as_int_matrix(raw, name)
    return M

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in","--inp","-i",dest="inp",required=True)
    ap.add_argument("--out","-o",dest="out",required=True)
    ap.add_argument("--pretty",action="store_true")
    ap.add_argument("--echo",action="store_true")
    args = ap.parse_args()

    with open(args.inp,"r") as f:
        cfg = yaml.safe_load(f)

    field_order = cfg.get("field_order", ['Q','uR','dR','L','eR','NR','H'])
    yukawa = cfg.get("yukawa_active", ['LeH','QdH','QuH'])
    majorana = cfg.get("majorana", [])

    A = build_A(field_order, yukawa, majorana)
    q_basis = integer_nullspace_right(A)

    b2_cfg = cfg.get("b2", None)
    b2 = int(b2_cfg) if b2_cfg is not None else q_basis.shape[1]

    C = load_mat("CdotGG", cfg, b2)
    L = load_mat("L", cfg, b2)

    if C.shape[0] != b2:
        raise ValueError(f"CdotGG ha {C.shape[0]} righe, ma b2={b2}.")
    if L.shape[0] != b2:
        raise ValueError(f"L ha {L.shape[0]} righe, ma b2={b2}.")

    B = C.row_join(L)
    rankB = int(sp.Matrix(B).rank())
    kernel_dim = b2 - rankB

    if kernel_dim > 0:
        K = integer_nullspace_right(B.T)
        ker_generators = [list(map(int, list(K[:, j]))) for j in range(K.shape[1])]
    else:
        ker_generators = []

    passes = rankB < b2

    if args.echo:
        print(f"==> FIELD_ORDER: {field_order}")
        print(f"==> Yukawa attivi: {yukawa}")
        print(f"==> Majorana: {majorana}")
        print("A ="); print(A)
        print("q_basis (colonne) ="); print(q_basis)
        print("C·GG ="); print(C)
        print("L ="); print(L)
        print("B = [C|L] ="); print(B)
        print(f"rank(B) = {rankB},  b2 = {b2}")
        if passes:
            print(f"--> dim ker(B^T) = {kernel_dim} (ALP fisici)")
            for i, v in enumerate(ker_generators):
                print(f"    v[{i}] (primitivo) = {v}")
        else:
            print("--> ker(B^T) banale (nessun ALP di nullspace)")

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    payload = {
        "input_yaml": args.inp,
        "b2": b2,
        "rank_B_over_Q": int(rankB),
        "kernel_dim": int(kernel_dim),
        "kernel_generators": ker_generators,
        "pass": bool(passes),
        "method": "rational-rank + integerized-nullspace"
    }
    with open(args.out, "w") as f:
        if args.pretty:
            json.dump(payload, f, indent=2, ensure_ascii=False)
        else:
            json.dump(payload, f, separators=(",", ":"), ensure_ascii=False)

    print(f"[OK] scritto certificato -> {args.out}")
    if passes:
        print(f"VERDETTO: PASS (rank(B)={rankB} < b2={b2}) -- esiste ALP fisico.")
    else:
        print(f"VERDETTO: FAIL (rank(B)={rankB} >= b2={b2}) -- nessun ALP di nullspace.")

if __name__ == "__main__":
    main()
