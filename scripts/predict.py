import argparse,json,sys,gzip
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from app.engine import Engine

def main():
    p=argparse.ArgumentParser();p.add_argument('--input',required=True);p.add_argument('--output',required=True);p.add_argument('--data-dir',default=None)
    args=p.parse_args(); engine=Engine(args.data_dir)
    opener=gzip.open if args.input.endswith('.gz') else open
    count=0
    with opener(args.input,'rt',encoding='utf-8') as fin,open(args.output,'w',encoding='utf-8') as out:
        for line in fin:
            if not line.strip():continue
            item=json.loads(line)
            # Do not use historical admin responses or ground-truth verdicts.
            ticket={k:v for k,v in item.items() if k not in ('verdict','punishment','violation','category','priority')}
            ticket['messages']=[m for m in ticket.get('messages',[]) if m.get('role') not in ('admin','moderator')]
            pred=engine.triage(ticket)
            pred['ticket_id']=item.get('ticket_id')
            out.write(json.dumps(pred,ensure_ascii=False)+'\n');count+=1
    print(f'Processed {count} tickets -> {args.output}')
if __name__=='__main__':main()
