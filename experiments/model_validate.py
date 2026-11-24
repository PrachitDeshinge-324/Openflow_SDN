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
def validate():
    for f in FOLDERS:
        rows={}
        for r,flows,sw,path in load(f):
            g='pair' if r['mode']=='reactive-pair' else 'dst'
            sim=simulate(flows,sw,path,g)
            rows.setdefault((r['network'],r['workload'],g),[]).append((r['hybrid']['hit_rate_pct'],sim,len(flows)))
        for k,v in rows.items():
            print(f,k,'n=%d flows~%d measured %.1f  predicted %.1f  | per-seed abs err %.1f'%(len(v),v[0][2],st.mean(x[0] for x in v),st.mean(x[1] for x in v),st.mean(abs(x[0]-x[1]) for x in v)))


# ---------------------------------------------------------------------------------------------
# SmartTime-style adaptive idle timeout (Vishnoi et al., DEBS 2014, "AdaptiveR"), replay model.
#   idle timeout of a rule = min(T_MIN * 2^n, T_MAX), n = times this rule (switch, key) was
#   installed before (the paper's FlowRepeatCount, counted on PACKET_INs, with no time window);
#   reset to T_MIN if the previous timeout was T_MAX and the rule's average hold factor
#   (lifetime / active time) is above 3; no hard timeout; with a per-switch cap, one random rule
#   is evicted on an install when the table is above 95% full (and always when it is full).
# The paper uses T_MIN = 100 ms, T_MAX = 10 s. OpenFlow 1.0 timeouts are whole seconds, so the
# testbed can only do T_MIN = 1 s; both are modelled.
#   python3 experiments/model_validate.py --smarttime [--cap N]   prediction for the testbed modes
#   python3 experiments/model_validate.py --caps                  hit rate against the table cap
#   python3 experiments/model_validate.py --paper-check           SmartTime vs the best static
#       timeout on the paper's own terms: pair = flow, full table, cost = installs + evictions
# ---------------------------------------------------------------------------------------------
import random
def simulate_policy(flows, sw, path, gran, policy='fixed', idle=IDLE, hard=HARD, t_min=1.0, t_max=10.0,
                    cap=0, overflow='refuse', seed=1, keepalive=0.05):
    """Replays flows through per-switch timeout caches. Returns a dict: hit (%), installs
    (= PACKET_INs that installed a rule), peak (rules, all switches), peak1 (one switch),
    evictions, refused (installs refused because the table was full), full_pct (% of install
    attempts that found the table full)."""
    rnd=random.Random(seed)
    ev=[]
    for i,(t,s,d,f) in enumerate(flows):
        ev.append((t,0,i)); ev.append((t+f,1,i))
        j=1   # a running flow's packets keep its rules alive: touch them every `keepalive` s
        while keepalive and j*keepalive<f: ev.append((t+j*keepalive,1,i)); j+=1
    ev.sort()
    last={}; inst={}; to={}; n_inst={}; hold={}; prev_to={}
    live={}; stamp={}; heap=[]; c=dict(n=0,peak=0,peak1=0,miss=0,installs=0,evictions=0,refused=0,attempts=0,full=0)
    evict = policy=='smarttime' or overflow=='evict'
    def expiry(k): return min(last[k]+to[k], inst[k]+hard) if hard else last[k]+to[k]
    def remove(k, t_removed):
        a=last[k]-inst[k]; life=t_removed-inst[k]
        hold.setdefault(k,[]).append(life/a if a>0 else 1e9)
        live[k[0]].discard(k); c['n']-=1; stamp[k]=stamp.get(k,0)+1
        del inst[k]
    def expire_until(t):
        while heap and heap[0][0]<=t:
            e,_,k,sp=heapq.heappop(heap)
            if k in inst and stamp.get(k,0)==sp and expiry(k)<=t: remove(k,e)
    def timeout_for(k):
        if policy=='fixed': return idle
        n=n_inst.get(k,0)
        tt=min(t_min*2**min(n,30), t_max) if n else t_min
        hs=hold.get(k)
        if prev_to.get(k)==t_max and hs and sum(hs)/len(hs)>3: tt=t_min
        return tt
    def touch(k,t):
        if k not in inst:   # a miss at this switch: PACKET_IN, try to install
            S=k[0]; L=live.setdefault(S,set()); c['attempts']+=1
            if cap and len(L)>=cap: c['full']+=1
            if cap and evict and L and (len(L)>=cap or len(L)>0.95*cap):
                victim=rnd.choice(sorted(L)); remove(victim,t); c['evictions']+=1
            if cap and len(L)>=cap:   # refused: the packet is forwarded, no rule
                c['refused']+=1; return
            to[k]=timeout_for(k); prev_to[k]=to[k]; n_inst[k]=n_inst.get(k,0)+1
            inst[k]=t; c['installs']+=1; L.add(k); c['n']+=1
            c['peak']=max(c['peak'],c['n']); c['peak1']=max(c['peak1'],len(L))
        last[k]=t
        heapq.heappush(heap,(expiry(k),id(k),k,stamp.get(k,0)))
    for t,kind,i in ev:
        expire_until(t)
        _,s,d,f=flows[i]
        ks=(sw[s],(s,d)) if gran=='pair' else (sw[s],d)
        if kind==0 and ks not in inst: c['miss']+=1
        for S in path(sw[s],sw[d]):
            for k in (((S,(s,d)),(S,(d,s))) if gran=='pair' else ((S,d),(S,s))):
                touch(k,t)
    return dict(hit=100.0*(1-c['miss']/len(flows)), installs=c['installs'], peak=c['peak'], peak1=c['peak1'],
                evictions=c['evictions'], refused=c['refused'], full_pct=100.0*c['full']/max(1,c['attempts']))

