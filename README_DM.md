# DM — Assione/ALP dal ledger (NO-GO per DM totale)

Catena certificata:
  - Norm dal collar: tools/dm_cert/axion_norm_from_collar.py → cert/DM/axion/axion_norm.json
  - Coefficienti anomali interi: axion_couplings_from_ledger.py → cert/DM/axion/axion_couplings.json
  - Rotazione EWSB + g fisici: axion_to_photon_gluon.py → cert/DM/axion/axion_ew_rot.json
  - f_a in GeV da M_pl: fa_from_units.py → cert/DM/axion/f_a_GeV.json
  - m_a(QCD) da f_a: axion_mass_from_fa.py → cert/DM/axion/m_a_from_fa.json
  - θ_i dagli invarianti: axion_theta_from_invariants.py → cert/DM/axion/theta_i.json
  - Misalignment: axion_misalignment_omega.py → cert/DM/axion/omega_QCD.json
  - Target mass per Ω_DM h^2≈0.12 (diagnostica): cert/DM/axion/m_a_target_for_DM.json

Verdetto:
  - Con f_a fissato (∼M_pl) e θ_i quantizzato → Ω_a h^2 ≫ 1 (overclosure) per m_a QCD-like.
  - Per forzare Ω ≈ 0.12 servirebbe m_a ~ 10^{-36} GeV → incompatibile con struttura.
  ⇒ ALP minimo non è DM totale (NO-GO). Resta componente subdominante/invisibile.

File chiave:
  - cert/DM/metrology.json
  - dm_inputs/U1X_charges.json, dm_inputs/brane_counts.json
  - tutti i JSON in cert/DM/axion/
