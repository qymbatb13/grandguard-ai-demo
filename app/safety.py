import re

def decision(category,kind,text,attachments=0):
    risks=[];s=text.lower()
    if category in ('report.account','report.payment','complaint.admin'):risks.append('sensitive account/payment/admin issue: human required')
    if kind=='complaint':risks.append('complaints require administrator to assess evidence')
    if any(k in s for k in ('апелляц','разбан','верните деньги','refund','взлом','накажите','забаньте')):
        risks.append('punishment, appeal, refund or account action requires human')
    if attachments:risks.append('attachment content not available; quantity is not proof')
    return bool(risks),risks

def valid_citations(candidates,index,message,category=None,taxonomy=None,claimed=None):
    """Allow only IDs present in official rules AND category's permitted references;
    never regard the player's alleged violation as independently verified."""
    allowed=set()
    if taxonomy:
        for row in taxonomy.get('categories',[]):
            if row.get('code')==category:allowed.update(map(str,row.get('rules',[])))
    if not allowed:return []
    picked=[]
    # A claimed rule ID is only a *candidate*, not evidence of a proven violation.
    for ref in claimed or []:
        if ref in allowed and index.get(ref) and ref not in picked:picked.append(ref)
    for row in candidates:
        ref=row['id']
        if ref in allowed and index.get(ref) and ref not in picked and row.get('score',0)>=1.5:picked.append(ref)
    return picked[:2]
