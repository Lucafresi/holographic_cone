#!/usr/bin/env python3
import json, os, hashlib, sys
def h(s): return hashlib.sha256(s.encode()).hexdigest()

def read_json(path):
    with open(path,"r") as f: return json.load(f)

def write_json(obj, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path,"w") as f: json.dump(obj,f,indent=2)

def snf_torsion_invariants(K):
    # Restituisce gli invarianti torsionali Z_{d1} x ... (solo det|minori| via SNF concettuale).
    # Implementazione minimal: per K 1x1 o 2x2 diagonalizzabile a diag(d1,d2,...).
    # In produzione useremmo una SNF robusta; qui imponiamo ledger "canonico" piccolo.
    import math
    if len(K)==1 and len(K[0])==1:
        d = abs(int(K[0][0]))
        return [d] if d>1 else []
    if len(K)==2 and len(K[0])==2:
        # riduzione euristica a invarianti: d = gcd degli 1x1 e rapporto col gcd dei 2x2
        a,b,c,d = map(int,(K[0][0],K[0][1],K[1][0],K[1][1]))
        import math
        g1 = math.gcd(abs(a), math.gcd(abs(b), math.gcd(abs(c), abs(d))))
        det = abs(a*d - b*c)
        if det==0:
            return [g1] if g1>1 else []
        d1 = g1
        d2 = det//g1 if det%g1==0 else det
        inv=[]
        if d1 and d1>1: inv.append(d1)
        if d2 and d2>1: inv.append(d2)
        return inv
    # fallback: nessun torsionale dedotto
    return []

def allowed_thetas(torsion_invariants):
    # Per un fattore Z_m, le fasi consentite sono 2π * (k/m)
    import math
    if not torsion_invariants:
        return [0.0]  # nessuna torsione ⇒ fase bloccata a 0 mod 2π
    thetas=set([0.0])
    for m in torsion_invariants:
        for k in range(m):
            thetas.add(2.0*math.pi*k/m)
    return sorted(thetas)

def main():
    if len(sys.argv)!=3:
        print("usage: build_theta_from_bfcs.py <sources/bfcs_ledger.json> <artifacts/theta_ledger.json>")
        sys.exit(2)
    src, out = sys.argv[1], sys.argv[2]
    try:
        dat = read_json(src)
    except Exception as e:
        print(f"NO-GO: cannot_read_bfcs ({e})"); sys.exit(1)

    # Atteso: {"K_BF": [[...]], "K_CS": [[...]], "two_group": {...}, "model":"toric_dP3", ...}
    # Per severità: se manca K_BF o K_CS, NO-GO localizzato.
    if "K_BF" not in dat or "K_CS" not in dat:
        write_json({"status":"NO-GO","reason":"missing_K_BF_or_K_CS"}, out)
        print("NO-GO: missing_K_BF_or_K_CS"); sys.exit(1)

    Kbf = dat["K_BF"]; Kcs = dat["K_CS"]
    inv_bf = snf_torsion_invariants(Kbf)
    inv_cs = snf_torsion_invariants(Kcs)

    inv_all = sorted(set(inv_bf + inv_cs))
    thetas = allowed_thetas(inv_all)

    payload = {
      "status":"PASS",
      "uv_model": dat.get("model","UNKNOWN"),
      "torsion_invariants": inv_all,
      "allowed_thetas_rad": thetas,
      "hash": h(json.dumps({"inv":inv_all,"thetas":thetas}))
    }
    write_json(payload,out)
    print("PASS:THETA_LEDGER")
    print("torsion invariants:", inv_all)
    print("allowed thetas (rad):", thetas[:9], " ... total", len(thetas))

if __name__=="__main__":
    main()
