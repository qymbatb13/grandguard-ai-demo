"""Extract PRIVATE original handout locally; never commit or publish data."""
import argparse,tarfile,shutil
from pathlib import Path

def main():
 p=argparse.ArgumentParser();p.add_argument('--archive',required=True);p.add_argument('--data-dir',default='data');args=p.parse_args()
 dest=Path(args.data_dir);dest.mkdir(parents=True,exist_ok=True)
 required=['rules.json','taxonomy.json','tickets_train.jsonl.gz','tickets_valid.jsonl']
 with tarfile.open(args.archive,'r:gz') as archive:
  for name in required:
   member=archive.getmember('handout/'+name)
   if not member.isfile():raise SystemExit('Not a regular file: '+name)
   with archive.extractfile(member) as inp,(dest/name).open('wb') as out:shutil.copyfileobj(inp,out)
 print('Private dataset ready:',dest.resolve())
 print('Do not push the data/ directory to GitHub.')
if __name__=='__main__':main()
