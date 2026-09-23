from common import *
def fmt(x):return f'{x:.6f}'
def main():
 s=pd.read_csv(OUT/'strong_default_summary.csv');syn=pd.read_csv(OUT/'new_synthetic_summary.csv');g=pd.read_csv(OUT/'geometry_summary.csv');a=pd.read_csv(OUT/'geometry_agreement.csv')
 lines=[r'\begin{tabular}{lrrrr}',r'\toprule Task & Cases & Default loss & Selected loss & Gain\\\midrule']
 for task in TASKS:
  r=s[(s.task==task)&(s.observer=='hard')].iloc[0];ci=f'[{r.ci_low:+.6f}, {r.ci_high:+.6f}]' if np.isfinite(r.ci_low) else '[not estimated]'
  lines.append(f'{LABELS[task]} & {r.cases} & {fmt(r.default_loss)} & {fmt(r.selected_loss)} & {r.gain:+.6f}'+r'\\')
 lines+=[r'\bottomrule\end{tabular}'];(OUT/'main_table.tex').write_text('\n'.join(lines))
 lines=[r'\begin{longtable}{llrrrr}',r'\caption{Error magnitudes on new synthetic cases. Positive gain favors case-specific selection.}\label{tab:synthetic-losses}\\',r'\toprule Task & Observer & Cases & Default & Selected & Gain\\\midrule\endhead']
 for task in TASKS:
  for ob in ['hard','soft']:
   r=syn[(syn.task==task)&(syn.observer==ob)].iloc[0];lines.append(f'{LABELS[task]} & {ob} & {r.cases} & {fmt(r.default_loss)} & {fmt(r.selected_loss)} & {r.gain:+.6f}'+r'\\')
 lines+=[r'\bottomrule\end{longtable}'];(OUT/'synthetic_table.tex').write_text('\n'.join(lines))
 lines=[r'\begin{longtable}{llrrrrr}',r'\caption{Case-specific selection versus strong defaults on empirical data.}\label{tab:policy-outcomes}\\',r'\toprule Task & Reader & Cases & Sources$^*$ & Better & Worse & Tied\\\midrule\endhead']
 assert (s[['default_failures','selected_failures']].to_numpy()==0).all(), 'Restore failure reporting if any policy fails'
 for task in TASKS:
  for ob in ['hard','soft']:
   r=s[(s.task==task)&(s.observer==ob)].iloc[0];lines.append(f'{LABELS[task]} & {ob} & {r.paired_n} & {r.clusters} & {r.improved} & {r.worsened} & {r.tied}'+r'\\')
 lines+=[r'\bottomrule\end{longtable}'];(OUT/'policy_outcomes_table.tex').write_text('\n'.join(lines))
 lines=[]
 for ob in ['hard','soft']:
  r=s[(s.task=='association')&(s.observer==ob)].iloc[0];name='HardAssociation' if ob=='hard' else 'SoftAssociation';lines.append("\\newcommand{\\"+name+'}{'+f'{r.gain:+.6f} [{r.ci_low:+.6f}, {r.ci_high:+.6f}]'+'}')
 emp=a[(a.kind=='empirical')&(a.H==256)];lines.append("\\newcommand{\\GeometryShared}{"+str(int(emp.any_shared.sum()))+'}')
 geo=g[(g.kind=='empirical')&(g.H==256)].set_index('family')
 for f,name in [('Pie chart','Pie'),('Donut chart','Donut'),('Bar chart','Bar'),('Stacked bar','Stack')]:lines.append("\\newcommand{\\Geometry"+name+'}{'+str(int(geo.loc[f,'wins']))+'}')
 (OUT/'numbers.tex').write_text('\n'.join(lines));print(syn.to_string(index=False));print(geo.to_string());print('Geometry shared',int(emp.any_shared.sum()))
if __name__=='__main__':main()
