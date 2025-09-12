#!/usr/bin/env python3
import json, os, math, hashlib
def h(s): import hashlib; return hashlib.sha256(s.encode()).hexdigest()
def rj(p): 
    with open(p,"r") as f: return json.load(f)
def wj(x,p):
    with open(p,"w") as f: json.dump(x,f,indent=2)

def best_factor_pair(n, Nmax, qmax):
    # trova una coppia (N,q) con N*q = n dentro i bounds, oppure None
    best=None
    for N in range(1, Nmax+1):
        if n % N == 0:
            q = n//N
            if 1 <= q <= qmax:
                # preferisci N e q più "bilanciati"
                cand=(N,q,abs(N-q))
                if (best is None) or (cand[2] < best[2]):
                    best=cand
    return None if best is None else (best[0], best[1])

def main():
    os.makedirs("artifacts", exist_ok=True)
    grid = rj("artifacts/sinst_grid.json")
    Sreq = rj("sources/sreq.json")["S_req"]
    Nmin,Nmax = grid["ranges"]["N"][0], grid["ranges"]["N"][1]
    qmin,qmax = grid["ranges"]["q"][0], grid["ranges"]["q"][1]

    # Analitico: S = pi * n  ⇒  n* = round(Sreq/pi)
    n_star = int(round(Sreq / math.pi))
    # prova n_star, poi anelli n_star±1, ±2, ... finché trovi fattorizzazione nei bounds
    found=None; k=0
    while found is None and k <= (Nmax*qmax):
        for n in (n_star-k, n_star+k) if k>0 else (n_star,):
            if n>=1:
                pair = best_factor_pair(n, Nmax, qmax)
                if pair:
                    found = (n, pair[0], pair[1])
                    break
        k += 1

    if found is None:
        # fallback: cerca sulla griglia numerica (ma ora è completa)
        entries = grid["grid"]
        best = min(entries, key=lambda e: abs(e["S_inst"]-Sreq))
        out = {"status":"FAIL", "reason":"no_factorization_in_bounds",
               "S_req":Sreq, "best_numeric":best, "abs_diff":abs(best["S_inst"]-Sreq),
               "hash":h(f'{Sreq}|{best}|F')}
        wj(out,"artifacts/sinst_vs_sreq.json")
        print(f"FAIL: no integer factorization within bounds. Best numeric N={best['N']} q={best['q']} |Δ|={abs(best['S_inst']-Sreq):.6f}")
        return

    n, N, q = found
    S = math.pi * n
    diff = abs(S - Sreq)
    verdict = "PASS" if diff<=5e-2 else "NEAR" if diff<=2e-1 else "FAIL"
    out = {"status":verdict, "S_req":Sreq, "chosen":{"N":N,"q":q,"n":n,"S_inst":S},
           "abs_diff":diff, "tolerance":"5e-2 (hard), 2e-1 (near)", "hash":h(f'{Sreq}|{n}|{N}|{q}|{diff:.6e}')}
    wj(out,"artifacts/sinst_vs_sreq.json")
    print(f"{verdict}: choose N={N}, q={q}, n={n}; S_inst={S:.6f}, |Δ|={diff:.6f}")
if __name__=="__main__": main()
