import os, json, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
CERT = ROOT/"cert"/"dsector_freezein"
CONFIGS = ROOT/"configs"

def read_RS_geometry():
    # Ricava L, zUV, zIR come abbiamo già fatto per Gate-ν (usa gli stessi file)
    # 1) configs/gate_nu_ledger_UV.json
    p = ROOT/"configs"/"gate_nu_ledger_UV.json"
    if p.exists():
        cfg = json.load(open(p))
        g = cfg["geometry"]
        return float(g["L"]), float(g["z_UV"]), float(g["z_IR"])
    # 2) cert/gate_nu/ledger_scan.json
    p2 = ROOT/"cert"/"gate_nu"/"ledger_scan.json"
    if p2.exists():
        sc = json.load(open(p2))
        return float(sc["L"]), float(sc["z_UV"]), float(sc["z_IR"])
    raise SystemExit("Impossibile recuperare (L,z_UV,z_IR) dal ledger.")

def probe_two_group_ledger():
    """
    Cerca parametri 2-group/Stückelberg nel repo.
    Se non trovati, genera template con MISSING_*.
    Attesi (ledger):
      - g5_X_sq   : costante di gauge 5D (quadrato)
      - kappa_a   : coeff. cinetico 5D della 2-forma (positivo)
      - ell       : livello intero BF/2-group (non nullo)
      - profile   : 'flat' oppure 'brane'
      - z_star    : 'UV'/'IR' (solo se profile='brane')
      - rB_coeff  : coefficiente di brana per B (solo se profile='brane')
    """
    # Possibili posizioni "canoniche"
    candidates = [
        ROOT/"configs"/"two_group_ledger.json",
        ROOT/"configs"/"u1x_2group.json",
        ROOT/"cert"/"two_group"/"ledger_scan.json",
    ]
    for p in candidates:
        if p.exists():
            return json.load(open(p))
    # Non trovato: torna un template dichiarato (nessun default)
    return {
        "g5_X_sq": "MISSING_g5_X_sq",
        "kappa_a": "MISSING_kappa_a",
        "ell":     "MISSING_ell",
        "profile": "flat",  # struttura minima; cambiare a 'brane' se da ledger
        # "z_star": "UV" or "IR"   (se profile='brane')
        # "rB_coeff": ...          (se profile='brane')
    }

def main(spinX, outpath):
    L, zUV, zIR = read_RS_geometry()
    tg = probe_two_group_ledger()

    # Verifica campi ledger richiesti (senza ad-hoc)
    missing = []
    def need_num(x): 
        return isinstance(x,(int,float)) and (x>0 if x!="ell" else True)

    g5sq   = tg.get("g5_X_sq", None)
    kap    = tg.get("kappa_a", None)
    ell    = tg.get("ell", None)
    profile= tg.get("profile","flat")
    zstar  = tg.get("z_star", None)
    rB     = tg.get("rB_coeff", None)

    if not isinstance(g5sq,(int,float)) or g5sq<=0: missing.append("g5_X_sq")
    if not isinstance(kap,(int,float)) or kap<=0:   missing.append("kappa_a")
    if not isinstance(ell,int) or ell==0:           missing.append("ell (integer non nullo)")
    if profile not in ("flat","brane"):             missing.append("profile in {flat,brane}")
    if profile=="brane":
        if zstar not in ("UV","IR"): missing.append("z_star in {UV,IR} (profile=brane)")
        if not isinstance(rB,(int,float)) or rB<=0: missing.append("rB_coeff (profile=brane)")

    cfg = {
        "ledger_RS": {"L": L, "z_UV": zUV, "z_IR": zIR},
        "topo_ledger": tg,  # lo includiamo "as-is" per trasparenza
        "dark_state": {"spin": spinX},  # la massa verrà calcolata a runtime
        "Mpl_reduced_GeV": 2.435e18,
        "gstar": 106.75, "gstars": 106.75,
        "target_Omega_h2": 0.12,
        "freezein": {"TR_GeV": 1.0e15}
    }

    out = ROOT/outpath
    out.parent.mkdir(parents=True, exist_ok=True)
    json.dump(cfg, open(out,"w"), indent=2)
    print(f"Wrote: {out}")

    if missing:
        # Scriviamo anche un blocco certificato che spiega cosa manca
        CERT.mkdir(parents=True, exist_ok=True)
        miss = {
            "message": "Ledger incompleto per massa Stückelberg; compilare i campi mancanti e rilanciare.",
            "missing_fields": missing,
            "where_to_put_them": [str(p) for p in [
                ROOT/'configs'/'two_group_ledger.json',
                ROOT/'configs'/'u1x_2group.json'
            ]],
            "copied_into_config": str(out)
        }
        json.dump(miss, open(CERT/"topo_missing.json","w"), indent=2)
        print("\n[HARD-FAIL] Mancano campi di ledger per il ramo topologico:", ", ".join(missing))
        print("Ho scritto una copia/placeholder nel file di config sopra. Compilala nel repo e rilancia.")
        raise SystemExit(2)

if __name__=="__main__":
    if len(sys.argv)!=3:
        print("Uso: python scripts/dsector_topo_build_config.py <scalar|fermion|vector> <out.json>")
        raise SystemExit(1)
    main(sys.argv[1], sys.argv[2])
