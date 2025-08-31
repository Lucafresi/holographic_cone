# ==== AUTO-INSERTED GUARD: topo OFF short-circuit ====
def _guard_topo_off(cfg_path):
    import json, pathlib
    cfg = json.load(open(cfg_path))
    def _pick(d, *keys):
        for k in keys:
            if isinstance(d, dict) and k in d:
                d = d[k]
            else:
                return None
        return d
    ell = _pick(cfg, "ell") or _pick(cfg, "topology","ell") or 0
    try:
        ell = int(ell)
    except Exception:
        ell = 0
    if ell == 0:
        base = pathlib.Path("cert/dsector_freezein")
        base.mkdir(parents=True, exist_ok=True)
        outp = base / "result_dsector_freezein_topo_from_ledger.json"
        out = {
            "two_group_active": False,
            "ell": 0, "kappa_a": 0.0, "g5_X_sq": 0.0,
            "reason": "gs_required=false ⇒ 2-group OFF"
        }
        # eredita m_X se già presente da altri certificati
        for tag in ("scalar","fermion","vector","topo"):
            q = base / f"result_dsector_freezein_{tag}_from_ledger.json"
            if q.exists():
                try:
                    mx = json.load(open(q)).get("m_X_GeV")
                    if mx is not None:
                        out["m_X_GeV"] = mx
                        break
                except Exception:
                    pass
        outp.write_text(json.dumps(out, indent=2))
        print("[topology] ℓ=0 ⇒ 2-group OFF. Scritto", outp)
        return True
    return False
# ==== END GUARD ====
import os, sys, json, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from dsector.topo_mass import mX_stueckelberg_from_ledger
from dsector.freezein import C_eff, Y_infinity, Omega_h2, TR_required



def main(cfgpath):
    if _guard_topo_off(cfgpath):
        return
    cfg = json.load(open(cfgpath))

    # RS geometry (ledger)
    L   = float(cfg["ledger_RS"]["L"])
    zUV = float(cfg["ledger_RS"]["z_UV"])
    zIR = float(cfg["ledger_RS"]["z_IR"])

    # topo ledger (tutti DEVONO essere presenti e fisici)
    tl  = cfg["topo_ledger"]
    g5sq   = float(tl["g5_X_sq"])
    kap    = float(tl["kappa_a"])
    ell    = int(tl["ell"])
    profile= tl.get("profile","flat")
    zstar  = tl.get("z_star", None)
    rB     = tl.get("rB_coeff", None)
    if profile=="brane":
        if zstar not in ("UV","IR") or (rB is None):
            raise SystemExit("profile=brane richiede z_star in {UV,IR} e rB_coeff>0 (ledger)")

    # massa topologica dal ledger
    mX, aux = mX_stueckelberg_from_ledger(
        g5_sq=g5sq, kappa_a=kap, L=L, zUV=zUV, zIR=zIR, ell=ell,
        profile=profile, z_star=zstar, rB_coeff=rB
    )

    # cosmologia
    Mpl   = float(cfg["Mpl_reduced_GeV"])
    gstar = float(cfg["gstar"])
    gstars= float(cfg["gstars"])
    TR    = float(cfg["freezein"]["TR_GeV"])
    spinX = cfg["dark_state"]["spin"]

    Ceff  = C_eff(spinX, include_S=True, include_F=True, include_V=True)
    Y     = Y_infinity(TR, Mpl, gstar, gstars, Ceff)
    Om    = Omega_h2(mX, Y)
    TRreq = TR_required(cfg["target_Omega_h2"], mX, Mpl, gstar, gstars, Ceff)

    outdir = os.path.abspath(os.path.join("cert","dsector_freezein"))
    os.makedirs(outdir, exist_ok=True)
    base = os.path.splitext(os.path.basename(cfgpath))[0]
    out = {
        "spin_X": spinX,
        "m_X_GeV_topological": mX,
        "stueckelberg_breakdown": aux,
        "TR_input_GeV": TR,
        "Mpl_reduced_GeV": Mpl,
        "gstar": gstar, "gstars": gstars,
        "C_eff": Ceff,
        "Y_infinity": Y,
        "Omega_h2_at_TR_input": Om,
        "TR_required_for_target_Omega_h2": TRreq,
        "target_Omega_h2": cfg["target_Omega_h2"],
        "ledger_RS": cfg["ledger_RS"],
        "topo_ledger_used": tl
    }
    outpath = os.path.join(outdir, f"result_{base}.json")
    json.dump(out, open(outpath,"w"), indent=2)

    print("=== D-sector topological mass + gravitational freeze-in (ledger-locked) ===")
    print(f"X spin = {spinX}")
    print(f"m_X (Stückelberg, ledger) = {mX:.6e} GeV")
    print(f"g4^2 = {aux['g4_sq']:.6e}   IB = {aux['IB']:.6e}   ZB = {aux['ZB']:.6e}")
    print(f"C_eff = {Ceff:.6e}")
    print(f"TR (input) = {TR:.3e} GeV")
    print(f"Y_inf = {Y:.6e}")
    print(f"Omega h^2 (at TR input) = {Om:.6e}")
    print(f"TR required for Omega h^2={cfg['target_Omega_h2']}: {TRreq:.3e} GeV")
    print(f"Outputs -> {outpath}")

if __name__=="__main__":
    if len(sys.argv)!=2:
        print("Uso: python scripts/dsector_topo_run.py <config.json>")
        raise SystemExit(1)
    main(sys.argv[1])
