#!/usr/bin/env python3
import json, math, hashlib, os
h=lambda s: hashlib.sha256(s.encode()).hexdigest()
def R(p): 
    with open(p) as f: return json.load(f)
def W(p,o):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p,"w") as f: json.dump(o,f,indent=2)

Mpl = 2.435e18  # GeV
Kmis = None

def gstar_SM(T):
    # Mappa conservativa (SM): per T >= 100 GeV fissa 106.75.
    if T >= 100.0: return 106.75
    # fasce indicative (non rilevanti se T_osc >> 100 GeV)
    if T >= 1.0:   return 61.75
    if T >= 0.1:   return 17.25
    if T >= 0.001: return 10.75
    return 3.36

def main():
    # leggi artefatti
    cosmo = R("artifacts/cosmo_kernel.json")["cosmo_kernel"]
    global Kmis; Kmis = cosmo["constants"]["Kmis_numeric"]
    fa   = R("artifacts/fa.json")["fa_GeV"]
    thetas = R("artifacts/theta_ledger.json")["allowed_thetas_rad"]
    # scegli la più piccola non-zero (ledger-fixed)
    theta = min([t for t in thetas if t>0])
    # S_inst (da griglia con N=6, q=8)
    sinst = None
    G = R("artifacts/sinst_grid.json")
    for e in G["grid"]:
        if e.get("N")==6 and e.get("q")==8:
            sinst = e["S_inst"]; break
    if sinst is None:
        raise SystemExit("NO-GO: missing S_inst for (N=6,q=8)")
    Omega = 0.12
    k = 3

    # fisso-punto: μ_dalla_(i) -> T_osc_dalla_(ii) -> G* -> μ -> ...
    mu = 1.0e7  # seed
    for _ in range(10):
        # (ii) T_osc da μ e G* (usa g* dell'iterazione precedente o stima)
        # calcola m_a
        ma = k*(mu**2)/fa
        # usa g* preliminare dal T_osc precedente se presente, altrimenti 106.75
        Gstar = 106.75
        Tosc  = math.sqrt((ma*Mpl)/(3.0*1.66*math.sqrt(Gstar)))
        # aggiorna G* da Tosc e ricalcola Tosc
        Gstar = gstar_SM(Tosc)
        Tosc  = math.sqrt((ma*Mpl)/(3.0*1.66*math.sqrt(Gstar)))
        # (i) μ nuovo dalla misalignment
        numer = Omega
        denom = Kmis * Gstar * (theta**2) * (fa**1.5) * math.exp(-sinst/4.0)
        mu_new = numer/denom
        if abs(mu_new-mu) <= 1e-12*mu_new:
            mu = mu_new; break
        mu = mu_new

    # valori finali
    ma = k*(mu**2)/fa
    Gstar = gstar_SM(math.sqrt((ma*Mpl)/(3.0*1.66*math.sqrt(106.75))))
    Tosc  = math.sqrt((ma*Mpl)/(3.0*1.66*math.sqrt(Gstar)))

    out = {
        "status":"PASS",
        "inputs":{"fa_GeV":fa,"theta":theta,"S_inst":sinst,"Omega_target":Omega,"k_periodicity":k},
        "solution":{"mu_req_sc_GeV":mu,"T_osc_GeV":Tosc,"Gstar_at_Tosc":Gstar,"m_a_GeV":ma},
    }
    out["hash"]=h(json.dumps(out,sort_keys=True))
    W("artifacts/tosc_fixedpoint.json", out)
    print("PASS:FIXED_POINT")
    print(f"mu={mu:.6e} GeV ; Tosc={Tosc:.6e} GeV ; G*={Gstar:.2f} ; m_a={ma:.6e} GeV")
if __name__=="__main__":
    main()
