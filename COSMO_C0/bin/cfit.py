#!/usr/bin/env python3
import sys, json, numpy as np, pandas as pd
from math import sqrt
from scipy.stats import kstest, norm, spearmanr

def load_json(p):
    with open(p,"r") as f: return json.load(f)

def chi2(y, yhat, sigma):
    r = (y - yhat)/sigma
    return float(np.sum(r*r)), int(y.size)

def sne_marginalized(z, mu_obs, sig, z_grid, DL_Mpc):
    # teorico senza intercetta
    DLq = np.interp(z, z_grid, DL_Mpc)
    mu_th = 5.0*np.log10(np.maximum(DLq,1e-30)) + 25.0
    # pesi e differenze
    w  = 1.0/np.maximum(sig, 1e-30)**2
    d  = mu_obs - mu_th
    S0 = np.sum(w)
    S1 = np.sum(w*d)
    S2 = np.sum(w*d*d)
    # chi^2 marginalizzato (analitico)
    chi2_marg = float(S2 - (S1*S1)/S0)
    dof = int(z.size - 1)  # 1 parametro (offset) marginalizzato
    # residui standardizzati per i test: togli l'offset ottimo Δ = S1/S0
    Delta = S1/S0
    res   = (d - Delta)/np.maximum(sig,1e-30)
    return chi2_marg, dof, res

def runs_test(signs):
    # signs: array di +1/-1 (zero esclusi)
    s = [int(1 if x>0 else -1) for x in signs if x!=0]
    if len(s)<2: return 1.0  # p=1 se troppo pochi
    R = 1 + sum(1 for i in range(1,len(s)) if s[i]!=s[i-1])
    n1 = s.count(1); n2 = s.count(-1); N = n1+n2
    if n1==0 or n2==0: return 0.0  # tutti stessi segni -> p≈0
    mu = 2*n1*n2/N + 1
    var = (2*n1*n2*(2*n1*n2 - n1 - n2))/((N**2)*(N-1))
    if var<=0: return 1.0
    z = (R - mu)/sqrt(var)
    # p-value due code ~ N(0,1)
    from math import erf
    p = 2*0.5*(1 - erf(abs(z)/sqrt(2)))
    return max(0.0, min(1.0, p))

def bin_uniformity_z(res_std, z, nbins=6):
    # controlla che in ciascun bin: sum(e_i^2) ~ dof_bin (z-score |z|<=3)
    edges = np.quantile(z, np.linspace(0,1,nbins+1))
    ok = True; worst = {"bin":None, "zscore":0.0}
    for b in range(nbins):
        lo, hi = edges[b], edges[b+1] + (1e-12 if b==nbins-1 else 0.0)
        sel = (z>=lo) & (z<hi)
        e = res_std[sel]
        dof = e.size
        if dof<5:  # troppo pochi per test sensato
            continue
        S = float(np.sum(e*e))
        zscore = (S - dof)/sqrt(2*dof)  # ~N(0,1)
        if abs(zscore) > abs(worst["zscore"]):
            worst = {"bin": b, "zscore": float(zscore)}
        if abs(zscore) > 3.0:  # 3σ severo
            ok = False
    return ok, worst

