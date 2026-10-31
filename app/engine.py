import json,os,re
from pathlib import Path
from .language import normalize,detect
from .classifier import label
from .rag import RuleIndex
from .safety import decision,valid_citations
from .generator import draft
from .dedup import DuplicateDetector

class Engine:
    def __init__(self,data_dir=None):
        folder=Path(data_dir or os.getenv('GG_DATA_DIR','data'))
        self.rules=RuleIndex(folder/'rules.json')
        tax=folder/'taxonomy.json'
        self.taxonomy=json.loads(tax.read_text(encoding='utf-8')) if tax.exists() else None
        self.dedup=DuplicateDetector()
        self.model=None
        modelpath=Path(os.getenv('GG_MODEL_PATH','artifacts/weak_classifier.joblib'))
        if modelpath.exists():
            try:
                import joblib
                self.model=joblib.load(modelpath) # ONLY trusted locally generated artifacts
            except Exception:self.model=None
    def triage(self,payload,detect_duplicates=True):
        messages=payload.get('messages') or []
        if not isinstance(messages,list): messages=[]
        player=[m for m in messages if isinstance(m,dict) and m.get('role') in ('player','reporter','user')]
        content=normalize(' '.join(str(m.get('text') or '') for m in player)) or normalize(str(payload.get('text') or ''))
        # never inspect admin messages or verdicts in prediction
        kind=payload.get('kind','report')
        lang=detect(content, payload.get('server_lang') if payload.get('server_lang') in ('ru','kk','uz','en','es','pt') else payload.get('lang'))
        category,priority,conf=label(content+' '+str(payload.get('rule_refs_raw') or ''),kind,self.taxonomy,self.model)
        def safe_count(value):
            try: return min(10000,max(0,int(value or 0)))
            except (ValueError,TypeError,OverflowError): return 0
        attachments=max([safe_count(m.get('attachments',0)) for m in player]+[safe_count(payload.get('images_count',0))])
        found=self.rules.search(content)
        rawrefs=str(payload.get('rule_refs_raw') or '')+' '+content
        refs=list(dict.fromkeys(re.findall(r'(?<!\d)\d+\.\d+(?:\.\d+)?(?!\d)',rawrefs)))
        cited=valid_citations(found,self.rules,content,category,self.taxonomy,refs)
        needs_human,reasons=decision(category,kind,content,attachments)
        if not cited and kind=='complaint':needs_human=True;reasons.append('no eligible official citation verified')
        if lang=='und':needs_human=True;reasons.append('language uncertain: manual review required')
        if conf<0.55:needs_human=True;reasons.append('low classification confidence: manual review required')
        if not self.rules.rules:needs_human=True;reasons.append('official rules not loaded')
        if self.taxonomy is None:needs_human=True;reasons.append('official taxonomy not loaded')
        duplicate=self.dedup.check(payload.get('reporter_hash'),content,payload.get('created_at')) if detect_duplicates else False
        if duplicate:reasons.append('similar recent ticket from same player')
        nick=payload.get('reported_nick')
        if not nick:
            match=re.search(r'\b[A-Za-z][A-Za-z0-9]{1,25}_[A-Za-z][A-Za-z0-9]{1,25}\b',content)
            nick=match.group(0) if match else None
        return {'lang':lang,'category':category,'priority':priority,'is_spam_or_duplicate':duplicate,
                'extracted':{'nickname':nick,'rule_refs':refs,'has_evidence':attachments>0,'server':payload.get('region')},
                'draft_reply':{'lang':lang,'text':draft(lang,category,cited,needs_human,bool(refs)),'cited':cited},
                'needs_human':needs_human,'confidence':round(conf,2),'reasons':list(dict.fromkeys(reasons))}
