# Operação automática — Instagram @davisondigital2

Repositório público com o que a publicação automática precisa:
- `img/` — os 7 slides de cada carrossel em JPEG (`<livro>-01.jpg` … `-07.jpg`), cópias dos originais do Richard;
- `fila.json` — ordem, horário previsto, legenda e imagens de cada carrossel;
- `calendario.csv` — o mesmo calendário em formato de planilha;
- `ferramentas/proximo.py` — decide o que publicar.

O **próprio Instagram é o registro**: um carrossel conta como publicado quando já existe no perfil
um post com a mesma legenda. Assim nada é publicado duas vezes, mesmo que uma execução falhe no meio.

## Roteiro de cada execução (tarefa agendada, de hora em hora, 07:41–22:41, horário de Brasília)

1. `git pull` (ou clone raso) deste repositório.
2. Busque no Windsor (conector `instagram`, conta `17841461048178740`) os posts dos últimos 60 dias com os campos
   `timestamp`, `media_caption`, `media_id`, `media_permalink`, usando `force_refresh: true`.
   Salve a lista em `/tmp/posts.json`.
3. Rode `python3 ferramentas/proximo.py /tmp/posts.json`.
4. Se a saída tiver `"nada"`, encerre sem publicar.
5. Se tiver `"publicar"`, chame o Windsor `execute_action` com connector `instagram`, account `17841461048178740`,
   action `create_carousel_post` e params `{"image_urls": <image_urls>, "caption": <caption>}` exatamente como vieram.
   Nunca altere imagens nem legenda. **No máximo uma publicação por execução.**
6. Se a publicação der erro, não tente de novo na mesma execução: a próxima execução tenta outra vez.
   Se o mesmo item falhar em 3 execuções seguidas, envie uma notificação ao Richard com o erro.
7. Ao final, relate em uma linha: o que foi publicado (título + link) ou o motivo de não publicar, e o `relatorio`.

## Reciclagem (depois do 1º ciclo)
Quando os 57 originais estiverem publicados, entram em `fila.json` as versões `curiosidade`, `autoridade`
e `conversao` de cada livro, em arquivos separados (`img/<livro>-<versao>-NN.jpg`), sem alterar os originais,
nos mesmos 4 horários diários.
