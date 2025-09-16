import csv, json, os
ROOT = os.path.dirname(os.path.dirname(__file__))
INP  = os.path.join(ROOT,"data","orbifold_parities.csv")
OUT  = os.path.join(ROOT,"certs","kY","orbifold_check.json")
def main():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    if not os.path.exists(INP):
        json.dump({"pass":False,"reasons":["missing orbifold_parities.csv"]}, open(OUT,"w"), indent=2)
        print("orbifold PASS = False (missing data)"); return
    ok=True; reasons=[]
    with open(INP) as f:
        r=csv.DictReader(f)
        for row in r:
            fld=row.get("field","").strip(); par=row.get("parity_PPprime","").strip()
            if "H_triplet" in fld and par!="--": ok=False; reasons.append(f"Triplet not projected: {fld} {par}")
            if "H_doublet" in fld and par=="--": ok=False; reasons.append(f"Doublet wrongly projected: {fld}")
            if "U1prime" in fld and ("+" in par): ok=False; reasons.append(f"Unwanted U(1)' survives: {fld} {par}")
    json.dump({"pass":ok,"reasons":reasons}, open(OUT,"w"), indent=2)
    print("orbifold PASS =", ok); 
    if not ok:
        for rr in reasons: print(" -", rr)
if __name__=="__main__": main()
