import os, re, json
from collections import defaultdict

try:
    import yaml
    HAVE_YAML = True
except Exception:
    HAVE_YAML = False

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTDIR = os.path.join(ROOT, "cert", "gate_nu")
os.makedirs(OUTDIR, exist_ok=True)

SKIP_DIRS = {".git", ".venv", "venv", "__pycache__", "build", "dist", ".ipynb_checkpoints", "cert"}

# mappa (path chiave -> (nome logico, tipo))
KEYS = {
    ("geometry","L"): ("L", float),
    ("geometry","z_UV"): ("z_UV", float),
    ("geometry","z_IR"): ("z_IR", float),
    ("sm","z_H"): ("z_H", str),
    ("sm","lambda_B"): ("lambda_B", float),
    ("sm","sterile_chirality_at_brane"): ("sterile_chirality_at_brane", str),
    ("fermion","c"): ("c_s", float),
    ("fermion","alpha_UV"): ("alpha_UV_s", "alpha"),
    ("fermion","alpha_IR"): ("alpha_IR_s", "alpha"),
    ("fermion_L","c"): ("c_L", float),
    ("fermion_L","alpha_UV"): ("alpha_UV_L", "alpha"),
    ("fermion_L","alpha_IR"): ("alpha_IR_L", "alpha"),
    ("fermion_L","zero_kind"): ("zero_kind_L", str),
}

def parse_alpha(x):
    if isinstance(x,str) and x.lower() in ("inf","+inf","infty","infinite","infinity"):
        return "inf"
    try:
        return float(x)
    except Exception:
        return str(x)

def visit_dict(d, path=()):
    if isinstance(d, dict):
        for k,v in d.items():
            for keypath,(logical,typ) in KEYS.items():
                if path+(k,) == keypath:
                    if typ==float:
                        try: yield logical, float(v)
                        except: pass
                    elif typ=="alpha":
                        yield logical, parse_alpha(v)
                    else:
                        yield logical, str(v)
            yield from visit_dict(v, path+(k,))
    elif isinstance(d, list):
        for i,v in enumerate(d):
            yield from visit_dict(v, path+(str(i),))

def harvest_from_json(path):
    try:
        with open(path,"r") as f:
            data = json.load(f)
        return list(visit_dict(data))
    except Exception:
        return []

def harvest_from_yaml(path):
    if not HAVE_YAML: return []
    try:
        with open(path,"r") as f:
            data = yaml.safe_load(f)
        return list(visit_dict(data))
    except Exception:
        return []

# fallback grezzo per file testuali (regex)
RX = re.compile(r'''
(?P<key>\b(?:L|z_UV|z_IR|z_H|lambda_B|c_L|c_s|alpha_UV(?:_L|_s)?|alpha_IR(?:_L|_s)?|zero_kind_L|sterile_chirality_at_brane)\b)
\s*[:=]\s*
(?P<val>"[^"]*"|'[^']*'|[A-Za-z\+\-\.0-9_]+)
''', re.X)

def clean_val(s):
    s = s.strip()
    if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
        s = s[1:-1]
    if s.lower() in ("inf","+inf","infty","infinite","infinity"):
        return "inf"
    try:
        return float(s)
    except Exception:
        return s

def harvest_from_text(path):
    out = []
    try:
        with open(path,"r",errors="ignore") as f:
            for ln, line in enumerate(f,1):
                for m in RX.finditer(line):
                    key = m.group("key")
                    val = clean_val(m.group("val"))
                    out.append((key, val, ln, line.strip()))
    except Exception:
        pass
    return out

candidates = defaultdict(list)

