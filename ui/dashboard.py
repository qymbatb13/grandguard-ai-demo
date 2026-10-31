"""Local-only operator preview. No real game integration or ticket action API."""
import json,os,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import streamlit as st
from app.engine import Engine

st.set_page_config(page_title='GrandGuard AI',page_icon='🛡️',layout='wide')
@st.cache_resource
def engine(folder): return Engine(folder)
@st.cache_data
def sample_tickets(folder,limit=150):
    f=Path(folder)/'tickets_valid.jsonl'
    if not f.exists(): f=Path('demo_data/tickets_demo.jsonl')
    rows=[]
    with f.open(encoding='utf-8') as inp:
        for i,line in enumerate(inp):
            if i>=limit:break
            if line.strip():rows.append(json.loads(line))
    return rows

folder=os.getenv('GG_DATA_DIR','data')
if not (Path(folder)/'rules.json').exists():folder='demo_data'
e=engine(folder)
st.title('🛡️ GrandGuard AI — Final MVP')
st.caption('Support Copilot · локальная демонстрация · не подключено к серверам Grand Mobile')
if folder=='demo_data': st.warning('Используются СИНТЕТИЧЕСКИЕ правила. Для реальных правил запустите GG_DATA_DIR=data.')
else: st.success(f'Локальный handout подключен: {len(e.rules.rules)} пунктов правил. Данные никуда не отправляются.')
st.caption('ML: '+('загружена слабая TF-IDF модель (не измеренная accuracy)' if e.model is not None else 'модель не обучена — действует rule-based baseline'))
tickets_summary=sample_tickets(folder)
from collections import Counter
kind_counts=Counter(t.get('kind','unknown') for t in tickets_summary)
top=st.columns(3)
top[0].metric('Обращений в локальной очереди',len(tickets_summary))
top[1].metric('Жалобы',kind_counts.get('complaint',0))
top[2].metric('Репорты',kind_counts.get('report',0))
with st.expander('Статистика категорий по текущему алгоритму (частота, не точность)'):
    counts=Counter(e.triage({**{k:v for k,v in t.items() if k not in ('verdict','punishment','violation','status','priority','category')},'messages':[m for m in t.get('messages',[]) if m.get('role')=='player']},detect_duplicates=False)['category'] for t in tickets_summary)
    st.bar_chart(dict(counts))
left,right=st.columns([1,1.5])
with left:
    st.subheader('Очередь обращений')
    tickets=sample_tickets(folder)
    filter_kind=st.selectbox('Фильтр типа',('Все','complaint','report'))
    indices=[i for i,t in enumerate(tickets) if filter_kind=='Все' or t.get('kind')==filter_kind]
    if not indices: st.warning('Нет обращений этого типа');st.stop()
    chosen=st.selectbox('Выбрать обращение',indices,format_func=lambda i:f"{i+1:03d} · {tickets[i].get('kind','report')} · {str(tickets[i].get('ticket_id',''))[:8]}")
    row=tickets[chosen]
    msg=' '.join(str(m.get('text') or '') for m in row.get('messages',[]) if m.get('role')=='player')
    st.text_area('Сообщение игрока',msg,height=170,disabled=True)
    st.caption('Исторические ответы админов не передаются в AI. Вложения отсутствуют, известно только количество.')
    st.write('Тип:',row.get('kind'),'· Вложений:',row.get('images_count',0))
    st.divider()
    st.subheader('Новый тикет')
    custom=st.text_area('Ввести своё сообщение',height=100,placeholder='Меня оскорбили в чате...')
    kind=st.selectbox('Тип',('complaint','report'))
    run_custom=st.button('Анализировать новый тикет',use_container_width=True)
with right:
    st.subheader('Анализ AI')
    if run_custom and custom.strip():
        p={'kind':kind,'messages':[{'role':'player','text':custom}]}
        selected_id='custom-'+custom
    else:
        p={k:v for k,v in row.items() if k not in ('verdict','punishment','violation','status','priority','category')}
        p['messages']=[m for m in row.get('messages',[]) if m.get('role')=='player']
        selected_id=row.get('ticket_id',str(chosen))
    result=e.triage(p,detect_duplicates=False)
    c1,c2,c3=st.columns(3)
    c1.metric('Категория',result['category']);c2.metric('Приоритет',result['priority'].upper());c3.metric('Язык',result['lang'].upper())
    st.caption(f"Оценка уверенности классификатора (не калибрована): {result['confidence']:.0%}. Это не вероятность достоверности жалобы или доказанности нарушения.")
    if result['needs_human']:st.warning('Требуется проверка администратором')
    else:st.info('Черновик доступен для проверки')
    st.text_area('Черновик ответа (можно редактировать)',value=result['draft_reply']['text'],height=140,key='draft-'+selected_id)
    st.write('Кандидаты на пункты правил:',result['draft_reply']['cited'] or 'Нет подходящих пунктов')
    st.caption('Ссылка означает совпадение с официальным справочником и категорией, а не доказанное нарушение. Релевантность подтверждает администратор.')
    for ref in result['draft_reply']['cited']:
        item=e.rules.get(ref)
        if item:
            with st.expander('Правило '+ref):st.write(item['text'])
    st.write('Причины решения:',result['reasons'] or ['Обязательная эскалация не выявлена'])
    st.caption('Категория и приоритет — рекомендации. Перед отправкой администратор проверяет факты и ссылки на правила.')
    with st.expander('Полный JSON'):st.json(result)
    a,b=st.columns(2)
    if a.button('Одобрить (только демо)'):st.success('Помечено локально. Игроку ничего не отправлено.')
    if b.button('Эскалировать (только демо)'):st.info('Отмечено для проверки только в этой сессии.')
