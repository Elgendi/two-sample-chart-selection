"""Pixel dependence and invariance checks; no human-performance claims."""
from pathlib import Path
import json,sys
import numpy as np
from PIL import Image
from observer import prepare,render,decode,score,SETTINGS,P
OUT=Path(__file__).parent/'results';OUT.mkdir(exist_ok=True)
x=np.linspace(-1,2,31);y=np.linspace(0,4,37);ctx=prepare(x,y)
checks=[]
for family,setting in SETTINGS:
 im,spec=render(ctx,family,setting,128,.25,42)
 try:
  q=decode(im,spec)
  assert q.shape==(2,5) and np.isfinite(q).all()
  assert np.all(np.diff(q,axis=1)>=-1e-12)
  # Positive unit rescaling leaves raster geometry and normalized score unchanged.
  ctx2=prepare(3*x,3*y);im2,spec2=render(ctx2,family,setting,128,.25,42)
  assert np.array_equal(np.asarray(im),np.asarray(im2)),(family,setting,'unit geometry')
  q2=decode(im2,spec2);assert np.allclose(q2,3*q,atol=1e-10)
  target=np.quantile(y,P)-np.quantile(x,P)
  assert np.isclose(score(target,q,ctx['scale'])[1],score(3*target,q2,ctx2['scale'])[1])
 except ValueError as exc:
  raise AssertionError((family,setting,str(exc)))
 checks.append([family,setting])
 # Erasing the actual pixels must prevent recovery regardless of known axes.
 try:decode(Image.new('RGB',im.size,'white'),spec)
 except ValueError:pass
 else:raise AssertionError('Blank image decoded: '+family)
# PNG round trip and changing group B pixels while holding metadata fixed.
im,spec=render(ctx,'Dot plot','means',128,0,42);im.save(OUT/'decoder_test.png')
q=decode(Image.open(OUT/'decoder_test.png'),json.loads(json.dumps(spec)))
a=np.array(im);a[:,144:]=np.roll(a[:,144:],5,axis=0)
qq=decode(Image.fromarray(a),spec);assert abs(qq[1,2]-q[1,2])>.01
assert np.allclose(q[0],qq[0])
assert set(spec)=={'family','setting','H','W','lo','hi','panels'}
(OUT/'decoder_test.png').unlink()
result=dict(settings_checked=len(checks),png_roundtrip=True,blank_image_rejected=True,pixel_perturbation_changes_estimate=True,positive_unit_invariance=True,decode_metadata_contains_no_samples_or_targets=True)
(OUT/'checks.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
