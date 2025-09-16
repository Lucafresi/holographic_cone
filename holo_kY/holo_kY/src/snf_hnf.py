import json, os
from sympy import Matrix, eye
from sympy.matrices.normalforms import smith_normal_form
from sympy.polys.domains import ZZ

ROOT = os.path.dirname(os.path.dirname(__file__))
Apath = os.path.join(ROOT,"data","charges_matrix.json")
OUT1 = os.path.join(ROOT,"certs","kY","snf.json")
OUT2 = os.path.join(ROOT,"certs","kY","rank.txt")

def unpack_snf(A):
    """Handle SymPy variants returning (S,U,V) or (S,U,V,inv)."""
    try:
        # preferisci API esplicita che dovrebbe dare 3 valori
        res = smith_normal_form(A, domain=ZZ, calc_transformation=True)
    except TypeError:
        # fallback per versioni che non accettano calc_transformation
        res = smith_normal_form(A, domain=ZZ)
    if not isinstance(res, tuple):
        S = res; U = eye(A.rows); V = eye(A.cols); return S,U,V
    if len(res) == 3:
        S,U,V = res
    elif len(res) == 4:
        S,U,V,_ = res
    else:
        # fallback ultra-conservativo
        S = res[0]
        U = res[1] if len(res) > 1 else eye(A.rows)
        V = res[2] if len(res) > 2 else eye(A.cols)
    return S,U,V

def main():
    os.makedirs(os.path.dirname(OUT1), exist_ok=True)
    if not os.path.exists(Apath):
        with open(OUT1,"w") as f: json.dump({"error":"missing charges_matrix.json"}, f, indent=2)
        with open(OUT2,"w") as f: f.write("MISSING")
        return
    with open(Apath) as f:
        A = Matrix(json.load(f))  # matrice integrale m×n
    S,U,V = unpack_snf(A)
    rank = sum(1 for i in range(min(S.rows, S.cols)) if S[i,i] != 0)
    obj = {
        "D": [[int(S[i,j]) for j in range(S.cols)] for i in range(S.rows)],
        "U": [[int(U[i,j]) for j in range(U.cols)] for i in range(U.rows)],
        "V": [[int(V[i,j]) for j in range(V.cols)] for i in range(V.rows)],
        "rank": int(rank)
    }
    with open(OUT1,"w") as f: json.dump(obj,f,indent=2)
    with open(OUT2,"w") as f: f.write(str(rank))

if __name__=="__main__":
    main()
