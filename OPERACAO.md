# Operação automática — Instagram @davisondigital2

Repositório público com tudo o que a publicação automática precisa:
- `img/` — os 7 slides de cada carrossel em JPEG (`<livro>-01.jpg` … `-07.jpg`), cópias dos originais;
- `vid/` — o vídeo animado de cada livro (`<livro>.mp4`, 1080x1920, 14 s), usado em Stories e Reels;
- `fila.json` — cada item tem `tipo` (`carrossel`, `story`, `reel`), horário previsto e **status**;
- `calendario.csv` — o calendário dos carrosséis;
- `historico.jsonl` — registro de cada tentativa, publicação e falha;
- `ferramentas/fila.py` — controla a fila (próximo item, trava, publicado, falha, incerto).

Ritmo: 4 carrosséis/dia (07:41, 12:41, 18:41, 21:41); logo após cada carrossel, um Story com o vídeo
do mesmo livro; 2 Reels/dia (12:41 e 21:41), sempre de um livro diferente do carrossel do horário.
Itens com status `bloqueado` não são publicados (aguardam liberação do Richard).

## Roteiro de cada execução (tarefa agendada de hora em hora, 07:41–22:41, horário de Brasília)

1. Atualize o repositório (`git pull`).
2. Repita o ciclo abaixo **no máximo 3 vezes** (no máximo 1 item de cada tipo por execução):
   a. Rode `python3 ferramentas/fila.py proximo`.
      - `{"nada": ...}` → pare o ciclo.
      - `{"conferir": id, "tipo": ...}` → uma tentativa anterior foi interrompida. **Não publique nada nesta execução.**
        * carrossel ou reel: consulte o Windsor (`get_data`, conector `instagram`, conta `17841461048178740`,
          campos `media_id`, `timestamp`, `media_caption`, `media_permalink`) e procure post recente cuja legenda
          comece com `inicio_legenda`. Achou → `fila.py publicado <id> <media_id> <permalink>`.
          Não achou → `fila.py falha <id> "interrompido"`.
        * story (sem legenda, não dá para confirmar com segurança) → `fila.py incerto <id> "interrompido"`
          (não tenta de novo, para nunca duplicar) e avise o Richard no resumo.
        * Commit + push e encerre a execução.
      - Item com `id` → continue.
   b. `fila.py iniciar <id>` e faça **commit + push antes de publicar** (trava contra duplicação).
   c. Publique com o Windsor `execute_action`: connector `instagram`, account `17841461048178740`,
      action = campo `acao`, params = campo `params`, **exatamente como vieram**. Nunca altere imagens, vídeo ou legenda.
   d. Sucesso → `fila.py publicado <id> <media_id>`. Erro → `fila.py falha <id> "<mensagem>"`
      (depois de 3 falhas o item vira `erro` e deixa de ser tentado — avise o Richard).
   e. Commit + push com a mensagem `post <id>: <resultado>`. Se houve erro, pare o ciclo.

## Garantias
- O status gravado no repositório antes da chamada impede que o mesmo item seja publicado duas vezes.
- Story só sai depois que o carrossel do mesmo livro estiver publicado.
- Horários perdidos são recuperados nas horas seguintes, com pelo menos 50 minutos entre itens do mesmo tipo.
- Destaques (as "bolinhas" do perfil) não existem na API do Instagram: são montados pelo Richard no app,
  a partir do Arquivo de stories.

## Reciclagem (depois do 1º ciclo)
Quando os 57 carrosséis originais estiverem publicados, entram em `fila.json` as versões `curiosidade`, `autoridade`
e `conversao` de cada livro, em arquivos separados (`img/<livro>-<versao>-NN.jpg`), sem alterar os originais.
