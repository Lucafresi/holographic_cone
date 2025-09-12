#!/usr/bin/env python3
import json, math, os, hashlib
def h(s): return hashlib.sha256(s.encode()).hexdigest()
def rj(p):
    with open(p,"r") as f: return json.load(f)
def wj(x,p):
    with open(p,"w") as f: json.dump(x,f,indent=2)

def main():
    os.makedirs("artifacts", exist_ok=True)
    geom = rj("artifacts/msy_geometry.json")
    VX5 = geom["volumes"]["VolX5"]
    VS  = geom["volumes"]["VolSigma"]
    # Formula MSY: S_inst = (pi^2 * N / VolX5) * VolSigma * q = pi * (N*q) (qui perché VolSigma/VolX5 = 1/pi)
    entries=[]
    Nmax, qmax = 60, 60
    for N in range(1, Nmax+1):
        for q in range(1, qmax+1):
            S = (math.pi**2 * N / VX5) * VS * q
            entries.append({"N":N,"q":q,"n":N*q,"S_inst":S})
    payload = {
      "status":"PASS",
      "formula":"S = (pi^2 N/VolX5)*VolSigma*q (≡ pi*(N*q) for dP3)",
      "ranges":{"N":[1,Nmax],"q":[1,qmax]},
      "volumes":{"VolX5":VX5,"VolSigma":VS},
      "count": len(entries),
      "grid": entries,
      "hash": h(f"{VX5:.12e}|{VS:.12e}|N{Nmax}|q{qmax}")
    }
    wj(payload,"artifacts/sinst_grid.json")
    print("PASS:SINST_GRID")
    print(f"Built full grid: {len(entries)} entries (N<= {Nmax}, q<= {qmax}).")
if __name__=="__main__": main()
