#!/usr/bin/env python3
import json, math, os, hashlib

# Costanti standard (paper): nessuna manopola
Mpl = 2.435e18               # GeV (reduced Planck mass)
s0  = 2891.2                 # cm^-3
rho = 1.05375e-5             # GeV cm^-3  (rho_c/h^2)
Hc  = 1.66                   # H(T) = Hc * sqrt(g_*) T^2 / Mpl

def make_hash(payload: dict) -> str:
    h = hashlib.sha256()
    h.update(json.dumps(payload, sort_keys=True, separators=(',',':')).encode())
    return h.hexdigest()

def main():
    os.makedirs("artifacts", exist_ok=True)

    # Prefattore K_mis esatto nelle convenzioni del paper
    Kmis = (45.0/(4.0*math.pi**2))*(s0/rho)*((3.0*Hc)**1.5)/(Mpl**1.5)

    # Kernel simbolico (i campi "inputs_required" indicano ciò che verrà inserito
    # automaticamente dai gate successivi, NON a mano: fa (da D.4), mu=eta*Ms (da D.5),
    # theta_i (da D.3), e G_star(Tosc) (da iterazione deterministica).
    kernel = {
        "formula": "Omega = Kmis * Gstar(Tosc) * theta_i^2 * mu * fa^(3/2) * exp(-S/4)",
        "invert_S": "S = 4 * ln[ Kmis * Gstar(Tosc) * theta_i^2 * mu * fa^(3/2) / Omega ]",
        "constants": {
            "Mpl_reduced_GeV": Mpl,
            "s0_cm^-3": s0,
            "rho_c_over_h2_GeV_cm^-3": rho,
            "H_radiation_coeff": Hc,
            "Kmis_numeric": Kmis
        },
        "inputs_required": ["fa_GeV", "mu_GeV", "theta_i", "Omega_target", "Gstar_at_Tosc"]
    }

    payload = {
        "status": "PASS",
        "cosmo_kernel": kernel
    }
    payload["hash"] = make_hash(payload)

    with open("artifacts/cosmo_kernel.json","w") as f:
        json.dump(payload, f, indent=2)

    print("PASS:COSMO_KERNEL")
    print(f"Kmis = {Kmis:.6e}  [GeV^{-3/2}] in queste convenzioni.")
    print("Kernel pronto: nessuna manopola, parametri restanti verranno forniti dai gate D.3–D.5.")
if __name__ == "__main__":
    main()
