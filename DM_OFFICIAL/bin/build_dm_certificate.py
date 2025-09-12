#!/usr/bin/env python3
import json, os, hashlib
def h(s): return hashlib.sha256(s.encode()).hexdigest()
def R(p):
    with open(p,"r") as f: return json.load(f)
def W(x,p):
    with open(p,"w") as f: json.dump(x,f,indent=2)

def main():
    os.makedirs("artifacts", exist_ok=True)
    theta = R("artifacts/theta_ledger.json")
    fa    = R("artifacts/fa.json")
    sinst = R("artifacts/sinst_vs_sreq.json")
    mu    = R("artifacts/mu_required.json")
    msy   = R("artifacts/msy_geometry.json")

    # Consistenza discreta
    assert sinst["status"]=="PASS"
    N, q = sinst["chosen"]["N"], sinst["chosen"]["q"]
    S    = sinst["chosen"]["S_inst"]

    # Griglia μ_req (nessuna manopola: {theta} ledger-fixed, G* discreto)
    grid = mu["grid"]

    cert = {
      "status":"PASS",
      "uv_toric":"CY_cone_on_dP3",
      "flux_integer_N": N,
      "wrapping_q": q,
      "S_inst": S,
      "theta_allowed_rad": theta["allowed_thetas_rad"],
      "fa_GeV": fa["fa_GeV"],
      "msy_volumes": msy["volumes"],
      "mu_required_grid": grid,
      # relazione deterministica per Ms: Ms = mu/eta (eta da §IV.1.RS)
      "Ms_relation":"Ms = mu_required / eta",
      "hash": None
    }
    cert["hash"] = h(json.dumps(cert, sort_keys=True))
    W(cert, "artifacts/dm_certificate.json")
    print("PASS:DM_CERT"); print(f"Promote N={N} (discrete), q={q}; S_inst={S:.6f}")
if __name__=="__main__": main()
