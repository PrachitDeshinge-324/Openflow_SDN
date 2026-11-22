"""
Flow-table replay model: first check against the measured wildcard runs
CS G525 Advanced Computer Networks - Project SA7

Treats every wildcard rule as an entry in a timeout cache (idle 10 s, hard 30 s),
replays the flow schedule stored in each result folder, and compares the predicted
hit rate with the one the testbed measured. No Mininet, no POX; runs in seconds.

  python3 experiments/model_validate.py        (from the repository root)

This is the seed for docs/Novelty_Plan.md; Step 1 there turns it into a full model.
"""
import json, glob, os, sys, math, heapq, re, statistics as st
R=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','results','measured','')
FOLDERS=['traffic-20261020-171718','traffic-20261020-183215','traffic-20261021-050401','traffic-20261021-060910','traffic-20261023-070549']
IDLE,HARD=10.0,30.0
def paths(topo):
    adj={}
    for l in topo['links']:
        w=l.get('delay_ms', l.get('delay', 1.0)) or 1.0
        adj.setdefault(l['dpid1'],{})[l['dpid2']]=w; adj.setdefault(l['dpid2'],{})[l['dpid1']]=w
    cache={}
    def path(a,b):
        if (a,b) in cache: return cache[(a,b)]
        dist={a:0}; prev={}; pq=[(0,a)]
        while pq:
            d,u=heapq.heappop(pq)
            if u==b: break
            if d>dist[u]: continue
            for v,w in adj[u].items():
                if d+w<dist.get(v,1e18): dist[v]=d+w; prev[v]=u; heapq.heappush(pq,(d+w,v))
        p=[b]
        while p[-1]!=a: p.append(prev[p[-1]])
        cache[(a,b)]=p[::-1]; return cache[(a,b)]
    return path
def simulate(flows, sw, path, gran, idle=IDLE, hard=HARD, pre=()):
    # flows: (start, src, dst, fct). events: start (check+install+touch), end (touch)
    ev=[]
    for i,(t,s,d,f) in enumerate(flows):
        ev.append((t,0,i)); ev.append((t+f,1,i))
    ev.sort()
    last={}; inst={}; miss=0; occ=[]
    def alive(k,t): return k in pre or (k in last and t-last[k]<idle and t-inst[k]<hard)
    def touch(k,t):
        if not alive(k,t): inst[k]=t
        last[k]=t
    for t,kind,i in ev:
        _,s,d,f=flows[i]
        ks=(sw[s],(s,d)) if gran=='pair' else (sw[s],d)
        if kind==0 and not alive(ks,t): miss+=1
        for S in path(sw[s],sw[d]):
            for k in (((S,(s,d)),(S,(d,s))) if gran=='pair' else ((S,d),(S,s))):
                touch(k,t)
    return 100.0*(1-miss/len(flows))
def load(folder):
    d=json.load(open(R+folder+'/traffic.json'))
    out=[]
    for r in d['results']:
        if r['mode'] not in ('reactive-pair','reactive-dst'): continue
        net=r['network']; topo=json.load(open(R+folder+'/%s-topo.json'%net))
        sw={h['name']:h['dpid'] for h in topo['hosts']}; ip={h['ip']:h['name'] for h in topo['hosts']}
        tag='%s-%s-%s-s%d'%(net,r['workload'],r['mode'],r['seed'])
        if not any(os.path.exists(R+folder+'/%s-sched-%s.txt'%(tag,h)) for h in sw):
            tag='%s-%s-%s'%(net,r['workload'],r['mode'])   # a run with --repeats 1 has no seed in its file names
        fct={(x['src'],round(x['start'],4)):(x['fct_ms'] or 0)/1000.0 for x in r['flows_detail']}
        flows=[]
        for h in sw:
            fn=R+folder+'/%s-sched-%s.txt'%(tag,h)
            if not os.path.exists(fn): continue
            for l in open(fn):
                a=l.split()
                if a: flows.append((float(a[0]),h,ip[a[1]],fct.get((h,round(float(a[0]),4)),0.05)))
        flows.sort()
        out.append((r,flows,sw,paths(topo)))
    return out
if __name__=='__main__':
    for f in FOLDERS:
        rows={}
        for r,flows,sw,path in load(f):
            g='pair' if r['mode']=='reactive-pair' else 'dst'
            sim=simulate(flows,sw,path,g)
            rows.setdefault((r['network'],r['workload'],g),[]).append((r['hybrid']['hit_rate_pct'],sim,len(flows)))
        for k,v in rows.items():
            print(f,k,'n=%d flows~%d measured %.1f  predicted %.1f  | per-seed abs err %.1f'%(len(v),v[0][2],st.mean(x[0] for x in v),st.mean(x[1] for x in v),st.mean(abs(x[0]-x[1]) for x in v)))
