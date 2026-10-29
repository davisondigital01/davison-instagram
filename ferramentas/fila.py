#!/usr/bin/env python3
"""Controle da fila de publicações do Instagram (Davison Digital).
Tipos de item: carrossel (feed), story (vídeo do livro, sai logo depois do carrossel do mesmo livro)
e reel (vídeo com legenda, 2 por dia).
Uso:
  fila.py proximo                     -> JSON do próximo item vencido (ou {"nada": motivo})
  fila.py iniciar <id>                -> marca como "publicando" (trava contra duplicação)
  fila.py publicado <id> <media_id> [permalink]
  fila.py falha <id> <mensagem>       -> volta para "pendente", conta tentativas (3 falhas = "erro")
  fila.py incerto <id> <mensagem>     -> interrompido sem como confirmar: NÃO tenta de novo (evita duplicar)
  fila.py status                      -> resumo
Regras: no máximo 1 publicação de cada tipo por execução; intervalo mínimo de 50 min entre
publicações do mesmo tipo; story só depois que o carrossel do qual depende estiver publicado;
item "publicando" exige conferência no Instagram antes de qualquer nova publicação."""
import json, sys, os, datetime as dt, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
F = ROOT / 'fila.json'; H = ROOT / 'historico.jsonl'
TZ = dt.timezone(dt.timedelta(hours=-3))
BASE = 'https://raw.githubusercontent.com/davisondigital01/davison-instagram/main/'
ORDEM = {'carrossel': 0, 'story': 1, 'reel': 2}
def now():
    o = os.environ.get('FILA_AGORA')  # só para testes
    return dt.datetime.fromisoformat(o) if o else dt.datetime.now(TZ)
def ts(s): return dt.datetime.fromisoformat(s)
def load(): return json.loads(F.read_text(encoding='utf-8'))
def save(q): F.write_text(json.dumps(q, ensure_ascii=False, indent=1), encoding='utf-8')
def log(**k):
    k['quando'] = now().isoformat(timespec='seconds')
    with open(H, 'a', encoding='utf-8') as f: f.write(json.dumps(k, ensure_ascii=False) + '\n')
def get(q, i): return next(x for x in q if x['id'] == i)
def tipo(x): return x.get('tipo', 'carrossel')

def proximo(q):
    trav = [x for x in q if x['status'] == 'publicando']
    if trav:
        x = trav[0]
        r = {'conferir': x['id'], 'tipo': tipo(x), 'titulo': x['titulo'],
             'minutos': round((now() - ts(x['iniciado_em'])).total_seconds() / 60)}
        if x.get('legenda'): r['inicio_legenda'] = x['legenda'][:80]
        else: r['dica'] = 'story não tem legenda: confira se há story publicado após iniciado_em (' + x['iniciado_em'] + ')'
        return r
    pubs = {x['id']: x for x in q if x['status'] == 'publicado'}
    candidatos = []
    for x in q:
        if x['status'] != 'pendente' or ts(x['agendado_para']) > now(): continue
        if x.get('depende') and x['depende'] not in pubs: continue
        ult = [ts(p['publicado_em']) for p in pubs.values() if tipo(p) == tipo(x) and p.get('publicado_em')]
        if ult and (now() - max(ult)).total_seconds() < 50 * 60: continue
        candidatos.append(x)
    if not candidatos:
        pend = sorted((x for x in q if x['status'] == 'pendente'), key=lambda x: x['agendado_para'])
        return {'nada': 'nenhum item liberado agora', 'proximo': pend[0]['agendado_para'] if pend else None, 'pendentes': len(pend)}
    x = sorted(candidatos, key=lambda x: (x['agendado_para'], ORDEM[tipo(x)]))[0]
    r = {'id': x['id'], 'tipo': tipo(x), 'titulo': x['titulo'],
         'atrasado_min': round((now() - ts(x['agendado_para'])).total_seconds() / 60)}
    if tipo(x) == 'carrossel':
        r.update(acao='create_carousel_post', params={'image_urls': [BASE + p for p in x['imagens']], 'caption': x['legenda']})
    elif tipo(x) == 'story':
        r.update(acao='create_story', params={'video_url': BASE + x['video']})
    else:
        r.update(acao='create_video_post', params={'video_url': BASE + x['video'], 'caption': x['legenda'], 'share_to_feed': True})
    return r

if __name__ == '__main__':
    cmd = sys.argv[1]; q = load()
    if cmd == 'proximo':
        print(json.dumps(proximo(q), ensure_ascii=False))
    elif cmd == 'iniciar':
        x = get(q, sys.argv[2]); assert x['status'] == 'pendente', x['status']
        x['status'] = 'publicando'; x['iniciado_em'] = now().isoformat(timespec='seconds'); save(q); log(id=x['id'], evento='iniciado')
    elif cmd == 'publicado':
        x = get(q, sys.argv[2]); x['status'] = 'publicado'; x['publicado_em'] = now().isoformat(timespec='seconds'); x['media_id'] = sys.argv[3]
        if len(sys.argv) > 4: x['permalink'] = sys.argv[4]
        save(q); log(id=x['id'], evento='publicado', media_id=sys.argv[3], titulo=x['titulo'])
    elif cmd == 'falha':
        x = get(q, sys.argv[2]); x['status'] = 'pendente'; x['tentativas'] = x.get('tentativas', 0) + 1; x.pop('iniciado_em', None)
        if x['tentativas'] >= 3: x['status'] = 'erro'
        save(q); log(id=x['id'], evento='falha', erro=' '.join(sys.argv[3:]), tentativas=x['tentativas'])
    elif cmd == 'incerto':
        x = get(q, sys.argv[2]); x['status'] = 'incerto'; x.pop('iniciado_em', None)
        save(q); log(id=x['id'], evento='incerto', obs=' '.join(sys.argv[3:]))
    elif cmd == 'status':
        from collections import Counter
        for t in ORDEM:
            its = [x for x in q if tipo(x) == t]
            nxt = next((x['agendado_para'] + ' ' + x['titulo'] for x in sorted(its, key=lambda x: x['agendado_para']) if x['status'] == 'pendente'), None)
            print(t, dict(Counter(x['status'] for x in its)), 'próximo:', nxt)
