# Operação automática — Instagram @davisondigital2

Repositório público com tudo o que a publicação automática precisa:
- `img/` — os 7 slides de cada carrossel em JPEG (`<livro>-01.jpg` … `-07.jpg`), cópias dos originais;
- `fila.json` — ordem, horário previsto, legenda, imagens e **status** de cada carrossel;
- `calendario.csv` — o calendário em formato de planilha;
- `historico.jsonl` — registro de cada tentativa, publicação e falha;
- `ferramentas/fila.py` — controla a fila (próximo item, trava, publicado, falha).

## Roteiro de cada execução (tarefa agendada de hora em hora, 07:41–22:41, horário de Brasília)

1. Atualize o repositório (`git pull`).
2. Rode `python3 ferramentas/fila.py proximo`.
   - `{"nada": ...}` → não publique nada. Encerre sem commit.
   - `{"conferir": id, ...}` → uma tentativa anterior foi interrompida. Abra o perfil
     https://www.instagram.com/davisondigital2/ ou consulte o Windsor (conector `instagram`, campos `timestamp`,
     `media_caption`, `media_id`, `media_permalink`) e veja se existe post recente começando com `inicio_legenda`.
     Se existir → `fila.py publicado <id> <media_id>`. Se não existir → `fila.py falha <id> "interrompido"`.
     Commit + push e encerre (não publique nesta execução).
   - Item com `id` → continue.
3. Rode `fila.py iniciar <id>` e faça **commit + push antes de publicar** (trava contra duplicação).
4. Publique com o Windsor `execute_action`: connector `instagram`, account `17841461048178740`,
   action `create_carousel_post`, params `{"image_urls": <image_urls>, "caption": <legenda>}` exatamente como vieram.
   Nunca altere imagens nem legenda. **No máximo uma publicação por execução.**
5. Sucesso → `fila.py publicado <id> <media_id>`. Erro → `fila.py falha <id> "<mensagem>"`
   (depois de 3 falhas o item vira `erro` e deixa de ser tentado — avise o Richard).
6. Commit + push com a mensagem `post <id>: <resultado>`.

## Garantias
- O status gravado no repositório antes da chamada impede que o mesmo item seja publicado duas vezes.
- Horários perdidos são recuperados um por hora, com pelo menos 50 minutos entre posts.

## Reciclagem (depois do 1º ciclo)
Quando os 57 originais estiverem publicados, entram em `fila.json` as versões `curiosidade`, `autoridade`
e `conversao` de cada livro, em arquivos separados (`img/<livro>-<versao>-NN.jpg`), sem alterar os originais.
