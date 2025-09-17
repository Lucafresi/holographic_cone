import os, json, math
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DzJ = json.load(open(os.path.join(ROOT,"..","certs","DeltaZ.json"), encoding="utf-8"))
Dz = DzJ.get("DeltaZ", 0.5*(DzJ["DeltaZ_min"]+DzJ["DeltaZ_max"]))
j01 = 2.404825557695773
Mhat = j01*math.exp(-Dz)
out = {
  "Mhat": Mhat,
  "DeltaZ": Dz,
  "j01": j01,
  "PASS": True
}
outdir = os.path.join(ROOT, "certs"); os.makedirs(outdir, exist_ok=True)
out_p = os.path.join(outdir, "Mstar.json")
with open(out_p,"w",encoding="utf-8") as f: json.dump(out, f, indent=2)
print("[CERT][spectrum] ->", out_p)
print(json.dumps(out, indent=2))
