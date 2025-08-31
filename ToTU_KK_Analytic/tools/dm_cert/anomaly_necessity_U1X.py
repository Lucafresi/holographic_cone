#!/usr/bin/env python3
import json, argparse
from fractions import Fraction
from collections import defaultdict

SIGMA = {"UV": -1, "IR": +1}
# Tracce/indici in base integrale: 2T(fund)=1 per SU(2), SU(3)
T2_SU2 = Fraction(1,1)
T2_SU3 = Fraction(1,1)

# Contenuto SM (una famiglia, basi integrali)
SM = [
  {"name":"Q_L",   "dim3":3, "dim2":2, "Y":Fraction(1,6),  "rep3":"3",    "rep2":"2"},
  {"name":"u_R^c", "dim3":3, "dim2":1, "Y":Fraction(-2,3), "rep3":"3bar", "rep2":"1"},
  {"name":"d_R^c", "dim3":3, "dim2":1, "Y":Fraction(1,3),  "rep3":"3bar", "rep2":"1"},
  {"name":"L_L",   "dim3":1, "dim2":2, "Y":Fraction(-1,2), "rep3":"1",    "rep2":"2"},
  {"name":"e_R^c", "dim3":1, "dim2":1, "Y":Fraction(1,1),  "rep3":"1",    "rep2":"1"}
]

def is_fund3(rep3): 
    if rep3=="3": return +1
    if rep3=="3bar": return -1
    return 0
def is_doublet(rep2): return rep2=="2"

def load_json(p): 
    with open(p,"r") as f: return json.load(f)

def compute_anomalies_per_brane(charges_U1X, brane_counts):
    # Calcola A^{(i)} per i canali: SU3^2-U1X, SU2^2-U1X, U1Y^2-U1X, U1X^3, grav^2-U1X
    out = {"UV": defaultdict(Fraction), "IR": defaultdict(Fraction)}
    for fam in SM:
        name=fam["name"]; qx = Fraction(charges_U1X["per_multiplet"][name],1)
        mult = fam["dim3"]*fam["dim2"]
        # contributi canale per famiglia
        if is_fund3(fam["rep3"])!=0:
            out["UV"]["SU3^2_U1X"] += brane_counts["UV"][name] * fam["dim2"] * T2_SU3 * qx
            out["IR"]["SU3^2_U1X"] += brane_counts["IR"][name] * fam["dim2"] * T2_SU3 * qx
        if is_doublet(fam["rep2"]):
            out["UV"]["SU2^2_U1X"] += brane_counts["UV"][name] * fam["dim3"] * T2_SU2 * qx
            out["IR"]["SU2^2_U1X"] += brane_counts["IR"][name] * fam["dim3"] * T2_SU2 * qx
        Y=fam["Y"]
        out["UV"]["U1Y^2_U1X"] += brane_counts["UV"][name] * mult * (Y*Y) * qx
        out["IR"]["U1Y^2_U1X"] += brane_counts["IR"][name] * mult * (Y*Y) * qx
        out["UV"]["U1X^3"]     += brane_counts["UV"][name] * mult * (qx*qx*qx)
        out["IR"]["U1X^3"]     += brane_counts["IR"][name] * mult * (qx*qx*qx)
        out["UV"]["grav^2_U1X"]+= brane_counts["UV"][name] * mult * qx
        out["IR"]["grav^2_U1X"]+= brane_counts["IR"][name] * mult * qx
    # cast a dict semplice con stringhe frazionarie
    def norm(d): 
        return {k: Fraction(v) for k,v in d.items()}
    return { "UV": norm(out["UV"]), "IR": norm(out["IR"]) }

def solvable_with_single_k_per_channel(A_UV, A_IR):
    # Condizione necessaria e sufficiente per esistenza di k intero (stessa k su entrambe le brane):
    # A_UV + sigma_UV*k = 0  e  A_IR + sigma_IR*k = 0  ⇒  k = A_UV (per sigma_UV=-1) e k = -A_IR ⇒ A_UV + A_IR = 0
    # Lavoriamo in base integrale ⇒ A_* sono frazioni con denominatore noto; la condizione è esatta.
    ok={}
    for ch in sorted(A_UV.keys() | A_IR.keys()):
        aUV = A_UV.get(ch, Fraction(0,1))
        aIR = A_IR.get(ch, Fraction(0,1))
        ok[ch] = (aUV + aIR == 0)
    all_ok = all(ok.values())
    # se all_ok, il k "unico" è k = aUV (che = -aIR). Deve essere intero in base integrale.
    k_int={}
    if all_ok:
        for ch in sorted(A_UV.keys() | A_IR.keys()):
            k = A_UV.get(ch, Fraction(0,1))  # sigma_UV=-1 ⇒ k = aUV
            k_int[ch] = (k.denominator==1)
        all_k_int = all(k_int.values())
    else:
        all_k_int = False
    return all_ok and all_k_int, ok, k_int

def frac_to_str(d): return {k: f"{v.numerator}/{v.denominator}" for k,v in d.items()}

def main():
    ap=argparse.ArgumentParser(description="D0-A: Necessità GS-axion da ledger U(1)_X (anomalie miste per brana).")
    ap.add_argument("--charges", default="dm_inputs/U1X_charges.json")
    ap.add_argument("--brane",   default="dm_inputs/brane_counts.json")
    ap.add_argument("--out",     default="cert/DM/axion/anomaly_necessity.json")
    args=ap.parse_args()

    charges = load_json(args.charges)
    branes  = load_json(args.brane)["per_brane"]
    A = compute_anomalies_per_brane(charges, branes)

    solv, per_chan_ok, per_chan_kint = solvable_with_single_k_per_channel(A["UV"], A["IR"])
    gs_required = (not solv)

    report = {
      "schema_version": 1,
      "sigma": SIGMA,
      "inputs": {
        "charges_file": args.charges,
        "brane_counts_file": args.brane
      },
      "anomalies": {
        "UV": frac_to_str(A["UV"]),
        "IR": frac_to_str(A["IR"])
      },
      "channel_constraints": {
        "sum_zero_condition": per_chan_ok,   # A_UV + A_IR == 0 ?
        "k_integer_if_sum_zero": per_chan_kint
      },
      "solvable_by_CS_only": solv,
      "gs_required": gs_required,
      "explanation": (
        "Solvable_by_CS_only richiede A_UV + A_IR = 0 per ogni canale e k intero unico per canale. "
        "Se fallisce, non esiste un singolo livello CS 5D che cancelli le anomalie su entrambe le brane; "
        "senza aggiungere materia 4D (vietato da NFF), è richiesto un termine di tipo Green–Schwarz (assione) o equivalente."
      )
    }

    with open(args.out,"w") as f: json.dump(report,f,indent=2)
    print(f"[D0-A] wrote {args.out}")
    print(f"[D0-A] gs_required = {gs_required}")

if __name__=="__main__":
    main()
