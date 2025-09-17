import os, sys, json, subprocess

ROOT = os.path.abspath(os.path.dirname(__file__))

# ---------- utils ----------
def banner(title):
    line = "=" * len(title)
    print("\n" + line)
    print(title)
    print(line)

def run(rel, title=None, what=None, expect=None):
    path = os.path.join(ROOT, rel)
    if title:
        banner(title)
    if what:
        print("• Cosa fa:", what)
    if expect:
        print("• Atteso (teoria):", expect)
    print(">>", path)
    subprocess.check_call([sys.executable, path])

def show(rel):
    p = os.path.join(ROOT, rel) if not os.path.isabs(rel) else rel
    ap = os.path.abspath(p)
    print(f"\n[OUT] {ap}:")
    if os.path.exists(p):
        with open(p, encoding="utf-8") as f:
            print(f.read())
        return True
    else:
        print("MISSING")
        return False

def jload(rel):
    p = os.path.join(ROOT, rel) if not os.path.isabs(rel) else rel
    with open(p, encoding="utf-8") as f:
        return json.load(f)

# ---------- guardrail checks (tecnici, non interpretativi) ----------
def strict_checks():
    fails = []
    # file indispensabili (devono esistere; se hanno "PASS" deve essere True)
    critical = [
        "certs/DeltaZ.json",
        "DBI/certs/gw_robin.json",
        "BVP/certs/DeltaZ_bounds.json",
        "geom/certs/volumes.json",
        "tad/certs/tadpole.json",
        "UVg/certs/alpha_U.json",
        "UVg_abelian/certs/alphaY_U.json",
        "spectrum/certs/Mstar.json",
        "kY/certs/kY/sigma3/cs_integrality.json",
        "kY/certs/kY/sigma3/orbifold_check.json",
        "kY/certs/kY/sigma3/snf.json",
    ]
    for rel in critical:
        p = os.path.join(ROOT, rel)
        if not os.path.exists(p):
            fails.append(f"MISSING: {rel}")
            continue
        try:
            j = jload(rel)
            if isinstance(j, dict) and "PASS" in j and j["PASS"] is not True:
                fails.append(f"PASS=False: {rel}")
        except Exception:
            # tutti questi sono JSON; qualunque errore di parsing è fail
            fails.append(f"UNREADABLE JSON: {rel}")

    # ampiezza bounds Δz: guardrail puramente numerico del test BVP
    try:
        bvp = jload("BVP/certs/DeltaZ_bounds.json")
        width = float(bvp.get("width", 1.0))
        if width > 1e-9:
            fails.append(f"BVP width too large: {width}")
    except Exception:
        fails.append("Cannot read BVP bounds for width check")

    return fails

def main():
    banner("Δz ORCHESTRATOR — esecuzione end-to-end con note 'bendate'")

    run(
        "src/flux_to_DeltaZ.py",
        title="FLUX → Δz",
        what="Deriva Δz dai flussi (ledger-only); nessun input IR.",
        expect="Un JSON con DeltaZ (o DeltaZ_min/DeltaZ_max) e un flag PASS."
    )

    run(
        "DBI/src/derive_robin.py",
        title="DBI/WZ → condizioni al bordo (gauge)",
        what="Deduce i coefficienti di Robin dallo stack D7 e Σ3.",
        expect="Parametri di bordo fissati; nessun knob locale p^2; presenza di r_gauge."
    )

    run(
        "BVP/src/rebuild_all.py",
        title="BVP su Δz",
        what="Risoluzione del problema ai bordi con le BC di sopra.",
        expect="Un intervallo stretto per Δz e un’indicazione PASS tecnica del solver."
    )

    run(
        "geom/src/volumes_y21.py",
        title="Volumi MSY",
        what="Calcola Vol(X5) e Vol(Σ3) in forma chiusa per Y^{2,1}.",
        expect="Numeri deterministici; nessun grado di libertà."
    )

    run(
        "tad/src/derive_tadpole.py",
        title="Consistenze globali",
        what="Controlli di tadpole/2-group compatibili con la scelta di Σ3.",
        expect="Un JSON con PASS/FAIL; nessun input IR."
    )

    run(
        "UVg/src/alpha_abs.py",
        title="Assoluto non-abeliano",
        what="Applica la formula chiusa per α^{-1} usando Δz e volumi MSY.",
        expect="Un JSON con α^{-1} non-abeliano e un flag di unificazione/consistenza."
    )

    run(
        "UVg_abelian/src/alphaY_abs.py",
        title="Ipercarica UV (embed kY)",
        what="Ottiene α_Y^{-1} dall’embed hypercharge con kY certificato da Σ3.",
        expect="Un JSON con α_Y e kY; nessun input IR."
    )

    run(
        "spectrum/src/first_mode.py",
        title="Primo modo gauge (+,+)",
        what="Usa BC e Δz per il primo autovalore (forma chiusa con j_{0,1}).",
        expect="Un JSON con Mhat definito da j_{0,1}·e^{-Δz}."
    )

    banner("Full JSON dump (audit)")
    for rel in [
        "certs/DeltaZ.json",
        "DBI/certs/gw_robin.json",
        "BVP/certs/DeltaZ_bounds.json",
        "geom/certs/volumes.json",
        "tad/certs/tadpole.json",
        "UVg/certs/alpha_U.json",
        "UVg_abelian/certs/alphaY_U.json",
        "spectrum/certs/Mstar.json",
        "kY/certs/kY/sigma3/snf.json",
        "kY/certs/kY/sigma3/cs_integrality.json",
        "kY/certs/kY/sigma3/orbifold_check.json",
        "certs/input_hashes.json",
    ]:
        show(rel)

    # guardrail tecnici finali
    fails = strict_checks()
    if fails:
        banner("Δz chain: FAIL (guardrail)")
        for f in fails: print(" -", f)
        sys.exit(2)
    else:
        banner("Δz chain: PASS")

if __name__ == "__main__":
    main()
