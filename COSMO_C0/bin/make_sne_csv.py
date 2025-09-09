#!/usr/bin/env python3
import re, pandas as pd
rows=[]
with open("data/Union2_1_mu_vs_z.txt","r") as f:
    for line in f:
        s=line.strip()
        if not s or s.startswith(('#','%','//')):
            continue
        parts=re.split(r'\s+', s)
        try:
            if len(parts)>=4:
                z=float(parts[1]); mu=float(parts[2]); sig=float(parts[3])
            else:
                z=float(parts[0]); mu=float(parts[1]); sig=float(parts[2])
            rows.append((z,mu,sig))
        except Exception:
            pass
pd.DataFrame(rows, columns=["z","mu","sigma_mu"]).sort_values("z").to_csv("data/sne.csv", index=False)