ST_FOLDERS=['traffic-20261119-114525','traffic-20261119-120616','traffic-20261119-123520']
TESTBED=(('reactive-pair (fixed 10/30 s)','pair',dict(policy='fixed')),
         ('smarttime-pair (1-10 s)','pair',dict(policy='smarttime',t_min=1.0,hard=0)),
         ('smarttime-pair (0.1-10 s, paper)','pair',dict(policy='smarttime',t_min=0.1,hard=0)),
         ('reactive-dst (fixed 10/30 s)','dst',dict(policy='fixed')),
         ('smarttime-dst (1-10 s)','dst',dict(policy='smarttime',t_min=1.0,hard=0)))
def _loaded():
    for f in ST_FOLDERS:
        runs=[(flows,sw,path) for r,flows,sw,path in load(f) if r['mode']=='reactive-pair']
        yield load(f)[0][0]['network']+'/'+load(f)[0][0]['workload'], runs
def _mean(rs,k): return st.mean(x[k] for x in rs)
def smarttime_report(caps=(0,)):
    hdr='%-24s %5s %-32s %6s %7s %6s %6s %6s %7s %6s'%('scenario','cap','mode','hit %','PKT_IN','peak','peak1','evict','refused','full%')
    print(hdr); print('-'*len(hdr))
    for net,runs in _loaded():
        for cap in caps:
            for name,g,kw in TESTBED:
                rs=[simulate_policy(fl,sw,pa,g,cap=cap,**kw) for fl,sw,pa in runs]
                print('%-24s %5s %-32s %6.1f %7.0f %6.0f %6.0f %6.0f %7.0f %6.1f'%(net,cap or '-',name,_mean(rs,'hit'),
                      _mean(rs,'installs'),_mean(rs,'peak'),_mean(rs,'peak1'),_mean(rs,'evictions'),_mean(rs,'refused'),_mean(rs,'full_pct')))
            print()

def paper_check():
    """The paper's own setting: a flow = a source-destination pair, a full table, random eviction
    for the static policies, cost = installs + evictions (C_evict / C_install = 1, their replay
    assumption). SmartTime should beat the best static timeout here, or the port is wrong."""
    statics=(0.1,0.5,1,5,10)   # the paper's static timeouts, s
    for net,runs in _loaded():
        unc=[simulate_policy(fl,sw,pa,'pair',policy='smarttime',t_min=0.1,hard=0) for fl,sw,pa in runs]
        for frac in (0.5,0.25):
            cap=max(2,int(frac*_mean(unc,'peak1')))
            res={}
            for T in statics:
                res['static %gs'%T]=[simulate_policy(fl,sw,pa,'pair',idle=T,hard=0,cap=cap,overflow='evict') for fl,sw,pa in runs]
            res['SmartTime 0.1-10 s']=[simulate_policy(fl,sw,pa,'pair',policy='smarttime',t_min=0.1,hard=0,cap=cap) for fl,sw,pa in runs]
            res['SmartTime 1-10 s']=[simulate_policy(fl,sw,pa,'pair',policy='smarttime',t_min=1.0,hard=0,cap=cap) for fl,sw,pa in runs]
            cost={k:_mean(v,'installs')+_mean(v,'evictions') for k,v in res.items()}
            best=min((k for k in cost if k.startswith('static')),key=cost.get)
            print('%s, cap %d rules/switch (%d%% of the busiest switch without a cap):'%(net,cap,100*frac))
            for k,v in res.items():
                print('   %-20s cost %7.0f  (installs %6.0f + evictions %6.0f)  hit %5.1f%%%s'%(k,cost[k],_mean(v,'installs'),
                      _mean(v,'evictions'),_mean(v,'hit'),'   <- best static' if k==best else ''))
            for k in ('SmartTime 0.1-10 s','SmartTime 1-10 s'):
                print('   %s vs best static: %+.1f%% cost'%(k,100*(cost[k]/cost[best]-1)))
            print()

if __name__=='__main__' and '--smarttime' in sys.argv:
    smarttime_report((int(sys.argv[sys.argv.index('--cap')+1]),) if '--cap' in sys.argv else (0,))
elif __name__=='__main__' and '--caps' in sys.argv:
    smarttime_report((0,20,12,6))
elif __name__=='__main__' and '--paper-check' in sys.argv:
    paper_check()
elif __name__=='__main__':
    validate()
