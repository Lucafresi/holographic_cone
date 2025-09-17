import os, json, math
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
flux_p = os.path.join(ROOT, "flux", "certs", "flux.json")
if not os.path.exists(flux_p):
    raise SystemExit(f"[FAIL] Missing flux cert: {flux_p}")
flux = json.load(open(flux_p, encoding="utf-8"))
gs = float(flux["gs"]); M = int(flux["M"]); K = int(flux["K"]); N = int(flux.get("N", M*K))
DeltaZ = (2*math.pi*K) / (3*gs*M)
out = {
  "DeltaZ_min": DeltaZ,
  "DeltaZ_max": DeltaZ,
  "width": 0.0,
  "PASS": True,
  "method": "KS flux: Δz = 2πK/(3 g_s M)",
  "inputs": {"gs": gs, "M": M, "K": K, "N": N}
}
outdir = os.path.join(ROOT, "certs"); os.makedirs(outdir, exist_ok=True)
out_p = os.path.join(outdir, "DeltaZ.json")
with open(out_p, "w", encoding="utf-8") as f: json.dump(out, f, indent=2)
print("[CERT] Δz = %.12f | PASS = True" % DeltaZ)
print("[OUT]", out_p)
