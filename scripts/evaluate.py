import argparse,json,statistics,time,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from app.engine import Engine

def main():
    p=argparse.ArgumentParser();p.add_argument('--input',required=True);p.add_argument('--data-dir',default=None);args=p.parse_args()
    e=Engine(args.data_dir); elapsed=[];total=0;human=0;bad=0
    from collections import Counter
    counts=Counter()
    with open(args.input,encoding='utf-8') as f:
        for line in f:
            if not line.strip(): continue
            item=json.loads(line)
            inp={k:v for k,v in item.items() if k not in ('verdict','punishment','violation','category','priority')}
            inp['messages']=[m for m in item.get('messages',[]) if m.get('role')!='admin']
            t=time.perf_counter();res=e.triage(inp);elapsed.append((time.perf_counter()-t)*1000)
            total+=1;human+=res['needs_human'];counts[res['category']]+=1
            bad+=sum(1 for x in res['draft_reply']['cited'] if e.rules.get(x) is None)
    p95=sorted(elapsed)[min(len(elapsed)-1,int(.95*len(elapsed)))] if elapsed else 0
    print(json.dumps({'samples':total,'p95_local_ms':round(p95,2),'needs_human_rate':round(human/total,3) if total else 0,
                      'invalid_rule_ids':bad,'categories':dict(counts),
                      'classification_accuracy':'NOT MEASURED: category/priority ground truth missing',
                      'draft_quality':'Requires human blind review',
                      'cost_per_ticket_usd':0,'cost_note':'Only local deterministic inference; excludes host infrastructure'},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
