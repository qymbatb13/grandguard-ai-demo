from collections import deque
from datetime import datetime,timezone
from difflib import SequenceMatcher
from .language import normalize

class DuplicateDetector:
    def __init__(self): self.entries=deque(maxlen=10000)
    def check(self,reporter,text,created_at=None):
        if not reporter:return False
        try: now=datetime.fromisoformat(created_at.replace('Z','+00:00')) if created_at else datetime.now(timezone.utc)
        except (ValueError,AttributeError): now=datetime.now(timezone.utc)
        s=normalize(text).lower();duplicate=False
        for who,old,when in self.entries:
            if who==reporter and abs((now-when).total_seconds())<=3600 and SequenceMatcher(None,s,old).ratio()>=.87:
                duplicate=True;break
        self.entries.append((reporter,s,now))
        return duplicate
