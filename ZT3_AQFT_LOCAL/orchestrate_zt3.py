#!/usr/bin/env python3
import json, pathlib, sys, hashlib

def sha256_file(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for b in iter(lambda: f.read(65536), b''):
            h.update(b)
    return h.hexdigest()

def jload(p):
    with open(p,"r") as f: return json.load(f)

def banner(t):
    line="="*len(t); print("\n"+line+"\n"+t+"\n"+line+"\n")

def section(t):
    line="="*len(t); print("\n"+t+"\n"+line)

def main():
    base=pathlib.Path(__file__).parent.resolve()
    prof=base/'profiles'/'sources.json'
    if not prof.exists(): print("Manca profiles/sources.json"); sys.exit(2)
    s=jload(prof)

    p_net=(base/pathlib.Path(s["net_ledger"])).resolve()
    p_mic=(base/pathlib.Path(s["microl_ledger"])).resolve()
    p_ch =(base/pathlib.Path(s["channels_ledger"])).resolve()
    p_pza=(base/pathlib.Path(s["pza_killswitch"])).resolve()
    p_mod=(base/pathlib.Path(s["modular_ledger"])).resolve()

    banner("ZT’3 AQFT LOCALE — orchestrator end-to-end con note 'bendate'")

    section("NET → rete locale Haag–Kastler")
    print("• Atteso: isotonia, località, additività, time_slice, covarianza = True.")
    print(">>", str(p_net))
    if not p_net.exists(): print("[LEDGER][net] MISSING:",str(p_net)); sys.exit(1)
    net=jload(p_net)
    net_pass=all(net.get(k) is True for k in ["isotony","locality","additivity","time_slice","covariance"])
    print(f"[LEDGER][net] isotony={net.get('isotony')} | locality={net.get('locality')} | additivity={net.get('additivity')} | time_slice={net.get('time_slice')} | covariance={net.get('covariance')} | PASS={net_pass}")
    print("[HASH]", sha256_file(p_net))

    section("MICROL → Hadamard, nuclearità, split")
    print("• Atteso: hadamard_state, nuclearity, split_property = True.")
    print(">>", str(p_mic))
    if not p_mic.exists(): print("[LEDGER][microl] MISSING:",str(p_mic)); sys.exit(1)
    mic=jload(p_mic)
    mic_pass=(mic.get('hadamard_state') is True and mic.get('nuclearity') is True and mic.get('split_property') is True)
    print(f"[LEDGER][microl] hadamard={mic.get('hadamard_state')} | nuclearity={mic.get('nuclearity')} | split={mic.get('split_property')} | PASS={mic_pass}")
    print("[HASH]", sha256_file(p_mic))

    section("CHANNELS → CPTP locali, Stinespring interna, monotonia")
    print("• Atteso: local_cptp, internal_stinespring, info_monotonicity = True.")
    print(">>", str(p_ch))
    if not p_ch.exists(): print("[LEDGER][channels] MISSING:",str(p_ch)); sys.exit(1)
    ch=jload(p_ch)
    ch_pass=(ch.get('local_cptp') is True and ch.get('internal_stinespring') is True and ch.get('info_monotonicity') is True)
    print(f"[LEDGER][channels] local_cptp={ch.get('local_cptp')} | internal_stinespring={ch.get('internal_stinespring')} | info_monotonicity={ch.get('info_monotonicity')} | PASS={ch_pass}")
    print("[HASH]", sha256_file(p_ch))

    section("PZA → kill-switch fondazionali")
    print("• Atteso: ks_loc, ks_rev, ks_freq, ks_erg = False.")
    print(">>", str(p_pza))
    if not p_pza.exists(): print("[LEDGER][pza] MISSING:",str(p_pza)); sys.exit(1)
    pza=jload(p_pza)
    ks_ok=all(pza.get(k) is False for k in ["ks_loc","ks_rev","ks_freq","ks_erg"])
    print(f"[LEDGER][pza] ks_loc={pza.get('ks_loc')} | ks_rev={pza.get('ks_rev')} | ks_freq={pza.get('ks_freq')} | ks_erg={pza.get('ks_erg')} | PASS={ks_ok}")
    print("[HASH]", sha256_file(p_pza))

    section("MOD → modularità & nuclearità forte (cunei, Tomita–Takesaki)")
    print("• Atteso: wedge_exists, reeh_schlieder, kms_passive, modular_nuclearity, bw_property = True.")
    print(">>", str(p_mod))
    if not p_mod.exists(): print("[LEDGER][mod] MISSING:",str(p_mod)); sys.exit(1)
    mod=jload(p_mod)
    mod_pass = (mod.get('wedge_exists') is True and mod.get('reeh_schlieder') is True and
                mod.get('kms_passive') is True and mod.get('modular_nuclearity') is True and
                mod.get('bw_property') is True)
    print(f"[LEDGER][mod] wedge_exists={mod.get('wedge_exists')} | reeh_schlieder={mod.get('reeh_schlieder')} | kms_passive={mod.get('kms_passive')} | modular_nuclearity={mod.get('modular_nuclearity')} | bw_property={mod.get('bw_property')} | PASS={mod_pass}")
    print("[HASH]", sha256_file(p_mod))

    verdict="PASS" if (net_pass and mic_pass and ch_pass and ks_ok and mod_pass) else "FAIL"
    section("SINTESI GATE ZT’3 + MOD")
    print("• Regola: PASS ⇔ NET ∧ MICROL ∧ CHANNELS ∧ (no PZA) ∧ MOD.")
    print("VERDETTO:", verdict)

    out=base/'certs'/'zt3_aqft_local.json'
    dump={"gate":"ZT3_AQFT_LOCAL","verdict_theory":verdict,
          "inputs":{"net_ledger":str(p_net),"microl_ledger":str(p_mic),
                    "channels_ledger":str(p_ch),"pza_killswitch":str(p_pza),
                    "modular_ledger":str(p_mod)}}
    out.parent.mkdir(parents=True, exist_ok=True); out.write_text(json.dumps(dump, indent=2))
    print("[OUT]", str(out)); print("[HASH]", sha256_file(out))

    final="ZT’3 AQFT+MOD chain: PASS" if verdict=="PASS" else "ZT’3 AQFT+MOD chain: FAIL"
    banner(final); sys.exit(0 if verdict=="PASS" else 1)

if __name__=="__main__":
    main()
