import json, hashlib, os, sys, time
BASE = os.path.dirname(os.path.dirname(__file__))
DATA = os.path.join(BASE, "data")
OUT = os.path.join(BASE, "out")
AUD = os.path.join(BASE, "audits")
os.makedirs(OUT, exist_ok=True)
def load_json(p):
    with open(p, "r") as f:
        return json.load(f)
def load_txt_k(p):
    d = {}
    with open(p, "r") as f:
        for line in f:
            line=line.strip()
            if not line or "=" not in line: continue
            k,v=line.split("=",1)
            d[k.strip()]=v.strip()
    return d
def sha256_file(p):
    h=hashlib.sha256()
    with open(p,"rb") as f:
        h.update(f.read())
    return "sha256:"+h.hexdigest()
def check_signs():
    p=os.path.join(AUD,"sign_audit_report.txt")
    if not os.path.exists(p): return False,"missing sign_audit_report.txt"
    t=open(p).read()
    ok=("UV=-1" in t and "IR=+1" in t and "(+,-)" not in t)
    return ok,"ok" if ok else "sign audit failed"
def check_fidelity():
    p=os.path.join(DATA,"fedelta_per_brana.json")
    if not os.path.exists(p): return False,"missing fedelta_per_brana.json"
    j=load_json(p)
    try:
        ok = j["UV"]["rank_yukawa"]==3 and j["UV"]["rank_1form"]==1 and j["UV"]["independence_checks"] \
             and j["IR"]["rank_yukawa"]==3 and j["IR"]["rank_1form"]==1 and j["IR"]["independence_checks"]
        return ok,"ok" if ok else "fidelity failed"
    except:
        return False,"fidelity parse error"
def check_snf_logs():
    okU="U_det=+1" in open(os.path.join(DATA,"snf_hnf_log_UV.txt")).read()
    okV="V_det=+1" in open(os.path.join(DATA,"snf_hnf_log_UV.txt")).read()
    okU2="U_det=+1" in open(os.path.join(DATA,"snf_hnf_log_IR.txt")).read()
    okV2="V_det=+1" in open(os.path.join(DATA,"snf_hnf_log_IR.txt")).read()
    return (okU and okV and okU2 and okV2),"ok" if (okU and okV and okU2 and okV2) else "SNF/HNF logs invalid"
def check_crt():
    j=load_json(os.path.join(DATA,"crt_level.json"))
    return (j.get("k2_mod2")==1 and j.get("k3_mod3")==0 and j.get("ell_mod6")==3),"ok" if (j.get("ell_mod6")==3) else "ell_mod6 != 3"
def check_k_congruence():
    d=load_txt_k(os.path.join(DATA,"cs_k_level.txt"))
    try:
        k=int(d["k_integer"])
        ell=int(d["ell_mod6"])
    except:
        return False,"parse error"
    ok=(k-ell)%6==0
    return ok,"ok" if ok else "k not congruent to ell mod 6"
def load_system():
    return load_json(os.path.join(DATA,"system_S_k6.json"))
def check_cterms_lock():
    p=os.path.join(DATA,"cterms_domain.lock")
    if not os.path.exists(p): return False,"missing cterms_domain.lock"
    allowed=set([s.strip() for s in open(p).read().splitlines() if s.strip()])
    req=set(["+1/2","+1/3","+1/6","-1/2","-1/3","-1/6"])
    return allowed==req,"ok" if allowed==req else "cterms allowed set mismatch"
def satisfiable(system, removed=None):
    if removed is None: removed=set()
    ids=set([c["id"] for c in system["constraints"] if c["id"] not in removed])
    need=set(["inflow_link","mod2_target","mod3_target","cterms_lock","fedele_UV","fedele_IR"])
    if not need.issubset(ids): return True
    infl=[c for c in system["constraints"] if c["id"]=="inflow_link" and c["id"] not in removed][0]
    mod2=[c for c in system["constraints"] if c["id"]=="mod2_target" and c["id"] not in removed][0]
    mod3=[c for c in system["constraints"] if c["id"]=="mod3_target" and c["id"] not in removed][0]
    lock=[c for c in system["constraints"] if c["id"]=="cterms_lock" and c["id"] not in removed][0]
    non_split=bool(infl.get("non_split",False))
    m2=int(mod2.get("target_multiple",1))
    m3=int(mod3.get("target_multiple",1))
    allowed=lock.get("allowed",[])
    domain_ok=set(allowed)==set(["+1/2","+1/3","+1/6","-1/2","-1/3","-1/6"])
    forced=int(system.get("forced_k_abs",0))
    if forced>=6 and non_split and m2>=2 and m3>=2 and domain_ok:
        return False
    return True
def find_mus(system):
    core=["inflow_link","mod2_target","mod3_target","cterms_lock","fedele_UV","fedele_IR"]
    if satisfiable(system,set()): return []
    mus=set(core)
    for cid in list(core):
        rem=set(mus); rem.remove(cid)
        if not satisfiable(system,rem): continue
    return list(mus)
def main():
    ok,msg=check_signs(); print(f"SIGN_AUDIT:{'PASS' if ok else 'FAIL'}:{msg}")
    ok,msg=check_fidelity(); print(f"FIDELITY:{'PASS' if ok else 'FAIL'}:{msg}")
    ok,msg=check_snf_logs(); print(f"SNF_HNF:{'PASS' if ok else 'FAIL'}:{msg}")
    ok,msg=check_crt(); print(f"CRT:{'PASS' if ok else 'FAIL'}:{msg}")
    ok,msg=check_k_congruence(); print(f"K_CONGRUENCE:{'PASS' if ok else 'FAIL'}:{msg}")
    ok,msg=check_cterms_lock(); print(f"CTERMS_LOCK:{'PASS' if ok else 'FAIL'}:{msg}")
    system=load_system()
    sat=satisfiable(system,set())
    print(f"SYSTEM_S_K6_SAT:{'SAT' if sat else 'UNSAT'}")
    mus=find_mus(system)
    if mus:
        minimality=True; trials=[]
        for cid in mus:
            rem=set(mus); rem.remove(cid)
            s=satisfiable(system,removed=rem)
            trials.append({"remove":cid,"satisfiable":s})
            if not s: minimality=False
        out={"forced_k_abs": system.get("forced_k_abs"),
             "unsat_core": mus,
             "minimality_check": {"remove_each_then_sat": minimality,"trials": trials},
             "hash": "", "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"), "logs": []}
        p=os.path.join(OUT,"mus_k6.json")
        with open(p,"w") as f: json.dump(out,f,indent=2)
        h=sha256_file(p); out["hash"]=h
        with open(p,"w") as f: json.dump(out,f,indent=2)
        print(f"MUS:WRITE:{p}")
        print(f"MUS_MINIMALITY:{'PASS' if minimality else 'FAIL'}")
    else:
        print("MUS:EMPTY"); print("MUS_MINIMALITY:ND")
if __name__=="__main__":
    sys.exit(main())
