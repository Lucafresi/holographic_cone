from dataclasses import dataclass
from typing import Dict, Any
import json

@dataclass(frozen=True)
class Coeff:
    cB: float
    cT: float

@dataclass(frozen=True)
class GlobalInput:
    Mpl: float
    t0: float
    Leff: float
    Aprime_UV: float
    Aprime_IR: float
    Tbar: float
    coeff: Coeff

def load_global_input(path: str) -> GlobalInput:
    with open(path, "r") as f:
        d = json.load(f)
    c = d.get("coeff", {})
    return GlobalInput(
        Mpl=float(d["Mpl"]),
        t0=float(d["t0"]),
        Leff=float(d["Leff"]),
        Aprime_UV=float(d["Aprime_UV"]),
        Aprime_IR=float(d["Aprime_IR"]),
        Tbar=float(d["Tbar"]),
        coeff=Coeff(cB=float(c.get("cB",1.0)), cT=float(c.get("cT",1.0)))
    )