for dirpath, dirnames, filenames in os.walk(ROOT):
    dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
    for fn in filenames:
        path = os.path.join(dirpath, fn)
        rel = os.path.relpath(path, ROOT)
        ext = os.path.splitext(fn)[1].lower()
        found = []
        if ext == ".json":
            for k,v in harvest_from_json(path):
                found.append((k,v,None,None))
        elif ext in (".yml",".yaml"):
            for k,v in harvest_from_yaml(path):
                found.append((k,v,None,None))
        elif ext in (".md",".txt",".py",".toml",".cfg",".ini"):
            for k,v,ln,ctx in harvest_from_text(path):
                # mappatura chiavi grezze -> logiche
                mapkey = {
                    "c_L":"c_L", "c_s":"c_s",
                    "alpha_UV_L":"alpha_UV_L","alpha_IR_L":"alpha_IR_L",
                    "alpha_UV_s":"alpha_UV_s","alpha_IR_s":"alpha_IR_s",
                    "alpha_UV":"alpha_UV_s","alpha_IR":"alpha_IR_s",
                    "L":"L","z_UV":"z_UV","z_IR":"z_IR","z_H":"z_H",
                    "lambda_B":"lambda_B","zero_kind_L":"zero_kind_L",
                    "sterile_chirality_at_brane":"sterile_chirality_at_brane"
                }.get(k, None)
                if mapkey:
                    found.append((mapkey, v, ln, ctx))
        if found:
            for k,v,ln,ctx in found:
                candidates[k].append({"value": v, "file": rel, "line": ln, "context": ctx})

# deduplica valori letterali (come chiave di confronto)
def vkey(v):
    if isinstance(v, float):
        return f"{v:.12g}"
    return str(v)

summary = {}
for k, lst in candidates.items():
    bucket = defaultdict(int)
    for it in lst:
        bucket[vkey(it["value"])] += 1
    # scegli il valore più frequente (stessa logica, nessun tuning)
    if bucket:
        chosen_key = max(bucket.items(), key=lambda kv: kv[1])[0]
        # converti back
        try:
            chosen_val = float(chosen_key)
        except:
            chosen_val = chosen_key
        summary[k] = {"chosen": chosen_val, "frequency": bucket[chosen_key], "candidates": lst}

# salva scan completo e un markdown "ledger-lock" per il paper
scan_path = os.path.join(OUTDIR, "ledger_scan.json")
with open(scan_path,"w") as f:
    json.dump({"summary": summary, "candidates": candidates}, f, indent=2)

md = ["# Ledger-Lock: parametri estratti dal repository\n"]
def md_line(name):
    if name in summary:
        ch = summary[name]["chosen"]
        src = summary[name]["candidates"][0]
        md.append(f"- **{name}** = `{ch}`  \n  (esempio di sorgente: `{src['file']}`" +
                  (f":{src['line']}" if src['line'] else "") + ")")
    else:
        md.append(f"- **{name}** = **NON TROVATO**")
for nm in ("L","z_UV","z_IR","z_H","lambda_B",
           "c_L","alpha_UV_L","alpha_IR_L","zero_kind_L",
           "c_s","alpha_UV_s","alpha_IR_s","sterile_chirality_at_brane"):
    md_line(nm)

md_path = os.path.join(OUTDIR, "ledger_lock.md")
with open(md_path,"w") as f:
    f.write("\n".join(md))

# genera una config coerente dai valori trovati (solo se presenti)
cfg = {"geometry":{}, "fermion":{}, "fermion_L":{}, "sm":{}, "grid":{"N":401}}
def put(dstkey, srcname):
    if srcname in summary:
        cfgpath, val = dstkey.split("."), summary[srcname]["chosen"]
        ref = cfg
        for part in cfgpath[:-1]:
            ref = ref[part]
        ref[cfgpath[-1]] = val

put("geometry.L", "L")
put("geometry.z_UV", "z_UV")
put("geometry.z_IR", "z_IR")
put("sm.z_H", "z_H")
put("sm.lambda_B", "lambda_B")
put("sm.sterile_chirality_at_brane", "sterile_chirality_at_brane")
put("fermion.c", "c_s")
put("fermion.alpha_UV", "alpha_UV_s")
put("fermion.alpha_IR", "alpha_IR_s")
put("fermion_L.c", "c_L")
put("fermion_L.alpha_UV", "alpha_UV_L")
put("fermion_L.alpha_IR", "alpha_IR_L")
put("fermion_L.zero_kind", "zero_kind_L")

auto_cfg_path = os.path.join(ROOT, "configs", "gate_nu_from_ledger.json")
os.makedirs(os.path.dirname(auto_cfg_path), exist_ok=True)
with open(auto_cfg_path, "w") as f:
    json.dump(cfg, f, indent=2)

print("Wrote:", scan_path)
print("Wrote:", md_path)
print("Wrote:", auto_cfg_path)
