"""Run all four documented examples and compare exported scores to benchmark cases."""
from common import *
import subprocess,os

def main():
 results=[];env=os.environ.copy();env.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
 marginal=json.loads((ROOT/'data/derived/comparisons.json').read_text());extension=json.loads((ROOT/'task_first/results/inputs.json').read_text());configs=all_configs()
 for task in ['spread','composition','profile','association']:
  folder=ROOT/'benchmark_release/examples'/task
  subprocess.run([sys.executable,str(ROOT/'benchmark_release/score_and_compare.py'),str(ROOT/'task_first/examples'/f'{task}.csv'),'--task',task,'--output-dir',str(folder)],check=True,env=env,cwd=ROOT,stdout=subprocess.DEVNULL)
  inp=json.loads((folder/'input.json').read_text());matches=[]
  for c in marginal if task=='spread' else extension:
   if task=='spread':same=all(len(c[g])==len(inp[g]) and np.allclose(c[g],inp[g],atol=1e-12,rtol=0) for g in ['x','y'])
   else:same=c['task']==task and np.shape(c['values'])==np.shape(inp['values']) and np.allclose(c['values'],inp['values'],atol=1e-12,rtol=0)
   if same:matches.append(c['key'])
  assert matches,(task,'No benchmark source match')
  expected=configs[(configs.key==matches[0])&(configs.task==task)&(configs.observer=='hard')]
  actual=pd.read_csv(folder/'scores.csv');z=actual.merge(expected,on=['candidate','H'],suffixes=('_cli','_benchmark'),validate='one_to_one');assert len(z)==len(actual);assert np.allclose(z.loss_cli,z.loss_benchmark,atol=1e-12,rtol=0,equal_nan=True)
  results.append(dict(task=task,matched_source=matches[0],configuration_losses=len(z),maximum_difference=float(abs(z.loss_cli-z.loss_benchmark).max())))
 (OUT/'example_verification.json').write_text(json.dumps(dict(status='passed',examples=results),indent=2));print(json.dumps(results,indent=2))
if __name__=='__main__':main()
