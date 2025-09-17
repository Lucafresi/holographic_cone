#!/usr/bin/env python3
import json, sys, pathlib, hashlib

def load_json(p):
    with open(p, "r") as f:
        return json.load(f)

def sha256_file(p):
    h = hashlib.sha256()
    with open(p,'rb') as f:
        for b in iter(lambda: f.read(65536), b''):
            h.update(b)
    return h.hexdigest()

def main():
    if len(sys.argv)!=3:
        print("Usage: delta_kk_locking_orchestrator.py <sources.json> <out.json>")
        sys.exit(2)
    sources_path = pathlib.Path(sys.argv[1])
    out_path = pathlib.Path(sys.argv[2])
    print("G1 Λ–KK Locking: avvio")
    if not sources_path.exists():
        print("MISSING sources.json")
        sys.exit(1)
    s = load_json(sources_path)
    required = ["background_ledger","kk_tensor_ledger","signs_audit"]
    for k in required:
        p = pathlib.Path(s[k])
        if not p.exists():
            print("MISSING DEPENDENCY:",k,str(p))
            result = {"gate":"G1_Lambda_KK_Locking","verdict_theory":"FAIL","reason":"missing_dependency","missing":k}
            out_path.parent.mkdir(parents=True, exist_ok=True)
            with open(out_path,'w') as f: json.dump(result,f,indent=2)
            sys.exit(1)
    bg = load_json(s["background_ledger"])
    kk = load_json(s["kk_tensor_ledger"])
    sg = load_json(s["signs_audit"])
    print("Analisi: bilancio BY e termine locale di brana")
    H2_brane_local = bg.get("H2_brane_local",None)
    proof = bg.get("H2_brane_local_proof",None)
    graviton_localized = kk.get("graviton_localized",None)
    self_adjoint = kk.get("self_adjoint",None)
    bounded = kk.get("spectrum_bounded_below",None)
    locking_verified = kk.get("locking_statement_verified",None)
    signs_ok = sg.get("signs_ok",None)
    print("Interpretazione: H2_brane_local deve essere 0.0 per identità on-shell")
    print("Valori:",{"H2_brane_local":H2_brane_local,"proof":proof,"graviton_localized":graviton_localized,"self_adjoint":self_adjoint,"bounded":bounded,"locking_verified":locking_verified,"signs_ok":signs_ok})
    pass_cond = (H2_brane_local==0.0 and proof in ["identity_on_shell","exact_cancellation"] and graviton_localized is True and self_adjoint is True and bounded is True and locking_verified is True and signs_ok is True)
    verdict = "PASS" if pass_cond else "FAIL"
    print("Esito teorico:",verdict)
    result = {
        "gate":"G1_Lambda_KK_Locking",
        "geometry_class":"RS_like",
        "graviton_localized":bool(graviton_localized),
        "brown_york":{"UV":bg.get("BY_UV"),"IR":bg.get("BY_IR")},
        "curvature_sources_partition":{
            "H2_bulk_global":bg.get("H2_bulk_global"),
            "H2_counterterms":bg.get("H2_counterterms"),
            "H2_brane_local":H2_brane_local
        },
        "B_Lambda":0.0 if H2_brane_local==0.0 else "nonzero",
        "sturm_liouville":{"self_adjoint":bool(self_adjoint),"spectrum_bounded_below":bool(bounded)},
        "locking_statement_verified":bool(locking_verified),
        "signs_ok":bool(signs_ok),
        "verdict_theory":verdict,
        "inputs_sha256":{
            "background_ledger":sha256_file(s["background_ledger"]),
            "kk_tensor_ledger":sha256_file(s["kk_tensor_ledger"]),
            "signs_audit":sha256_file(s["signs_audit"])
        }
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path,'w') as f: json.dump(result,f,indent=2)
    print("Report salvato:",str(out_path))

if __name__=="__main__":
    main()
