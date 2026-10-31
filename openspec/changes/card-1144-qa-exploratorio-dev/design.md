## Context

Status: Design. Briefing copiado do issue #1144 (REST, 2026-10-30) em `proposal.md`. O issue deixou com o Design: como o teste encaixa na FSM, a regressão, a ferramenta de navegador e a evidência. O ensaio de 30/10 fechou o modelo (o padrão de execução do fluxo).

UI impact: none
live_route: N/A — card de processo e de teste, nenhuma tela do produto muda
surface: none

Sem superfície: o card mexe no motor do fluxo, em scripts de operação e na configuração do servidor. Prototype: N/A. Impeccable: N/A (nenhuma tela, componente ou texto de produto muda; o texto que o Alan lê no comentário é contrato de processo, fixado nas specs).

### O que muda para você

- Depois do merge, o card fica em `QA` enquanto um agente usa o DEV logado com o seu usuário. Ele testa cada critério e tenta quebrar.
- Você recebe no issue um relatório por critério (PASS, FAIL ou NÃO TESTADO), com links para os prints e o vídeo no Drive, numa pasta aberta só para a sua conta. O comentário é público e não traz valores da sua conta: cita tela e comportamento, não saldo, posição ou e-mail.
- **O que acontece depois do relatório:**
  - Algo passou, nada falhou e os serviços do DEV estão de pé: o card segue para `Done` e chega à homologação já exercitado. Critério NÃO TESTADO aparece no relatório, com motivo.
  - FAIL: o card para em `QA` e o agente pergunta a você. Se o defeito for real, ele volta para `Em desenvolvimento` e só chega ao `Done` depois de a correção entrar no DEV e o critério passar. Se a leitura do agente estiver errada, você diz qual é a certa, e ele refaz o teste sem mexer no código.
  - Nenhum critério passou, ou o DEV ou um serviço caiu: o card fica em `QA` como `INCONCLUSIVO`, e você decide entre consertar e testar de novo, devolver o card ou liberar por um comentário exato seu (D9).
  - Nada mudou no produto: o relatório diz "nada para testar no DEV", e o card segue.
- **Efeito no release:** entre o FAIL e a correção, o defeito fica em `develop` e no DEV. Nesse intervalo, `develop -> main` fica proibido: `docs/crypto-overlay.md` exige `release-*` a partir de `main` só com os aprovados, ou decisão sua. Nada barra isso sozinho, porque o `pre` do `release-guard` não consulta o board. A regra é a de hoje para qualquer conteúdo não homologado em `develop`, mas o intervalo fica mais comum.
- **Mudança na lei do fluxo, que sua aprovação do design autoriza:** a T14 deixa de ser um passo só. Não nasce aresta, coluna nem evento, mas a guarda e as ações da T14 mudam (D1).
- Cada card custa de US$ 3,35 a cerca de US$ 7,35 a preço de tabela e de 6 a 18 minutos a mais, além das esperas reais de backtest e worker. O piso é a estimativa do ensaio; o teto é o limite de chamadas dos blocos (D5). Numa assinatura, isso consome cota.
- **Você faz, nesta ordem, no bash comum:**
  1. Revisão de confiança do pin novo: `install.sh --account` e `cf_shim.py trust --record`, depois sessão nova `#1144`.
  2. Registro do navegador: `setup-dev.sh`, porque ele altera a lista de permissões da sua conta, e isso não é ato de agente. Depois, `setup-dev.sh --check` e sessão nova.
  3. Cadastro da senha do DEV e da sua conta Google no cofre, depois `dev_session.py --check` (D10).
  4. No piloto, abrir os prints e o vídeo pelos links e confirmar que enxerga e que não há senha.

### Fatos verificados em 2026-10-30

