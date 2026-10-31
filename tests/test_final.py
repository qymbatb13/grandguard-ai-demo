from app.engine import Engine
from app.language import detect

def test_unknown_language_escalation():
 e=Engine('demo_data');r=e.triage({'kind':'report','messages':[{'role':'player','text':'12345 ????'}]},False)
 assert r['needs_human'] and r['lang']=='und'

def test_bad_attachment_count_is_safe():
 e=Engine('demo_data');r=e.triage({'kind':'complaint','messages':[{'role':'player','text':'оскорбил','attachments':'invalid'}]},False)
 assert r['needs_human']

def test_admin_reply_not_used_for_prediction():
 e=Engine('demo_data')
 a={'kind':'complaint','messages':[{'role':'player','text':'меня оскорбили'}]}
 b={'kind':'complaint','messages':a['messages']+[{'role':'admin','text':'мошенничество донат банк'}]}
 assert e.triage(a,False)['category']==e.triage(b,False)['category']

def test_rule_ids_exist():
 e=Engine('demo_data');r=e.triage({'kind':'complaint','messages':[{'role':'player','text':'софт 5.2'}]},False)
 assert all(e.rules.get(x) for x in r['draft_reply']['cited'])
