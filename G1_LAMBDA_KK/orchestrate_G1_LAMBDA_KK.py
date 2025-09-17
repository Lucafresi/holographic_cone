#!/usr/bin/env python3
import json, subprocess, pathlib, sys, hashlib

def sha256_file(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for b in iter(lambda: f.read(65536), b''):
            h.update(b)
    return h.hexdigest()

def banner(t):
    line="="*len(t)
    print("\n"+line+"\n"+t+"\n"+line+"\n")

def section(t):
    line="="*len(t)
    print("\n"+t+"\n"+line)

def resolve(base, p):
    q=pathlib.Path(p)
    return q if q.is_absolute() else (base/q).resolve()

def load_json(p):
    with open(p,"r") as f:
        return json.load(f)

def main():
    base=pathlib.Path(__file__).parent.resolve()
    prof=base/'profiles'/'sources.json'
    src=base/'src'/'delta_kk_locking_orchestrator.py'
    cert=base/'certs'/'g1_lambda_kk_lock.json'
    if not prof.exists():
        print("Manca profiles/sources.json"); sys.exit(2)
    s=load_json(prof)
    p_bg=resolve(base, s["background_ledger"])
    p_kk=resolve(base, s["kk_tensor_ledger"])
    p_sg=resolve(base, s["signs_audit"])

    banner("G1 Λ–KK ORCHESTRATOR — esecuzione end-to-end con note 'bendate'")

    section("BACKGROUND → bilancio BY e frazione di brana")
    print("• Cosa guardare: assenza on-shell di contributi locali di brana a H^2.")
    print("• Atteso: H2_brane_local = 0.0 per identità; nessuna manopola.")
    print(">>",str(p_bg))
    if not p_bg.exists():
        print("[LEDGER][background] MISSING:",str(p_bg)); sys.exit(1)
    bg=load_json(p_bg)
    bg_pass = (bg.get("H2_brane_local",None)==0.0 and bg.get("H2_brane_local_proof",None) in ["identity_on_shell","exact_cancellation"])
    print(f"[LEDGER][background] H2_brane_local={bg.get('H2_brane_local')} | proof={bg.get('H2_brane_local_proof')} | PASS={bg_pass}")
    print("[HASH]",sha256_file(p_bg))

    section("SPETTRO TENSORIALE → locking KK")
    print("• Cosa guardare: localizzazione gravitone e vincolo strutturale m_KK ~ H.")
    print("• Atteso: graviton_localized=True; self_adjoint=True; spectrum_bounded_below=True; locking_statement_verified=True.")
    print(">>",str(p_kk))
    if not p_kk.exists():
        print("[LEDGER][kk] MISSING:",str(p_kk)); sys.exit(1)
    kk=load_json(p_kk)
    kk_pass = (kk.get("graviton_localized") is True and kk.get("self_adjoint") is True and kk.get("spectrum_bounded_below") is True and kk.get("locking_statement_verified") is True)
    print(f"[LEDGER][kk] graviton_localized={kk.get('graviton_localized')} | self_adjoint={kk.get('self_adjoint')} | bounded={kk.get('spectrum_bounded_below')} | locking={kk.get('locking_statement_verified')} | PASS={kk_pass}")
    print("[HASH]",sha256_file(p_kk))

    section("CONVENZIONI DI SEGNO → audit")
    print("• Cosa guardare: coerenza segni BY/giunzioni già fissati nel Gate-E.")
    print("• Atteso: signs_ok=True.")
    print(">>",str(p_sg))
    if not p_sg.exists():
        print("[LEDGER][signs] MISSING:",str(p_sg)); sys.exit(1)
    sg=load_json(p_sg)
    sg_pass = (sg.get("signs_ok") is True)
    print(f"[LEDGER][signs] signs_ok={sg.get('signs_ok')} | PASS={sg_pass}")
    print("[HASH]",sha256_file(p_sg))

    if not src.exists():
        print("Manca",str(src)); sys.exit(2)
    cert.parent.mkdir(parents=True, exist_ok=True)

    section("SINTESI GATE → esecuzione combinata")
    print("• Cosa fa: combina i tre controlli in un verdetto binario teorico.")
    print("• Atteso: PASS solo se tutti e tre i blocchi sono PASS e B_Lambda=0.0.")
    run = subprocess.run([sys.executable, str(src), str(prof), str(cert)], capture_output=True, text=True)
    if run.stdout: print(run.stdout.strip())
    if run.stderr: print(run.stderr.strip())
    if not cert.exists():
        print("[CERT] non prodotto:",str(cert)); sys.exit(2)
    data=load_json(cert)
    verdict=data.get("verdict_theory","FAIL")
    print("[CERT] PASS =", (verdict=="PASS"))
    print("[OUT]", str(cert))
    print("[HASH]", sha256_file(cert))
    section("Full JSON dump (audit)")
    print(json.dumps(data, indent=2, ensure_ascii=False))
    final="G1 Λ–KK chain: PASS" if verdict=="PASS" else "G1 Λ–KK chain: FAIL"
    banner(final)
    sys.exit(0 if verdict=="PASS" else 1)

if __name__=="__main__":
    main()
