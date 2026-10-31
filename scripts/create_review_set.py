"""Create a human-labeling sheet from PRIVATE validation data; never commit output."""
import argparse,csv,json,random
from pathlib import Path

def main():
 p=argparse.ArgumentParser();p.add_argument('--input',default='data/tickets_valid.jsonl');p.add_argument('--output',default='data/manual_review.csv');p.add_argument('--size',type=int,default=100);args=p.parse_args()
 rows=[json.loads(x) for x in Path(args.input).read_text(encoding='utf-8').splitlines() if x.strip()]
 rng=random.Random(42); selected=rng.sample(rows,min(args.size,len(rows)))
 dest=Path(args.output);dest.parent.mkdir(parents=True,exist_ok=True)
 with dest.open('w',encoding='utf-8',newline='') as fh:
  out=csv.DictWriter(fh,fieldnames=['ticket_id','kind','player_text','gold_category','gold_priority','reviewer_note']);out.writeheader()
  for r in selected:
   out.writerow({'ticket_id':r.get('ticket_id',''),'kind':r.get('kind',''),'player_text':' '.join(str(m.get('text') or '') for m in r.get('messages',[]) if m.get('role')=='player')})
 print(f'Created {len(selected)} rows: {dest}. Fill gold_category and gold_priority manually. PRIVATE FILE; never publish.')
if __name__=='__main__':main()
