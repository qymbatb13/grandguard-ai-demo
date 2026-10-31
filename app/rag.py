"""BM25 retrieval over official rules[].points[].ref. Never cite section block IDs."""
import json,re,math
from pathlib import Path
from collections import Counter
from .language import normalize

def tokenize(s): return re.findall(r'[^\W_]+', normalize(str(s)).lower(),flags=re.UNICODE)

class RuleIndex:
    def __init__(self,path=None):
        self.rules=[];self.by_id={};self.tokens=[];self.df=Counter();self.avg=1
        if path and Path(path).exists(): self.load(path)
    def load(self,path):
        data=json.loads(Path(path).read_text(encoding='utf-8'))
        found=[]
        for section in data.get('rules',[]):
            for point in section.get('points',[]):
                ref=str(point.get('ref') or '').strip()
                body=str(point.get('text') or '').strip()
                if ref and body: found.append({'id':ref,'text':body,'section':section.get('category','')})
        self.by_id={r['id']:r for r in found};self.rules=list(self.by_id.values())
        self.tokens=[tokenize(r['text']) for r in self.rules]
        self.df=Counter(t for ts in self.tokens for t in set(ts))
        self.avg=sum(map(len,self.tokens))/max(1,len(self.tokens))
    def get(self,ref): return self.by_id.get(str(ref))
    def search(self,query,limit=5):
        q=set(tokenize(query));n=len(self.rules);scored=[]
        for r,toks in zip(self.rules,self.tokens):
            freqs=Counter(toks);score=0;length=len(toks)
            for term in q:
                if not freqs[term]: continue
                idf=math.log(1+(n-self.df[term]+.5)/(self.df[term]+.5))
                score+=idf*(freqs[term]*2.2)/(freqs[term]+1.2*(.25+.75*length/self.avg))
            if score>0: scored.append((score,r))
        scored.sort(key=lambda x:x[0],reverse=True)
        return [{**r,'score':round(score,3)} for score,r in scored[:limit]]
