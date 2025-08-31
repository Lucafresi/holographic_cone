import os, sys, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from dsector.freezein import C_eff, Y_infinity, Omega_h2, TR_required

def main(cfgpath):
    cfg = json.load(open(cfgpath))
    Mpl   = float(cfg["Mpl_reduced_GeV"])
    gstar = float(cfg["gstar"])
    gstars= float(cfg["gstars"])
    TR    = float(cfg["freezein"]["TR_GeV"])
    spinX = cfg["dark_state"]["spin"]
    mX    = float(cfg["dark_state"]["mass_GeV"])

    Ceff = C_eff(spinX, include_S=True, include_F=True, include_V=True)
    Y    = Y_infinity(TR, Mpl, gstar, gstars, Ceff)
    Om   = Omega_h2(mX, Y)
    TRreq= TR_required(cfg["target_Omega_h2"], mX, Mpl, gstar, gstars, Ceff)

    outdir = os.path.abspath(os.path.join("cert","dsector_freezein"))
    os.makedirs(outdir, exist_ok=True)
    out = {
        "spin_X": spinX,
        "m_X_GeV": mX,
        "TR_input_GeV": TR,
        "Mpl_reduced_GeV": Mpl,
        "gstar": gstar, "gstars": gstars,
        "C_eff": Ceff,
        "Y_infinity": Y,
        "Omega_h2_at_TR_input": Om,
        "TR_required_for_target_Omega_h2": TRreq,
        "target_Omega_h2": cfg["target_Omega_h2"]
    }
    # salva
    base = os.path.splitext(os.path.basename(cfgpath))[0]
    outpath = os.path.join(outdir, f"result_{base}.json")
    json.dump(out, open(outpath,"w"), indent=2)
    # report
    print("=== D-sector gravitational freeze-in (ledger-locked) ===")
    print(f"X spin = {spinX}")
    print(f"m_X = {mX:.6e} GeV (from 1/z_IR)")
    print(f"C_eff = {Ceff:.6e}")
    print(f"TR (input) = {TR:.3e} GeV")
    print(f"Y_inf = {Y:.6e}")
    print(f"Omega h^2 (at TR input) = {Om:.6e}")
    print(f"TR required for Omega h^2={cfg['target_Omega_h2']}: {TRreq:.3e} GeV")
    print(f"Outputs -> {outpath}")

if __name__=="__main__":
    if len(sys.argv)!=2:
        print("Uso: python scripts/dsector_run.py <config.json>")
        raise SystemExit(1)
    main(sys.argv[1])
