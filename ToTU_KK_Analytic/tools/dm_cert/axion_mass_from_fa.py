#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json, argparse

def load(p): 
    with open(p,"r") as f: return json.load(f)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fa_file", required=True, help="JSON con f_a_GeV")
    ap.add_argument("--out",      required=True, help="Output JSON con m_a (eV/GeV)")
    args = ap.parse_args()

    fa_GeV = float(load(args.fa_file)["f_a_GeV"])
    # m_a ≈ 5.7 μeV * (1e12 GeV / f_a)
    m_eV  = 5.7e-6 * (1.0e12 / fa_GeV)        # in eV
    m_GeV = m_eV * 1.0e-9

    out = {
        "schema_version": 1,
        "fa_GeV": fa_GeV,
        "ma_eV": m_eV,
        "ma_GeV": m_GeV,
        "convention": "QCD axion: m_a ≈ 5.7 μeV × (1e12 GeV / f_a)"
    }
    with open(args.out,"w") as f: json.dump(out,f,indent=2)
    print(f"[D4] wrote {args.out}")
    print(f"[D4] m_a = {m_eV:.3e} eV = {m_GeV:.3e} GeV  (from f_a = {fa_GeV:.3e} GeV)")
if __name__=="__main__": main()
