import json
from pathlib import Path
from scripts.train import extract
from app.classifier import label

def test_no_admin_leakage():
 row={'messages':[{'role':'player','text':'читер'}, {'role':'admin','text':'приговор и секрет'}]}
 assert extract(row)=='читер'

def test_kind_separation():
 assert label('читер soft',kind='complaint')[0].startswith('complaint.')
 assert label('застрял в текстурах',kind='report')[0].startswith('report.')
