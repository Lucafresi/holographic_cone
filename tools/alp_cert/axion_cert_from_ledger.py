#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse, json, yaml, math
import sympy as sp

# ------------------------
# Smith (opzionale) + rango
# ------------------------
try:
    from sympy.matrices.normalforms import smith_normal_form as SNF
    HAS_SNF = True
except Exception:
    HAS_SNF = False

def smith_data_int(M: sp.Matrix):
    """
    Se disponibile, calcola SNF su Z; altrimenti torna rango(Q) e diag vuota.
    Ritorna: (diag_invarianti, rankZ, U, S, V)
    """
    if not HAS_SNF:
        return [], int(M.rank()), None, None, None
    res = SNF(M, domain=sp.ZZ)
    if isinstance(res, tuple):
        if len(res) == 3:
            S, U, V = res
        elif len(res) == 4:
            S, U, V, _ = res
        else:
            S = res; U = sp.eye(M.rows); V = sp.eye(M.cols)
    else:
        S = res; U = sp.eye(M.rows); V = sp.eye(M.cols)
    diag = [int(S[i, i]) for i in range(min(S.rows, S.cols)) if S[i, i] != 0]
    rankZ = len(diag) if diag else int(M.rank())
    return diag, rankZ, U, S, V

# ------------------------
# Nullspace intero (senza SNF)
# ------------------------
def gcd_list(lst):
    g = 0
    for x in lst:
        g = math.gcd(g, abs(int(x)))
    return g

