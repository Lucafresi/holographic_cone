#!/usr/bin/env python3
import json, argparse, math
import mpmath as mp
from pathlib import Path

def loadj(p): 
    with open(p,"r") as f: return json.load(f)

def rho_radiation_phys(T_GeV, N_eff, Tnu_over_Tg):
    # ρ_γ = (π^2/15) T^4 ;  ρ_ν = (7/8)(π^2/15) N_eff (Tν)^4
    pi2_over_15 = (mp.pi**2)/15
    rho_gamma = pi2_over_15 * (T_GeV**4)
    rho_nu    = (7/8)*pi2_over_15 * mp.mpf(N_eff) * (Tnu_over_Tg**4) * (T_GeV**4)
    return rho_gamma + rho_nu, rho_gamma, rho_nu

def K_to_GeV(T_K):
    # k_B in GeV/K
    kB_GeV_per_K = 8.617333262145e-14
    return mp.mpf(T_K) * kB_GeV_per_K

def main():
    ap = argparse.ArgumentParser(description="C_obs: H(z) deterministico da Λ4 + radiazione SM (+ opz. materia/curvatura).")
    ap.add_argument("--Lambda4", default="cert/cosmo/Lambda4.json")
    ap.add_argument("--units",   default="cert/units/eh_units.json")
    ap.add_argument("--met",     default="cert/obs/metrology_cosmo.json")
    ap.add_argument("--matter",  default="", help="(opz.) JSON con {rho_m0_EH, rho_k0_EH} in unità EH")
    ap.add_argument("--zmax", type=float, default=1100.0)
    ap.add_argument("--Nz",   type=int,   default=400)
    ap.add_argument("--out_json", default="cert/cosmo/C_obs/H_curve.json")
    ap.add_argument("--out_csv",  default="cert/cosmo/C_obs/H_curve.csv")
    ap.add_argument("--prec", type=int, default=120)
    args = ap.parse_args()

    mp.mp.dps = args.prec

    # --- input di ledger ---
    Lam = mp.mpf(loadj(args.Lambda4)["Lambda4"])              # Λ4 in unità EH (≡ densità vacuo in unità Mpl=1)
    units = loadj(args.units)
    met   = loadj(args.met)

    Mpl  = mp.mpf(units["Mpl_reduced_GeV"])                   # GeV
    Tcmb = mp.mpf(met["T_CMB_K"])
    Neff = mp.mpf(met["N_eff"])
    Tnu_over_Tg = mp.mpf(met["Tnu_over_Tgamma"])

    # radiazione SM: ρ_r (GeV^4) e conversione a unità EH (GeV^2) dividendo per Mpl^2
    Tcmb_GeV = K_to_GeV(Tcmb)
    rho_r_phys, rho_gamma_phys, rho_nu_phys = rho_radiation_phys(Tcmb_GeV, Neff, Tnu_over_Tg)
    rho_r_EH = rho_r_phys / (Mpl**2)
    rho_gamma_EH = rho_gamma_phys / (Mpl**2)
    rho_nu_EH = rho_nu_phys / (Mpl**2)

    # opzionale: materia e curvatura in unità EH
    rho_m0_EH = mp.mpf("0")
    rho_k0_EH = mp.mpf("0")
    matter_src = "none"
    if args.matter:
        m = loadj(args.matter)
        rho_m0_EH = mp.mpf(m.get("rho_m0_EH", 0.0))
        rho_k0_EH = mp.mpf(m.get("rho_k0_EH", 0.0))
        matter_src = "explicit_EH_densities"

    # H_Λ = sqrt(Λ4/3) in unità EH (GeV)
    H_L = mp.sqrt(Lam/3)

    # E(z)^2 = 1 + (ρ_r0/Λ) (1+z)^4 + (ρ_m0/Λ)(1+z)^3 + (ρ_k0/Λ)(1+z)^2
    eps_r = rho_r_EH / Lam
    eps_m = rho_m0_EH / Lam if rho_m0_EH != 0 else mp.mpf("0")
    eps_k = rho_k0_EH / Lam if rho_k0_EH != 0 else mp.mpf("0")

    def E_of_z(z):
        zp1 = 1+z
        return mp.sqrt( 1 + eps_r * (zp1**4) + eps_m * (zp1**3) + eps_k * (zp1**2) )

    # griglia z (densa a basso z + log up to zmax)
    zmax = mp.mpf(args.zmax)
    Nz   = int(args.Nz)
    z_lin = [ mp.mpf(i)/(Nz//2) * min(zmax, mp.mpf("3.0")) for i in range(Nz//2) ]
    z_log = []
    if zmax > 3:
        zmin_log = mp.mpf("3.0")+1e-12
        for i in range(Nz//2):
            t = mp.mpf(i)/(Nz//2-1) if Nz//2>1 else mp.mpf("0")
            val = zmin_log * (zmax/zmin_log)**t
            z_log.append(val)
    Z = z_lin + z_log

    # H(z), E(z); distanze (flat se rho_k=0). Unità: H in GeV; distanze in GeV^-1 e in Mpc
    hbar_GeVs = mp.mpf(met["hbar_GeVs"])
    s_per_GeV = 1 / hbar_GeVs
    Mpc_km    = mp.mpf(met["Mpc_km"])

    def H_of_z(z): return H_L * E_of_z(z)  # GeV
    def chi_of_z(z):
        # χ(z) = ∫_0^z dz'/H(z')
        f = lambda zz: 1 / H_of_z(zz)
        return mp.quad(f, [0, z])
    def DL_DA(z):
        chi = chi_of_z(z)    # GeV^-1
        DA  = chi / (1+z)    # GeV^-1
        DL  = chi * (1+z)    # GeV^-1
        return DL, DA, chi

    # conversioni utili
    # H0 [km/s/Mpc] = H0 [s^-1] * Mpc[km]
    H0_GeV   = H_of_z(0)
    H0_sinv  = H0_GeV * s_per_GeV
    H0_km_s_Mpc = H0_sinv * Mpc_km
    little_h = H0_km_s_Mpc / 100

    # dump CSV
    Path(args.out_csv).parent.mkdir(parents=True, exist_ok=True)
    with open(args.out_csv,"w") as f:
        f.write("z,H_GeV,E,DL_GeV^-1,DA_GeV^-1,chi_GeV^-1\n")
        for z in Z:
            DL, DA, chi = DL_DA(z)
            f.write(f"{float(z)},{float(H_of_z(z))},{float(E_of_z(z))},{float(DL)},{float(DA)},{float(chi)}\n")

    # dump JSON
    out = {
      "schema_version": 1,
      "inputs": {
        "Lambda4_file": args.Lambda4,
        "units_file": args.units,
        "met_file": args.met,
        "matter_file": args.matter if args.matter else None
      },
      "ledger": {
        "Lambda4_EH": float(Lam),
        "rho_r0_EH": float(rho_r_EH),
        "rho_gamma0_EH": float(rho_gamma_EH),
        "rho_nu0_EH": float(rho_nu_EH),
        "rho_m0_EH": float(rho_m0_EH),
        "rho_k0_EH": float(rho_k0_EH),
        "eps_r": float(eps_r), "eps_m": float(eps_m), "eps_k": float(eps_k),
        "matter_source": matter_src
      },
      "anchors": {
        "H_L_GeV": float(H_L),
        "H0_GeV": float(H0_GeV),
        "H0_s^-1": float(H0_sinv),
        "H0_km/s/Mpc": float(H0_km_s_Mpc),
        "h": float(little_h)
      },
      "grid": [float(z) for z in Z],
      "note": "C_obs deterministic: H(z) from Λ4 + SM radiation (+ optional EH-densities for matter/curvature)."
    }
    Path(args.out_json).parent.mkdir(parents=True, exist_ok=True)
    with open(args.out_json,"w") as f: json.dump(out, f, indent=2)

    print(f"[C_obs] wrote {args.out_csv} and {args.out_json}")
    print(f"[C_obs] H_L = {mp.nstr(H_L, 8)} GeV;  H0 = {mp.nstr(H0_km_s_Mpc, 8)} km/s/Mpc;  h = {mp.nstr(little_h, 8)}")
    print(f"[C_obs] eps: rad={mp.nstr(eps_r,10)}, mat={mp.nstr(eps_m,10)}, curv={mp.nstr(eps_k,10)}")

if __name__ == "__main__":
    main()
