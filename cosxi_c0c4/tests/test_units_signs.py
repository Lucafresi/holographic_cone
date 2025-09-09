from cosxi.units import MPL_GEV, seconds_to_GeVinv
def test_units_basic():
    assert MPL_GEV > 0
    t0 = 4.35e17
    t_gevinv = seconds_to_GeVinv(t0)
    assert t_gevinv > 0
def test_signs_consistency():
    from cosxi.io import GlobalInput, Coeff
    from cosxi.sequester import compute_xi, compute_rho_Lambda_t0
    g = GlobalInput(Mpl=2.435e18, t0=4.35e17, Leff=1.0,
                    Aprime_UV=-0.3, Aprime_IR=-0.299999998,
                    Tbar=1e-12, coeff=Coeff(cB=1.0,cT=1.0))
    xi = compute_xi(g)
    rho = compute_rho_Lambda_t0(g, xi)
    assert xi > 0
    assert rho > 0
