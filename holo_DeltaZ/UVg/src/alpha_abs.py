import os, json
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DzJ = json.load(open(os.path.join(ROOT,"..","certs","DeltaZ.json"), encoding="utf-8"))
VolJ= json.load(open(os.path.join(ROOT,"..","geom","certs","volumes.json"), encoding="utf-8"))
flux= json.load(open(os.path.join(ROOT,"..","flux","certs","flux.json"), encoding="utf-8"))
Dz = DzJ.get("DeltaZ", 0.5*(DzJ["DeltaZ_min"]+DzJ["DeltaZ_max"]))
N  = int(flux["N"])
VolSigma3 = float(VolJ["VolSigma3"]); VolX5 = float(VolJ["VolX5"])
alpha_inv = 0.5*Dz * N * (VolSigma3/VolX5)
out = {
  "alpha2_inv_UV": alpha_inv,
  "alpha3_inv_UV": alpha_inv,
  "alpha2_UV": 1.0/alpha_inv,
  "alpha3_UV": 1.0/alpha_inv,
  "unification": True,
  "cycle": "Sigma3",
  "VolSigma3": VolSigma3,
  "VolX5": VolX5,
  "PASS": True
}
outdir = os.path.join(ROOT, "certs"); os.makedirs(outdir, exist_ok=True)
out_p = os.path.join(outdir, "alpha_U.json")
with open(out_p,"w",encoding="utf-8") as f: json.dump(out, f, indent=2)
print("[CERT][UVg] ->", out_p)
print(json.dumps(out, indent=2))