if __name__=="__main__":
    if len(sys.argv)<5:
        print("usage: cfit.py H_curve.csv distances.csv cfit_config.json out_report.json"); sys.exit(2)

    dfH = pd.read_csv(sys.argv[1])
    dfd = pd.read_csv(sys.argv[2])
    cfg = load_json(sys.argv[3])

    z_grid = dfd["z"].values
    H  = dfH["H_km_s_Mpc"].values
    H0 = float(H[0])
    DL = dfd["D_L_Mpc"].values

    chi2_tot = 0.0
    dof_tot  = 0
    blocks   = {}
    used_any = False
    hard_tests = {}

    # ===== SNe (marginalizzazione analitica; test severi su residui) =====
    if cfg.get("sne_csv", None):
        sne = pd.read_csv(cfg["sne_csv"])
        zq   = sne["z"].values
        mu   = sne["mu"].values
        sig  = sne["sigma_mu"].values
        c2, dof, res_std = sne_marginalized(zq, mu, sig, z_grid, DL)
        chi2_tot += c2; dof_tot += dof; used_any = True
        blocks["SNe_chi2"] = c2; blocks["SNe_dof"] = dof

        # Test 1: normalità KS su residui standardizzati
        ks_stat, ks_p = kstest(res_std, cdf='norm')
        hard_tests["SNe_KS_p"] = float(ks_p)
        # Test 2: indipendenza (runs test)
        runs_p = runs_test(np.sign(res_std))
        hard_tests["SNe_Runs_p"] = float(runs_p)
        # Test 3: assenza trend con z (Spearman)
        rho, sp_p = spearmanr(zq, res_std)
        hard_tests["SNe_Spearman_rho"] = float(rho)
        hard_tests["SNe_Spearman_p"]   = float(sp_p)
        # Test 4: uniformità per bin
        ok_bins, worst = bin_uniformity_z(res_std, zq, nbins=6)
        hard_tests["SNe_BinUniform_ok"] = bool(ok_bins)
        hard_tests["SNe_BinUniform_worst_zscore"] = float(worst["zscore"])

    # ===== BAO (opzionale; richiede rs_Mpc nei dati) =====
    if cfg.get("bao_csv", None):
        bao = pd.read_csv(cfg["bao_csv"])
        c_km_s = 299792.458
        zb = bao["z"].values
        DM = np.interp(zb, z_grid, dfd["D_M_Mpc"].values)
        DA = np.interp(zb, z_grid, dfd["D_A_Mpc"].values)
        Hz = np.interp(zb, dfH["z"].values, dfH["H_km_s_Mpc"].values)
        if {"DV_over_rs","sigma","rs_Mpc"} <= set(bao.columns):
            DV = ((1.0+zb)**2*DA**2*c_km_s*zb/Hz)**(1.0/3.0)
            yhat = DV/bao["rs_Mpc"].values
            c2, n = chi2(bao["DV_over_rs"].values, yhat, bao["sigma"].values)
            blocks["BAO_DVrs_chi2"] = c2; blocks["BAO_DVrs_dof"] = n
            chi2_tot += c2; dof_tot += n; used_any = True
        if {"DM_over_rs","sigma_DM","rs_Mpc"} <= set(bao.columns):
            yhat = DM/bao["rs_Mpc"].values
            c2, n = chi2(bao["DM_over_rs"].values, yhat, bao["sigma_DM"].values)
            blocks["BAO_DMrs_chi2"] = blocks.get("BAO_DMrs_chi2",0.0)+c2
            blocks["BAO_DMrs_dof"]  = blocks.get("BAO_DMrs_dof",0)+n
            chi2_tot += c2; dof_tot += n; used_any = True
        if {"Hz_rs","sigma_Hz","rs_Mpc"} <= set(bao.columns):
            yhat = Hz*bao["rs_Mpc"].values/c_km_s
            c2, n = chi2(bao["Hz_rs"].values, yhat, bao["sigma_Hz"].values)
            blocks["BAO_Hzrs_chi2"] = blocks.get("BAO_Hzrs_chi2",0.0)+c2
            blocks["BAO_Hzrs_dof"]  = blocks.get("BAO_Hzrs_dof",0)+n
            chi2_tot += c2; dof_tot += n; used_any = True

    # ===== H0 (opzionale) =====
    if cfg.get("h0_csv", None):
        h0 = pd.read_csv(cfg["h0_csv"])
        H0_obs = float(h0["H0_km_s_Mpc"].iloc[0])
        sig = float(h0["sigma"].iloc[0])
        c2 = (H0 - H0_obs)**2/(sig*sig)
        blocks["H0_chi2"] = c2; blocks["H0_dof"] = 1
        chi2_tot += c2; dof_tot += 1; used_any = True

    # Nessun dataset => FAIL
    if not used_any:
        report = {"reason":"NO_DATASETS","chi2_total":0.0,"dof_total":0,"chi2_reduced":None,
                  "PASS": False, "blocks": blocks, "hard_tests": hard_tests}
        with open(sys.argv[4],"w") as f: json.dump(report,f,indent=2)
        print("C_FIT: PASS=False reason=NO_DATASETS")
        sys.exit(0)

    red = chi2_tot/max(dof_tot,1)
    # Regole dure: chi2_red <= 1.0 ; KS p>=0.01 ; runs p>=0.01 ; Spearman p>=0.01 ; bin-uniform ok
    pass_reduced = (red <= 1.0)
    t_ok = True
    if "SNe_KS_p" in hard_tests:        t_ok &= (hard_tests["SNe_KS_p"]      >= 0.01)
    if "SNe_Runs_p" in hard_tests:      t_ok &= (hard_tests["SNe_Runs_p"]    >= 0.01)
    if "SNe_Spearman_p" in hard_tests:  t_ok &= (hard_tests["SNe_Spearman_p"]>= 0.01)
    if "SNe_BinUniform_ok" in hard_tests: t_ok &= bool(hard_tests["SNe_BinUniform_ok"])

    PASS = bool(pass_reduced and t_ok)

    report = {
        "chi2_total": float(chi2_tot),
        "dof_total": int(dof_tot),
        "chi2_reduced": float(red),
        "PASS_REDUCED_CHI2_LE_1": bool(pass_reduced),
        "PASS": PASS,
        "blocks": blocks,
        "hard_tests": hard_tests
    }
    with open(sys.argv[4],"w") as f: json.dump(report,f,indent=2)
    print(f"C_FIT: PASS={PASS} chi2_red={red:.3f}")
