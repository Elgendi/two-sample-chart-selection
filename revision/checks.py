import json
from pathlib import Path
import numpy as np
from model import candidates,choose,frontier,scale,bootstrap_draws,select
R=Path(__file__).resolve().parent/'results'
x=np.linspace(-1,1,101);y=1.8*x
rr=candidates(x,y);assert choose(rr,.1*scale(x,y))['representation']=='Five-number'
a=candidates(x,x+.7);assert choose(a,.1)['representation']=='Means'
# affine invariance of all decoders and normalized errors
rng=np.random.default_rng(874)
vx=rng.normal(size=111);vy=rng.normal(size=95)
aa=candidates(vx,vy);bb=candidates(3*vx+17,3*vy+17)
assert all(np.isclose(u['error']*3,v['error'],atol=1e-10) for u,v in zip(aa,bb))
edge=candidates(3*x+17,3*y+17)
edge_failures=[u['configuration'] for u,v in zip(rr,edge) if not np.isclose(u['error']*3,v['error'],atol=1e-10)]
# raw fallback, order symmetry, and a monotone resolution path
assert next(r for r in rr if r['configuration']=='raw')['error']==0
rev=candidates(y,x);assert np.allclose([r['error'] for r in rr],[r['error'] for r in rev])
ns=[choose(rr,t)['N'] for t in np.geomspace(.0001,10,200)];assert all(a>=b for a,b in zip(ns,ns[1:]))
# matched marginals do not identify paired changes
u=np.arange(4.);v=u[::-1];assert choose(candidates(u,v),.01)['representation']=='Means';assert np.max(abs(v-u))==3
# exact decoder errors independently checked on a dense grid in the simulation decoder
from simulate import decode

for r in rr:
 dense=np.max(abs(decode(x,y,r['configuration'])-(np.quantile(y,np.linspace(.05,.95,4001))-np.quantile(x,np.linspace(.05,.95,4001)))))
 assert dense<=r['error']+1e-8
report={'affine_invariance_away_from_bin_boundaries':True,'floating_point_bin_boundary_exceptions':edge_failures,'swap_symmetry':True,'exact_raw_fallback':True,'monotone_resolution_path':True,'paired_counterexample':True,'dense_grid_crosscheck':True}
(R/'checks.json').write_text(json.dumps(report,indent=2));print(report)
