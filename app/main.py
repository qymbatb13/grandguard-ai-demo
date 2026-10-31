from fastapi import FastAPI,HTTPException
from pydantic import BaseModel,Field
from typing import Any
from .engine import Engine

app=FastAPI(title='GrandGuard AI',version='0.1.0',description='Game support triage copilot; not an autonomous moderator')
engine=Engine()
class Ticket(BaseModel):
    kind: str='report'
    messages: list[dict[str,Any]]=Field(default_factory=list)
    text: str|None=None
    lang: str|None=None
    server_lang: str|None=None
    region: str|None=None
    reporter_hash: str|None=None
    reported_nick: str|None=None
    images_count: int=0
    created_at: str|None=None
    model_config={'extra':'allow'}

@app.get('/health')
def health(): return {'status':'ok','rules_loaded':len(engine.rules.rules),'taxonomy_loaded':engine.taxonomy is not None}

@app.post('/triage')
def triage(ticket:Ticket):
    if not ticket.messages and not ticket.text: raise HTTPException(422,'At least one message or text required')
    return engine.triage(ticket.model_dump())
