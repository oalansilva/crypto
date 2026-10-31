Lembrete: usar as skills do projeto quando couber (`.agents/skills`, `.cursor/skills`). Este card é `UI impact: none`, mas segue o portão normal: Design → Aprovação de Design → Pronto para Dev, com a aprovação humana do Alan.

Apply MUST NOT escrever em `design.md`, `specs/` ou `.design-digest` deste change (digest muda e o card volta a Design). Nota de Apply vai no comentário do card.

## 1. Motor no `covenant-flow` (`/srv/apps/dev/covenant-flow-worktrees/card-1144-qa-exploratorio-dev`)

- [x] 1.1 Criar o worktree a partir da tag pinada `v1.1.26` (conferir `pin` em `.covenant-flow/overlay.yaml` antes), nunca do `main`. Comparar `scripts/process-fsm/`, `.cursor/` e `install.sh` da tag com a cópia do crypto e registrar diferenças no card, porque o pin apaga o que só existe no consumidor.
- [x] 1.2 `.cursor/process-fsm.yaml`: T14 declara `checks_green` e `qa_dev_ok` de forma visível, ações por fase, I8 com as duas fases, `context_file[QA]` com `qa_dev_pendente`, `qa_dev_fail` (pausa antes da T13) e `qa_dev_inconclusivo` (paging ≤ 20 linhas). Sem aresta, estado ou evento novo. `fsm.py`: guarda nomeada.
- [x] 1.3 `scripts/process-fsm/overlay.py`: leitura da chave opcional `qa_dev`, inclusive `autor_relatorio` e `caminhos_sem_produto`. Chave ausente equivale a desligada.
- [x] 1.4 `scripts/process-fsm/qa_dev.py`:
  - `plan`: lista C1…Cn de `## Entra`, protótipo aprovado ou `prototipo: N/A`, `admin` da sessão, FAIL abertos, `--reteste-de <run> --leitura`.
  - Trava atômica com vencimento: `plan` pega ou renova, devolve `qa_dev_ocupado` se for de outro card, e há comando para soltar na falha de ferramenta.
  - `report`: repete a checagem de saúde e serviços, junta blocos, calcula veredito com `INCONCLUSIVO` na ordem de D5, deixa `passagem` e `passos` fora do comentário, chama `--scan --publico` e evidência pelo overlay, posta com marcador, lista as saídas no `INCONCLUSIVO`, atualiza o registro de FAIL abertos.
  - Classificação `NADA_PARA_TESTAR` por `qa_dev.caminhos_sem_produto`: todos os arquivos casam; falha ao listar o PR não classifica.
  - Leitura do marcador e de `/qa-dev-liberar <run>` só de `qa_dev.autor_relatorio`.
  - Testes sem GitHub.
- [x] 1.5 `scripts/process-fsm/t14.py` e `process_event.py`: fase 1 (trava, closeout, recibo, comentário, `qa_dev_pendente`), trava solta se a fase 1 falhar, `qa_dev_ocupado`, fase 2 (`qa_dev_ok`, `comment_done` lendo o recibo e dizendo quando houve liberação, move), `qa_dev_fail`, `qa_dev_inconclusivo`. Com `qa_dev` desligado, comportamento idêntico ao de hoje. Testes cobrindo os cenários de `specs/process-fsm-event`.
- [x] 1.6 `.cursor/model-policy.yaml`: `qa-dev: execucao`. Teste de que o papel resolve para a faixa e de que o título `qa-dev` casa com o destape.
- [x] 1.7 Skill `.cursor/skills/qa-dev/SKILL.md` e pontes em `.agents/skills/` e `.claude/skills/`: contrato do filho (D3, D5, D9, D11), sem a frase "pare quando tiver evidência suficiente".
  - Proíbe `filename` em print e vídeo, `browser_start_tracing`, `browser_run_code_unsafe`, leitura de `localStorage`, `process_event` e postar `/qa-dev-liberar`.
  - Roteiro com o protótipo do plano.
  - Autorização do Alan e o limite dela, por escrito: criar, alterar e apagar favoritos, estratégias, alertas e configurações, inclusive existentes, sem restaurar, só no DEV, nunca em PROD.
  - Ações sobre usuários fora do teste.
  - Texto do resultado com tela e comportamento, nunca valores da conta.
  - FAIL aberto de outro card vira NÃO TESTADO.
  - Regenerar `.covenant-flow/adapters.json` no fluxo do produto.
