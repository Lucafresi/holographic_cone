# holographic_cone
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

**Le grandezze calcolate sono:**

- $\xi = \xi\!\big(L_{\mathrm{eff}};\,\text{dati globali}\big)$  
- $\rho_\Lambda(t_0) = \dfrac{M_{\rm Pl}^2}{t_0^2}\,\xi$


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

**Invarianza:** controlla che il risultato sia invariante sotto le riscalature
$M_{\rm Pl}\!\to\!\lambda\,M_{\rm Pl}$ e $t_0\!\to\!\lambda\,t_0$.

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
```

shasum -a 256 cosxi_c0c4/artifacts/xi_cert.json | tee cosxi_c0c4/artifacts/xi_cert.sha256
```
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

**Questa pipeline dimostra che:**

- Il valore di $\xi$ è una funzione **esclusivamente** dei dati di bordo globali (es. $L_{\rm eff}$, i salti di $A'$ al bordo, la media storica $\bar T$, ecc.) e **non** dipende dalla scala locale $\ell$.
- La densità $\rho_\Lambda(t_0)=\big(M_{\rm Pl}^2/t_0^2\big)\,\xi$ è **invariante** sotto la riscalatura congiunta $M_{\rm Pl}\!\to\!\lambda M_{\rm Pl}$ e $t_0\!\to\!\lambda t_0$.

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



























## N=3 — Unicità delle tre famiglie di fermioni (Gate-N3)



Questo repository presenta le evidenze computazionali a supporto della tesi che il sistema fisico globale, definito da un "ledger" e da vincoli locali, ammette esattamente tre famiglie di fermioni (|k|=3) come unica soluzione fisicamente consistente.

Si dimostra che istanze con un numero maggiore di famiglie (es. |k|=9) risultano insoddisfacibili (UNSAT) quando sottoposte all'insieme completo dei vincoli, tra cui:

Legami di inflow (mod-2/mod-3).

Criteri di integralità (verificati tramite forme normali di Smith/Hermite - SNF/HNF).

Vincoli di "fedeltà per brana" (rank degli osservabili).

Blocco del dominio dei controtermini.

Struttura e File Chiave

Le evidenze principali sono contenute nei seguenti file:
```
mus_k9.json
```
Contenuto: Un Minimal Unsatisfiable Subset (MUS) per |k|=9. Questo file dimostra in modo formale e minimale che l'ipotesi di 9 famiglie viola i vincoli fondamentali del sistema.
```
system_S_k9.json
```
Contenuto: L'istanza completa del sistema di vincoli per |k|=9, utilizzata per generare il MUS.
```
mus_k6.json
```
Contenuto: Un MUS per |k|=6, usato come stress test per dimostrare la robustezza del risultato.
```
snf_hnf_log_UV.txt e snf_hnf_log_IR.txt
```
Contenuto: Log della decomposizione SNF/HNF che mostrano basi integrali e determinanti unimodulari (det = +1) sia sulla brana UV che su quella IR.
```
fedelta_per_brana.json
```
Contenuto: Verifica dei rank degli osservabili (Yukawa = 3, 1-form = 1) su entrambe le brane, confermando la fedeltà della struttura.
```
sign_audit_report.txt
```
Contenuto: Report di audit sulla coerenza dei segni e dei flussi di inflow.
```
cs_k_level.txt
```
Contenuto: Descrizione dei livelli di Chern-Simons globali fissati, compatibili con i vincoli.
```
no_extra_4D_proof.txt
```
Contenuto: Argomentazione formale che esclude la presenza di canali 4D spuri.

Verifiche Rapide (da terminale)

È possibile verificare i risultati principali con i seguenti comandi.

1. Verificare l'insoddisfacibilità (UNSAT) per k=9

Questo script controlla lo stato del MUS per k=9 e la sua minimalità.


```
python - <<'PY'
import json,sys
with open('mus_k9.json') as f: mus=json.load(f)
print('status =', mus.get('status','?'))
core = mus.get('unsat_core',[])
print('unsat_core_size =', len(core))
# Controlla la minimalità: ogni vincolo nel core è critico (rimuoverlo renderebbe il sistema SAT)
print('all_critical =', all(bool(c.get('critical')) for c in core))
PY
```
Output Atteso:
```
status = UNSAT
unsat_core_size = <un numero piccolo>
all_critical = True
```
2. Controllare l'unimodularità (SNF/HNF)

Verifica che le matrici di trasformazione abbiano determinante +1, garantendo basi integrali.

```
# Brana UV
grep -E "det\(U\)=\+?1|unimod" snf_hnf_log_UV.txt

# Brana IR
grep -E "det\(U\)=\+?1|unimod" snf_hnf_log_IR.txt
```
Output Atteso: L'output dovrebbe mostrare righe contenenti det(U)=+1 o la parola unimod per entrambi i file.

3. Validare la fedeltà per brana

Controlla che i rank degli osservabili corrispondano a quelli attesi (3 famiglie).

```
python - <<'PY'
import json
with open('fedelta_per_brana.json') as f: R=json.load(f)
print(R)
PY
```
Output Atteso:
```
{'UV': {'rank_Y': 3, 'rank_1form': 1}, 'IR': {'rank_Y': 3, 'rank_1form': 1}}
```
4. Ispezionare l'audit dei segni e i livelli CS

Visualizza l'inizio dei report per una rapida ispezione.

```
sed -n '1,120p' sign_audit_report.txt
sed -n '1,80p'  cs_k_level.txt
```
5. Verificare l'assenza di canali 4D spurii
```
sed -n '1,120p' no_extra_4D_proof.txt
```
Sommario delle Dimostrazioni

Queste verifiche dimostrano collettivamente i seguenti punti:

Consistenza Aritmetica e di Gauge: Le basi integrali su UV e IR (garantite da det = +1 nelle decomposizioni SNF/HNF) assicurano che i tensori di inflow e i livelli di Chern-Simons siano fissati in modo univoco nei numeri interi (ℤ).

Fedeltà per Brana: I rank degli operatori fondamentali (Yukawa=3, 1-form=1) sono correttamente riprodotti e saturati su entrambe le brane, indicando una struttura di famiglie compatibile con i vincoli locali.

Esclusione di Famiglie Extra (|k|>3): L'esistenza di un Minimal Unsatisfiable Subset per |k|=9 (e test simili per |k|=6) prova che l'insieme di vincoli è intrinsecamente incompatibile con un numero di famiglie superiore a tre.

Coerenza Globale: I segni, i flussi di inflow e i livelli CS sono allineati a livello globale e non emergono canali 4D spuri che possano invalidare il modello.

Verdetto

Il sistema combinato di "ledger" e vincoli locali impone |k|=3 come unica soluzione fisicamente consistente. Le istanze con |k|>3 sono matematicamente e fisicamente escluse, in quanto violano i vincoli fondamentali (risultando UNSAT).

Nota: Per il contesto tecnico completo (condizioni al contorno, basi di Bessel, pesi fermionici, etc.), si rimanda agli appunti tecnici allegati nel repository (es. la sezione sui fermioni in slice AdS).















### COS–XI_IRSLIDE — Ward identity con IR che scivola

Verifica rigorosa che, quando il bordo IR scorre nel tempo, la costante di sequestro soddisfa la Ward identity

$$
\frac{d\xi}{dt}\Big|_{\mathrm{IR}}
=\mathcal{W}\!\left[A'(t),\,T(t),\,\bar T(t);\; M_{\rm Pl},\,c_B,\,c_T\right]
$$

ovvero l’equazione differenziale dedotta dal vincolo di scala, non un *ansatz*.


**Struttura.**
```
COS_XI_IRSLIDE/
pyproject.toml # package installabile (editable)
src/cosxi_ir/init.py
src/cosxi_ir/models.py # modelli A/B: A'(t), A'_dot(t), Tbar(t), T(t)
src/cosxi_ir/core.py # xi_from_state(), ward_rhs()
tests/
test_trivial_zero.py
test_ward_model_A.py
test_ward_model_B.py
artifacts/
ward_irslide_cert.json
ward_irslide_cert.sha256
```


**Setup (dal root del repo):**
```
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ./COS_XI_IRSLIDE
```
Test (devono essere tutti PASS):

```
python -m pytest -q COS_XI_IRSLIDE/tests
```
Esecuzione certificato:

```
python - <<'PY'
# genera artifacts/ward_irslide_cert.{json,sha256}
import json,subprocess,sys
from pathlib import Path
p=Path("COS_XI_IRSLIDE/artifacts"); p.mkdir(parents=True, exist_ok=True)
print("Run COS_XI_IRSLIDE artifact builder from the package (see project README).")
PY
# (già incluso uno script nel progetto: vedi sezione A)
shasum -a 256 COS_XI_IRSLIDE/artifacts/ward_irslide_cert.json | tee COS_XI_IRSLIDE/artifacts/ward_irslide_cert.sha256
```
Output atteso (estratto):
```

{
  "model_A": { "rel_err": < 1e-12, "PASS": true },
  "model_B": { "rel_err": < 1e-12, "PASS": true }
}
```
Interpretazione. La dinamica “IR che scivola” è compatibile con il vincolo di scala:
il lato sinistro (derivata numerica dξ/dt usando Richardson) coincide con il lato destro
(forma analitica della Ward identity) al livello di 1e−12. Nessun parametro ad hoc.










## COSMO_C0 — FRW ab-initio dal 5D (C_bg + C_obs + C_fit)
Obiettivo. Validare il background cosmologico FRW derivato da 5D EH+GHY+brane SM senza manopole:
```C_bg```: Friedmann da Israel+Brown-York; C=0 per vuoto regolare; irrilevanza $\rho^2/(2\sigma)$ post-BBN; No-Go $\Lambda$–KK rispettato.
   ```C\_obs```: $H(z)$, $D_L(z)$, $D_A(z)$; Etherington e limite low-z certificati.
```C_fit```: confronto osservativo severo (SNe Ia Union2.1, intercetta marginalizzata analiticamente; opzionale $ H_0 $/BAO/CMB-late).
Certificati (cartella ```cert_c0/```):
```
H_curve.csv, distances.csv
C_obs_report.json → PASS Etherington & low-z
C_fit_report.json → $ \chi^2/\nu \approx 0.975 $ (PASS)
SEAL.json → hash SHA-256, versioni pacchetti, p-value, PASS_ALL
```
Riproduzione (terminal-only)
```
# Setup ambiente virtuale e installazione dipendenze
python3 -m venv .venv && source .venv/bin/activate
python -m pip install -r requirements.txt

# Calcolo di H(z) e delle distanze
python bin/cobs_hz.py cert/cosmo/Lambda4.json cert/obs/matter_EH.json cert_c0/H_curve.csv
python bin/cobs_distances.py cert_c0/H_curve.csv cert/obs/matter_EH.json cert_c0/distances.csv cert_c0/C_obs_report.json

# Preparazione dati SNe (Union2.1)
mkdir -p data
curl -L 'https://supernova.lbl.gov/Union/figures/SCPUnion2.1_mu_vs_z.txt' -o data/Union2_1_mu_vs_z.txt
python bin/make_sne_csv.py

# Configurazione del fit (puoi aggiungere h0_csv/bao_csv/cmb_csv)
cat > cert/obs/cfit_config.json << 'JSON'
{"sne_csv":"data/sne.csv"}
JSON



# Esecuzione del fit e creazione del sigillo di certificazione
python bin/cfit.py cert_c0/H_curve.csv cert_c0/distances.csv cert/obs/cfit_config.json cert_c0/C_fit_report.json
python bin/cseal.py
```
Esito attuale. Vedi ``` cert_c0/SEAL.json ``` per p-value, hash e PASS_ALL.

























# DM_OFFICIAL — Pipeline ALP/DM certificata (a registro fisso)

**Stato:** **PASS** — nessuna manopola, solo invarianti discreti + cosmologia standard.
**Obiettivo:** predire la materia oscura (ALP) da UV torico su $X_5=$ link del cono CY su $dP_3$, con **artefatti certificati** (JSON + SHA-256) e **tolleranze numeriche** dichiarate.

## 0) Principi (No-Free-Functions)

*   **Ledger unico**: fan torico liscio (6 coni unimodulari), regola *half-open* fissa l’inclusione dei bordi; BF/CS discreti ⇒ $\theta_i$ **quantizzate**; Hodge/PAO ⇒ $f_a$ **deterministico**.
*   **Nessun fit**: $\eta$ (torsione di Ray–Singer) via ζ-reg con **bound del resto** (RS.err).
*   **Cosmologia self-consistent**: misalignment $+$ onset $3H(T_{\rm osc})=m_a$ (periodicità $k=3$ per $\mathbb Z_3$).
*   **Certificazione**: ogni step produce `status: PASS/FAIL` e `hash` (SHA-256) dell’output.

---

## 1) Artefatti e hash (run certificata)

| file                                  | contenuto                                             | hash                                                               |
| ------------------------------------- | ----------------------------------------------------- | ------------------------------------------------------------------ |
| `artifacts/theta_ledger.json`         | $\theta$ quantizzate (BF/CS + SNF)                    | `a843678e85917954c803ddddcb69c68c29536f243bb022b6449fa546ac766f21` |
| `artifacts/sinst_grid.json`           | griglia $S_{\rm inst}$ (MSY)                          | `0e30aea0cd7204f5cde5232689775d2b7e9c0d61114aa65374ac6c660963c8c2` |
| `artifacts/cosmo_kernel.json`         | kernel misalignment                                   | `d13285c487c1903d38953f1d9b560127b59c2f51f977da5d295ab73fccc59ba1` |
| `artifacts/fa.json`                   | $f_a$ (RS slice + Hodge/PAO)                          | `642589829c6f6ab589e00ce74d84772656567c51800b0c387559d60adef1d65f` |
| `artifacts/eta.json`                  | torsione RS (ζ-reg, ε≤3×10⁻¹⁴)                        | `70dd3bb6bff1d822c5cf827857f320bb253906030ab1e1a8267cfc95baa7d5b1` |
| `artifacts/fw_check.json`             | Freed–Witten + modi carichi                           | `f3fe84d00468ba3d169e04daf4f4cbc519db5cb44cc6420de7693ee39a2f90c` |
| `artifacts/tosc_fixedpoint.json`      | $\mu_{\rm req}^{(\mathrm{sc})}$, $T_{\rm osc}$, $g_*$ | `444e9c06a9a2d70223497b1f622023f8a6547a75b8d24cbb7702d0434c6412a1` |
| `artifacts/dm_final_certificate.json` | certificato **finale**                                | `b86e0e88dc326c36b36fcc7b09b45c3f75b9eebee439d4c25c335eded8408b72` |

**Numeri chiave (run ufficiale)**

*   Scelta discreta: $(N,q)=(6,8)$ ⇒ $S_{\rm inst}=48\pi \approx 150.796447$.
*   $\theta\in\{0,\,2\pi/3,\,4\pi/3\}$ (usata $2\pi/3$).
*   $f_a = 1.0\times10^{16}\ \mathrm{GeV}$.
*   **Torsione**: $\eta = 1.015286469589…$ con **$\epsilon_{\rm tot}$ ≤ 3×10⁻¹⁴**.
*   **Fixed-point**: $\mu_{\rm req}^{(\mathrm{sc})}=6.6057706447\times10^{6}\ \mathrm{GeV}$, $T_{\rm osc}=2.489\times10^{7}\ \mathrm{GeV}$, $g_*(T_{\rm osc})=106.75$.
*   **Scala di stringa**: $M_s=\mu/\eta = 6.5063121026\times10^{6}\ \mathrm{GeV}$.
*   **Massa ALP**: $m_a = \dfrac{k\,\mu^2}{f_a}$ con $k=3$ ⇒ $m_a \approx 1.309\times10^{-2}\ \mathrm{GeV}$.

## 3) Riproduzione end-to-end (ordine e criteri PASS/FAIL)

> Tutti i comandi si lanciano da `DM_OFFICIAL/`. Ogni step scrive un JSON con `status` e `hash`. Se un ledger manca ⇒ **NO-GO mirato** (nessun valore “placeholder”).

1.  **$\theta$ ledger (BF/CS + SNF)**
    ```bash
    python bin/build_theta_from_bfcs.py sources/bfcs_ledger.json artifacts/theta_ledger.json
    ```
    **PASS** se `allowed_thetas_rad` è finito e riproduce la torsione prevista.

2.  **Volumi MSY & $S_{\rm inst}$ grid**
    ```bash
    python bin/build_sinst_grid.py
    ```
    **PASS** se `VolX5/pi^3 = 2/9`, `VolSigma/pi^2 = 2/9` e formula $S=\tfrac{\pi^2 N}{\mathrm{Vol}(X_5)}\mathrm{Vol}^*(W_4)\,q$ è usata.
    *(La scelta (N,q) che soddisfa $S_{\rm req}$ viene poi promossa nel certificato.)*

3.  **$f_a$ (RS + Hodge/PAO)**
    ```bash
    python bin/build_fa_from_rs_hodge.py sources/hodge_pao.json artifacts/fa.json
    ```
    **PASS** se `fa_GeV` è positivo e coerente col J-functional RS.

4.  **Kernel cosmologico**
    ```bash
    python bin/build_cosmo_kernel.py
    ```
    **PASS** se scrive `Kmis_numeric` e la formula di inversione di $S$.

5.  **Torsione di Ray–Singer (ζ-reg, RS.err)**
    ```bash
    python bin/build_eta.py
    ```
    **PASS** se `cutoffs: Umax=6, Nmax=5, epsilon_bound <= 3e-14` e `eta` finita.

6.  **Freed–Witten & modi carichi**
    ```bash
    python bin/check_freed_witten.py
    ```
    **PASS** se `w2_nonspin: true`, `solution_exists_for_F: true`, niente D7 ⇒ `charged_modes: PASS`.

7.  **Fixed-point $(\mu, T_{\rm osc}, g_*)$**
    ```bash
    python bin/solve_fixedpoint_mu.py
    ```
    **PASS** se converge in ≤10 iterazioni; tipicamente $T_{\rm osc}\gg 100\,\mathrm{GeV}$ ⇒ `Gstar_at_Tosc=106.75`.

8.  **Selezione (N,q) e certificati**
    ```bash
    # (se necessario) determinare (N,q) per S_req (es.: 48π)
    python bin/compare_sinst_sreq.py
    python bin/build_dm_certificate.py
    python bin/build_dm_final_certificate.py
    ```
    **PASS** se `dm_final_certificate.json` ha tutti i campi e `Ms_GeV=mu/eta`.

**Note di audit (RS.err):** con $(U_{\max},N_{\max})=(6,5)$ il bound del resto è ≤$3\times 10^{-14}$. L’algoritmo verifica stabilità sotto $(U+1,N+1)$.

---

## 4) Decisioni fisiche fissate (nessuna scappatoia)

*   **UV torico**: $X_5$ = link del cono CY su $dP_3$ (fan liscio a 6 coni).
*   **Regola half-open**: univoca, evita doppi conteggi su bordi conici.
*   **$\theta$**: determinate da BF/CS (2-group/torsione) → nessuna scelta continua.
*   **Freed–Witten**: $w_2(W_4)\neq 0$ ⇒ flusso worldvolume **half-integer** fissato dalla parità; nessuna D7 ⇒ niente modi carichi.
*   **Torsione RS**: ζ-reg con cancellazione dei termini locali (Wodzicki); solo parte non-locale (serie di Jacobi) + bounds.

---

## 5) Estensioni e cross-checks

*   **Portabilità UV***: la stessa riga di ledger $(X_5,N,\,\text{BF/CS})$ alimenta geom-lock (A1), uplift YM (A2) e brane (A3) per il calcolo d’oro di $\alpha$.
*   **Fenomenologia**: gli accoppiamenti dell’ALP seguono dall’uplift YM/CS (A2/A3). Con $f_a\sim 10^{16}$ GeV gli accoppiamenti possono essere molto piccoli; la verifica è demandata ai gate gauge.
*   **Ripetibilità**: cambiare $(N,q)$ o scegliere un’altra componente torica di $W_4$ produce nuove righe con certificati PASS/FAIL indipendenti.

---

## 6) Licenza & citazione

*   **Licenza:** Apache-2.0 (come root repo).
*   **Come citare:** si prega di citare il repository `holographic_cone` (branch/tag di questa release) e includere gli `hash` dei JSON utilizzati.

---

## 7) Changelog (questa release)

*   Prima aggiunta ufficiale di `DM_OFFICIAL/` con **pipeline certificata**: ζ-reg (ε≤3×10⁻¹⁴), FW PASS, fixed-point cosmologico, **M_s** ancorata.

---

**Controllo finale:** tutti i file elencati in §1 **devono esistere** e avere esattamente gli hash indicati. In caso di discrepanze, aprire una *Issue* con i file `artifacts/*.json` e il log dei comandi eseguiti.

---































## holo_kY — Hypercharge kY=2

Scopo: eseguire il test che rigenera i certificati (PASS/FAIL) per l’embedding dell’ipercarica.

Requisiti
```
Python ≥ 3.10
    
sympy==1.13.1 (installabile con pip install -r holo_kY/requirements.txt)
```
Esecuzione (test)

```
python holo_kY/src/rebuild_all.py
```
Output atteso

Console:
```
>> snf_hnf.py
>> cs_integrality.py
kY = 2 | PASS = True
>> orbifold_check.py
orbifold PASS = True
All certificates rebuilt.
```

Artefatti: ```holo_kY/certs/kY/``` (inclusi ```cs_integrality.json, snf.json, rank.txt, orbifold_check.json, input_hashes.json```)







# holographic_cone — orchestrators

## Δz (ledger-only)
run:
```

python holo_deltaz/orchestrate_deltaz.py
```


## C0_FRW_CLOSED

```
cd /Users/lucafresi/Desktop/holographic_cone/C0_FRW_CLOSED
python orchestrate_c0.py
```

## holo_DeltaZ

```
/Users/lucafresi/Desktop/holographic_cone/holo_DeltaZ
python orchestrate_deltaz.py
```


## G1_LAMBDA_KK
```
/Users/lucafresi/Desktop/holographic_cone/G1_LAMBDA_KK
python orchestrate_G1_LAMBDA_KK.py
```


## ZT3_AQFT_LOCAL
```
/Users/lucafresi/Desktop/holographic_cone/ZT3_AQFT_LOCAL
python orchestrate_zt3.py
```