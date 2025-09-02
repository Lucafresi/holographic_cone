#!/usr/bin/env python3
import sys, yaml
import sympy as sp
from sympy.matrices.normalforms import hermite_normal_form

def load_B(path):
    with open(path, "r") as f:
        cfg = yaml.safe_load(f)
    C = sp.Matrix(cfg["CdotGG"])
    b2 = C.shape[0]
    L_list = cfg.get("L", [])
    if L_list is None or (isinstance(L_list, list) and len(L_list) == 0):
        L = sp.Matrix.zeros(b2, 0)
    else:
        L = sp.Matrix(L_list)
        if L.shape[0] != b2:
            raise ValueError(f"L ha {L.shape[0]} righe, ma b2={b2}.")
    return C.row_join(L)

def row_hnf_Z(B):
    try:
        res = hermite_normal_form(B, D=sp.ZZ)
    except TypeError:
        # fallback per versioni che non accettano D=
        res = hermite_normal_form(B)
    # alcune versioni ritornano (H, U), altre solo H
    if isinstance(res, tuple):
        H = res[0]
    else:
        H = res
    return H

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True)
    args = ap.parse_args()
    B = load_B(args.inp)
    H = row_hnf_Z(B)
    print("B ="); sp.pprint(B)
    print("\nrow-HNF(B) ="); sp.pprint(H)
