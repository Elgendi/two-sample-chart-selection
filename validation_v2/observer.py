"""Extended computational benchmark. No human-performance model is claimed."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'rendered_study'))
import importlib.util
_spec=importlib.util.spec_from_file_location('legacy_observer',Path(__file__).resolve().parents[1]/'rendered_study/observer.py')
legacy=importlib.util.module_from_spec(_spec);_spec.loader.exec_module(legacy)
import numpy as np
from PIL import Image,ImageDraw,ImageFilter
P=legacy.P
SETTINGS=legacy.SETTINGS+[('ECDF','full'),('Quantile plot','five')]
FIXED=[('Bar chart','means'),('Box plot','five'),('Interval plot','five'),('Dot plot','raw'),('Histogram','16'),('Heatmap','16'),('Violin plot','64'),('ECDF','full'),('Quantile plot','five')]

def prepare(x,y,axis='zero'):
    ctx=legacy.prepare(x,y)
    if axis=='tight':
        groups=ctx['groups'];bw=max(*[np.std(v,ddof=1)*len(v)**(-.2) for v in groups],.01*ctx['scale'])
        ctx['lo']=min(v.min() for v in groups)-4*bw;ctx['hi']=max(v.max() for v in groups)+4*bw
        for f,s in legacy.SETTINGS:
            if f in ['Histogram','Heatmap']:
                edges=np.linspace(ctx['lo'],ctx['hi'],int(s)+1)
                ctx['payload'][(f,s)]=[np.histogram(v,edges)[0]/len(v) for v in groups]
            elif f=='Violin plot':
                z=np.linspace(ctx['lo'],ctx['hi'],int(s));out=[]
                for v in groups:
                    if np.std(v)>0:a=legacy.gaussian_kde(v)(z)
                    else:
                        a=-.5*((z-v[0])/(.01*ctx['scale']))**2;a=np.exp(a-a.max())
                    out.append(a)
                ctx['payload'][(f,s)]=out
    return ctx

def render(ctx,family,setting,H=256,phase=0.,seed=0):
    if family not in ['ECDF','Quantile plot']:return legacy.render(ctx,family,setting,H,phase,seed)
    S=4;W=2*H+16;im=Image.new('RGB',(W*S,H*S),'white');draw=ImageDraw.Draw(im)
    spec=dict(family=family,setting=setting,H=H,W=W,lo=ctx['lo'],hi=ctx['hi'],panels=[])
    for g,v in enumerate(ctx['groups']):
        L=g*(H+16)+8;R=g*(H+16)+H-9;T=8.;B=H-9.;color=legacy.COLORS[g]
        spec['panels'].append(dict(L=L,R=R,T=T,B=B,color=color))
        def xy(x,y):return (round(x*S),round(y*S))
        def Y(a):return B-(a-ctx['lo'])/(ctx['hi']-ctx['lo'])*(B-T)+phase
        if family=='Quantile plot':
            for p,q in zip(P,np.quantile(v,P)):
                xx=L+p*(R-L);yy=Y(q)
                draw.ellipse([*xy(xx-2,yy-2),*xy(xx+2,yy+2)],fill=color)
        else:
            sv=np.sort(v);points=[xy(L,Y(ctx['lo']))]
            # Vertical measurement axis; horizontal cumulative probability.
            for i,q in enumerate(sv):
                points.extend([xy(L+i/len(v)*(R-L),Y(q)),xy(L+(i+1)/len(v)*(R-L),Y(q))])
            points.append(xy(R,Y(ctx['hi'])))
            draw.line(points,fill=color,width=2*S)
    return im.resize((W,H),Image.Resampling.LANCZOS).filter(ImageFilter.GaussianBlur(.5)),spec

def decode(image,spec,observer='threshold'):
    if spec['family'] not in ['ECDF','Quantile plot']:
        return legacy.decode(image,spec) if observer=='threshold' else decode_alpha(image,spec)
    a=np.asarray(image,float);out=[]
    for panel in spec['panels']:
        L,R,T,B=[panel[k] for k in ['L','R','T','B']];patch=a[int(T):int(B)+1,int(L):int(R)+1]
        col=np.array(panel['color']);alpha=np.clip(((255-patch)@(255-col))/np.sum((255-col)**2),0,1)
        ink=(np.linalg.norm(patch-col,axis=2)<80).astype(float) if observer=='threshold' else np.where(alpha>.05,alpha,0)
        estimates=[]
        for p in P:
            j=round(p*(R-L));weights=ink[:,max(0,j-2):j+3].sum(1) if spec['family']=='Quantile plot' else ink[:,j]
            if weights.sum()==0:raise ValueError('Target mark not recovered')
            y=np.average(np.arange(len(weights))+T,weights=weights)
            estimates.append(spec['lo']+(B-y)/(B-T)*(spec['hi']-spec['lo']))
        out.append(np.maximum.accumulate(estimates))
    return np.array(out)

# Alternative observer: color-projection alpha, a softer mask and integrated ink.
# It shares known geometry with the original; it is an algorithmic sensitivity,
# NOT an independently trained or human-validated observer.

def decode_alpha(image,spec):
    """Pixels + known axis/layout metadata only. No raw-data access."""
    arr=np.asarray(image).astype(float);family=spec['family'];setting=spec['setting'];out=[]
    for panel in spec['panels']:
        L,R,T,B=[panel[k] for k in ['L','R','T','B']]
        patch=arr[int(T):int(B)+1,int(L):int(R)+1]
        color=np.array(panel['color']);alpha=np.clip(((255-patch)@(255-color))/np.sum((255-color)**2),0,1);mask=alpha>.2
        black=np.linalg.norm(patch,axis=2)<.78*np.linalg.norm(color)
        row=np.where(alpha>.05,alpha,0).sum(axis=1);rows=np.arange(len(row))+T
        def val(y):return spec['lo']+(B-y)/(B-T)*(spec['hi']-spec['lo'])
        if family=='Bar chart':
            hit=rows[row>(R-L)*.2]
            if len(hit)==0:raise ValueError('Bar not recovered')
            zero=B-(0-spec['lo'])/(spec['hi']-spec['lo'])*(B-T)
            endpoint=hit[np.argmax(abs(hit-zero))];out.append(np.full(5,val(endpoint)))
        elif family=='Dot plot' and setting=='means':
            if row.sum()==0:raise ValueError('Mean dot not recovered')
            out.append(np.full(5,val(np.average(rows,weights=row))))
        elif family in ['Box plot','Interval plot']:
            anymark=mask|black;rr=anymark.sum(axis=1);hit=rows[rr>0]
            wide=rows[rr>((R-L)*.3 if family=='Box plot' else 2.5)]
            br=black.sum(axis=1)
            if not len(hit) or not len(wide) or br.sum()==0:raise ValueError('Quantile marks not recovered')
            median=np.average(rows,weights=br)
            q=val(np.array([hit.max(),wide.max(),median,wide.min(),hit.min()]))
            q=np.maximum.accumulate(q)
            out.append(np.interp(P,[0,.25,.5,.75,1],q))
        elif family=='Histogram':
            n=int(setting);m=[]
            for j in range(n):
                col=int(round((j+.5)*(R-L)/n));col=min(col,mask.shape[1]-1)
                # Position calibrated against the zero-frequency baseline.
                hit=rows[mask[:,col]]
                m.append(max(0,(B-hit.min())/(B-T)) if len(hit) else 0.)
            out.append(legacy.mass_quantiles(m,np.linspace(spec['lo'],spec['hi'],n+1)))
        elif family=='Heatmap':
            n=int(setting);m=[];rr=int(.5*(B-T))
            for j in range(n):
                col=min(patch.shape[1]-1,int(round((j+.5)*(R-L)/n)))
                m.append(1-np.mean(patch[max(0,rr-1):rr+2,max(0,col-1):col+2,0])/255)
            out.append(legacy.mass_quantiles(m,np.linspace(spec['lo'],spec['hi'],n+1)))
        else:
            # Uniform-area reader: violin width or opaque dot coverage by value row.
            out.append(legacy.mass_quantiles(row[::-1],np.linspace(spec['lo'],spec['hi'],len(row)+1)))
    return np.array(out)