- [x] 1.8 `.cursor/skills/covenant-flow/SKILL.md`, seção "QA closeout": as duas fases, blocos, reteste, a pausa antes da T13, reteste sem diff de FAIL contestado, as três saídas do `INCONCLUSIVO` e o caminho de T13 (branch nova com o nome exato do change). Não crescer `AGENTS.md`.
- [x] 1.9 Corrigir `.agents/skills/playwright-cli/SKILL.md` no produto, sem o wrapper ausente.
- [x] 1.10 `pytest scripts/process-fsm -q` verde no produto; tag nova (próxima livre depois de `v1.1.26`). Registrar a saída no card.

## 2. Pin no crypto

- [x] 2.1 `install.sh --pin <tag> --target /srv/apps/dev/criptofarol/crypto-worktrees/card-1144-qa-exploratorio-dev` a partir do worktree do produto. Só o pin, o OpenSpec e arquivos do consumidor mudam no crypto; nenhum byte manual em `scripts/process-fsm/`, `.cursor/` ou hooks.
- [x] 2.2 Preparar o texto do passo do Alan, em comandos separados, para colar em bash comum. O Alan roda `install.sh --account` e `cf_shim.py trust --record`, e abre sessão nova `#1144`. Registrar no card. <!-- covenant-flow:after-pin -->
- [ ] 2.3 Com o pin novo no worktree do crypto e a sessão nova: `pytest scripts/process-fsm -q` verde e `integrar_develop --dry-run` sem erro, com `qa_dev` desligado. Registrar a saída no card. <!-- covenant-flow:after-pin -->

## 3. Consumidor no crypto

- [x] 3.1 `scripts/qa/dev_session.py`:
  - Login fora do agente (D3), `--check` e saída `sessao_ok admin=<sim|nao>`.
  - Códigos distintos para 401 (`senha_recusada`) e 403 (`conta_bloqueada`).
  - `--scan` nas formas literal, JSON, JSON dentro de JSON, URL e URL com `+`.
  - `--scan --publico` acrescenta JWT e e-mail de login.
  - `--scan --self-test` com senha sintética de caracteres especiais em cada forma, sem levar a senha real a arquivo.
  - Recusa de origem que não seja a do DEV, `storage-state.json` 0600.
  - Saída sem valor. Testes com servidor falso e cofre falso, sem ler o segredo real.
- [x] 3.2 `scripts/qa/bloqueia-ordens.js` (D11) e teste: bloqueia `POST /api/monitor/spot-market-orders`, `POST`/`DELETE /api/monitor/spot-stop-order` e `POST`/`PUT`/`DELETE` em `/api/admin/users`; deixa passar `/preview`, `/eligibility` e `GET` de `/api/admin/users`.
- [x] 3.3 `scripts/qa/publish_evidence.py`: cria `QA/<card>/<run>/` na pasta do projeto pelo `gog-bws`, compartilha só com o e-mail de `CRIPTOFAROL_QA_DRIVE_READER` (`--to user --role reader`), nunca usa `--to anyone` nem `--to domain`, confere `gog drive permissions` e recusa enviar com acesso `anyone` ou `domain`, inclusive herdado. Envia, devolve links. Falha não bloqueia. Teste com `gog` falso.
- [x] 3.4 `scripts/qa/setup-dev.sh`: pastas 0700, cópia do init script, `claude mcp add --scope user playwright-qa` (D4), `permissions.allow`, `permissions.deny` de `browser_run_code_unsafe` e `browser_start_tracing`, modo `--check`. Idempotente. O agente escreve o script e não o executa; só o `--check` pode rodar por agente.
- [x] 3.5 `.covenant-flow/overlay.yaml`: chave `qa_dev` com `enabled: false`, `autor_relatorio` e `caminhos_sem_produto`, sem alterar `product_globs`.
- [x] 3.6 `docs/crypto-overlay.md`: regra de implementação por card com as duas fases, operação do teste, nomes dos segredos, Drive, e a regra de release com FAIL aberto em `develop`. `.agents/skills/playwright-cli/SKILL.md`: mesma correção da task 1.9, sem tocar na ponte `.claude/skills/playwright-cli/SKILL.md`.
- [x] 3.7 Passo no `qa-gate` (`.github/workflows/ci.yml`): com `qa_dev.enabled` true na base e head sem a chave ligada, falha com a mensagem de atualizar a partir de `develop`; com a chave desligada na base, não bloqueia. Testes de `scripts/qa/` ligados ao CI. Registrar a saída.
- [ ] 3.8 Provar num PR de teste que o passo alcança branch sem o workflow novo; se não alcançar, registrar no card e parar antes de ligar. <!-- covenant-flow:after-commit -->

