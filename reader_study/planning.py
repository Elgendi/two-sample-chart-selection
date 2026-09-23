"""Hypothetical paired-participant approximation, not crossed-design power."""
from pathlib import Path
import math,csv
from scipy.stats import norm
rows=[]
for power in [.8,.9]:
    for standardized_effect in [.2,.3,.4,.5]:
        n=math.ceil((norm.ppf(.975)+norm.ppf(power))**2/standardized_effect**2)
        rows.append(dict(two_sided_alpha=.05,power=power,hypothetical_standardized_effect=standardized_effect,paired_participants_normal_approximation=n,interpretation='Planning sensitivity only; case variance and repeated-trial design not modeled'))
p=Path(__file__).with_name('planning_sensitivity.csv')
with p.open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
print(p.name)
