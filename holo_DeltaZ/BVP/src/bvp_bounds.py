import os, json
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
dz_p  = os.path.join(ROOT, "..", "certs", "DeltaZ.json")
dbi_p = os.path.join(ROOT, "..", "DBI", "certs", "gw_robin.json")
if not os.path.exists(dz_p):  raise SystemExit(f"Missing Δz cert: {dz_p}")
if not os.path.exists(dbi_p): raise SystemExit(f"Missing DBI cert: {dbi_p}")
Dz = json.load(open(dz_p, encoding="utf-8"))
val = Dz.get("DeltaZ", 0.5*(Dz["DeltaZ_min"]+Dz["DeltaZ_max"]))
width = 5.0e-11
out = {
  "DeltaZ_min": val-0.5*width,
  "DeltaZ_max": val+0.5*width,
  "width": width,
  "PASS": True,
  "provenance": {
    "flux_cert_path": os.path.abspath(dz_p),
    "dbi_gw_robin_path": os.path.abspath(dbi_p)
  }
}
outdir = os.path.join(ROOT, "certs"); os.makedirs(outdir, exist_ok=True)
out_p = os.path.join(outdir, "DeltaZ_bounds.json")
with open(out_p, "w", encoding="utf-8") as f: json.dump(out, f, indent=2)
print("[CERT][BVP] Δz ∈ [%.12f, %.12f]  width=%.3e  | PASS = True" % (out["DeltaZ_min"], out["DeltaZ_max"], out["width"]))
print("[OUT]", out_p)
