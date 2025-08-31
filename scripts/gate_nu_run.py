import json, os, sys, numpy as np
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))

from gate_nu.spectrum import find_roots_phi
from gate_nu.bc import r_uv, phi_ir
from gate_nu.fermion_bessel import fL_fR_profile, fL_fR_point
from gate_nu.normalize import cheb_lobatto, normalize_mode
from gate_nu.zero_mode import zero_mode_profile_L
from gate_nu.mixing import pick_value_at_brane, y4D_brane, sin2_2theta



def resid_norm_at_IR(m, c, aUV, aIR, zUV, zIR):
    r = float(r_uv(m, c, aUV, zUV))
    fL_IR, fR_IR = fL_fR_point(zIR, m, c, r)

    def comp(alpha, fL, fR):
        if isinstance(alpha, str) and alpha.lower() in ("inf","+inf","infty","infinite","infinity"):
            num = abs(fL)
            den = np.sqrt(fL*fL + fR*fR)
        else:
            a = float(alpha)
            num = abs(fR + a*fL)
            den = np.sqrt(fR*fR + (1.0 + a*a)*fL*fL)
        return float(num), float(den)

    num, den = comp(aIR, fL_IR, fR_IR)
    eps = 1e-300
    if not np.isfinite(den) or den < eps:
        # probe leggermente dentro la brana IR per evitare 0/0 numerico
        delta = max((zIR - zUV) * 1e-9, 1e-15)
        zP = zIR - delta
        fL_P, fR_P = fL_fR_point(zP, m, c, r)
        numP, denP = comp(aIR, fL_P, fR_P)
        if not np.isfinite(denP) or denP < eps:
            # se anche il probe è degenerato: 0 se entrambi ~0, altrimenti 1
            if (not np.isfinite(num) or num <= eps) and (not np.isfinite(numP) or numP <= eps):
                return 0.0
            return 1.0
        return float(numP / denP)

    return float(num / den)

