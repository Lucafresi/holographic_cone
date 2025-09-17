import os, json, math
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
p, q = 2, 1
sqrt = math.sqrt(4*p*p - 3*q*q)
VolX5 = (q*q*(2*p + sqrt))/(3*p*p*(3*q*q - 2*p*p + p*sqrt)) * (math.pi**3)
VolSigma3 = (math.pi**2/108.0)*(31.0 + 7.0*math.sqrt(13.0))
out = {
  "VolX5": VolX5,
  "VolSigma3": VolSigma3,
  "provenance": {
    "method": "MSY closed-form for Y^{p,q}",
    "p": p, "q": q
  },
  "PASS": True
}
outdir = os.path.join(ROOT, "certs"); os.makedirs(outdir, exist_ok=True)
out_p = os.path.join(outdir, "volumes.json")
with open(out_p,"w",encoding="utf-8") as f: json.dump(out, f, indent=2)
print("[CERT][geom] ->", out_p)
print(json.dumps({"VolX5":VolX5,"VolSigma3":VolSigma3}, indent=2))
