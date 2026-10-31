import json
from pathlib import Path
from fastapi.testclient import TestClient
from app.engine import Engine
from app.language import normalize,detect
from app.rag import RuleIndex
from app.main import app

def fixture(tmp_path):
 (tmp_path/'rules.json').write_text(json.dumps({'rules':[{'id':30,'category':'Общие','text':'Много текста','points':[{'ref':'2.1','text':'Запрещено оскорблять игроков и родственников в чате'}]}]},ensure_ascii=False))
 (tmp_path/'taxonomy.json').write_text(json.dumps({'categories':[{'code':'complaint.insult','rules':['2.1']},{'code':'complaint.other','rules':[]},{'code':'report.account','rules':[]},{'code':'report.help','rules':[]},{'code':'report.offtopic','rules':[]}]}))
 return tmp_path

def test_legacy_characters():
 assert normalize('ќ ґ ѕ є ј ў ї')=='қ ғ ң ә ө ұ ү'
 assert detect('Мені қорлады')=='kk'
def test_official_rule_point_refs(tmp_path):
 idx=RuleIndex(fixture(tmp_path)/'rules.json')
 assert idx.get('2.1') and not idx.get('30') and not idx.get('999')
def test_triage_safe(tmp_path):
 e=Engine(fixture(tmp_path))
 out=e.triage({'kind':'complaint','rule_refs_raw':'2.1','messages':[{'role':'player','text':'Arman_Petrov оскорблял мою семью','attachments':2}]})
 assert out['needs_human'] and out['category']=='complaint.insult'
 assert 'мут на' not in out['draft_reply']['text'].lower()
 assert out['draft_reply']['cited']==['2.1']
def test_hacked_escalation(tmp_path):
 out=Engine(fixture(tmp_path)).triage({'kind':'report','messages':[{'role':'player','text':'Мой аккаунт взломали'}]})
 assert out['needs_human'] and out['priority']=='p0'
def test_api_contract():
 response=TestClient(app).post('/triage',json={'kind':'report','messages':[{'role':'player','text':'Помогите, застрял в текстурах'}]})
 assert response.status_code==200
 for key in ['lang','category','priority','is_spam_or_duplicate','extracted','draft_reply','needs_human','confidence','reasons']:assert key in response.json()
def test_admin_leakage_ignored(tmp_path):
 e=Engine(fixture(tmp_path));p={'kind':'complaint','messages':[{'role':'player','text':'Он меня оскорблял'},{'role':'admin','text':'Аккаунт взломан, вернуть деньги'}]}
 o=e.triage(p)
 assert o['category']=='complaint.insult'

def test_latin_gaming_abbreviation_uses_server_language(tmp_path):
 e=Engine(fixture(tmp_path))
 o=e.triage({'kind':'complaint','server_lang':'ru','messages':[{'role':'player','text':'5.2 OP, soft, fraps: <url>'}]})
 assert o['lang']=='ru'

def test_explicit_kazakh_overrides_server_hint():
 assert detect('Мені чатта қорлады', 'ru')=='kk'

def test_unverified_rule_not_cited(tmp_path):
 e=Engine(fixture(tmp_path))
 o=e.triage({'kind':'complaint','messages':[{'role':'player','text':'Оскорблял, пункт 999.1'}]})
 assert '999.1' not in o['draft_reply']['cited']
 assert o['needs_human']

def test_multilingual_grounded_templates(tmp_path):
 from app.generator import draft
 for lang in ('ru','kk','uz','en','es','pt'):
  s=draft(lang,'complaint.insult',[],True,False)
  assert len(s)>40
  assert '30 минут' not in s
