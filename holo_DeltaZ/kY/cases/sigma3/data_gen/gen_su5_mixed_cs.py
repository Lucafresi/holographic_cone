from fractions import Fraction
import json, os, math

# Hypercharge SU(5): diag(-1/3,-1/3,-1/3,+1/2,+1/2)
Y_diag = [-Fraction(1,3), -Fraction(1,3), -Fraction(1,3), Fraction(1,2), Fraction(1,2)]
# Convenzione di traccia: Tr_fund(T^a T^b) = 1/2 δ^{ab}
Tr_norm = "Tr_fund(T^a T^b) = 1/2 δ^{ab}"

# Coefficienti misti grezzi (anomaly-like) nel fondamental:
# c3 ~ Tr(Y T_SU(3)^2)  -> blocco 3x3 con Y = -1/3  e index_fund(SU3)=1/2  => -1/6
# c2 ~ Tr(Y T_SU(2)^2)  -> blocco 2x2 con Y = +1/2  e index_fund(SU2)=1/2  => +1/4
aY33_raw = Fraction(-1,6)
aY22_raw = Fraction(1,4)

# Quantizzazione FW/CS: scegli il minimo intero pari K che rende entrambi interi
den = (aY22_raw.denominator * aY33_raw.denominator) // math.gcd(aY22_raw.denominator, aY33_raw.denominator)
K_min = den
if K_min % 2 != 0:
    K_min *= 2

A22 = int((aY22_raw * K_min))   # = 3 se K_min=12
A33 = int((aY33_raw * K_min))   # = -2 se K_min=12

# La riduzione 2-group/SNF (vedi charges_matrix) permette un cambio unimodulare di base
# che porta (A22, A33) a livelli unitari e stessi segni per Σ3.
# Qui non imponiamo ancora quell’uguaglianza: salviamo i grezzi + K_min.
out = {
  "Y_diag": [float(x) for x in Y_diag],
  "trace_convention": Tr_norm,
  "raw_mixed": {"aY22_raw": float(aY22_raw), "aY33_raw": float(aY33_raw)},
  "FW_min_even": K_min,
  "mixed_integers_before_2group": {"aY22_int": A22, "aY33_int": A33},
  "kY_from_embedding": 2
}

dst = os.path.join("holo_DeltaZ","kY","cases","sigma3","data","su5_mixed_cs.json")
os.makedirs(os.path.dirname(dst), exist_ok=True)
with open(dst,"w",encoding="utf-8") as f:
    json.dump(out, f, indent=2)
print("wrote:", dst)
