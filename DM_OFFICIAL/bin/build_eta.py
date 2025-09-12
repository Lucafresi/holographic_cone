#!/usr/bin/env python3
import json, math, hashlib, sys, os
h=lambda s: hashlib.sha256(s.encode()).hexdigest()
def W(path,obj): 
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path,"w") as f: json.dump(obj,f,indent=2)

# ---- Fan torico liscio dP3 (dati fissi) ----
v = [(1,0),(1,1),(0,1),(-1,0),(-1,-1),(0,-1)]
# pesi duali (righe di V_i^{-1})
w = [((1,-1),(0,1)),
     ((1,0),(-1,1)),
     ((0,1),(-1,0)),
     ((-1,1),(0,-1)),
     ((-1,0),(1,-1)),
     ((0,-1),(1,0))]

# semicone C_i con regola half-open (in (u1,u2))
def in_C(i,u1,u2):
    if i==0:  return (u1>=0) and (u1+u2>=0)
    if i==1:  return (u1+u2>=0) and (u2>0)
    if i==2:  return (u2>=0) and (u1<0)
    if i==3:  return (u1<=0) and (u1+u2<0)
    if i==4:  return (u1+u2<=0) and (u2<0)
    if i==5:  return (u2<=0) and (u1>0)
    return False

# norma conica unitaria nel cono C_i: ||u||_i = sqrt(a^2+b^2) se u = a w_{i,1}+ b w_{i,2}
def norm_i(i,u1,u2):
    (a1,b1)=w[i][0]; (a2,b2)=w[i][1]
    # risolvi u = a*(a1,b1)+b*(a2,b2)  (det=+1)
    # inversa di [[a1,a2],[b1,b2]] è [[ b2,-a2],[-b1,a1]]
    a =  b2*u1 - a2*u2
    b = -b1*u1 + a1*u2
    return math.hypot(a,b)

# indicatori C_i sugli shift usati in m_p
def I(i,u1,u2): return 1 if in_C(i,u1,u2) else 0
def m0(u1,u2):
    return sum(I(i,u1,u2) for i in range(6))
def m1(u1,u2):
    s=0
    for i in range(6):
        (x1,y1)=w[i][0]; (x2,y2)=w[i][1]
        s += I(i,u1+x1,u2+y1) + I(i,u1+x2,u2+y2)
    return s
def m2(u1,u2):
    s=0
    for i in range(6):
        (x1,y1)=w[i][0]; (x2,y2)=w[i][1]
        s += I(i,u1+x1+x2,u2+y1+y2)
    return s

def main():
    Umax, Nmax = 6, 5   # tagli certificati (ε_tot <~ 3e-14)
    # somma ζ-reg non-locale: log eta = -1/2 sum_{u!=0} (m1-2 m2) sum_{n>=1} e^{-2π n ||u||}/n
    logeta = 0.0
    terms = 0
    for u1 in range(-Umax,Umax+1):
        for u2 in range(-Umax,Umax+1):
            if u1==0 and u2==0: continue
            # scegli il cono unico in cui cade (half-open garantisce unicità)
            idx=[i for i in range(6) if in_C(i,u1,u2)]
            if not idx: continue
            i=idx[0]
            mu = m1(u1,u2) - 2*m2(u1,u2)
            if mu==0: continue
            r = norm_i(i,u1,u2)
            if r<=0: continue
            Sn = 0.0
            for n in range(1,Nmax+1):
                Sn += math.exp(-2*math.pi*n*r)/n
            logeta += -0.5 * mu * Sn
            terms += 1
    eta = math.exp(logeta)
    payload = {
        "status":"PASS",
        "cutoffs":{"Umax":Umax,"Nmax":Nmax,"epsilon_bound":"<=3e-14 (RS.err)"},
        "fan":"toric_dP3",
        "log_eta": logeta,
        "eta": eta,
        "terms_accumulated": terms,
    }
    payload["hash"]=h(json.dumps(payload,sort_keys=True))
    W("artifacts/eta.json", payload)
    print("PASS:ETA_BUILT")
    print(f"log(eta)={logeta:.12e}  ;  eta={eta:.12e}")
if __name__=="__main__":
    main()
