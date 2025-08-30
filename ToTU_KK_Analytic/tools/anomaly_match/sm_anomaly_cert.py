# -*- coding: utf-8 -*-
"""
SM anomaly matcher & 5D CS certification (per brana) — Sezione 7.

- Calcola esattamente (fractions) i tensori d’anomalia 4D per UNA famiglia SM per brana
  nel dialetto integrale (Y_int = 6Y; 2T(fund)=1).
- Risolve il matcher per brana e certifica che tutti i canali SM hanno K=0 ⇒ k_canale=0.
- Scrive due certificati JSON (UV/IR) in ToTU_KK_Analytic/cert/anomaly_match/.

NOTA: questo NON è il k topologico che entra in N=|k| (Catena A). Qui certifichiamo
SOLO che nei canali SM il matcher locale richiede livelli CS nulli (coerente con NFF).
"""

from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction
from typing import List, Dict
from collections import defaultdict
import argparse, json, os
from datetime import datetime

# Ledger e convenzioni (coerenti con il manoscritto)
SIGMA = {"UV": -1, "IR": +1}           # outward–normal–first
T2_DOUBLE = Fraction(1, 1)             # 2*T(fund)=1 (e 2*T(doublet)=1)
BASIS_DESC = "integral (Y_int = 6Y); 2T(fund)=1"

@dataclass(frozen=True)
class Multiplet:
    """Rappresentazione LH con carica Y standard (non 6Y)."""
    name: str
    dim_su3: int
    dim_su2: int
    Y: Fraction
    rep_su3: str          # '3', '3bar' o '1'
    rep_su2: str          # '2' o '1'

    def multiplicity(self) -> int:
        return self.dim_su3 * self.dim_su2

    def is_su3_fund(self) -> int:
        if self.rep_su3 == '3':
            return +1
        elif self.rep_su3 == '3bar':
            return -1
        return 0

    def is_su2_doublet(self) -> bool:
        return self.rep_su2 == '2'


def sm_one_family_LH_basis() -> List[Multiplet]:
    """Le cinque reps SM in base LH (conjugate per i destri), Y in normalizzazione standard."""
    return [
        Multiplet("Q_L",   3, 2, Fraction(1, 6),  '3',    '2'),
        Multiplet("u_R^c", 3, 1, Fraction(-2, 3), '3bar', '1'),
        Multiplet("d_R^c", 3, 1, Fraction(1, 3),  '3bar', '1'),
        Multiplet("L_L",   1, 2, Fraction(-1, 2), '1',    '2'),
        Multiplet("e_R^c", 1, 1, Fraction(1, 1),  '1',    '1'),
    ]


def compute_anomaly_coeffs(mults: List[Multiplet]) -> Dict[str, Fraction]:
    """
    Restituisce i tensori d’anomalia esatti (Fractions) nel ledger integrale.
    Canali:
      - SU3_cubic   : [SU(3)]^3
      - SU2_cubic   : [SU(2)]^3 (0 in teoria perturbativa)
      - U1_cubic    : U(1)^3
      - U1_SU3sq    : U(1)-SU(3)^2
      - U1_SU2sq    : U(1)-SU(2)^2
      - U1_grav     : U(1)-grav^2
    """
    K = defaultdict(Fraction)

    for m in mults:
        mult = m.multiplicity()

        # Abeliano cubico e grav^2
        K["U1_cubic"] += mult * (m.Y ** 3)
        K["U1_grav"]  += mult * m.Y

        # SU(3) cubico: multiplicità SU(2) * (fund - antifund)
        if m.rep_su3 in ('3', '3bar'):
            K["SU3_cubic"] += m.dim_su2 * m.is_su3_fund()
            # U(1)-SU(3)^2: 2T(fund)=1
            K["U1_SU3sq"] += m.dim_su2 * m.Y * T2_DOUBLE

        # SU(2) cubico: 0 (nessun invariante cubico per SU(2))
        # U(1)-SU(2)^2: solo doublet, contare la molteplicità di colore
        if m.is_su2_doublet():
            color_mult = m.dim_su3
            K["U1_SU2sq"] += color_mult * m.Y * T2_DOUBLE

    K["SU2_cubic"] = Fraction(0, 1)
    return dict(K)


def cert_json_for_brane(brane: str, K: Dict[str, Fraction]) -> Dict:
    """
    Certificato per brana:
      - 'K_exact': frazioni esatte
      - 'K_float': numeri in virgola mobile (solo per comodità visiva)
      - 'k_solution_min': soluzione minima del matcher (attesa 0 per tutti i canali SM)
      - 'pass': True se tutti i canali SM sono annullati per brana (K=0)
    """
    sigma = SIGMA[brane]  # tracciabilità, anche se qui K=0 ⇒ k=0
    solutions = {ch: 0 if K[ch] == 0 else None for ch in K}
    passed = all(K[ch] == 0 for ch in K)

    return {
        "schema_version": 1,
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "brane": brane,
        "sigma": sigma,
        "basis": BASIS_DESC,
        "channels": sorted(list(K.keys())),
        "K_exact": {ch: f"{K[ch]}" for ch in K},
        "K_float": {ch: float(K[ch]) for ch in K},
        "k_solution_min": solutions,
        "pass": passed
    }


def write_certificates(output_dir: str) -> None:
    os.makedirs(output_dir, exist_ok=True)
    K = compute_anomaly_coeffs(sm_one_family_LH_basis())
    for brane in ("UV", "IR"):
        data = cert_json_for_brane(brane, K)
        path = os.path.join(output_dir, f"{brane}.json")
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
        print(f"[OK] wrote {path}")


def main(argv=None) -> int:
    p = argparse.ArgumentParser(
        description="Certifica anomalie SM per brana e livelli CS_canale minimi (0)."
    )
    p.add_argument(
        "--out",
        default=os.path.join("ToTU_KK_Analytic", "cert", "anomaly_match"),
        help="Dir di output per i certificati JSON (default: ToTU_KK_Analytic/cert/anomaly_match)"
    )
    args = p.parse_args(argv)
    write_certificates(args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
