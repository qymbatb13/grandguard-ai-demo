"""Train a character TF-IDF model with WEAK, partially rule-generated labels.
Metrics against weak labels are agreement only, NOT true classification accuracy.
Never use historical admin messages or outcomes as prediction input.
"""
import argparse,collections,gzip,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from app.classifier import label
from app.language import normalize

def extract(row):
 return normalize(' '.join(str(m.get('text') or '') for m in row.get('messages',[]) if m.get('role')=='player'))

def main():
 p=argparse.ArgumentParser();p.add_argument('--input',required=True);p.add_argument('--output',default='artifacts/weak_classifier.joblib');p.add_argument('--data-dir',default='data');p.add_argument('--max-rows',type=int,default=60000);a=p.parse_args()
 import joblib
 from sklearn.pipeline import make_pipeline
 from sklearn.feature_extraction.text import TfidfVectorizer
 from sklearn.linear_model import LogisticRegression
 from sklearn.model_selection import train_test_split
 from sklearn.metrics import classification_report,confusion_matrix
 tax=json.loads((Path(a.data_dir)/'taxonomy.json').read_text(encoding='utf-8'))
 samples=[];labels=[];seen=set()
 # Seed authoritative CATEGORY EXAMPLES (not gold ticket annotations); may be few.
 for category in tax.get('categories',[]):
  for example in category.get('examples',[]):
   if example and (example,category['code']) not in seen:
    samples.append(normalize(example));labels.append(category['code']);seen.add((example,category['code']))
 opener=gzip.open if a.input.endswith('.gz') else open
 with opener(a.input,'rt',encoding='utf-8') as stream:
  for line in stream:
   if not line.strip():continue
   row=json.loads(line);msg=extract(row)
   if not msg:continue
   cat,_,confidence=label(msg+' '+str(row.get('rule_refs_raw') or ''),row.get('kind','report'),tax)
   if confidence<0.60:continue
   features=row.get('kind','report')+' '+msg
   if features in seen:continue
   seen.add(features);samples.append(features);labels.append(cat)
   if len(samples)>=a.max_rows:break
 if len(set(labels))<2:raise SystemExit('Not enough weak categories for fitting')
 counts=collections.Counter(labels)
 keep=[i for i,c in enumerate(labels) if counts[c]>=2];samples=[samples[i] for i in keep];labels=[labels[i] for i in keep]
 xtr,xt,yt,ytest=train_test_split(samples,labels,test_size=0.2,random_state=42,stratify=labels if min(collections.Counter(labels).values())>=2 else None)
 def mk():return make_pipeline(TfidfVectorizer(analyzer='char',ngram_range=(2,4),min_df=2,max_features=80000,sublinear_tf=True),LogisticRegression(max_iter=350,class_weight='balanced'))
 holdout=mk();holdout.fit(xtr,yt);pred=holdout.predict(xt)
 from sklearn.metrics import f1_score
 score=f1_score(ytest,pred,average='macro',zero_division=0)
 final=mk();final.fit(samples,labels)
 dest=Path(a.output);dest.parent.mkdir(parents=True,exist_ok=True);joblib.dump(final,dest)
 result={'trained_rows':len(samples),'weak_labels_by_category':dict(collections.Counter(labels)),'holdout_weak_label_macro_f1':round(float(score),4),'important':'Agreement with noisy weak labels only; NOT accuracy against hidden/ground-truth labels','model_path':str(dest)}
 (dest.parent/'training_report.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
