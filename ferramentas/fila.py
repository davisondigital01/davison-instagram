#!/usr/bin/env python3
"""Controle da fila de publicações do Instagram (Davison Digital).
Uso:
  fila.py proximo                     -> imprime JSON do próximo item vencido (ou {"nada": motivo})
  fila.py iniciar <id>                -> marca como "publicando" (trava contra duplicação)
  fila.py publicado <id> <media_id> [permalink]
  fila.py falha <id> <mensagem>       -> volta para "pendente", conta tentativas
  fila.py status                      -> resumo
Regras: no máximo 1 publicação por execução; intervalo mínimo de 50 min entre posts;
itens "publicando" há mais de 20 min exigem conferência no Instagram antes de nova tentativa."""
import json, sys, datetime as dt, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
F = ROOT / 'fila.json'; H = ROOT / 'historico.jsonl'
TZ = dt.timezone(dt.timedelta(hours=-3))
import os
def now():
    o = os.environ.get('FILA_AGORA')  # só para testes
    return dt.datetime.fromisoformat(o) if o else dt.datetime.now(TZ)
def load(): return json.loads(F.read_text(encoding='utf-8'))
def save(q): F.write_text(json.dumps(q, ensure_ascii=False, indent=1), encoding='utf-8')
def log(**k):
    k['quando'] = now().isoformat(timespec='seconds')
    with open(H, 'a', encoding='utf-8') as f: f.write(json.dumps(k, ensure_ascii=False) + '\n')
def get(q, i): return next(x for x in q if x['id'] == i)
cmd = sys.argv[1]
q = load()
if cmd == 'proximo':
    pub = [x for x in q if x['status'] == 'publicado' and x.get('publicado_em')]
    trav = [x for x in q if x['status'] == 'publicando']
    if trav:
        x = trav[0]; age = (now() - dt.datetime.fromisoformat(x['iniciado_em'])).total_seconds() / 60
        print(json.dumps({'conferir': x['id'], 'titulo': x['titulo'], 'minutos': round(age), 'inicio_legenda': x['legenda'][:80]}, ensure_ascii=False)); sys.exit()
    if pub:
        last = max(dt.datetime.fromisoformat(x['publicado_em']) for x in pub)
        if (now() - last).total_seconds() < 50 * 60:
            print(json.dumps({'nada': 'último post há menos de 50 min'})); sys.exit()
    due = [x for x in q if x['status'] == 'pendente' and dt.datetime.fromisoformat(x['agendado_para']) <= now()]
    if not due:
        nxt = [x for x in q if x['status'] == 'pendente']
        print(json.dumps({'nada': 'nenhum item vencido', 'proximo': nxt[0]['agendado_para'] if nxt else None, 'pendentes': len(nxt)})); sys.exit()
    x = sorted(due, key=lambda x: x['agendado_para'])[0]
    base = 'https://raw.githubusercontent.com/davisondigital01/davison-instagram/main/'
    print(json.dumps({'id': x['id'], 'titulo': x['titulo'], 'legenda': x['legenda'],
                      'image_urls': [base + p for p in x['imagens']], 'atrasado_min': round((now() - dt.datetime.fromisoformat(x['agendado_para'])).total_seconds() / 60)}, ensure_ascii=False))
elif cmd == 'iniciar':
    x = get(q, sys.argv[2]); assert x['status'] == 'pendente'; x['status'] = 'publicando'; x['iniciado_em'] = now().isoformat(timespec='seconds'); save(q); log(id=x['id'], evento='iniciado')
elif cmd == 'publicado':
    x = get(q, sys.argv[2]); x['status'] = 'publicado'; x['publicado_em'] = now().isoformat(timespec='seconds'); x['media_id'] = sys.argv[3]
    if len(sys.argv) > 4: x['permalink'] = sys.argv[4]
    save(q); log(id=x['id'], evento='publicado', media_id=sys.argv[3], titulo=x['titulo'])
elif cmd == 'falha':
    x = get(q, sys.argv[2]); x['status'] = 'pendente'; x['tentativas'] = x.get('tentativas', 0) + 1; x.pop('iniciado_em', None)
    if x['tentativas'] >= 3: x['status'] = 'erro'
    save(q); log(id=x['id'], evento='falha', erro=' '.join(sys.argv[3:]), tentativas=x['tentativas'])
elif cmd == 'status':
    from collections import Counter
    print(dict(Counter(x['status'] for x in q)), 'próximo:', next((x['agendado_para'] + ' ' + x['titulo'] for x in q if x['status'] == 'pendente'), None))
