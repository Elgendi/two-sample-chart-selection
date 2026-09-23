"""Development raster observer; not a calibrated model of human perception.

Decoder inputs: RGB pixels and public chart/axis specification only.
No source observations, target contrasts or stored summaries reach decode().
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy.stats import gaussian_kde
P=np.array([.1,.25,.5,.75,.9])
COLORS=[(38,126,165),(223,120,54)]
SETTINGS=[('Bar chart','means'),('Box plot','five'),('Interval plot','five'),('Dot plot','means'),('Dot plot','raw')]
SETTINGS += [('Histogram',str(n)) for n in [4,8,16,32,64]]
SETTINGS += [('Heatmap',str(n)) for n in [4,8,16,32,64]]
SETTINGS += [('Violin plot',str(n)) for n in [8,16,32,64,128,256]]
FAMILIES=list(dict.fromkeys(f for f,c in SETTINGS))

def prepare(x,y):
    groups=[np.asarray(x,dtype=float),np.asarray(y,dtype=float)]
    sd=np.sqrt(sum((len(v)-1)*np.var(v,ddof=1) for v in groups)/(sum(map(len,groups))-2))
    # Constant samples use a declared one-source-unit fallback.
    norm=sd if sd>0 else 1.
    bw=max(*[np.std(v,ddof=1)*len(v)**(-.2) for v in groups],.01*norm)
    lo=min(0.,min(v.min() for v in groups)-4*bw)
    hi=max(0.,max(v.max() for v in groups)+4*bw)
    if hi<=lo:hi=lo+1.
    ctx=dict(groups=groups,lo=lo,hi=hi,scale=norm,constant_scale_fallback=bool(sd==0),payload={})
    for family,setting in SETTINGS:
        if setting=='means':values=[v.mean() for v in groups]
        elif setting=='five':values=[np.quantile(v,[0,.25,.5,.75,1]) for v in groups]
        elif setting=='raw':values=groups
        elif family in ['Histogram','Heatmap']:
            edges=np.linspace(lo,hi,int(setting)+1)
            values=[np.histogram(v,edges)[0]/len(v) for v in groups]
        else:
            z=np.linspace(lo,hi,int(setting));values=[]
            for v in groups:
                if np.std(v)>0:f=gaussian_kde(v)(z)
                else:
                    logf=-.5*((z-v[0])/(.01*norm))**2;f=np.exp(logf-logf.max())
                values.append(f)
        ctx['payload'][(family,setting)]=values
    return ctx

def render(ctx,family,setting,H=256,phase=0.,seed=0):
    """Two nonoverlapping group panels, each H x H; axes defined in spec.

    Fourfold supersampling, Lanczos downsampling and 0.5-pixel blur are fixed.
    Mark area is not a proxy for cognitive effort or visual quality.
    """
    S=4;W=2*H+16;im=Image.new('RGB',(W*S,H*S),'white');dr=ImageDraw.Draw(im)
    specs=dict(family=family,setting=setting,H=H,W=W,lo=ctx['lo'],hi=ctx['hi'],panels=[])
    def xy(x,y):return (int(round(x*S)),int(round(y*S)))
    for g,val in enumerate(ctx['payload'][(family,setting)]):
        x0=g*(H+16);L=x0+8;R=x0+H-9;T=8.;B=H-9.;mid=(L+R)/2
        specs['panels'].append(dict(L=L,R=R,T=T,B=B,color=COLORS[g]))
        color=COLORS[g]
        def Y(v):return B-(v-ctx['lo'])/(ctx['hi']-ctx['lo'])*(B-T)+phase
        def line(points,fill=color,width=1):dr.line([xy(*q) for q in points],fill=fill,width=max(1,round(width*S)))
        def rect(a,b,fill=color):
            ax,ay=xy(*a);bx,by=xy(*b);dr.rectangle([min(ax,bx),min(ay,by),max(ax,bx),max(ay,by)],fill=fill)
        if family=='Bar chart':rect((mid-.2*H,Y(0)),(mid+.2*H,Y(val)))
        elif family=='Dot plot' and setting=='means':
            yy=Y(val);dr.ellipse([*xy(mid-2,yy-2),*xy(mid+2,yy+2)],fill=color)
        elif family in ['Box plot','Interval plot']:
            yy=[Y(q) for q in val];line([(mid,yy[0]),(mid,yy[4])])
            if family=='Box plot':
                rect((mid-.2*H,yy[1]),(mid+.2*H,yy[3]))
                line([(mid-.2*H,yy[2]),(mid+.2*H,yy[2])],fill=(0,0,0),width=1)
            else:
                line([(mid,yy[1]),(mid,yy[3])],width=5)
                dr.ellipse([*xy(mid-2.5,yy[2]-2.5),*xy(mid+2.5,yy[2]+2.5)],fill=(0,0,0))
        elif family=='Dot plot':
            rng=np.random.default_rng(seed+g*100003)
            for v,xx in zip(val,rng.uniform(mid-.35*H,mid+.35*H,len(val))):
                yy=Y(v);dr.ellipse([*xy(xx-1.5,yy-1.5),*xy(xx+1.5,yy+1.5)],fill=color)
        elif family in ['Histogram','Heatmap']:
            n=len(val)
            for j,mass in enumerate(val):
                left=L+j*(R-L)/n;right=L+(j+1)*(R-L)/n
                if family=='Histogram':
                    if mass>0:rect((left,B+phase),(right,B-mass*(B-T)+phase))
                else:
                    tone=int(round(255*(1-mass)));rect((left,T+.35*(B-T)),(right,T+.65*(B-T)),fill=(tone,tone,255))
        elif family=='Violin plot':
            z=np.linspace(ctx['lo'],ctx['hi'],len(val));width=.4*H*val/max(val.max(),1e-300)
            pts=[xy(mid-w,Y(v)) for w,v in zip(width,z)]+[xy(mid+w,Y(v)) for w,v in zip(width[::-1],z[::-1])]
            dr.polygon(pts,fill=color)
    im=im.resize((W,H),Image.Resampling.LANCZOS).filter(ImageFilter.GaussianBlur(.5))
    return im,specs

def mass_quantiles(masses,edges):
    masses=np.maximum(np.asarray(masses,float),0)
    if masses.sum()<=0:raise ValueError('No recoverable mass')
    c=np.r_[0,np.cumsum(masses)/masses.sum()]
    # Explicit generalized inverse with linear interpolation within a nonempty bin.
    ans=[]
    for p in P:
        j=min(len(masses)-1,max(0,np.searchsorted(c,p,side='right')-1))
        frac=(p-c[j])/(c[j+1]-c[j]) if c[j+1]>c[j] else 0
        ans.append(edges[j]+frac*(edges[j+1]-edges[j]))
    return np.array(ans)

def decode(image,spec):
    """Pixels + known axis/layout metadata only. No raw-data access."""
    arr=np.asarray(image).astype(float);family=spec['family'];setting=spec['setting'];out=[]
    for panel in spec['panels']:
        L,R,T,B=[panel[k] for k in ['L','R','T','B']]
        patch=arr[int(T):int(B)+1,int(L):int(R)+1]
        color=np.array(panel['color']);mask=np.linalg.norm(patch-color,axis=2)<80
        black=np.linalg.norm(patch,axis=2)<.78*np.linalg.norm(color)
        row=mask.sum(axis=1);rows=np.arange(len(row))+T
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
            out.append(mass_quantiles(m,np.linspace(spec['lo'],spec['hi'],n+1)))
        elif family=='Heatmap':
            n=int(setting);m=[];rr=int(.5*(B-T))
            for j in range(n):
                col=min(patch.shape[1]-1,int(round((j+.5)*(R-L)/n)))
                m.append(1-patch[rr,col,0]/255)
            out.append(mass_quantiles(m,np.linspace(spec['lo'],spec['hi'],n+1)))
        else:
            # Uniform-area reader: violin width or opaque dot coverage by value row.
            out.append(mass_quantiles(row[::-1],np.linspace(spec['lo'],spec['hi'],len(row)+1)))
    return np.array(out)

def score(target,recovered,scale):
    loss=float(np.mean(abs((recovered[1]-recovered[0])-target))/scale)
    return loss,100/(1+loss)
