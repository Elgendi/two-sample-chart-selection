"""Small tests of the actual rendering/decoding contract, not winning ranks."""
from pathlib import Path
import sys,json
sys.path.insert(0,str(Path(__file__).resolve().parent))
from benchmark import *
fixtures=[dict(task='composition',values=[.2,.3,.5]),dict(task='profile',values=np.linspace(40,120,12).tolist()),dict(task='association',values=np.c_[np.arange(30),np.arange(30)*2+3].tolist())]
checks=[]
for case in fixtures:
 for fam in FAMILIES[case['task']]:
  im,sp=render(case,fam)
  assert not any(k in sp for k in ['values','target','correlation','probabilities'])
  for obs in ['hard','soft']:
   got=decode(im,sp,obs);ll=loss(case,got);assert np.isfinite(ll) and ll<.04,(fam,obs,ll)
   # Blank pixels cannot reproduce the target from hidden numerical metadata.
   try:blank=decode(Image.new('RGB',im.size,'white'),sp,obs);rejected=not np.isfinite(blank).all()
   except (ValueError,ZeroDivisionError):rejected=True
   assert rejected,(fam,obs,'blank unexpectedly decoded')
   checks.append(dict(task=case['task'],family=fam,observer=obs,fixture_loss=ll,blank_rejected=True))
# Profile values and axis calibration scale together; normalized errors should agree.
c=fixtures[1];scaled=dict(task='profile',values=(np.array(c['values'])*10).tolist())
for fam in FAMILIES['profile']:
 a,sa=render(c,fam);b,sb=render(scaled,fam);assert np.array_equal(a,b)
 for obs in ['hard','soft']:assert np.isclose(loss(c,decode(a,sa,obs)),loss(scaled,decode(b,sb,obs)),atol=1e-12)
OUT.mkdir(exist_ok=True);(OUT/'fixture_checks.json').write_text(json.dumps(checks,indent=2));print(len(checks),'fixture contracts; unit-rescaling invariance checked')
