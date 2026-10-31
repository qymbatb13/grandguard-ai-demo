"""Taxonomy-aligned weak supervision baseline; not a validated ML classifier."""
from .language import normalize
PATTERNS={
 'complaint.insult':['оскорб','обзыв','балағат','қорла','haqorat','матер','родственник','2.1 оп'],
 'complaint.cheat':['читер','софт','soft','читы','аимбот','aimbot','читы','5.2 оп','fraps'],
 'complaint.dm':['дм','dm','убил без','без причины','зеленой зоне','спавн','5.3 оп','5.4 оп'],
 'complaint.scam':['обман','скам','мошенн','вымога','украл деньги','не отдал'],
 'complaint.rmt_ads':['реклама','реклам','продам за реал','реал','продает аккаунт','телеграм'],
 'complaint.admin':['админ','администратор','снятие наказания','разбан','мут без причины'],
 'complaint.invalid':['нет доказательств','жб без','как купить','просто жб'],
 'report.question':['как ','где ','как устроиться','подскажите','қайда','как получить'],
 'report.help':['застрял','текстур','телепорт','баг','завис','қысылып','bug'],
 'report.complaint':['оскорб','дмят','читер','убивают','помеха'],
 'report.account':['взлом','аккаунт','пропал аккаунт','потерял доступ','заблокирован','блокировка'],
 'report.payment':['донат','оплат','платеж','купил гк','не пришли гк','төлем'],
 'report.offtopic':['привет','ау','ку','qq','hello','помогите'],
}

def allowed_categories(data):
    return {v['code'] for v in data.get('categories',[]) if 'code' in v} if isinstance(data,dict) else set()

def label(text,kind='report',taxonomy=None,model=None):
    s=normalize(text).lower(); kind=kind if kind in ('complaint','report') else 'report'
    permitted=allowed_categories(taxonomy)
    scores={k:sum((2 if len(w)>=5 else 1) for w in keys if w in s) for k,keys in PATTERNS.items() if k.startswith(kind+'.') and (not permitted or k in permitted)}
    cat=max(scores,key=scores.get) if scores else ('complaint.other' if kind=='complaint' else 'report.offtopic')
    score=scores.get(cat,0)
    if model is not None and len(s)>8:
        try:
            probs=model.predict_proba([s])[0]; classes=model.classes_
            best=int(probs.argmax());candidate=str(classes[best]);p=float(probs[best])
            if candidate.startswith(kind+'.') and (not permitted or candidate in permitted) and p>=.48 and score<2:
                cat=candidate;score=2
        except Exception:pass
    if not score: cat='complaint.other' if kind=='complaint' else 'report.offtopic'
    if permitted and cat not in permitted: cat=next((c for c in sorted(permitted) if c.startswith(kind+'.')),cat)
    if cat in ('report.account','report.payment'):priority='p0'
    elif cat in ('complaint.cheat','complaint.scam','complaint.rmt_ads','complaint.admin'): priority='p1'
    elif cat in ('complaint.insult','complaint.dm','report.complaint','report.help'):priority='p2'
    else:priority='p3'
    return cat,priority,min(.92,.42+.10*score)
