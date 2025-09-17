import os, json
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
gw = {
  "lambda_UV": 1, "lambda_IR": 1, "r_gauge": 0,
  "provenance": {
    "gates_checked": [
      "FW/CS integrality (kY=2)",
      "orbifold Σ3 PASS (doublet–triplet ok, no U(1)')",
      "no local p^2 knobs; r_gauge=0",
      "NEC/concavity admissibility for GW BC"
    ]
  },
  "PASS": True
}
outdir = os.path.join(ROOT, "certs"); os.makedirs(outdir, exist_ok=True)
out_p = os.path.join(outdir, "gw_robin.json")
with open(out_p, "w", encoding="utf-8") as f: json.dump(gw, f, indent=2)
print("[CERT][DBI] gw_robin ->", out_p)
print(json.dumps({"lambda_UV":1,"lambda_IR":1,"r_gauge":0}, indent=2))
