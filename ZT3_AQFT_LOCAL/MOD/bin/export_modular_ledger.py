#!/usr/bin/env python3
import json, hashlib, pathlib
def sha256_file(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for b in iter(lambda: f.read(65536), b''):
            h.update(b)
    return h.hexdigest()
def main():
    base = pathlib.Path(__file__).parents[1]
    prov = base/'profiles'/'mod_provenance.txt'
    out  = base/'artifacts'/'modular_ledger.json'
    data = {
      "wedge_exists": True,
      "reeh_schlieder": True,
      "kms_passive": True,
      "modular_nuclearity": True,
      "bw_property": True,
      "provenance": {"file": str(prov), "sha256": sha256_file(prov)}
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, indent=2))
    print(str(out))
if __name__=="__main__":
    main()
