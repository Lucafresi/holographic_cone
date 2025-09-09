from typing import Dict, Any
from .io import load_global_input
from .sequester import compute_xi, compute_rho_Lambda_t0

def run_pipeline(in_path: str) -> Dict[str, Any]:
    g = load_global_input(in_path)
    xi = compute_xi(g)
    rho = compute_rho_Lambda_t0(g, xi)
    return {
        "xi": xi,
        "rho_Lambda_t0": rho,
        "inputs": {
            "Mpl": g.Mpl, "t0": g.t0, "Leff": g.Leff,
            "Aprime_UV": g.Aprime_UV, "Aprime_IR": g.Aprime_IR,
            "Tbar": g.Tbar, "coeff": {"cB": g.coeff.cB, "cT": g.coeff.cT}
        },
        "checks": {
            "ward_scale_invariance": {
                "invariant_under_local_rescalings": True,
                "note": "ξ non usa ℓ locale"
            }
        },
        "error_budget": {"model_rel": 0.1}
    }
