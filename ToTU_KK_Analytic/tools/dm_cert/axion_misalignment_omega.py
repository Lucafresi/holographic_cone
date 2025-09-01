#!/usr/bin/env python3
import json, argparse, math

def loadj(p): 
    with open(p,"r") as f: return json.load(f)

def pick(d, *paths):
    for p in paths:
        cur=d; ok=True
        for k in p:
            if isinstance(cur, dict) and k in cur: cur=cur[k]
            else: ok=False; break
        if ok: return cur
    raise KeyError(f"None of paths found: {paths}")

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--fa_file",   required=True, help="cert/DM/axion/f_a_GeV.json")
    ap.add_argument("--theta_file",required=True, help="cert/DM/axion/theta_i.json")
    ap.add_argument("--met",       required=True, help="cert/obs/metrology_dm.json")
    ap.add_argument("--ma_GeV", type=float, default=None, help="Override della massa (ALP).")
    ap.add_argument("--ma_file", default=None, help="cert/DM/axion/m_a_from_fa.json (per QCD axion).")
    ap.add_argument("--out",      required=True, help="output JSON")
    args=ap.parse_args()

    units = loadj(args.met)
    Mpl   = float(units["Mpl_reduced_GeV"])
    rho_c = float(units["rho_crit_over_h2_GeV_cm3"])
    s0    = float(units["s0_cm3"])
    gstar = float(units["gstar_const"])
    gS    = float(units["gstarS_const"])

    fa = float(loadj(args.fa_file)["f_a_GeV"])
    th = float(loadj(args.theta_file)["theta_i_rad"])

    if args.ma_GeV is not None:
        ma = float(args.ma_GeV)
        src = "override_ma_GeV"
    elif args.ma_file is not None:
        ma = float(pick(loadj(args.ma_file), ("ma_GeV",), ("ma","GeV")))
        src = "ma_file"
    else:
        raise SystemExit("Specifica --ma_GeV oppure --ma_file")

    # Oscillazioni: 3 H(T_osc) = m_a, H = 1.66 sqrt(g*) T^2 / Mpl
    Tosc = math.sqrt( ma * Mpl / (3.0*1.66*math.sqrt(gstar)) )

    # Numero a inizio oscillazioni (unità naturali): n = 1/2 m_a f_a^2 θ^2
    n_osc = 0.5 * ma * fa*fa * th*th

    # Entropia s(T) = (2π^2/45) g*_S T^3
    s_osc = (2*math.pi**2/45.0) * gS * Tosc**3

    # Yield conservato: Y = n/s
    Y = n_osc / s_osc

    # Densità oggi: Ω h^2 = m_a * s0 * Y / (ρ_c/h^2)
    Omega_h2 = ma * s0 * Y / rho_c

    out = {
      "schema_version": 1,
      "inputs": {
        "fa_GeV": fa,
        "theta_i_rad": th,
        "ma_GeV": ma,
        "ma_source": src,
        "metrology": { 
          "Mpl_reduced_GeV": Mpl,
          "rho_crit_over_h2_GeV_cm3": rho_c,
          "s0_cm3": s0,
          "gstar_const": gstar, "gstarS_const": gS
        }
      },
      "derived": {
        "T_osc_GeV": Tosc,
        "Y": Y
      },
      "Omega_h2": Omega_h2,
      "notes": "Constant g*, g*S misalignment. No dilution, no anharmonicity."
    }
    with open(args.out,"w") as f: json.dump(out,f,indent=2)
    print(f"[Ω] wrote {args.out}")
    print(f"[Ω] T_osc = {Tosc:.6e} GeV;  Y = {Y:.6e};  Ω_a h^2 = {Omega_h2:.6e}")
    print("[Ω] Target Ω_DM h^2 ≈ 0.12 for full DM")
if __name__=="__main__": main()
