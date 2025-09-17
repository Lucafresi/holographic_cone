#!/usr/bin/env python3
import json, pathlib, sys, hashlib

def sha256_file(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for b in iter(lambda: f.read(65536), b''):
            h.update(b)
    return h.hexdigest()

def jload(p):
    with open(p,"r") as f:
        return json.load(f)

def banner(t):
    line="="*len(t); print("\n"+line+"\n"+t+"\n"+line+"\n")

def section(t):
    line="="*len(t); print("\n"+t+"\n"+line)

def main():
    base=pathlib.Path(__file__).parent.resolve()
    prof=base/'profiles'/'sources.json'
    if not prof.exists():
        print("Manca profiles/sources.json"); sys.exit(2)
    s=jload(prof)

    p_frw=(base/ pathlib.Path(s["frw_reduction_ledger"])).resolve()
    p_bg =(base/ pathlib.Path(s["background_ledger"])).resolve()
    p_sg =(base/ pathlib.Path(s["signs_audit"])).resolve()
    p_kk =(base/ pathlib.Path(s["kk_tensor_ledger"])).resolve()

    banner("C0 FRW CLOSED — orchestrator end-to-end con note 'bendate'")

    section("FRW ridotta (chiusura funzionale)")
    print("• Atteso: free_functions_present=False; radion_closed=True (locked|dynamic_closed).")
    print(">>", str(p_frw))
    if not p_frw.exists(): print("[LEDGER][frw] MISSING:",str(p_frw)); sys.exit(1)
    frw=jload(p_frw)
    frw_pass=(frw.get("free_functions_present") is False and frw.get("radion_closed") is True and frw.get("by_signs_ok") is True and frw.get("junctions_ok") is True and frw.get("H2_from_bulk_ct_only") is True)
    print(f"[LEDGER][frw] free_functions_present={frw.get('free_functions_present')} | radion_closed={frw.get('radion_closed')} ({frw.get('radion_mode')}) | by_signs_ok={frw.get('by_signs_ok')} | junctions_ok={frw.get('junctions_ok')} | H2_from_bulk_ct_only={frw.get('H2_from_bulk_ct_only')} | PASS={frw_pass}")
    print("[HASH]", sha256_file(p_frw))

    section("Λ locale di brana assente (consistenza con G1)")
    print("• Atteso: H2_brane_local=0.0 on-shell.")
    print(">>", str(p_bg))
    if not p_bg.exists(): print("[LEDGER][background] MISSING:",str(p_bg)); sys.exit(1)
    bg=jload(p_bg)
    bg_pass=(bg.get("H2_brane_local")==0.0)
    print(f"[LEDGER][background] H2_brane_local={bg.get('H2_brane_local')} | PASS={bg_pass}")
    print("[HASH]", sha256_file(p_bg))

    section("Segni BY/giunzioni (Gate-E)")
    print("• Atteso: signs_ok=True.")
    print(">>", str(p_sg))
    if not p_sg.exists(): print("[LEDGER][signs] MISSING:",str(p_sg)); sys.exit(1)
    sg=jload(p_sg)
    sg_pass=(sg.get("signs_ok") is True)
    print(f"[LEDGER][signs] signs_ok={sg.get('signs_ok')} | PASS={sg_pass}")
    print("[HASH]", sha256_file(p_sg))

    section("Coerenza canale tensoriale (opzionale)")
    print(">>", str(p_kk))
    kk_pass=True
    if p_kk.exists():
        kk=jload(p_kk)
        kk_pass=(kk.get("graviton_localized") is True and kk.get("self_adjoint") is True and kk.get("spectrum_bounded_below") is True)
        print(f"[LEDGER][kk] localized={kk.get('graviton_localized')} | self_adjoint={kk.get('self_adjoint')} | bounded={kk.get('spectrum_bounded_below')} | PASS={kk_pass}")

    verdict = ("PASS" if (frw_pass and bg_pass and sg_pass and kk_pass) else "FAIL")
    section("SINTESI GATE C0")
    print("VERDETTO:", verdict)

    dump={
      "gate": "C0_FRW_CLOSED",
      "verdict_theory": verdict,
      "inputs": {
        "frw_reduction_ledger": str(p_frw),
        "background_ledger": str(p_bg),
        "signs_audit": str(p_sg),
        "kk_tensor_ledger": str(p_kk) if p_kk.exists() else None
      }
    }
    out=(base/'certs'/'c0_frw_closed.json')
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(dump, indent=2))
    print("[OUT]", str(out))
    print("[HASH]", sha256_file(out))

    final="C0 FRW chain: PASS" if verdict=="PASS" else "C0 FRW chain: FAIL"
    banner(final)
    sys.exit(0 if verdict=="PASS" else 1)

if __name__=="__main__":
    main()
