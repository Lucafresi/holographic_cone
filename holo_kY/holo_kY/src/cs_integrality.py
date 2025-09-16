import json, os
from fractions import Fraction
from math import gcd
ROOT = os.path.dirname(os.path.dirname(__file__))
INP  = os.path.join(ROOT,"data","su5_mixed_cs.json")
OUT  = os.path.join(ROOT,"certs","kY","cs_integrality.json")
def lcm(a,b): return abs(a*b)//gcd(a,b) if a and b else 0
def to_frac(x):
    if isinstance(x,(int,)): return Fraction(x,1)
    if isinstance(x,str):
        if "/" in x: p,q=x.split("/"); return Fraction(int(p),int(q))
        return Fraction(int(x),1)
    if isinstance(x,list) and len(x)==2: return Fraction(int(x[0]),int(x[1]))
    raise ValueError("bad rational")
def minimal_integer_scale(vals):
    den=1
    for v in vals: den = lcm(den, v.denominator)
    return den
if __name__=="__main__":
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    if not os.path.exists(INP):
        with open(OUT,"w") as f: json.dump({"error":"missing su5_mixed_cs.json"}, f, indent=2)
    else:
        data=json.load(open(INP))
        aY22=to_frac(data["mixed_cs"]["Y_SU2"])
        aY33=to_frac(data["mixed_cs"]["Y_SU3"])
        scale=minimal_integer_scale([aY22,aY33])
        verdict={"aY22":f"{aY22.numerator}/{aY22.denominator}",
                 "aY33":f"{aY33.numerator}/{aY33.denominator}",
                 "scale_min":scale, "kY":scale, "pass": (scale==2)}
        json.dump(verdict, open(OUT,"w"), indent=2)
        print("kY =", scale, "| PASS =", verdict["pass"])
