"""Evaluate human-verified categories/priority; discard unlabeled rows."""
import argparse,csv,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from app.engine import Engine

def main():
 p=argparse.ArgumentParser();p.add_argument('--input',default='data/manual_review.csv');p.add_argument('--data-dir',default='data');args=p.parse_args()
 e=Engine(args.data_dir)
 with open(args.input,encoding='utf-8',newline='') as f: rows=list(csv.DictReader(f))
 pairs=[]
 for row in rows:
  if not row.get('gold_category') or not row.get('gold_priority'):continue
  pred=e.triage({'kind':row['kind'],'messages':[{'role':'player','text':row['player_text']}]},detect_duplicates=False)
  pairs.append((row['gold_category'],row['gold_priority'],pred['category'],pred['priority']))
 if not pairs:raise SystemExit('No fully human-reviewed rows. Fill gold_category and gold_priority first.')
 from sklearn.metrics import accuracy_score,f1_score
 print(json.dumps({'human_reviewed_rows':len(pairs),'category_accuracy':round(accuracy_score([x[0] for x in pairs],[x[2] for x in pairs]),4),'category_macro_f1':round(f1_score([x[0] for x in pairs],[x[2] for x in pairs],average='macro',zero_division=0),4),'priority_macro_f1':round(f1_score([x[1] for x in pairs],[x[3] for x in pairs],average='macro',zero_division=0),4),'note':'Local human reviewed subset; not organizer hidden benchmark'},indent=2))
if __name__=='__main__':main()
