import os, json, subprocess, itertools, sys
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def run(cfg):
    p = os.path.join(root, "configs", "SWEEP.json")
    with open(p,"w") as f: json.dump(cfg,f,indent=2)
    subprocess.run([sys.executable, os.path.join(root,"scripts","gate_nu_run.py"), p], check=True)
    sp = json.load(open(os.path.join(root,"cert","gate_nu","spectrum.json")))
    mx = json.load(open(os.path.join(root,"cert","gate_nu","mixing.json")))
    return sp["m_s"], mx["sin2_2theta"]

base = {
  "geometry": { "L": 1.0, "z_UV": 1e-3, "z_IR": 9325.35 },
  "fermion":  { "c": 0.6, "alpha_UV": 0.0, "alpha_IR": "inf" },
  "sm":       { "z_H": "IR", "lambda_B": 1.0, "sterile_chirality": "AUTO" },
  "grid":     { "N": 401 }
}

vals_c  = [0.4, 0.5, 0.6, 0.7]
vals_aIR= ["inf", 1.0]
print("c,alpha_IR,m_s[GeV],sin^2(2theta)")
for c,aIR in itertools.product(vals_c, vals_aIR):
    cfg = json.loads(json.dumps(base))
    cfg["fermion"]["c"] = c
    cfg["fermion"]["alpha_IR"] = aIR
    m_s, s2 = run(cfg)
    print(f"{c},{aIR},{m_s:.6e},{s2:.6e}")
