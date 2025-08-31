# Gradi di libertà SM relativistici sopra EW:
# V: gluoni(8)*2 + W^a(3)*2 + B(1)*2 = 24
# S: Higgs (doublet complesso) = 4 real scalars
# F: conteggio totale fermioni (in g_*): 90
SM_DOFS = {"V": 24, "S": 4, "F": 90}

def pair_weight_same_category(g_total: int) -> float:
    """
    Somma su tutte le coppie i<=j della stessa categoria con S_ij:
    sum_{i<j} g_i g_j + 1/2 sum_i g_i^2 = 1/2 (sum_i g_i)^2
    Se assumiamo coefficiente di canale uguale all'interno della categoria,
    il peso totale è 0.5 * g_total^2.
    """
    return 0.5 * (g_total ** 2)
