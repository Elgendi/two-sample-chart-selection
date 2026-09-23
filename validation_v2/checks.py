from pathlib import Path
import json
import numpy as np
from PIL import Image
from observer import prepare,render,decode,legacy,P,SETTINGS
OUT=Path(__file__).parent/'results'
x=np.linspace(-1,2,31);y=np.linspace(0,4,37);ctx=prepare(x,y);checked=[]
for f,s in SETTINGS:
    im,spec=render(ctx,f,s,256,.25,42)
    for obs in ['threshold','alpha']:
        q=decode(im,spec,obs);assert q.shape==(2,5) and np.isfinite(q).all();assert np.all(np.diff(q,axis=1)>=-1e-12)
        ctx2=prepare(3*x,3*y);im2,spec2=render(ctx2,f,s,256,.25,42)
        assert np.array_equal(im,im2);assert np.allclose(decode(im2,spec2,obs),3*q,atol=1e-9)
        try:decode(Image.new('RGB',im.size,'white'),spec,obs)
        except ValueError:pass
        else:raise AssertionError(('blank',f,s,obs))
        a=np.array(im)
        if f=='Heatmap':a[:,272:400]=255
        else:a[:,272:]=np.roll(a[:,272:],3,axis=0)
        qq=decode(Image.fromarray(a),spec,obs)
        assert np.allclose(qq[0],q[0]);assert not np.allclose(qq[1],q[1]),(f,s,obs)
        assert set(spec)=={'family','setting','H','W','lo','hi','panels'}
        checked.append([f,s,obs])
    if f in legacy.FAMILIES:
        li,ls=legacy.render(legacy.prepare(x,y),f,s,256,.25,42)
        assert np.array_equal(im,li);assert np.array_equal(decode(im,spec),legacy.decode(li,ls))
# Fractional-error cancellation is an identity, not empirical perceptual evidence.
truth=np.array([np.quantile(x,P),np.quantile(y,P)]);q=truth+10
assert np.max(abs((q[1]-q[0])-(truth[1]-truth[0])))<1e-12
assert np.mean(abs(q-truth))==10
result=dict(passed=len(checked),settings=23,observers=2,legacy_fixture_parity=True,blank_rejection=True,pixel_dependence=True,positive_unit_rescaling=True,metadata_target_free=True,cancellation_counterexample=True)
(OUT/'checks.json').write_text(json.dumps(result,indent=2));print(result)
