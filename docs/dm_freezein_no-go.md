# Gravitational freeze-in del D-sector (ledger-locked): **NO-GO**

## Tesi
Con il ledger attuale (RS) e **solo gravità**, la produzione per freeze-in non può spiegare la dark matter: il reheat necessario \(T_R^{\rm req}\) per ottenere \(\Omega h^2=0.12\) eccede di ~14–15 ordini di grandezza il cut-off dell’EFT \(1/z_{\rm UV}\). Nessun parametro può essere “scelto”: tutto discende in modo univoco da ledger e anomalie.

---

## (A) Anomalie \(\Rightarrow\) 2-group OFF (niente GS/Stückelberg/CS)
1. **Input**: `configs/u1x_charges.json`, `configs/uv_ir_branes.json` \(\to\) `anomaly_necessity_U1X.py`.
2. **Output**: `cert/dsector_freezein/topo_anoms.json` con
   - `solvable_by_CS_only: true`
   - `gs_required: false`
3. **Conseguenza**: nessuna necessità di meccanismi alla Green-Schwarz; il parametro di quantizzazione della 2-group
   \(\ell = 0\) ⇒ **2-group OFF**, e quindi
   \[
   \ell=0,\qquad \kappa_a=0,\qquad g_{5,X}^2=0.
   \]
   Non esistono portali topologici aggiuntivi, né massa “extra” da Stückelberg/CS. (Questi valori sono scritti sia a livello root sia in `topology` in `configs/dsector_freezein_topo_from_ledger.json`.)

---

## (B) Spettro dal ledger RS
Ledger: `configs/dsector_freezein_topo_from_ledger.json` (blocco `ledger_RS`)
\[
z_{\rm UV}=10^{-3}\ \text{GeV}^{-1}\quad\Rightarrow\quad 1/z_{\rm UV}=10^3\ \text{GeV},
\]
\[
z_{\rm IR}=9325.35\ \text{GeV}^{-1}\quad\Rightarrow\quad m_X=\frac{1}{z_{\rm IR}}
= 1.072346\times10^{-4}\ \text{GeV}.
\]
Questa \(m_X\) è **fissata** dal ledger (niente libertà GS).

---

## (C) Pipeline di freeze-in gravitazionale (senza portali)
Script: `scripts/dsector_run.py` con config `configs/dsector_freezein_[spin]_from_ledger.json`.

Parametri cosmologici: \(M_{\rm Pl}^{\rm red}=2.435\times10^{18}\) GeV, \(g_* = g_{*s}=106.75\).
Si calcola il coefficiente efficace di produzione gravitazionale \(C_{\rm eff}\), poi la resa \(Y_\infty\),
\(\Omega h^2\) a \(T_R\) dato, e quindi si inverte per \(T_R^{\rm req}\).

Risultati (tutti **derivati** dal ledger):
- **Input comune**: \(T_R=10^{15}\) GeV (usato solo per mostrare la scala della resa).
- **Uscite**:
  - **Scalare**
    - \(C_{\rm eff}=10.870833\)
    - \(\Omega h^2(T_R{=}10^{15}\,{\rm GeV}) = 4.5187\times10^{-10}\)
    - \(T_R^{\rm req} = 6.4277\times10^{17}\) GeV
  - **Fermione**
    - \(C_{\rm eff}=32.52917\)
    - \(\Omega h^2(T_R{=}10^{15}\,{\rm GeV}) = 1.35215\times10^{-9}\)
    - \(T_R^{\rm req} = 4.4605\times10^{17}\) GeV
  - **Vettore**
    - \(C_{\rm eff}=140.9542\)
    - \(\Omega h^2(T_R{=}10^{15}\,{\rm GeV}) = 5.85909\times10^{-9}\)
    - \(T_R^{\rm req} = 2.7360\times10^{17}\) GeV

---

## (D) Vincolo EFT dal cut-off del ledger
Il cut-off dell’EFT è \(1/z_{\rm UV}=10^3\) GeV. Requisito minimo di consistenza:
\[
T_R \le \frac{1}{z_{\rm UV}} = 10^3\ {\rm GeV}.
\]
Confronto:
\[
\frac{T_R^{\rm req}}{1/z_{\rm UV}} =
\begin{cases}
6.43\times10^{14} & (\text{scalare})\\
4.46\times10^{14} & (\text{fermione})\\
2.74\times10^{14} & (\text{vettore})
\end{cases}
\]
⇒ **violazione EFT** di 14–15 ordini di grandezza.

Se si forza \(T_R = 1/z_{\rm UV}=10^3\) GeV (entro EFT), l’abbondanza crolla:
es. caso vettore
\(\Omega h^2(T_R{=}10^3\,\text{GeV}) = 5.86\times10^{-45}\)
⇒ **sottoproduzione** di \(\sim 10^{44}\).

---

## (E) Conclusione (NO-GO)
- Anomalie: `gs_required=false` ⇒ \(\ell=0\) ⇒ nessun portale topologico.
- Massa \(m_X\) fissa dal ledger \((=1/z_{\rm IR})\).
- Gravitational freeze-in puro richiede \(T_R^{\rm req}\sim10^{17}\) GeV, **incompatibile** con il cut-off \(10^3\) GeV.
- Non esistono gradi di libertà da “tarare”: ogni passo è determinato da ledger e teoria.
- **Verdetto**: _il meccanismo è falciato dalla teoria sotto i vincoli del ledger_.

### Reproducibilità
1) Anomalie/2-group:
```bash
python ToTU_KK_Analytic/tools/dm_cert/anomaly_necessity_U1X.py \
  --charges configs/u1x_charges.json \
  --brane   configs/uv_ir_branes.json \
  --out     cert/dsector_freezein/topo_anoms.json

