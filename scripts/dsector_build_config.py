import json, os, sys

def read_zIR():
    # prova 1: usa configs/gate_nu_ledger_UV.json (già presente)
    p = os.path.join("configs", "gate_nu_ledger_UV.json")
    if os.path.exists(p):
        cfg = json.load(open(p))
        return float(cfg["geometry"]["z_IR"])
    # prova 2: usa ledger_scan.json se presente
    p2 = os.path.join("cert","gate_nu","ledger_scan.json")
    if os.path.exists(p2):
        scan = json.load(open(p2))
        return float(scan["z_IR"])
    raise SystemExit("Impossibile ricavare z_IR dal ledger.")

def main(spin_X: str, outpath: str):
    zIR = read_zIR()
    mX = 1.0 / zIR  # GeV (unità del tuo repo: z in GeV^{-1})
    cfg = {
        "Mpl_reduced_GeV": 2.435e18,
        "gstar": 106.75,
        "gstars": 106.75,
        "target_Omega_h2": 0.12,
        "dark_state": {
            "spin": spin_X,          # "scalar" | "fermion" | "vector"
            "mass_GeV": mX
        },
        "freezein": {
            "TR_GeV": 1.0e15        # valore di riferimento (verrà anche invertito)
        }
    }
    os.makedirs(os.path.dirname(outpath), exist_ok=True)
    json.dump(cfg, open(outpath,"w"), indent=2)
    print(f"Wrote: {outpath}  (m_X = {mX:.6e} GeV from z_IR={zIR})")

if __name__=="__main__":
    if len(sys.argv)!=3:
        print("Uso: python scripts/dsector_build_config.py <scalar|fermion|vector> <out.json>")
        raise SystemExit(1)
    main(sys.argv[1], sys.argv[2])