- **T14 hoje:** `run_t14` (`scripts/process-fsm/t14.py`) faz `squash`, `sync_dev_source`, `restart` e `comment_done`, e o `process_event` move para `Done` em seguida. Mas já existe um recibo (`closeout_done`): repetir `integrar_develop` com o fechamento feito e o Status ainda em `QA` só pede o move, sem refazer nada e sem medir o PR de novo.
- **Overlay na T14:** `t14.py` lê o overlay de `REPO_ROOT`, a árvore do próprio card. Branch sem o pin novo roda o motor antigo, que não enxerga `qa_dev` em lugar nenhum.
- **`qa-gate`:** roda em `pull_request` para `develop`. Pela documentação do GitHub, nesse evento o workflow vem do merge com a base, então a regra nova vale também para branch antiga. **Não verificado** aqui: a task 3.7 prova isso num PR de teste.
- **Executor:** `scripts/process-fsm/portao/decisao.py` confere coluna de origem, evento e ator; não mede guarda (decisão D3 do #1135). A aresta `QA → Done` por `integrar_develop` já existe no `PIN` dele.
- **Login:** `POST /api/auth/login` devolve `accessToken`, `refreshToken` e `isAdmin`; o frontend guarda em `localStorage` (`auth_access_token`, `auth_refresh_token`, `auth_user`, em `frontend/src/stores/authStore.tsx`). Acesso dura 15 min, renovação 7 dias. Credencial errada dá 401. Conta suspensa, banida ou com senha temporária vencida dá 403.
- **Área administrativa:** `/admin/users`, `/combo/discovery` e `/combo/select` são `requireAdmin`. `POST /api/admin/users/{id}/suspend` não protege o próprio usuário. **Não verificado** se o seu usuário no DEV é admin; não li `.env` nem banco.
- **Playwright MCP 0.0.83:** pede o Chromium 1247; o cache tem o 1248 em `~/.cache/ms-playwright/chromium-1248/chrome-linux-arm64/chrome`, e o ffmpeg 1011 que ele pede está lá. Não há flag de vídeo em 0.0.83: o vídeo vem das ferramentas `browser_start_video` e `browser_stop_video`, que exigem `--caps=devtools`. Ferramentas `core` ficam sempre ligadas, inclusive `browser_run_code_unsafe`, que roda JavaScript no servidor do Playwright, e nenhuma flag desliga uma ferramenta. As capacidades `storage` e `network` só entram por `--caps`.
- **Sonda sem login em 30/10** (script local, contra a página pública do DEV): o `storage-state` foi lido depois de o servidor subir; depois de `browser_close`, o contexto seguinte releu o arquivo novo; o vídeo gravou com `--caps=devtools`; print e vídeo foram para o `--output-dir`, fora do cwd.
- **Skill `playwright-cli`:** está na tag `v1.1.26`, mas o `install.sh` a copia com `copy_tree_if_missing` e ela não entra no manifesto `.covenant-flow/adapters.json`. O pin não a sobrescreve, então a cópia do crypto é do consumidor. `playwright-cli` e `playwright-cli-headed` não estão no PATH deste servidor.
- **Hook da conta:** o `PreToolUse` do Claude casa `Bash|Edit|Write|MultiEdit|NotebookEdit|Agent|mcp__ccd_.*`. Ferramenta `mcp__playwright-qa__*` não passa pelo shim.
- **Repositório `oalansilva/crypto` é público.** Comentário de issue e o que ele aponta por link aberto ficam públicos. Qualquer conta pode comentar num issue.
- **Código do produto fora de `product_globs`:** `backend/app` importa `src.engine.backtester`, `src.report.metrics` e `src.data.incremental_loader`. `frontend/public/**`, `frontend/index.html` e `frontend/package.json` também ficam de fora.
- **Ordem real:** `POST /api/monitor/spot-market-orders` e `POST`/`DELETE /api/monitor/spot-stop-order` usam a chave da Binance salva no usuário, e `BINANCE_BASE_URL` cai em `https://api.binance.com` por padrão (`backend/app/services/binance_spot_orders.py`). **Não verificado** se o seu usuário no DEV tem chave salva nem o valor dessa variável no DEV: não li `.env` nem banco.
- **Drive:** `gog drive share --to user --email` compartilha com uma conta, e `gog drive permissions` lista quem tem acesso.
- **Board em 30/10:** nenhum card em `Done`, nenhum em `Homologado`. #600, #614 e #728 estão em `Aprovação de Design`.

## Goals / Non-Goals

**Goals:**

- Todo card com código de produto é testado no DEV antes do `Done`, como uma pessoa de QA faria.
- Um FAIL segura o card fora do `Done` até a correção entrar no DEV e o critério passar.
- Card sem nenhum critério aprovado não chega ao `Done` sem decisão do Alan.
- A senha não passa pelo modelo, e dados da conta do Alan não vão para o comentário público.
- O relatório diz o que passou, o que falhou e o que não deu para testar, com motivo.

**Non-Goals:**

- O que o issue lista em "Não entra".
- Registrar o navegador em Cursor, Codex, Grok, OpenCode ou dsh.
- Medir guarda no executor.
- Tirar do agente a capacidade de ler o cofre: o nível é cooperativo (D3).

## Decisions

### D1. Quando o teste roda: T14 em duas fases, na mesma aresta

**A contradição.** O issue quer o teste com o código no DEV, antes do `Done`. Hoje a T14 faz merge, restart e move num passo só, e o código só chega ao DEV depois do merge. Depois do `Done` não há volta, salvo a T18 do Alan.

| Alternativa | Custo | Fere o issue? |
|---|---|---|
| **A. T14 em duas fases na mesma aresta (escolhida).** 1ª chamada integra e reinicia, card fica em `QA`. 2ª chamada, depois do relatório, move para `Done`. | Muda guarda e ações da T14, motor e testes. Não mexe no `PIN` do executor nem no board. `QA` passa a ter dois momentos, que só o comentário distingue. Um FAIL deixa o defeito no `develop` até a correção. | Não. |
| **B. Aresta ou coluna nova** (por exemplo "Teste no DEV"). | Tudo de A, mais evento novo na FSM, opção nova no Project e em `board.status_options`, e `PIN` novo no `crypto-portao` antes do primeiro uso (PR aprovado por você). Ganho: dá para ver a etapa no board. | Não. |
| **C. Subir a branch do card num ambiente de teste antes do merge.** Precedente: backend transitório do #1160 (`:8014`, rota no Caddy). | Por card: backend, frontend, workers e banco separados (migração da branch no banco do DEV pode quebrar o DEV). Edição do Caddy com sudo. Mais serviços numa máquina que já roda DEV e PROD. Ganho: `develop` limpa. | Sim: o issue diz `dev.criptofarol.com.br`, "roda quando o card entra no DEV" e "a correção entrar no DEV". Backtest e worker de verdade ficariam de fora, ou custariam o ambiente inteiro. |
| **D. Testar depois da T14, com o card em `Done`.** | Quase nada no motor. | Sim, nos dois pontos: "antes do Done" e "FAIL deixa o card fora do Done". O agente não tem aresta de saída do `Done`, e dar uma a ele enfraquece a T18. |

**Por que A e não B:** entrega o mesmo comportamento sem coluna, sem mexer no board e sem passo seu no executor. O motor já tolera o estado "fechado e ainda em `QA`" (o recibo do `closeout_done`). O custo é a etapa não aparecer como coluna; o comentário da fase 1 cobre isso. Se você preferir ver no board, B continua possível depois, sem refazer o resto (Perguntas).

**Como fica, com `qa_dev.enabled: true` no overlay:**

1. **Fase 1** (`integrar_develop`, `checks_green`): pega a trava do teste, faz `squash`, `sync_dev_source` e `restart`, grava o recibo, comenta "Integrado no DEV; teste em andamento" e devolve `reject` com `reason=qa_dev_pendente`. Status continua `QA`.
2. O pai roda o teste (D5) e posta o relatório.
3. **Fase 2** (`integrar_develop` de novo): com o recibo, lê o último relatório válido.

| Último relatório | Resultado da fase 2 |
|---|---|
| `PASS`, `NAO_TESTADO` ou `NADA_PARA_TESTAR` | `comment_done` e move para `Done` |
| `FAIL` | `reject` com `reason=qa_dev_fail`; o pai para e pergunta a você (abaixo) |
| `INCONCLUSIVO`, sem liberação sua | `reject` com `reason=qa_dev_inconclusivo`; o pai para e mostra as saídas (D9) |
| `INCONCLUSIVO`, com `/qa-dev-liberar <run>` seu | `comment_done`, dizendo que você liberou, e move para `Done` |
| Nenhum, ou de código anterior ao integrado | `reject` com `reason=qa_dev_pendente` |

Com `qa_dev` ausente ou `enabled: false`, a T14 é a de hoje. Assim os outros consumidores do `covenant-flow` e o período até o piloto não mudam.

**`qa_dev_ok`** lê o marcador `<!-- covenant-flow:qa-dev veredito=<V> sha=<SHA testado> run=<id> -->` no último comentário do card cujo autor seja `qa_dev.autor_relatorio`. Comentário de qualquer outra conta é ignorado: o repo é público, e um comentário HTML invisível de terceiro não pode decidir a guarda. O commit do recibo tem de ser ancestral de `SHA`, para relatório de versão antiga não valer. O issue fica como fonte de verdade: outra sessão consegue continuar. A liberação é a linha exata `/qa-dev-liberar <run>`, do mesmo autor, depois do relatório e com o `run` dele. É guarda cooperativa, como `checks_green`: agente e Alan usam o mesmo login no `gh`, então o agente poderia forjar o comentário, e a skill proíbe.

**Pausa antes da T13.** Depois da T13 não há reteste sem diff: o PR já está integrado, a branch é renomeada, e a volta exige Apply, Code Review e PR novo. No ensaio, dois FAIL eram leitura do agente, então o caso não é raro. Por isso o pai não chama `falha_codigo` no turno do `qa_dev_fail`. Ele mostra os critérios em FAIL e para, sem prazo; o card fica em `QA`, e a trava já foi solta.

- **Você confirma o defeito:** o pai chama T13.
- **Você discorda:** `qa_dev.py plan --reteste-de <run> --leitura "<sua leitura>"` refaz só os critérios em FAIL, com a sua leitura escrita no plano, e gera relatório e marcador novos. Nada é integrado, e o Status não muda. O relatório registra a contestação e a leitura usada.

Sua resposta no chat só dispara um teste ou uma chamada que o agente já faria. Não é evento seu e não cria portão.

**Volta depois de FAIL:** T13, depois o mesmo caminho do pós-T18: branch nova a partir do `develop`, com o nome exato do change (a antiga, já integrada, é renomeada), Apply, Code Review, `QA` e T14 de novo. O reteste roda os critérios em FAIL e os que o diff da correção tocar; os demais aparecem como "PASS no run `<id>`".

**Um teste por vez:** um `./restart` no meio de um teste gera falso FAIL, e dois testes disputariam a mesma conta. A trava é um arquivo em `~/.local/state/covenant-flow/qa-dev/lock` (card, run, início), criado de forma atômica. Dois pontos a pegam: a fase 1 da T14 e `qa_dev.py plan`, ao iniciar ou reiniciar o teste. Sem o segundo, um teste retomado depois do vencimento correria sem proteção contra o `./restart` de outro card. Trava do mesmo card é renovada; vencida ou ausente é tomada; de outro card devolve `reason=qa_dev_ocupado`, e o teste espera. Ela é solta ao postar o relatório, na falha de ferramenta (D9) e na falha da própria fase 1, para que "senha recusada" não prenda os outros cards. Vence em `teto_total_min` + 15 min, para sessão morta não prender o fluxo.

**Defeito de outro card no DEV.** Depois do FAIL de um card, o código dele continua no DEV, e o teste seguinte pode tropeçar nele. `report` registra em `~/.local/state/covenant-flow/qa-dev/fail-abertos.json` o card, os critérios em FAIL e os arquivos do PR, e o registro sai quando um relatório novo do card vem sem FAIL ou quando o Status vivo dele é `Cancelado`. `plan` entrega essa lista ao filho. Sintoma ligado a ela vira NÃO TESTADO com motivo `defeito de #<card>: <critério>`, nunca FAIL. Assim, um card não vai para a T13 por defeito alheio.

### D2. Onde cada peça mora

**Genérico nasce no `covenant-flow`**, num worktree `/srv/apps/dev/covenant-flow-worktrees/card-1144-qa-exploratorio-dev` criado a partir da tag `v1.1.26`, com tag nova ao fim. O crypto recebe pelo pin.

| Peça | Caminho no `covenant-flow` |
|---|---|
| Lei da T14, guarda, página de QA | `.cursor/process-fsm.yaml` |
| Duas fases, trava, medida da guarda | `scripts/process-fsm/t14.py`, `process_event.py`, `fsm.py` |
| Plano, trava, junção do relatório, veredito, marcador | `scripts/process-fsm/qa_dev.py` (novo) |
| Papel `qa-dev: execucao` | `.cursor/model-policy.yaml` |
| Contrato do agente | `.cursor/skills/qa-dev/SKILL.md` (novo) e pontes `.agents/skills/`, `.claude/skills/` |
| Runbook | `.cursor/skills/covenant-flow/SKILL.md`, seção "QA closeout" |
| Leitura da chave `qa_dev` | `scripts/process-fsm/overlay.py` |

**O que é do crypto fica no crypto:**

| Peça | Caminho no `crypto` |
|---|---|
| Pin e configuração | `.covenant-flow/overlay.yaml` (`pin`, `qa_dev`) |
| Login fora do agente, varredura | `scripts/qa/dev_session.py` |
| Envio de prints e vídeo ao Drive | `scripts/qa/publish_evidence.py` |
| Trava de ordem real e de ação administrativa | `scripts/qa/bloqueia-ordens.js` |
| Registro do navegador | `scripts/qa/setup-dev.sh` |
| Recusa de branch sem a chave ligada | passo no `qa-gate`, `.github/workflows/ci.yml` |
| Regra escrita | `docs/crypto-overlay.md` |
| Correção da skill | `.agents/skills/playwright-cli/SKILL.md` |

Chave no overlay:

```yaml
qa_dev:
  enabled: false
  autor_relatorio: oalansilva
  session_cmd: scripts/qa/dev_session.py
  scan_cmd: scripts/qa/dev_session.py --scan
  evidence_cmd: scripts/qa/publish_evidence.py
  espera_max_min: 20
  teto_total_min: 120
  telas_regressao: [/monitor, /favorites, /combo/discovery, /combo/select]
  caminhos_sem_produto:
    - openspec/**
    - docs/**
    - tests/**
    - frontend/tests/**
    - frontend/public/prototypes/**
    - scripts/process-fsm/**
    - scripts/qa/**
    - .agents/**
    - .claude/**
    - .codex/**
    - .covenant-flow/**
    - .cursor/**
    - .dsh/**
    - .github/**
    - .grok/**
    - .impeccable/**
    - .opencode/**
    - AGENTS.md
    - CLAUDE.md
    - CONTRIBUTING.md
    - DESIGN.md
    - PRODUCT.md
    - README.md
    - rules.md
```

A URL vem de `environments.dev.url`, e os serviços de `environments.dev.services`. Os nomes dos segredos ficam só nos helpers.

**Skill `playwright-cli`:** o teste não a usa. Mesmo assim, ela manda usar um wrapper que não existe. A correção vai na cópia do crypto, sem risco de `adapter_divergent`, porque ela está fora do manifesto, e a mesma correção vai para o `covenant-flow`, para consumidor novo não herdar a regra errada. A ponte `.claude/skills/playwright-cli/SKILL.md` não muda.

### D3. A senha nunca passa pelo modelo

Digitar a senha por `browser_type` ou `browser_fill_form` põe o valor no argumento da ferramenta e, portanto, no transcript. Por isso o agente não faz login: ele recebe a sessão pronta.

1. O pai roda `scripts/qa/dev_session.py`. O agente só vê `sessao_ok admin=<sim|nao>`, a partir do `isAdmin` do login, ou um código de erro. 401 dá `senha_recusada`; 403 dá `conta_bloqueada`, que é outra causa e pede outra providência.
2. O helper carrega `~/.config/bws/access.env` dentro do próprio processo, como o `gog-bws` faz, e lê o segredo `CRIPTOFAROL_DEV_ALAN_PASSWORD`. O valor é a senha, e a nota do segredo é o e-mail de login.
3. Faz `POST /api/auth/login` com biblioteca padrão. A senha fica só na memória: nunca em argumento de processo, variável exportada, arquivo ou log.
4. Grava `~/.local/state/covenant-flow/qa-dev/storage-state.json` (modo 0600) com os três itens de `localStorage` para a origem do DEV. Recusa rodar se a origem não for `environments.dev.url`.
5. O navegador abre com `--isolated --storage-state`, e o app já entra logado.

**Prints e vídeo ficam limpos por construção:** a senha nunca entra no navegador, a tela de login não recebe valor, e o `POST /login` nem passa pela rede dele. Gravação de sessão e tracing ficam desligados: `--save-session` não entra no registro e `browser_start_tracing` é negada (D4), porque o trace guarda cabeçalhos. Os `page-*.yml` que o MCP grava no `--output-dir` ficam locais e nunca são publicados. O `storage-state.json` é apagado ao fim do run.

**O token é outra coisa.** O agente não precisa dele, mas conseguiria vê-lo: `browser_network_request` sem `part` mostra o cabeçalho `Authorization`. A skill manda usar `part=response-body` para investigar 4xx e 5xx, não ler `localStorage` e não pedir `browser_storage_state`. A capacidade `storage` fica desligada. A varredura do relatório recusa padrão de JWT.

**Sessão que cai:** se aparecer a tela de login no meio do run (logout testado, renovação vencida), o agente roda o helper de novo, chama `browser_close` e segue. A sonda confirmou a releitura. Não digita senha.

**Fora do teste:** trocar senha ou e-mail e apagar a conta ficam como NÃO TESTADO, porque deixariam o cofre errado. Card que mexe na tela de login: digitar credencial válida na tela fica NÃO TESTADO. Ações administrativas sobre usuários (criar, editar, suspender, reativar, banir, apagar) também ficam como NÃO TESTADO: não estão na sua autorização de 28/10, e suspender o próprio usuário faz o login devolver 403 e prende os cards em `QA`. A tela `/admin/users` pode ser lida.

**Nível: cooperativo.** O agente roda no mesmo usuário que lê o cofre e poderia chamar `bws` por conta própria. O desenho garante que ele não precisa da senha e que ela não aparece por acidente, mas não impede quem decidir buscá-la. O mesmo limite do #1135.

**Varredura, em todo run e no piloto.** `dev_session.py --scan <arquivos>` lê a senha dentro do próprio processo e devolve só `ausente` ou `PRESENTE: <arquivo>`, nunca o valor. Transcripts são JSONL, com aspas e barras escapadas, e valor em URL viria codificado, então busca literal não prova ausência. Ela procura cinco formas: literal, JSON, JSON dentro de JSON (resultado de ferramenta em transcript é string dentro de string), URL e URL com `+` no lugar de espaço. `--scan --publico` vale para o que sai no issue: acrescenta padrão de JWT e o e-mail de login, nas mesmas formas. O e-mail fica fora da varredura de transcripts, onde aparece legitimamente. `--scan --self-test` semeia em arquivos temporários uma senha sintética, com aspas, barra invertida, barra, `%`, `+`, espaço e acento, em cada forma, e exige `PRESENTE` em todas. A senha real nunca vai para arquivo; o auto-teste só confere que ela foi lida do cofre sem vazio.

O relatório passa por `--scan --publico` antes de ser postado em todo run. No piloto, `--scan` cobre também os transcripts do pai e dos filhos, os `page-*.yml` e o journal do backend DEV, e `--scan --publico` cobre o comentário baixado do issue.

Alternativas descartadas: `--secrets` do MCP (a senha ficaria em arquivo dotenv em texto puro e continuaria a ser digitada no navegador); perfil persistente com login feito uma vez (você não está no servidor, e a sessão vence).

### D4. Ferramenta de navegador

Playwright MCP com versão fixa, registrado na conta do Claude Code por `scripts/qa/setup-dev.sh`, que **você** roda no terminal (D10). O agente escreve o script, mas não o executa: ele altera a lista de permissões da sua conta, e um agente não concede permissão a si mesmo.

```bash
claude mcp add --scope user playwright-qa -- \
  npx -y @playwright/mcp@0.0.83 --headless --isolated \
  --executable-path "$HOME/.cache/ms-playwright/chromium-1248/chrome-linux-arm64/chrome" \
  --storage-state "$HOME/.local/state/covenant-flow/qa-dev/storage-state.json" \
  --output-dir "$HOME/.local/state/covenant-flow/qa-dev/saida" \
  --init-script "$HOME/.config/covenant-flow/qa-dev/bloqueia-ordens.js" \
  --blocked-origins "https://criptofarol.com.br;https://www.criptofarol.com.br" \
  --caps=devtools --viewport-size 1440x900
```

- **`--executable-path`:** sem isso, o MCP procura o build 1247, ausente. Se o arquivo sumir, o `setup-dev.sh --check` acusa, e isso é falha de ferramenta (D9).
- **Registro na conta (`--scope user`):** vale em todo worktree. `.mcp.json` versionado exigiria aprovação por worktree e levaria um caminho desta máquina para o repo; escopo local teria de repetir por pasta. Custo: o servidor sobe em toda sessão do Claude Code nesta VM, mas ele só abre navegador no primeiro uso.
- **Permissão:** `setup-dev.sh` acrescenta `mcp__playwright-qa` a `permissions.allow` e `mcp__playwright-qa__browser_run_code_unsafe` e `mcp__playwright-qa__browser_start_tracing` a `permissions.deny`, em `~/.claude/settings.json`. Um servidor MCP novo só aparece em sessão nova.
- **`--blocked-origins`:** barra PROD por acidente. A documentação diz que isso não é fronteira de segurança; a regra forte continua "nunca PROD" na skill.
- **Celular:** `browser_resize` para 390×844, como no ensaio.
- **Nome de arquivo:** nunca passar `filename` em print ou vídeo. Com nome explícito, o arquivo vai para a raiz do worktree; sem nome, vai para o `--output-dir`.

**Outros clientes:** nesta entrega, o teste roda só no Claude Code. Se outro cliente levar um card à fase 1, a fase 2 devolve `qa_dev_pendente` com a mensagem "o teste roda no Claude Code: abra a sessão `#<id>`". Essa sessão continua do mesmo ponto, porque o recibo e o relatório não dependem do cliente. Registrar nos outros fica para outro card, se for preciso, com ensaio próprio.

### D5. Teste em blocos

Uma sessão só estoura o contexto: cada leitura de tela custa de 5 a 7 mil tokens. Cada bloco é um filho novo, com contexto limpo. Eles rodam em sequência, porque usam a mesma conta e o mesmo navegador.

- **Plano:** `qa_dev.py plan --card N` retoma a trava (D1) e extrai do `## Entra` a lista numerada (C1…Cn), para nenhum critério se perder. O plano leva também o protótipo aprovado, quando houver: `frontend/public/prototypes/card-<N>-*` em `develop`, com a URL dele no DEV, ou `prototipo: N/A`. Leva `admin`, da sessão, e a lista de FAIL abertos (D1).
- **Divisão:** o pai agrupa por tela ou fluxo, com até 3 critérios por bloco e teto de 60 chamadas de ferramenta. O número 3 vem do ensaio medido: 3 critérios, 32 turnos, 139 s com o modelo padrão. Critério que estoura o teto volta para o bloco seguinte.
- **Custo:** um card de 10 critérios dá 4 blocos. O piso é a estimativa linear do ensaio, cerca de US$ 3 e de 5 a 8 minutos. O teto, com 60 chamadas nos 4 blocos e US$ 0,029 e 4,3 s por turno, é de cerca de US$ 7 e 17 minutos. Os dois sem a volta rápida (D8) e antes das esperas.
- **Pasta do run:** `~/.local/state/covenant-flow/qa-dev/<card>/<run>/`, fora do git, com `plano.json`, `bloco-<n>.json` e `evidencia/`.
- **Passagem:** cada `bloco-<n>.json` traz resultado por critério, passos, evidências, achados de passagem e um campo `passagem`: o que foi criado no DEV (nomes e ids), o estado em que ficou e o que ainda desconfia. O filho seguinte lê o plano e só a passagem do bloco anterior. `passagem` e `passos` nunca entram no comentário.
- **Início e fim do bloco:** `browser_start_video` no início; `browser_stop_video`, mover arquivos para `evidencia/` e `browser_close` no fim. Um vídeo por bloco.
- **Junção:** `qa_dev.py report` confere a saúde do DEV e os serviços contínuos, junta os blocos, sem modelo, e calcula o veredito, nesta ordem: `FAIL` se houver FAIL; `NADA_PARA_TESTAR` se o caso for esse (D9); `INCONCLUSIVO` se nenhum critério tiver PASS ou se o DEV ou um serviço contínuo tiver falhado em qualquer checagem do run; `PASS` se todos passarem; `NAO_TESTADO` nos demais casos. Critério sem bloco vira NÃO TESTADO com motivo "sem bloco". O texto passa por `--scan --publico` (D3) e sai com `gh issue comment --body-file`. Se a varredura recusar, nada é postado, ela aponta o arquivo, e o pai reescreve o campo sem o valor e roda `report` de novo.

**Contrato do filho** (`qa-dev/SKILL.md`):

- **Roteiro:** os critérios do plano e o protótipo aprovado, quando houver. Caminho feliz e tentativas de quebrar por critério (campo vazio ou inválido, duplo clique, voltar, recarregar no meio, celular, esperar de verdade); console e 4xx/5xx em todo passo relevante.
- **Fim do bloco:** o ensaio mostrou que o Sonnet parou cedo por causa da frase "pare quando tiver evidência suficiente", então a skill não usa essa frase: o bloco acaba quando cada critério dele tem resultado.
- **Veredito por critério:** FAIL exige o critério citado e a evidência. Dúvida de interpretação vira NÃO TESTADO com motivo `interpretação: <dúvida>`, porque no ensaio dois FAIL eram leitura do agente, e quem decide isso é você.
- **Autorização e limite:** a skill transcreve a sua decisão de 28/10. Pode criar, alterar e apagar favoritos, estratégias, alertas e configurações, inclusive os que já existiam, sem devolver ao estado anterior. Vale só no DEV, nunca em PROD. Ordem real (D11) e ações sobre usuários (D3) estão fora dela.
- **Texto do resultado:** vai para um comentário público. Cita tela e comportamento ("o saldo some depois de recarregar"), nunca valores da conta: saldo, posição, quantidade, preço de entrada, nome, e-mail, chave. O valor fica no print, que vai para o Drive.
- **Limites do papel:** o filho não chama `process_event`, não muda Status, não homologa e não posta `/qa-dev-liberar`.

### D6. Modelo do agente

`qa-dev: execucao` entra em `roles` de `.cursor/model-policy.yaml`, ao lado de `apply-coluna` e `qa-gate`. Esse arquivo só diz a qual faixa o papel pertence, sem nenhum par de modelo. O par continua na escolha local, `~/.config/covenant-flow/model-selection.yaml`, que não ganha chave nova: o QA herda o que estiver em `execucao` no cliente. Cada bloco nasce com a captura de sempre, `resolve --role qa-dev`. O título do filho leva `qa-dev`, o que casa com o papel e com o classificador do destape (`\bqa\b`), sem needle novo. O relatório termina com a linha de runtime observado, igual à do grill.

### D7. Evidência: Drive, com links no comentário

| Opção | Por que não / por que sim |
|---|---|
| **Pasta no Drive do projeto (escolhida)** | O overlay já oferece: `gog-bws`, conta da Clara, pasta do projeto. Com o repo público, é a única opção em que a evidência não fica aberta a quem lê o issue. Os prints mostram sua conta no DEV. Custo: a imagem não aparece dentro do comentário; você clica no link. |
| Gist secreto, por `git push` | Link no issue público equivale a público. E mistura com os Gists do OpenSpec. |
| Asset de release | Público, e no meio do fluxo do `release-guard`. |
| Commit no repo | Público e permanente, e incha o histórico. |
| Servidor de protótipos | Público, e some se o DEV cair. |

`publish_evidence.py` usa `gog-bws`: cria `QA/<card>/<run>/` dentro da pasta do projeto (`1OE0D_nsb7BAMQ_ntZXUonnsfX9MtXhT9`), nunca solto na raiz, e envia `evidencia/`. Devolve os links que `qa_dev.py report` põe no comentário: um por print de achado, um por vídeo e o da pasta.

**Quem abre:** só a sua conta. O script compartilha a pasta do run com `gog drive share --to user --role reader`, para o e-mail que vem do segredo `CRIPTOFAROL_QA_DRIVE_READER`, assim ele não entra no repo público. Ele nunca usa `--to anyone` nem `--to domain` e, com `gog drive permissions`, recusa enviar se a pasta do run tiver acesso `anyone` ou `domain`, inclusive herdado da pasta do projeto. Nesse caso, a evidência fica no servidor. Assim, o link no issue público não abre para mais ninguém.

**Não verificado:** se a pasta do projeto tem hoje algum acesso aberto (confere no piloto) e o tamanho do vídeo (`size` 1280×720, `fps` 5, a medir no piloto). Se o envio falhar, o relatório sai mesmo assim, dizendo que a evidência ficou no servidor e onde; isso não prende o card.

### D8. Regressão: sim, uma volta rápida

Depois dos blocos de critério, um último bloco visita as quatro telas de `telas_regressao` no desktop: carrega, lê a tela, confere console e 4xx/5xx, tira um print. `/combo/discovery` e `/combo/select` são `requireAdmin`: com `admin=nao` na sessão, ficam como NÃO TESTADO na seção da volta rápida, com motivo "usuário sem admin no DEV".

**Custo estimado**, a partir do ensaio com o modelo padrão (US$ 0,93 em 32 turnos, ou US$ 0,03 por turno; 139 s, ou 4,3 s por turno): 3 turnos por tela, 12 turnos, cerca de US$ 0,35 e 1 minuto. São 12% sobre o piso de US$ 3 e 5% sobre o teto de US$ 7 do card de 10 critérios (D5). Veio de uma rodada só e é linear; o piloto mede.

Vale a pena porque é o tipo de quebra que nenhum critério do card cobre, e o custo é pequeno. Os achados vão para uma seção à parte e não entram no veredito: o card não é preso por algo fora dos critérios dele. Não roda em `NADA_PARA_TESTAR`.

### D9. Nada para testar, esperas e DEV fora do ar

**Nada para testar**, em dois passos:

1. Sem navegador: `qa_dev.py` lista os arquivos do PR do card e compara com `qa_dev.caminhos_sem_produto`, uma lista própria, que não mexe no `product_globs` do Guard. Só dá `NADA_PARA_TESTAR` se **todos** os arquivos casarem, e o relatório os cita. `product_globs` não serve aqui porque deixa de fora código do produto (ver Fatos). Arquivo fora da lista, ou falha ao listar o PR, segue para o passo 2: caminho novo conta como produto até entrar na lista. Não há login nem custo de modelo.
2. Com produto tocado mas sem tela óbvia (backend, worker): o filho parte dos endpoints e tarefas alterados, acha as telas que os consomem e testa por elas. Só se nada depender disso ele devolve `nada_para_testar` com o que examinou.

**Antes de abrir o navegador:** saúde do DEV (`<url>/api/health`) e `systemctl is-active` dos serviços contínuos de `environments.dev.services`. Os `oneshot`, como candle-writer e telegram-alert-scan, ficam de fora. Grava também o SHA do DEV, que vai para o marcador. `report` repete a checagem no fim do run. Falha antes do navegador gera relatório `INCONCLUSIVO`, sem login e sem custo de modelo.

**Esperar de verdade:** o agente aguarda na tela com `browser_wait_for`, até `espera_max_min` por espera (20 min) e `teto_total_min` por run (120 min). São números de partida, ainda não medidos, e o piloto ajusta.

**Três classes de impedimento**, para não prender card à toa nem aprovar sem teste:

| Situação | Resultado | Veredito e card |
|---|---|---|
| Espera estourou, com serviços de pé | NÃO TESTADO naquele critério, com último estado, id do job e estado do worker | `NAO_TESTADO` se houver PASS; segue |
| Teto total estourou, com serviços de pé | NÃO TESTADO nos restantes | `NAO_TESTADO` se houver PASS; segue |
| Nenhum critério com PASS, por qualquer motivo | NÃO TESTADO, com motivo | `INCONCLUSIVO`; fica em `QA` |
| DEV fora do ar depois de 3 tentativas em 5 minutos | NÃO TESTADO nos critérios restantes, motivo "DEV fora do ar às `<hora>`" | `INCONCLUSIVO`; fica em `QA` |
| Serviço contínuo parado, no início, no meio ou no fim | NÃO TESTADO nos critérios que dependem dele | `INCONCLUSIVO`; fica em `QA` |
| Senha recusada, conta bloqueada, navegador não abre, cliente sem navegador | Sem relatório. Comentário dizendo o que falta. Trava solta. `qa_dev_pendente` | Fica em `QA` |

Só as duas primeiras linhas deixam passar critério não testado, e o relatório mostra quais. Um card não vai ao `Done` sem nenhum critério aprovado: a etapa obrigatória sumiria em silêncio. E serviço parado não é só problema do ambiente: o teste vem logo depois do `./restart` do card, e a fase 1 só confere `/api/health`, nenhum worker, então o próprio card pode ter derrubado o serviço. A última linha é a ferramenta do teste quebrada. Queda no meio do run: um bloco que parou por DEV fora do ar é repetido uma vez quando a saúde voltar.

**Saídas do `INCONCLUSIVO`,** escritas no comentário do relatório, para você escolher (Pergunta 5):

1. **Testar de novo:** você conserta o ambiente ou pede novo teste, e o pai roda outro run, sem diff.
2. **Devolver:** se o card derrubou o DEV ou o worker, o pai chama T13.
3. **Liberar:** você mesmo comenta no issue a linha exata `/qa-dev-liberar <run>`. Serve para critério que este teste não alcança, como Telegram. Não é evento nem portão novo, é uma entrada da guarda da T14, e a skill proíbe o agente de postá-la.

FAIL não tem liberação: o issue exige que o critério passe de novo.

### D10. Piloto

**Card:** o issue pede um card em `Done`, mas hoje não há nenhum. Regra: o primeiro card em `Done` com tela logada na hora do piloto. Se não houver, recomendo o **#1123** (`Pronto`, código no DEV): tem backtest e resultado de verdade, planilhas e tela logada, e nenhum critério depende de Telegram. O #1122 do ensaio teria boa parte como NÃO TESTADO, por causa do Telegram. Usar card em `Pronto` foge do texto do issue (Perguntas).

O piloto não usa a T14: roda `qa_dev.py` direto, posta o relatório no issue e não move nada.

**O que depende de você:**

1. No terminal, registrar o navegador, porque isso altera as permissões da sua conta:

```bash
bash /srv/apps/dev/criptofarol/crypto-worktrees/card-1144-qa-exploratorio-dev/scripts/qa/setup-dev.sh
```

```bash
bash /srv/apps/dev/criptofarol/crypto-worktrees/card-1144-qa-exploratorio-dev/scripts/qa/setup-dev.sh --check
```

   A saída esperada do `--check` é `ok`. Depois, abra sessão nova `#1144`, para o MCP aparecer.

2. No site do Bitwarden: Secrets Manager → projeto `Crypto` → New secret, duas vezes.
   - Name `CRIPTOFAROL_DEV_ALAN_PASSWORD`; Value a senha atual do DEV; Note o e-mail de login.
   - Name `CRIPTOFAROL_QA_DRIVE_READER`; Value o e-mail da conta Google em que você quer abrir a evidência.
3. No bash comum, para conferir sem ver o valor:

```bash
python3 /srv/apps/dev/criptofarol/crypto-worktrees/card-1144-qa-exploratorio-dev/scripts/qa/dev_session.py --check
```

   A saída esperada é `sessao_ok admin=sim` ou `sessao_ok admin=nao`. Isso responde também se o seu usuário é admin no DEV.
4. Depois do relatório, abrir os prints e o vídeo pelos links e confirmar que enxerga e que não há senha.

**Passa quando:** há relatório por critério com prints e vídeo acessíveis por você no issue do card; o comentário não traz valor da conta; a pasta do run dá acesso só à sua conta; a varredura dá `ausente` em todos os arquivos e o auto-teste dá `PRESENTE` em todas as formas; você abre o vídeo e confirma que não há senha; e a trava recusa as provas abaixo.

**Prova das travas, sem risco de ordem de verdade:** dois envios que o backend recusaria mesmo se a trava falhasse. `POST /api/monitor/spot-market-orders` com `preview_token` falso (é JWT assinado, e o erro seria `INVALID_PREVIEW`) e `POST /api/monitor/spot-stop-order` com `stop_price: 0` (o payload exige maior que zero, e o erro seria 422, antes de qualquer chamada à Binance). O esperado é 403 local e nada no log do backend DEV. Nenhuma prova usa prévia real nem fluxo válido de ordem.

**Depois do piloto:** `qa_dev.enabled: true` no último commit do card. A própria T14 do #1144 faz o primeiro ensaio vivo das duas fases: todos os arquivos do card caem em `caminhos_sem_produto`, então sai `NADA_PARA_TESTAR`.

### D11. Trava contra ordem real (não previsto no issue)

Sua autorização de 28/10 cita favoritos, estratégias, alertas e configurações. Ordem na Binance não está na lista e não tem volta. No DEV, esse caminho existe (ver Fatos), e um agente que "tenta quebrar" a tela de operar pode acioná-lo.

`bloqueia-ordens.js` entra por `--init-script`, antes do código da página, e recusa em `fetch` e `XMLHttpRequest`, com resposta 403 local, `POST` em `/api/monitor/spot-market-orders` (sem `/preview` nem `/eligibility`) e `POST`/`DELETE` em `/api/monitor/spot-stop-order`. Recusa também `POST`, `PUT` e `DELETE` em `/api/admin/users`, pelo motivo de D3. A prévia continua testável. O envio de ordem fica NÃO TESTADO, com motivo. É barreira no navegador do teste, cooperativa, e não muda o produto.

`browser_run_code_unsafe` sairia desse alcance: pelo `page.request`, a requisição não passa por `fetch` nem por `XMLHttpRequest` da página. Por isso a ferramenta é negada em `permissions.deny` (D4) e proibida na skill.

## Risks / Trade-offs

- [Defeito fica no `develop` e no DEV entre o FAIL e a correção] → `develop -> main` fica proibido nesse intervalo: o release sai por `release-*` a partir de `main` só com os aprovados, ou por decisão sua. O `pre` do `release-guard` não consulta o board, então isso depende de quem monta o lote. O lote já escolhe por `Homologado`, e card em `QA` não entra. Ver "O que muda para você".
- [Agente marca FAIL errado e prende o card] → FAIL exige critério e evidência; dúvida vira NÃO TESTADO. Se ainda assim errar, a pausa antes da T13 deixa você contestar, com reteste sem diff (D1).
- [FAIL parado à espera da sua resposta] → O card fica em `QA`, sem prazo, e o defeito continua no DEV. A trava está solta, e os outros cards seguem, com o FAIL aberto na lista deles.
- [Card herda defeito de outro no DEV] → `plan` lista os FAIL abertos, e o sintoma ligado a eles vira NÃO TESTADO com motivo (D1). Depende de o filho ligar sintoma à lista; dúvida vira NÃO TESTADO, e você vê no relatório.
- [Agente aprova o que não testou] → Veredito por script, critério sem resultado vira NÃO TESTADO, e zero PASS vira `INCONCLUSIVO`, que não vai ao `Done` sem você.
- [`NAO_TESTADO` deixa passar critério não testado] → Só com pelo menos um PASS e serviços de pé, sempre com motivo. Ferramenta quebrada não vira NÃO TESTADO (D9).
- [Marcador forjado] → Comentário de terceiro é ignorado (D1). O próprio agente ainda conseguiria forjar, porque usa o mesmo login no `gh`: nível cooperativo.
- [Dado da conta vai para o comentário público] → A skill proíbe valores no texto, e `--scan --publico` recusa senha, JWT e e-mail de login. Saldo e posição não têm padrão que a varredura reconheça; aí a defesa é a skill, e `passagem` e `passos` nunca entram no comentário.
- [Trava do teste segura T14 de outro card] → Espera visível (`qa_dev_ocupado`), com vencimento. Custo: o outro card espera alguns minutos, mais as esperas de backtest e worker do teste em curso.
- [Branch antiga fura o teste] → O motor antigo não enxerga `qa_dev` e faria a T14 sem teste e sem trava. O `qa-gate` recusa a branch sem a chave ligada (Migration Plan).
- [Teste muda dados do DEV enquanto você usa] → Decisão sua de 28/10.
- [Playwright sobe de versão e o Chromium 1248 some do cache] → Versão fixa no registro; `setup-dev.sh --check`; ferramenta quebrada fica visível (D9).
- [Custo por card] → De US$ 3,35 a cerca de US$ 7,35 a preço de tabela, com piso de uma rodada só e teto pelo limite dos blocos, antes das esperas. O piloto mede; a divisão em blocos e a escolha de quando ler a tela são os ajustes.
- [Backtest ou worker demora mais que o teto] → NÃO TESTADO com o último estado; o piloto ajusta os números.
- [Vídeo grande no Drive da Clara] → `fps` baixo; medir no piloto. Limpeza da pasta fica fora deste card.

## Migration Plan

A ordem garante que o fluxo não muda até o piloto passar.

1. **Motor no `covenant-flow`:** worktree a partir de `v1.1.26`, com T14 em duas fases atrás de `qa_dev.enabled`, papel, skill e `qa_dev.py`. Tag nova.
2. **Pin no crypto:** comparar antes a cópia do crypto com a tag, porque o pin apaga o que só existe no consumidor. `install.sh --pin <tag> --target <worktree>`. A sessão trava de propósito (adapter novo sem revisão).
3. **Alan, no terminal:** `install.sh --account` e `cf_shim.py trust --record`, depois sessão nova `#1144`.
4. **Consumidor:** `scripts/qa/`, chave `qa_dev` com `enabled: false`, overlay doc, skill `playwright-cli` e o passo no `qa-gate`.
5. **Alan, no terminal:** `setup-dev.sh`, `setup-dev.sh --check` e sessão nova (D10).
6. **Alan:** cadastra os dois segredos e roda `dev_session.py --check` (D10).
7. **Piloto** (D10). Se falhar, corrigir no card; a chave continua desligada.
8. **Ligar:** conferir no board que nenhum outro card está em `QA`; se houver, ele fecha a T14 antes. Depois, `enabled: true` no último commit, com a T14 do próprio card como ensaio vivo.
9. **Branches abertas:** o pin e a chave chegam juntos ao `develop`, na integração do #1144. A partir daí, o `qa-gate` falha, com mensagem dizendo para atualizar a partir do `develop`, em todo PR cuja base tenha `qa_dev.enabled: true` e cujo head não tenha. Sem isso, #600, #614 e #728, se nascerem antes, fariam a T14 antiga, sem teste e sem trava, e poderiam reiniciar o DEV no meio de outro teste. A checagem fica no `qa-gate`, e não na T14, porque branch antiga roda o motor antigo: só o workflow vindo da base a alcança. O passo 8 cobre o único furo, um `qa-gate` já verde.

Volta: `enabled: false` num PR devolve a T14 de hoje, sem tocar no motor, e o passo do `qa-gate` deixa de exigir a chave.

## Detalhes de Apply

- Como a segunda guarda fica no yaml: hoje `_guard_holds` lê um nome só por linha. Definir ali como a T14 declara `checks_green` e `qa_dev_ok`. O `.cursor/process-fsm.yaml` tem de deixar as duas visíveis.
- `comment_done` escreve o recibo hoje. Separar: o recibo sai da fase 1, e `comment_done` lê o `commit` do recibo, porque a fase 2 é outro processo.
- `Write` em `QA`: o filho grava só fora do repo. Conferir se a Guard aceita `Bash` nessa pasta.
- Local dos testes de `scripts/qa/` e a linha no CI: o job de `scripts/process-fsm` não os alcança.
- Ajuste de `--snapshot-mode none` se o piloto mostrar contexto apertado. A resposta de cada ação traz a tela inteira, e esse é o maior gasto de tokens.
- Tamanho do comentário: o GitHub limita a 65.536 caracteres. Relatório grande resume a passagem de cada critério e leva o texto integral para o Drive.

## Detalhes de Apply aceitos

P3 aceitos na crítica, para o Apply resolver:

- `environments.dev` não tem `oneshot_services`, só PROD; D9 precisa dessa lista.
- Duas specs conflitam quando o último marcador é `FAIL` de SHA antigo (`qa_dev_fail` ou `qa_dev_pendente`): conferir o SHA primeiro.
- `qa_dev_ocupado` falta na página Moore e na task 1.2.
- `_write_receipt` engole `OSError` e não grava sem `pr`, e o recibo é local ao worktree; sem ele, a fase 1 repete o `restart` e nunca chega à fase 2.
- `setup-dev.sh --check` deve comparar a cópia de `bloqueia-ordens.js` e rodar a cada run.
- A menção a Binance da D11 fica no consumidor, não na skill do `covenant-flow`.
- A task 5.1 gera commit novo depois do piloto, com reviewers de novo no SHA.

## Design Critique

- P1 — `NADA_PARA_TESTAR` deixava passar card de produto, porque `product_globs` não cobre `src/` nem parte do `frontend/`. Disposition: resolvido no rework com a lista `qa_dev.caminhos_sem_produto` (D9).
- P1 — `NAO_TESTADO` liberava `Done` com zero critério testado, ou com o próprio card derrubando o DEV. Disposition: resolvido no rework com o veredito `INCONCLUSIVO` e a Pergunta 5.
- P1 — O comentário público podia carregar dados da conta do Alan. Disposition: resolvido no rework; a skill proíbe valores da conta e a varredura pública recusa senha, JWT e e-mail de login (D5, D7).
- P2 — Treze achados: trava só na fase 1; branches anteriores ao pin; defeito herdado de outro card; efeito no release; FAIL contestado sem caminho; marcador forjável por terceiros; varredura da senha; acesso ao Drive; duas folgas da trava de ordem; `/admin/users`; dois itens de Entra sem contrato; custo; agente concedendo permissão a si mesmo. Disposition: todos resolvidos no rework.
- P3 — detalhe de Apply (aceito): os sete itens de "Detalhes de Apply aceitos".
- Sem achado: tokens `UI impact`/`live_route`/`surface` parseáveis, sem rota de catálogo e sem tela do produto mudando; T14 sem aresta, coluna, evento ou PIN novo; caminho de ordem real no DEV confirmado no código de rotas; fronteira com o `covenant-flow` respeitada em `tasks.md`; D11 e regressão cabem no escopo; nada de "Não entra" vazou.
- Não passou pelo crítico (nasceu no rework, o teto não abre segunda crítica): `/qa-dev-liberar <run>` como entrada da guarda da T14; o passo no `qa-gate` contra branch anterior ao pin; o segredo `CRIPTOFAROL_QA_DRIVE_READER`; a recusa de escrita em `/api/admin/users` em `bloqueia-ordens.js`; a negação de `browser_start_tracing`. O primeiro é decisão do Alan na Pergunta 5: funciona como aprovação dele por comentário, fora da lista de seis portões, e só é cooperativo, porque agente e Alan usam o mesmo login no `gh`.
- Teto: 1 autor + 1 crítico + 1 rework (sem-tela), fechado.
- Verdict: approve após rework.

## Perguntas para o Alan

1. **T14 em duas fases, sem coluna nova?** Recomendo sim (D1). A etapa não aparece como coluna no board; você a vê pelo comentário "teste em andamento". Se preferir uma coluna, custa uma opção nova no Project e um PR seu no `crypto-portao`.
2. **Piloto em card `Pronto`?** O issue pede `Done`, e hoje não há nenhum. Recomendo aceitar o #1123 se continuar sem card em `Done` quando o piloto estiver pronto.
3. **FAIL para e espera a sua resposta antes da T13?** Recomendo sim (D1), porque depois da T13 não há reteste sem diff. Custo: todo FAIL espera uma frase sua, sem prazo. A alternativa é T13 automática, mais rápida, em que um FAIL errado vira um ciclo inteiro de correção sem nada para corrigir.
4. **Trava de ordem real:** recomendo manter sempre ligada, mesmo que seu usuário no DEV não tenha chave da Binance. Se quiser que o agente teste o envio de verdade, isso precisa de testnet, que seria outro card.
5. **Card com zero PASS, ou com DEV ou serviço parado depois da própria integração, fica em `QA` para você decidir?** Recomendo sim, com o veredito `INCONCLUSIVO` e as três saídas de D9: testar de novo, devolver ou liberar por `/qa-dev-liberar <run>`. Custo: esses cards param até você olhar, inclusive os que só têm critério inalcançável, como Telegram. A alternativa é deixar seguir para `Done` como `NAO_TESTADO`, o que deixa passar card sem nenhum critério aprovado.
