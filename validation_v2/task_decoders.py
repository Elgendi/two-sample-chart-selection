"""Fixed geometry, requested quantile probabilities. Generated from documented decoders."""
import numpy as np
def mass_quantiles(masses,edges,P):
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

def decode_threshold_at(image,spec,P):
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
            endpoint=hit[np.argmax(abs(hit-zero))];out.append(np.full(len(P),val(endpoint)))
        elif family=='Dot plot' and setting=='means':
            if row.sum()==0:raise ValueError('Mean dot not recovered')
            out.append(np.full(len(P),val(np.average(rows,weights=row))))
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
            out.append(mass_quantiles(m,np.linspace(spec['lo'],spec['hi'],n+1),P))
        elif family=='Heatmap':
            n=int(setting);m=[];rr=int(.5*(B-T))
            for j in range(n):
                col=min(patch.shape[1]-1,int(round((j+.5)*(R-L)/n)))
                m.append(1-patch[rr,col,0]/255)
            out.append(mass_quantiles(m,np.linspace(spec['lo'],spec['hi'],n+1),P))
        else:
            # Uniform-area reader: violin width or opaque dot coverage by value row.
            out.append(mass_quantiles(row[::-1],np.linspace(spec['lo'],spec['hi'],len(row)+1),P))
    return np.array(out)

def decode_alpha_at(image,spec,P):
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
            endpoint=hit[np.argmax(abs(hit-zero))];out.append(np.full(len(P),val(endpoint)))
        elif family=='Dot plot' and setting=='means':
            if row.sum()==0:raise ValueError('Mean dot not recovered')
            out.append(np.full(len(P),val(np.average(rows,weights=row))))
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
            out.append(mass_quantiles(m,np.linspace(spec['lo'],spec['hi'],n+1),P))
        elif family=='Heatmap':
            n=int(setting);m=[];rr=int(.5*(B-T))
            for j in range(n):
                col=min(patch.shape[1]-1,int(round((j+.5)*(R-L)/n)))
                m.append(1-np.mean(patch[max(0,rr-1):rr+2,max(0,col-1):col+2,0])/255)
            out.append(mass_quantiles(m,np.linspace(spec['lo'],spec['hi'],n+1),P))
        else:
            # Uniform-area reader: violin width or opaque dot coverage by value row.
            out.append(mass_quantiles(row[::-1],np.linspace(spec['lo'],spec['hi'],len(row)+1),P))
    return np.array(out)
