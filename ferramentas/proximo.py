#!/usr/bin/env python3
"""Decide o próximo carrossel a publicar, usando o próprio Instagram como registro (sem estado local).
Uso: python3 ferramentas/proximo.py posts_recentes.json
posts_recentes.json = lista [{"timestamp": "...", "media_caption": "...", "media_id": "...", "media_permalink": "..."}]
com os posts do perfil nos últimos 60 dias (Windsor, conector instagram).
Saída (JSON):
  {"publicar": {...}}  -> publique este item (image_urls + legenda), exatamente como está
  {"nada": "..."}      -> não publique nada nesta execução
  e sempre "relatorio": publicados / pendentes / atrasados."""
import json, sys, os, datetime as dt
RAW = 'https://raw.githubusercontent.com/davisondigital01/davison-instagram/main/'
TZ = dt.timezone(dt.timedelta(hours=-3))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
agora = dt.datetime.fromisoformat(os.environ['FILA_AGORA']) if os.environ.get('FILA_AGORA') else dt.datetime.now(TZ)
fila = json.load(open(os.path.join(ROOT, 'fila.json'), encoding='utf-8'))
posts = json.load(open(sys.argv[1], encoding='utf-8')) if len(sys.argv) > 1 else []
def norm(s): return ' '.join((s or '').split())[:120]
caps = {norm(p.get('media_caption')): p for p in posts}
def ts(p):
    t = p['timestamp'].replace('+0000', '+00:00'); return dt.datetime.fromisoformat(t)
publicados, pend = [], []
for x in fila:
    (publicados if norm(x['legenda']) in caps else pend).append(x)
vencidos = [x for x in pend if dt.datetime.fromisoformat(x['agendado_para']) <= agora]
rel = {'publicados': len(publicados), 'pendentes': len(pend), 'vencidos': len(vencidos),
       'proximo_agendado': pend[0]['agendado_para'] + ' ' + pend[0]['titulo'] if pend else None}
ultimo = max((ts(p) for p in posts), default=None)
if not vencidos:
    out = {'nada': 'nenhum item vencido'}
elif ultimo and (agora - ultimo).total_seconds() < 50 * 60:
    out = {'nada': 'último post há menos de 50 minutos'}
else:
    x = sorted(vencidos, key=lambda x: x['agendado_para'])[0]
    out = {'publicar': {'id': x['id'], 'titulo': x['titulo'], 'caption': x['legenda'],
                        'image_urls': [RAW + p for p in x['imagens']],
                        'atrasado_min': round((agora - dt.datetime.fromisoformat(x['agendado_para'])).total_seconds() / 60)}}
out['relatorio'] = rel
print(json.dumps(out, ensure_ascii=False, indent=1))