def primitive_integer_basis_from_Q(K: sp.Matrix):
    if K.cols == 0:
        return K
    cols = []
    for j in range(K.cols):
        col = [int(K[i, j]) for i in range(K.rows)]
        g = gcd_list(col)
        if g != 0:
            col = [x // g for x in col]
            for x in col:
                if x != 0:
                    if x < 0:
                        col = [-y for y in col]
                    break
        cols.append(col)
    return sp.Matrix(cols).T

def integer_nullspace_right(M: sp.Matrix):
    NS = M.nullspace()
    if not NS:
        return sp.zeros(M.rows, 0)
    Q = sp.Matrix.hstack(*NS)
    Qint_cols = []
    for j in range(Q.cols):
        col = Q[:, j]
        den = 1
        for x in col:
            den = math.lcm(den, sp.denom(x))
        cint = [int(x*den) for x in col]
        Qint_cols.append(cint)
    K = sp.Matrix(Qint_cols).T
    return primitive_integer_basis_from_Q(K)

# ------------------------
# Modellazione UV → b2, q, C·GG, L
# ------------------------

FIELD_ORDER = ["Q", "uR", "dR", "L", "eR", "NR", "H"]

def build_yukawa_A(cfg):
    branes = (cfg.get("branes") or {})
    UV = (branes.get("UV") or {})
    IR = (branes.get("IR") or {})

    yuk_uv = set(UV.get("yukawas", []) or [])
    yuk_ir = set(IR.get("yukawas", []) or [])
    yset = yuk_uv.union(yuk_ir)

    rows = []
    row_LeH = [0]*len(FIELD_ORDER)
    if "LeH" in yset:
        for f in ["L","eR","H"]:
            row_LeH[FIELD_ORDER.index(f)] = 1
    rows.append(row_LeH)

    row_QdH = [0]*len(FIELD_ORDER)
    if "QdH" in yset:
        for f in ["Q","dR","H"]:
            row_QdH[FIELD_ORDER.index(f)] = 1
    rows.append(row_QdH)

    row_QuH = [0]*len(FIELD_ORDER)
    if "QuH" in yset:
        for f in ["Q","uR","H"]:
            row_QuH[FIELD_ORDER.index(f)] = 1
    rows.append(row_QuH)

    A = sp.Matrix(rows) % 2
    return A, sorted(list(yset))

def build_axion_basis_q(A):
    NS = A.nullspace()
    if not NS:
        return sp.zeros(A.cols, 0)
    M = sp.Matrix.hstack(*NS)
    M_int = []
    for j in range(M.cols):
        col = M[:, j]
        den = 1
        for x in col:
            den = math.lcm(den, sp.denom(x))
        col_int = [int(x*den) for x in col]
        g = gcd_list(col_int)
        if g != 0:
            col_int = [x//g for x in col_int]
            for x in col_int:
                if x != 0:
                    if x < 0:
                        col_int = [-y for y in col_int]
                    break
        M_int.append(col_int)
    Q = sp.Matrix(M_int).T
    return Q

def parse_L_matrix(cfg, b2):
    L_list = cfg.get("L", None)
    if L_list is None:
        return sp.zeros(b2, 0)
    rows = len(L_list)
    cols = len(L_list[0]) if rows else 0
    if rows != b2:
        raise ValueError(f"L ha {rows} righe, ma b2={b2}.")
    M = sp.Matrix(L_list)
    for x in M:
        if int(x) != x:
            raise ValueError("L contiene elementi non interi.")
    return M

# --------- NUOVO: C·GG fisico dalle anomalie SM ---------
def build_CdotGG_from_SM(q_basis: sp.Matrix):
    """
    C·GG (b2 x 2) per (QCD, EM) calcolato dai coefficienti d'anomalia
    con 3 generazioni SM. Convenzioni:
      - QCD: N = Σ_i q_i * [multiplicità_SU2] * (2T(R_color)) * n_gen
             (2T(fondamentale)=1; color singlet → 0)
      - EM : E = Σ_i q_i * n_gen * Σ_componenti (Q_em^2 * multiplicity_color)
    Campi in FIELD_ORDER = [Q, uR, dR, L, eR, NR, H].
    Gli scalari (H) non contribuiscono.
    """
    b2 = q_basis.cols
    if b2 == 0:
        return sp.zeros(0, 2)

    n_gen = 3
    twoT_fund = 1  # 2*T(3) = 1

    # contributi per QCD (moltiplicatori per i q_i, già includono n_gen)
    # Q: doppietto SU(2) → 2 copie colorate per generazione
    coeff_QCD = {
        "Q":  n_gen * 2 * twoT_fund,  # = 3*2*1 = 6
        "uR": n_gen * 1 * twoT_fund,  # = 3
        "dR": n_gen * 1 * twoT_fund,  # = 3
        "L":  0,
        "eR": 0,
        "NR": 0,
        "H":  0,
    }

    # contributi per EM (Σ Q_em^2 * n_color * n_gen) per campo
    # calcolo: 
    #   Q: 3 colori * [(2/3)^2 + (-1/3)^2] = 3*(5/9) = 5/3 → n_gen→ 5
    #   uR: 3*( (2/3)^2 ) = 3*(4/9)=4/3 → n_gen→ 4
    #   dR: 3*( (1/3)^2 ) = 3*(1/9)=1/3 → n_gen→ 1
    #   L: (0^2 + (-1)^2) = 1 → n_gen→ 3
    #   eR: 1 → n_gen→ 3
    #   NR: 0, H: 0
    coeff_EM = {
        "Q":  5,
        "uR": 4,
        "dR": 1,
        "L":  3,
        "eR": 3,
        "NR": 0,
        "H":  0,
    }

    C = sp.zeros(b2, 2)
    for j in range(b2):
        # vettore di cariche PQ (q_i) per l'assione j
        qvec = { FIELD_ORDER[i]: int(q_basis[i, j]) for i in range(len(FIELD_ORDER)) }
        N_qcd = ( qvec["Q"]*coeff_QCD["Q"]
                + qvec["uR"]*coeff_QCD["uR"]
                + qvec["dR"]*coeff_QCD["dR"] )
        E_em  = ( qvec["Q"]*coeff_EM["Q"]
                + qvec["uR"]*coeff_EM["uR"]
                + qvec["dR"]*coeff_EM["dR"]
                + qvec["L"]*coeff_EM["L"]
                + qvec["eR"]*coeff_EM["eR"] )
        C[j, 0] = int(N_qcd)
        C[j, 1] = int(E_em)
    return C
# --------------------------------------------------------

# ------------------------
# I/O e certificato
# ------------------------
def main():
    ap = argparse.ArgumentParser(description="Certificatore ALP: test su B=[C|L] e ker(B^T) (anomaly-exact).")
    ap.add_argument("--in", dest="inp", required=True, help="modello YAML")
    ap.add_argument("--out", dest="out", required=True, help="certificato JSON")
    ap.add_argument("--pretty", action="store_true", help="JSON leggibile")
    ap.add_argument("--echo", action="store_true", help="stampa matrici")
    args = ap.parse_args()

    with open(args.inp, "r") as f:
        cfg = yaml.safe_load(f)

    print(f"==> FIELD_ORDER: {FIELD_ORDER}")
    A, yset = build_yukawa_A(cfg)
    print(f"==> Yukawa attivi: {yset}")
    print(f"==> Majorana: []")

    if args.echo:
        print("A ="); print(A)

    q_basis = build_axion_basis_q(A)  # n_fields x b2
    b2 = q_basis.cols
    if args.echo:
        print("q_basis (colonne) ="); print(q_basis)

    C = build_CdotGG_from_SM(q_basis)  # b2 x 2 (QCD, EM)
    if args.echo:
        print("C·GG ="); print(C)

    L = parse_L_matrix(cfg, b2)        # b2 x n_BF
    if args.echo:
        print("L ="); print(L)

    B = sp.Matrix.hstack(C, L)
    if args.echo:
        print("B = [C|L] ="); print(B)

    S_diag, rankB_Z, _, _, _ = smith_data_int(B)
    rankB_Q = int(B.rank())
    rankB = rankB_Z if HAS_SNF and S_diag else rankB_Q

    kerBT = integer_nullspace_right(B.T)  # b2 x dim
    ker_dim = kerBT.cols

    print(f"rank_Z(B) ≈ {rankB},  b2 = {b2}")
    passes = rankB < b2
    if passes:
        print(f"--> dim ker(B^T) = {ker_dim} (ALP fisici)")
        for j in range(ker_dim):
            v = [int(kerBT[i, j]) for i in range(b2)]
            print(f"    v[{j}] (primitivo) = {v}")
    else:
        print("--> ker(B^T) banale (nessun ALP di nullspace)")

    payload = {
        "model": args.inp,
        "b2": int(b2),
        "SNF_diag": S_diag,
        "rankZ_B": int(rankB),
        "passes": bool(passes),
        "ker_dim": int(ker_dim),
        "ker_basis_cols": [[int(kerBT[i, j]) for i in range(b2)] for j in range(ker_dim)],
        "CdotGG": [[int(C[i, j]) for j in range(C.cols)] for i in range(C.rows)],
        "L": [[int(L[i, j]) for j in range(L.cols)] for i in range(L.rows)],
        "B_shape": [int(B.rows), int(B.cols)]
    }

    with open(args.out, "w") as f:
        if args.pretty:
            json.dump(payload, f, indent=2, ensure_ascii=False)
        else:
            json.dump(payload, f, separators=(",", ":"), ensure_ascii=False)

    print(f"[OK] scritto certificato -> {args.out}")
    if passes:
        print(f"VERDETTO: PASS (rank_Z(B)={rankB} < b2={b2}) -- esiste ALP fisico.")
    else:
        print(f"VERDETTO: FAIL (rank_Z(B)={rankB} >= b2={b2}) -- nessun ALP di nullspace.")

if __name__ == "__main__":
    main()
