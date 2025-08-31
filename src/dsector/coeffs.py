# Coefficienti universali per sigma_ij->XX(s) = [c_{ij->X}/(8π)] * s / Mpl^4
# (limite relativistico, iniziali massless; nessun portale: solo gravità)
# Categorie iniziali: S (scalare SM: Higgs), F (fermioni SM), V (vettori di gauge massless)
# Finale X: "scalar" | "fermion" | "vector"
COEFFS = {
    "scalar": {  # X finale scalare
        ("S","S"): 1.0/240.0,
        ("F","F"): 1.0/480.0,
        ("V","V"): 1.0/120.0,
    },
    "fermion": { # X finale fermione
        ("S","S"): 1.0/480.0,
        ("F","F"): 1.0/160.0,
        ("V","V"): 1.0/40.0,
    },
    "vector": {  # X finale vettore
        ("S","S"): 1.0/120.0,
        ("F","F"): 13.0/480.0,
        ("V","V"): 13.0/120.0,
    },
}
