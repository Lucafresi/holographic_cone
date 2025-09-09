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
```





















## COS–ξ — Holographic sequester of the cosmological constant (C0/C4)

Questo repository contiene una pipeline minimale e certificata per calcolare il valore di ξ e della densità di energia del vuoto ρ_Λ secondo il modello del sequestro olografico.

L'obiettivo è fornire un calcolo con le seguenti garanzie:

Invarianza di scala locale: Il risultato non dipende da lunghezze locali arbitrarie (ℓ).

Riproducibilità bit-for-bit: L'esecuzione della pipeline produce risultati identici su sistemi compatibili.

Artefatto certificato: L'output viene salvato con un hash crittografico (SHA-256) per garantirne l'integrità e facilitare l'audit.

Le grandezze calcolate sono:

ξ = ξ(L_eff; dati globali)

ρ_Λ(t₀) = (M_Pl² / t₀²) * ξ

Struttura del Progetto

```
cosxi_c0c4/
├── pyproject.toml
├── src/cosxi/
│   ├── __init__.py
│   ├── cli.py
│   ├── io.py
│   ├── pipeline.py
│   ├── report.py
│   ├── sequester.py
│   └── units.py
├── inputs/
│   ├── baseline.json
│   └── observed.json
├── tests/
│   ├── test_cli.py
│   ├── test_invariance.py
│   ├── test_regression.py
│   └── test_units_signs.py
└── artifacts/
    ├── xi_cert.json        # (generato durante l'esecuzione)
    └── xi_cert.sha256      # (generato durante l'esecuzione)

```
Installazione e Setup

Tutti i comandi devono essere eseguiti dalla directory radice del repository.

Crea e attiva un ambiente virtuale Python:

```
python -m venv .venv
source .venv/bin/activate
```
Installa il modulo cosxi in modalità "editable":
Questo permette di modificare il codice sorgente senza dover reinstallare il pacchetto.

```
python -m pip install -e ./cosxi_c0c4
```
In alternativa (solo per test veloci), puoi aggiungere il modulo al PYTHONPATH della sessione corrente:

```
export PYTHONPATH="$PWD/cosxi_c0c4/src
```
Esecuzione dei Test

Per verificare la correttezza dell'installazione e del codice, esegui la suite di test.
```

python -m pytest -q cosxi_c0c4/tests
```
Output Atteso:
```

........                               [100%]
5 passed in X.XXs
```
I test coprono i seguenti aspetti:

Regressione numerica: Verifica che ξ non cambi rispetto a un valore di riferimento.

Invarianza: Controlla che il risultato sia invariante sotto le riscalature M_Pl → λ*M_Pl e t₀ → λ*t₀.

Segni e unità: Assicura la coerenza fisica dei calcoli.

CLI: Testa il corretto funzionamento dell'interfaccia a riga di comando.

Esecuzione della Pipeline

La pipeline calcola ξ e produce un artefatto certificato in formato JSON.

Esegui la pipeline con i dati di input di baseline:

```
python -m cosxi.cli cosxi_c0c4/inputs/baseline.json cosxi_c0c4/artifacts/xi_cert.json
```
Genera l'hash SHA-256 dell'artefatto per la certificazione:
Il comando tee mostra l'hash a schermo e lo salva nel file specificato.


shasum -a 256 cosxi_c0c4/artifacts/xi_cert.json | tee cosxi_c0c4/artifacts/xi_cert.sha256

(Opzionale) Verifica la riproducibilità bit-for-bit:
Esegui nuovamente la pipeline e confronta gli hash dei due artefatti generati.
```

# Genera un secondo artefatto
python -m cosxi.cli cosxi_c0c4/inputs/baseline.json cosxi_c0c4/artifacts/xi_cert_2.json

# Confronta gli hash (devono coincidere)
shasum -a 256 cosxi_c0c4/artifacts/xi_cert.json cosxi_c0c4/artifacts/xi_cert_2.json
Output Atteso (con dati baseline.json)

Il file xi_cert.json conterrà valori simili a questi:


{
  "results": {
    "xi": 1.9999999989472883e-09,
    "rho_Lambda_t0": 6.266851628356843e-08
  },
  "checks": {
    "ward_scale_invariance": {
      "invariant_under_local_rescalings": true
    }
  }
}

```
Cosa Dimostra (Formalmente)

Questa pipeline dimostra che:

Il valore di ξ è una funzione esclusivamente dei dati di bordo globali (come L_eff, le discontinuità di A' al bordo, la media storica T̄, etc.) e non dipende dalla scala locale ℓ.

La densità ρ_Λ(t₀) = (M_Pl² / t₀²) * ξ è invariante sotto la riscalatura congiunta M_Pl → λ*M_Pl e t₀ → λ*t₀.

La combinazione di un artefatto JSON e del suo hash SHA-256 garantisce un framework per audit e riproducibilità scientifica.

Troubleshooting
```
ModuleNotFoundError: No module named 'cosxi'
```
Causa: Il modulo non è stato installato o il PYTHONPATH non è configurato correttamente.

Soluzione: Assicurati di aver attivato l'ambiente virtuale ed esegui il comando di installazione:
```

python -m pip install -e ./cosxi_c0c4

L'hash SHA-256 non coincide
```
Causa: La riproducibilità bit-for-bit può essere sensibile a versioni diverse di Python, delle librerie o del sistema operativo. Anche una minima modifica (byte-per-byte) ai file di input invaliderà l'hash.

Soluzione: Verifica che l'ambiente di esecuzione sia identico (stessa versione di Python, stesse dipendenze). Assicurati che lo stato del repository Git sia pulito e che i file di input non siano stati modificati.