## 4. Piloto

- [ ] 4.1 Passo do Alan, no terminal, em comandos separados para colar em bash comum (D10): `setup-dev.sh`, `setup-dev.sh --check` e sessão nova `#1144`. O agente não roda `setup-dev.sh`, só prepara o texto. Na sessão nova, confirmar que os filhos enxergam `mcp__playwright-qa__*` sem pedido de permissão e que `browser_run_code_unsafe` é negada. <!-- covenant-flow:after-commit -->
- [ ] 4.2 Alan cadastra no projeto `Crypto` do cofre `CRIPTOFAROL_DEV_ALAN_PASSWORD` (Value = senha, Note = e-mail de login) e `CRIPTOFAROL_QA_DRIVE_READER` (Value = e-mail da conta Google) e roda `python3 /srv/apps/dev/criptofarol/crypto-worktrees/card-1144-qa-exploratorio-dev/scripts/qa/dev_session.py --check`. Esperado: `sessao_ok admin=<sim|nao>`. Registrar no card se é admin. <!-- covenant-flow:after-commit -->
- [ ] 4.3 Escolher o card piloto (D10, pergunta 2 do design) e rodar plano, blocos, volta rápida e `qa_dev.py report`, sem mover Status. Relatório por critério com PASS, FAIL ou NÃO TESTADO, prints e vídeo, postado no issue do piloto, sem valor da conta no texto. <!-- covenant-flow:after-commit -->
- [ ] 4.4 Rodar `--scan` nos transcripts do pai e dos filhos, no relatório, nos `page-*.yml` e no journal do backend DEV, e `--scan --publico` no relatório e no comentário baixado do issue: todos `ausente`. `--scan --self-test`: `PRESENTE` em todas as formas. <!-- covenant-flow:after-commit -->
- [ ] 4.5 Comprovar a trava com envios que o backend recusaria sem ela: `POST /api/monitor/spot-market-orders` com `preview_token` falso e `POST /api/monitor/spot-stop-order` com `stop_price: 0`. Os dois recebem 403 local, e nada chega ao log do backend DEV. Não usar prévia real nem fluxo válido de ordem. <!-- covenant-flow:after-commit -->
- [ ] 4.6 Conferir com `gog drive permissions` que a pasta do run não tem acesso `anyone` nem `domain`. Alan abre prints e vídeo pelos links do relatório e confirma que enxerga e que não há senha. Registrar no card. <!-- covenant-flow:after-commit -->
- [ ] 4.7 Registrar no card as medidas do piloto: tempo, custo, turnos por bloco, tamanho do vídeo, maior espera. Ajustar `espera_max_min`, `teto_total_min` e os limites do bloco no overlay ou na skill, se preciso. <!-- covenant-flow:after-commit -->

## 5. Ligar e fechar

- [ ] 5.1 Conferir no board que nenhum outro card está em `QA`; se houver, ele fecha a T14 antes. `qa_dev.enabled: true` no overlay, no último commit do card, só depois de a seção 4 passar. <!-- covenant-flow:after-commit -->
- [ ] 5.2 Conferir que todos os arquivos do PR do #1144 casam com `caminhos_sem_produto`. Ensaio vivo no próprio #1144: a fase 1 da T14 devolve `qa_dev_pendente`, com o card em `QA`, e o relatório sai `NADA_PARA_TESTAR`, sem login. Registrar no card. Neste card, o pai roda `review_process_checklist.py --phase postqa` depois desse relatório e antes da fase 2, porque esta task depende da fase 1. <!-- covenant-flow:after-qa -->
- [ ] 5.3 Depois do merge do #1144, listar as branches `card-*` abertas sem a chave e registrar no card quais precisam atualizar a partir de `develop`. <!-- covenant-flow:after-qa -->
