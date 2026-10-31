"""Conservative language detection for short multilingual player tickets."""
import re

LEGACY = str.maketrans({'ќ':'қ','ґ':'ғ','ѕ':'ң','є':'ә','ј':'ө','ў':'ұ','ї':'ү','Ќ':'Қ','Ґ':'Ғ','Ѕ':'Ң','Є':'Ә','Ј':'Ө','Ў':'Ұ','Ї':'Ү'})
LANGS={'ru','kk','uz','en','es','pt'}

def normalize(text: str) -> str:
    return re.sub(r'\s+', ' ', (text or '').translate(LEGACY)).strip()

def detect(text: str, hint: str | None = None) -> str:
    s=normalize(text).lower()
    hint=hint if hint in LANGS else None
    # Uzbek-specific letters before shared Kazakh/Uzbek қ / ғ.
    if re.search(r'[ўҳ]', s) or re.search(r"\b(salom|rahmat|iltimos|menga|sizga|shikoyat|akkauntim|yordam|oʻyin|o‘yin)\b",s):return 'uz'
    if re.search(r'[әіңөұүһі]',s) or re.search(r'\b(мені|маған|сәлем|ойыншы|көмек|қорлады|рахмет|қайда)\b',s):return 'kk'
    if re.search(r'[қғ]',s):return hint if hint in ('kk','uz') else 'kk'
    if re.search(r'[а-яё]',s):return 'ru'
    # Latin-script gaming abbreviations have no reliable linguistic signal.
    # Prefer a provided server language, but never mistake an explicit English phrase.
    if re.search(r'\b(the|please|hello|my account|i need help|player banned)\b',s):return 'en'
    if re.search(r'\b(hola|ayuda|cuenta|jugador|por favor)\b',s):return 'es'
    if re.search(r'\b(olá|ajuda|conta|jogador|obrigado)\b',s):return 'pt'
    if re.search(r'\b(salom|rahmat|yordam)\b',s):return 'uz'
    return hint or 'und'
