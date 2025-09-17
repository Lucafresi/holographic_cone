import os, json
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
dz_p  = os.path.abspath(os.path.join(ROOT, "..", "certs", "DeltaZ.json"))
dbi_p = os.path.abspath(os.path.join(ROOT, "..", "DBI", "certs", "gw_robin.json"))
vol_p = os.path.abspath(os.path.join(ROOT, "..", "geom", "certs", "volumes.json"))
need = [dz_p, dbi_p, vol_p]
fails = [p for p in need if not os.path.exists(p)]
PASS = not fails
out = {"PASS": PASS}
if not PASS:
  out["FAIL_reasons"] = fails
outdir = os.path.join(ROOT, "certs"); os.makedirs(outdir, exist_ok=True)
out_p = os.path.join(outdir, "tadpole.json")
with open(out_p,"w",encoding="utf-8") as f: json.dump(out, f, indent=2)
print("[CERT][tad] ->", out_p)
print(json.dumps(out, indent=2))
if not PASS: raise SystemExit(1)