def main(cfg_path):
    with open(cfg_path, "r") as f: cfg = json.load(f)

    L      = float(cfg["geometry"]["L"])
    z_UV   = float(cfg["geometry"]["z_UV"])
    z_IR   = float(cfg["geometry"]["z_IR"])

    # Sterile
    c_s    = float(cfg["fermion"]["c"])
    aUV_s  = cfg["fermion"]["alpha_UV"]
    aIR_s  = cfg["fermion"]["alpha_IR"]

    # Fermione L del SM (zero-mode)
    c_L    = float(cfg["fermion_L"]["c"])
    aUV_L  = cfg["fermion_L"]["alpha_UV"]
    aIR_L  = cfg["fermion_L"]["alpha_IR"]
    L_kind = str(cfg["fermion_L"].get("zero_kind","L")).upper()  # "L" o "R" per il tipo di zero-mode desiderato

    gridN  = int(cfg["grid"]["N"])
    zH_loc = str(cfg["sm"]["z_H"])  # "UV" o "IR"
    lamB   = float(cfg["sm"]["lambda_B"])
    h0     = float(cfg["sm"].get("H0", 1.0))  # fattore Higgs locale (1 se puramente di brana)

    z_H = z_UV if zH_loc.upper()=="UV" else z_IR

    # Spettro sterile
    m_min = 1e-8 / z_IR; m_max = 50.0 / z_IR
    roots = find_roots_phi(c_s, aUV_s, aIR_s, z_UV, z_IR, m_min=m_min, m_max=m_max,
                           n_samples=20000, max_roots=6, tol=1e-14)
    if not roots: raise SystemExit("Nessun autovalore sterile trovato.")

    m_s = float(roots[0])
    z_grid, w = cheb_lobatto(z_UV, z_IR, gridN)
    r_s = float(r_uv(m_s, c_s, aUV_s, z_UV))
    fL_s, fR_s = fL_fR_profile(z_grid, m_s, c_s, r_s)
    fL_s, fR_s, _ = normalize_mode(fL_s, fR_s, z_grid, w, L=L)

    # Zero-mode del fermione L (analitico + normalizzazione)
    fL_L, fR_L, _ = zero_mode_profile_L(z_grid, c_L, L, kind=L_kind)

    # Residuo relativo su sterile
    resid_raw = float(abs(phi_ir(m_s, c_s, aUV_s, aIR_s, z_UV, z_IR)))
    resid_rel = resid_norm_at_IR(m_s, c_s, aUV_s, aIR_s, z_UV, z_IR)
    pass_rel  = bool(resid_rel < 1e-10)

    # Valori dei profili alla brana z_H (NB: se un proiettore azzera la componente alla brana, il valore sarà ~0)
    f_s_L_at = pick_value_at_brane(fL_s, z_grid, z_H)
    f_s_R_at = pick_value_at_brane(fR_s, z_grid, z_H)
    g_L_L_at = pick_value_at_brane(fL_L, z_grid, z_H)
    g_L_R_at = pick_value_at_brane(fR_L, z_grid, z_H)

    # Scelta delle componenti chirali che partecipano al vertice (ledger: dipende da parità/BC).
    # Default: L zero-mode sinistro ("L_kind"="L") e sterile destrino su brana (usa componente R dello sterile).
    use_s = "R" if cfg["sm"].get("sterile_chirality_at_brane","R").upper()=="R" else "L"
    use_L = "L" if L_kind=="L" else "R"

    f_s_at = f_s_R_at if use_s=="R" else f_s_L_at
    g_L_at = g_L_L_at if use_L=="L" else g_L_R_at

    # Yukawa 4D corretto e mixing
    y4d = y4D_brane(lamB, L, z_H, f_s_at, g_L_at, h0=h0)
    s2  = sin2_2theta(m_s, y4d, v=246.0)

    outdir = os.path.join(ROOT, "cert", "gate_nu"); os.makedirs(outdir, exist_ok=True)
    with open(os.path.join(outdir, "spectrum.json"), "w") as f:
        json.dump({"masses":[float(x) for x in roots], "m_s": m_s}, f, indent=2)
    with open(os.path.join(outdir, "mode_s.json"), "w") as f:
        json.dump({"z": z_grid.tolist(),"fL_norm": fL_s.tolist(),"fR_norm": fR_s.tolist()}, f, indent=2)
    with open(os.path.join(outdir, "mode_L0.json"), "w") as f:
        json.dump({"z": z_grid.tolist(),"fL0_norm": fL_L.tolist(),"fR0_norm": fR_L.tolist(),
                   "c_L": c_L, "alpha_UV_L": aUV_L, "alpha_IR_L": aIR_L, "zero_kind": L_kind}, f, indent=2)
    with open(os.path.join(outdir, "mixing.json"), "w") as f:
        json.dump({
            "z_H": float(z_H), "lambda_B": float(lamB), "H0": float(h0),
            "use_sterile_chirality": use_s, "use_L_chirality": use_L,
            "y4D": float(y4d), "sin2_2theta": float(s2)
        }, f, indent=2)
    with open(os.path.join(outdir, "cert.json"), "w") as f:
        json.dump({
            "residual_Phi_IR_raw": resid_raw,
            "residual_Phi_IR_rel": resid_rel,
            "residual_rel_pass": pass_rel,
            "grid_nodes": int(gridN)
        }, f, indent=2)

    print("=== Gate-ν run ===")
    print(f"m_s = {m_s:.12e}")
    print(f"phi_raw = {resid_raw:.3e}   phi_rel = {resid_rel:.3e}  -> PASS:{pass_rel}")
    print(f"y4D = {y4d:.6e}   sin^2(2θ) = {s2:.6e}")
    print(f"Outputs -> {outdir}/(spectrum.json, mode_s.json, mode_L0.json, mixing.json, cert.json)")

if __name__ == "__main__":
    if len(sys.argv)!=2:
        print("Uso: python scripts/gate_nu_run.py configs/gate_nu_ledger.json"); sys.exit(1)
    main(sys.argv[1])
