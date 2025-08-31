import math

def g4_from_g5_RS(g5_sq, L, zUV, zIR):
    # 1/g4^2 = (L/g5^2) * log(zIR/zUV)  ->  g4^2 = g5^2 / (L log)
    if g5_sq <= 0 or L <= 0 or not (zIR > zUV > 0):
        raise ValueError("Parametri non fisici per g4_from_g5_RS")
    return g5_sq / (L * math.log(zIR / zUV))

def IB_flat_RS(L, zUV, zIR):
    # I_B = ∫(L/z)^3 dz = (L^3/2)(1/zUV^2 - 1/zIR^2)
    if not (zIR > zUV > 0) or L <= 0:
        raise ValueError("Parametri non fisici per IB_flat_RS")
    return (L**3) * 0.5 * (1.0/(zUV**2) - 1.0/(zIR**2))

def mX_stueckelberg_from_ledger(*, g5_sq, kappa_a, L, zUV, zIR, ell, profile="flat", z_star=None, rB_coeff=None):
    """
    m_X = |ell| * g4 / sqrt(Z_B), con:
      g4^2 = g5^2 / (L log(zIR/zUV))
      Z_B  = kappa_a * I_B
    profile:
      - "flat":   I_B = ∫(L/z)^3 dz     (profilo 0-mode piatto; dipendenza geometrica pura)
      - "brane":  I_B = (L/z_star)^3 * rB_coeff   (2-forma localizzata in brana con coeff. di brana)
    Tutti i parametri devono arrivare dal ledger (nessun default ad-hoc).
    """
    if ell is None:
        raise ValueError("ell (livello BF/2-group) mancante dal ledger")
    if not isinstance(ell, int) or ell == 0:
        raise ValueError("ell deve essere un intero non nullo (quantizzazione 2-group)")

    g4_sq = g4_from_g5_RS(g5_sq, L, zUV, zIR)

    if profile == "flat":
        IB = IB_flat_RS(L, zUV, zIR)
    elif profile == "brane":
        if z_star not in ("UV","IR"):
            raise ValueError("profile=brane richiede z_star in {UV,IR}")
        zpos = zUV if z_star == "UV" else zIR
        if rB_coeff is None or rB_coeff <= 0:
            raise ValueError("profile=brane richiede rB_coeff > 0 dal ledger")
        IB = (L / zpos)**3 * rB_coeff
    else:
        raise ValueError("profile non riconosciuto: usare 'flat' o 'brane'")

    ZB = kappa_a * IB
    if ZB <= 0:
        raise ValueError("Z_B non fisico (<=0)")

    g4 = math.sqrt(g4_sq)
    fX = 1.0 / math.sqrt(ZB)
    mX = abs(ell) * g4 * fX   # in GeV (unità del repo: z in GeV^-1)
    return mX, {"g4_sq": g4_sq, "IB": IB, "ZB": ZB, "fX": fX}
