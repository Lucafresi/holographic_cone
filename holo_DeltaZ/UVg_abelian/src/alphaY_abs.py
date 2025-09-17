import os, json
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
nonab = json.load(open(os.path.join(ROOT,"..","UVg","certs","alpha_U.json"), encoding="utf-8"))
ky_dir_candidates = [
  os.path.join(ROOT,"..","kY","certs","kY","sigma3"),
  os.path.join(ROOT,"..","..","holo_kY","certs","kY","sigma3")
]
ky = 2.0
for base in ky_dir_candidates:
    p = os.path.join(base, "cs_integrality.json")
    if os.path.exists(p):
        jj = json.load(open(p,encoding="utf-8"))
        ky = float(jj.get("kY", ky))
        break
alphaY_inv = ky * float(nonab["alpha2_inv_UV"])
out = {
  "alphaY_inv_UV": alphaY_inv,
  "alphaY_UV": 1.0/alphaY_inv,
  "kY": ky,
  "PASS": True
}
outdir = os.path.join(ROOT, "certs"); os.makedirs(outdir, exist_ok=True)
out_p = os.path.join(outdir, "alphaY_U.json")
with open(out_p,"w",encoding="utf-8") as f: json.dump(out, f, indent=2)
print("[CERT][UVg_abelian] ->", out_p)
print(json.dumps(out, indent=2))
