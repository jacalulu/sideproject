import json, sys
rows=[json.loads(l) for l in open(sys.argv[1])]
Z=["Lagoon","Coral/sand","Kelp/anchor","Ship/crate","Pearl/oyster","Jelly","Twilight","Starlight"]
print(f"{'zone':14s} {'breather':>9s} {'mechanic':>9s}   by mechanic")
for z in range(8):
    zs=[r for r in rows if (r['L']-1)//25==z]
    br=[r for r in zs if not r['mech'].replace('+jelly','').strip()]; me=[r for r in zs if r['mech'].replace('+jelly','').strip()]
    rate=lambda rs: f"{100*sum(r['wins'] for r in rs)/max(1,sum(r['runs'] for r in rs)):5.0f}%" if rs else "   -  "
    by={}
    for r in me:
        k=" ".join(sorted(x.split(':')[0] for x in r['mech'].replace('+jelly','').split()))
        by.setdefault(k,[]).append(r)
    print(f"{Z[z]:14s} {rate(br):>9s} {rate(me):>9s}   "+", ".join(f"{k} {rate(v).strip()}" for k,v in by.items()))
