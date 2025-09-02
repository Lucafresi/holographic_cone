# olographic_cone
Official repo for the 5D holographic-cone program: rigorous, fully reproducible HOLO/KK validations (Gate-E and beyond), code, tests, and certified pipelines.

---

## HOLO_KK — Gate-E (KK ≡ HOLO) benchmark

```bash
### Requirements
python -m venv .venv
source .venv/bin/activate
pip install mpmath

### Run (from repo root)

mkdir -p HOLO_KK/KK/cert_kk HOLO_KK/HOLO/cert_holo HOLO_KK/cert

PYTHONUNBUFFERED=1 python3 -u HOLO_KK/KK/kk_analytic_modes.py \
  --N 150 \
  --out HOLO_KK/KK/cert_kk/modes_analytic.json

PYTHONUNBUFFERED=1 python3 -u HOLO_KK/KK/kk_gateE_from_modes.py \
  --modes HOLO_KK/KK/cert_kk/modes_analytic.json \
  --csv   HOLO_KK/KK/cert_kk/pi.csv \
  --out   HOLO_KK/KK/cert_kk/fit_gateE.json

PYTHONUNBUFFERED=1 python3 -u HOLO_KK/HOLO/holo_gateE_dtn.py \
  --csv HOLO_KK/HOLO/cert_holo/pi.csv \
  --out HOLO_KK/HOLO/cert_holo/fit_gateE.json

### Detailed compare + audit report

PYTHONUNBUFFERED=1 python3 - <<'PY' | tee HOLO_KK/cert/report_kk_vs_holo.txt
import json,hashlib,subprocess,sys,platform
def sha256(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for c in iter(lambda:f.read(8192),b''):
            h.update(c)
    return h.hexdigest()
def load(p):
    with open(p) as f:
        return json.load(f)
def git_rev():
    try:
        r=subprocess.run(['git','rev-parse','--short','HEAD'],capture_output=True,text=True,check=True).stdout.strip()
        d=subprocess.run(['git','status','--porcelain'],capture_output=True,text=True).stdout.strip()
        return r+('+dirty' if d else '')
    except Exception:
        return 'unknown'
kk_path='HOLO_KK/KK/cert_kk/fit_gateE.json'
ho_path='HOLO_KK/HOLO/cert_holo/fit_gateE.json'
kk=load(kk_path); ho=load(ho_path)
tol_abs_phys=5e-10; tol_rel_phys=5e-10
tol_abs=1e-12; tol_rel=1e-9
print('FILE_KK',kk_path)
print('SHA256_KK',sha256(kk_path))
print('FILE_HOLO',ho_path)
print('SHA256_HOLO',sha256(ho_path))
print('GIT_COMMIT',git_rev())
print('PYTHON',platform.python_version())
print('PLATFORM',platform.platform())
print('THRESHOLDS',f'alpha|C_log abs<={tol_abs_phys:.1e} rel<={tol_rel_phys:.1e} ; other abs<={tol_abs:.1e} rel<={tol_rel:.1e}')
ok_all=True
rows=[]
for k in ['alpha','C_log']:
    a=kk.get(k); b=ho.get(k)
    da=abs(a-b); denom=max(1.0,abs(a),abs(b)); rel=da/denom
    ok=(da<=tol_abs_phys and rel<=tol_rel_phys); ok_all&=ok
    rows.append((k,f'{a}',f'{b}',f'{da:.3e}/{rel:.3e}','PASS' if ok else 'FAIL'))
print('CHECKS')
for r in rows: print(f'{r[0]:20s} kk={r[1]:<20s} holo={r[2]:<20s} diff_abs/diff_rel={r[3]:<24s} {r[4]}')
other=[]
for k in sorted(set(kk.keys()) & set(ho.keys())):
    if k in ('alpha','C_log'): continue
    va=kk[k]; vb=ho[k]
    if isinstance(va,(int,float)) and isinstance(vb,(int,float)):
        da=abs(va-vb); denom=max(1.0,abs(va),abs(vb)); rel=da/denom
        ok=(da<=tol_abs and rel<=tol_rel); ok_all&=ok
        other.append((k,f'{va}',f'{vb}',f'{da:.3e}/{rel:.3e}','PASS' if ok else 'FAIL'))
print('OTHER_NUMERIC_KEYS')
for r in other: print(f'{r[0]:20s} kk={r[1]:<20s} holo={r[2]:<20s} diff_abs/diff_rel={r[3]:<24s} {r[4]}')
print('VERDETTO','PASS' if ok_all else 'FAIL')
sys.exit(0 if ok_all else 1)
PY
