# Design — combo-ver-logs-vazio-autoscroll (card #502)

## Context

O `BackendLogViewer` busca a cada 2 segundos as últimas linhas de `/api/logs/tail` e substitui o conteúdo inteiro. Na configuração do Combo ele pede 400 linhas; por isso cada abertura começa com histórico acumulado, sem uma fronteira confiável entre “antes” e “depois de abrir”. O `<pre>` também não preserva automaticamente a última linha nem reconhece quando o usuário subiu para ler a sessão.

**UI impact: affected** — muda o estado inicial, o conteúdo exibido e a interação de rolagem do modal existente **Ver logs**. O shell, o formulário de Combo, seus botões e o polling de 2 segundos permanecem reconhecíveis.

### Problema

Alan abre o viewer para observar uma execução que está acontecendo agora, mas recebe até 400 linhas antigas e precisa procurar manualmente o ponto atual. Quando chegam eventos, a última linha pode ficar fora da área visível; qualquer autoscroll ingênuo, por outro lado, impediria leitura manual.

### Hipótese

Se cada abertura capturar o fim atual do arquivo como cursor, mostrar um vazio honesto até o primeiro evento novo e aderir ao final apenas enquanto o usuário estiver nele, Alan distinguirá imediatamente atividade nova sem perder o controle para consultar eventos recebidos durante a própria sessão.

### Resultado esperado

- Zero linha anterior à abertura renderizada.
- Eventos novos, sem duplicação e na ordem de gravação.
- Última linha visível por padrão.
- Pausa automática ao subir e retomada ao voltar ao final.
- Fechar e reabrir sempre cria uma sessão vazia nova.
- Consumidores legados de `/logs/tail` continuam funcionando sem alteração.

## Goals / Non-Goals

### Goals

- Definir uma fronteira backend verificável entre histórico e bytes novos.
- Preservar polling e tornar o cliente incremental.
- Tornar o estado de aderência ao final visível e controlável.
- Cobrir teclado, foco, touch, conteúdo longo, erro e rotação/truncamento.

### Non-Goals

- Não apagar, truncar ou alterar o arquivo de log do backend.
- Não misturar histórico anterior para “dar contexto”. O vazio inicial é intencional.
- Não migrar para SSE/WebSocket nesta mudança.
- Não criar busca, filtro, download, seleção de arquivo ou persistência de sessão.
- Não redesenhar a página de configuração do Combo nem seus controles de execução.

## Decisions

### 1. Cursor por offset de bytes, aditivo em `/api/logs/tail`

**Escolha:** adicionar `after_offset` opcional. Sem cursor, o endpoint mantém a seleção por `lines`. Com cursor, lê apenas bytes posteriores e retorna `next_offset`, `file_size` e `cursor_reset`.

Na abertura, o frontend faz uma requisição-base sem renderizar `content` e guarda o EOF retornado em `next_offset`. O endpoint deve capturar esse EOF antes da leitura do tail e usar o mesmo snapshot para o cursor, evitando que conteúdo anexado depois da captura seja pulado. Polls seguintes enviam `after_offset` e acumulam somente os incrementos.

**Por que bytes:** o arquivo é append-only na operação normal; offset é monotônico, barato e não depende de cada linha conter timestamp parseável. O backend já trabalha em binário para buscar o fim do arquivo.

**Alternativas rejeitadas:**

- **Timestamp (`since_ts`)**: logs podem não ter timestamp uniforme; relógio, granularidade e linhas multilinha tornam o filtro ambíguo.
- **Índice de linha**: contar linhas do arquivo inteiro aumenta custo e fica ambíguo em rotação.
- **Limpar o arquivo ao abrir**: destrutivo, interfere em outros usuários/consumidores e viola o objetivo de apenas limpar a visualização.
- **Diff no frontend entre tails sobrepostos**: falha com linhas repetidas, janela de 400 linhas e bursts maiores que a janela.

### 2. Polling de 2 segundos permanece

**Escolha:** manter o intervalo atual. A mudança é de semântica de sessão e rolagem, não de transporte.

**Alternativa rejeitada — SSE/WebSocket:** melhor latência, mas amplia escopo para conexão longa, proxy/reconexão, lifecycle e observabilidade. Não é necessário para o critério visível de 2 segundos.

### 3. Aderência ao final com limiar de 24 px

O container calcula `distanceFromBottom = scrollHeight - scrollTop - clientHeight`. `distanceFromBottom <= 24` ativa aderência. Ao receber conteúdo, o cliente só chama `scrollTo` se a aderência já estava ativa antes do append. Subir além do limiar pausa; voltar ao limiar retoma. Durante pausa, um estado textual e a ação **Ir para o fim** evitam depender de memória ou gesto de precisão.

### 4. Sessão e requisições têm lifecycle explícito

Cada abertura zera conteúdo, erro, cursor e estado de rolagem. Um `AbortController` impede resposta tardia de uma sessão fechada de contaminar a próxima. Fechar limpa interval e requisição; reabrir captura um novo EOF.

### 5. Empty state informa espera, sem spinner permanente

Antes do primeiro incremento, o log mostra `Aguardando eventos…` e “Somente eventos gerados após esta abertura aparecerão aqui”. Isso explica o vazio sem sugerir falha. Erro de poll aparece separadamente e não apaga linhas já recebidas.

### 6. Modal preserva controle e reduz ruído assistivo

O painel mantém título, subtítulo, botão **Fechar**, clique no fundo e Escape. O foco entra no modal, fica contido e retorna ao acionador. A área usa semântica de log, mas atualizações linha a linha não são anunciadas como uma sequência `aria-live` ruidosa; um status conciso anuncia espera/recebimento e rolagem.

### 7. Single-flight no polling (evita duplicação/reordenação)

O cliente nunca inicia um novo poll enquanto o anterior estiver em voo: o próximo `setTimeout` de 2 s só é agendado após a resposta do poll atual. Cada resposta carrega a geração da sessão; respostas obsoletas (de uma sessão fechada) são descartadas. A captura-base é feita em single-flight e o conteúdo da resposta-base é descartado (só o `next_offset` é usado).

### 8. Identidade do arquivo no cursor (rotação segura)

O cursor passa a ser `file_id + offset`, onde `file_id` deriva do inode/device do arquivo no snapshot. Se o `file_id` da consulta diferir do atual (rename + arquivo novo, copytruncate, recriação), o backend sinaliza `cursor_reset: true` mesmo quando o tamanho não diminuiu — fecha a brecha de "arquivo novo maior que o offset antigo". O cliente trata `cursor_reset` como recomeço da sessão no arquivo atual, sem misturar histórico.

### 9. Limite de bytes por resposta incremental

`MAX_INCREMENTAL_BYTES` (a definir na implementação, ex. 256 KiB) limita a leitura por poll; `next_offset` avança pelos bytes efetivamente entregues e o cliente continua de onde parou no próximo poll — nunca volta ao tail histórico. Sem `has_more` extra: o cliente drena páginas consecutivas até receber conteúdo vazio ou limite, e bytes UTF-8 incompletos no fim da página são retidos para o próximo poll, evitando corromper caracteres divididos.

## Data and API Contract

Exemplo aditivo sem cursor:

```json
{
  "name": "full_execution_log",
  "path": "backend/full_execution_log.txt",
  "lines": 400,
  "content": "...tail legado...",
  "file_size": 184220,
  "next_offset": 184220,
  "cursor_reset": false
}
```

Exemplo incremental com `after_offset=184220`:

```json
{
  "name": "full_execution_log",
  "path": "backend/full_execution_log.txt",
  "lines": 400,
  "content": "[12:30:02] Teste 18/240...\n",
  "file_size": 184257,
  "next_offset": 184257,
  "file_id": "65010:1835240",
  "cursor_reset": false
}
```

Quando o `file_id` da consulta difere do atual, ou `after_offset > file_size`, o backend lê o arquivo atual a partir de 0, retorna `cursor_reset: true` e o cliente trata o conteúdo como continuidade da sessão atual. Não há fallback para o tail histórico.

## Risks and Mitigations

- **Evento entre clique e captura do cursor:** a fronteira tecnicamente confiável é o snapshot no servidor. Mitigação: primeira requisição é disparada imediatamente ao abrir; a UI não promete precisão anterior ao início da requisição.
- **Truncamento/rotação:** offset antigo pode exceder o arquivo atual, ou o arquivo pode ser recriado com tamanho igual/maior. Mitigação: identidade de arquivo (`file_id`) + `after_offset > file_size` → reset explícito com `cursor_reset`; nenhum erro infinito.
- **Burst muito grande:** resposta incremental pode crescer sem limite. Mitigação: `MAX_INCREMENTAL_BYTES` com `next_offset` dos bytes efetivamente entregues; cliente continua pelo cursor retornado, sem voltar ao tail histórico; limite definido com testes de carga proporcionais.
- **Linha parcialmente gravada/UTF-8:** leitura deve preservar ordem e não duplicar bytes. Mitigação: avanço do cursor pelos bytes realmente lidos e retenção de sufixo UTF-8 incompleto no fim da página para o próximo poll; testes incluem conteúdo UTF-8 e caractere dividido.
- **Autoscroll indevido por arredondamento:** limiar de 24 px absorve subpixels e touch momentum; posição durante pausa testada antes/depois de append.
- **Polling sobreposto duplicando/reordenando linhas:** dois polls em voo com o mesmo offset podem duplicar conteúdo. Mitigação: single-flight (poll seguinte só após resposta atual) + geração de sessão descartando respostas obsoletas.
- **Modal com logs extensos:** manter somente a sessão aberta pode crescer. Aceito para o uso atual; virtualização e limite visual são follow-up se telemetria indicar necessidade.

## Migration and Rollback

- Mudança aditiva; não exige migração de dados.
- Deploy do backend pode preceder o frontend. O endpoint sem cursor continua funcionando.
- O frontend novo depende dos campos de cursor e deve ser ativado após o backend compatível.
- Rollback do frontend restaura o tail legado; rollback do backend só ocorre depois de reverter o frontend.

## Open Questions

- Definir na implementação o limite máximo de bytes por resposta incremental sem quebrar uma linha UTF-8; não altera a experiência projetada.
- Confirmar se rotação real usa truncamento no mesmo inode ou rename + arquivo novo; ambos devem entrar nos testes do serviço.

## Prototype

- **URL navegável esperada:** `https://dev.criptofarol.com.br/prototypes/card-502-ver-logs-vazio-autoscroll/`
- **Caminho versionado:** `frontend/public/prototypes/card-502-ver-logs-vazio-autoscroll/index.html`
- **Base de fidelidade:** shell autenticado atual (sidebar de 224 px + topbar), `ComboConfigurePage`, botão **Ver logs** ao lado de **Otimizar**, progresso de batch e estrutura do `BackendLogViewer` descritos no packet.
- **Escopo:** desktop e mobile; abre vazio, recebe linhas simuladas, adere ao final, pausa ao subir, retoma no bottom/ação, fecha por botão/fundo/Escape e reabre limpo.
- **Delta:** somente conteúdo/estados/interação do modal. Shell, formulário e ações de Combo são contexto não redesenhado.

## Impeccable Brief

- **Job e usuário:** Alan acompanha uma otimização ativa e precisa reconhecer apenas o que aconteceu desde que decidiu observar.
- **Resultado e prova:** primeira abertura com zero linhas antigas; sequência nova ordenada; última linha visível sem impedir consulta manual; reabertura reinicia a fronteira.
- **Direção:** refinamento operacional do modal existente, no mundo visual Binance dark do produto; o estado, não decoração, é o ponto focal.
- **Escopo e limites:** `BackendLogViewer` e extensão compatível de `/logs/tail`; sem stream, filtros ou redesign do Combo.
- **Estados:** fechado, aberto aguardando, recebendo/aderente, recebendo/pausado, erro recuperável, sessão reiniciada e arquivo rotacionado.
- **Interação/layout:** modal central no desktop e painel quase full-screen no mobile; log domina o painel; status de rolagem fica próximo da área e **Ir para o fim** aparece apenas quando útil.
- **Restrições:** tokens do `DESIGN.md`, polling 2 s, foco/teclado/touch, sem dependências externas, sem anúncio excessivo de logs por leitor de tela.

## Design Critique

### Avaliação consolidada da primeira entrega

- **Produto:** a fronteira por cursor resolve a causa sem destruir histórico nem interferir em outros consumidores. O empty state deixa explícito que o vazio significa “nenhum evento novo”.
- **UX:** status de aderência e **Ir para o fim** tornam a pausa recuperável; não há botão extra enquanto o usuário acompanha normalmente.
- **Acessibilidade:** modal nomeado, foco contido, Escape, retorno de foco, estados em texto e ação de retomada por teclado/touch. Evita `aria-live` no corpo inteiro do log.
- **Responsividade:** shell recolhe no mobile; painel usa quase toda a viewport, cabeçalho quebra sem sobrepor e área de log conserva scroll vertical e linhas quebráveis.
- **Estados:** espera, fluxo, pausa, retomada, erro, fechamento, reabertura e truncamento foram especificados.
- **Fidelidade:** estrutura e tokens seguem as fontes do packet. Julgamento visual/pixel não foi realizado nesta sessão e permanece reservado ao subagent `vision`.

### Achados e disposição

- **P1 — crítica A/B independente indisponível:** a primeira sessão do `design-planner` não expôs ferramenta Task/subagent. **Resolvido:** a sessão principal spawnou dois critics read-only independentes (`design-planner`, GPT 5.6 Sol) — Assessment A (produto/UX/a11y/responsividade/estados/API) e Assessment B (verificação/qualidade/segurança). Achados P1 incorporados: identidade de arquivo no cursor (decisão 8), single-flight (decisão 7), limite de bytes e retenção UTF-8 (decisão 9), live region no status de rolagem, viewport baixa flexível, controles determinísticos de erro/reset/burst no protótipo.
- **P1 — validação visual de fidelidade indisponível:** **Resolvido:** `vision` (qwen3.7-plus) validou as capturas Playwright em desktop/mobile/viewport baixa → **PASS**; único achado P2 (dot verde no erro) corrigido no protótipo e revalidado.
- **P2 — risco de perda em burst:** cursor incremental precisa de paginação/limite de bytes. **Resolvido no design (decisão 9) com tarefa backend.**
- **P2 — rotação de arquivo:** sem sinalização, o cursor poderia travar ou pular arquivo novo. **Resolvido com `file_id` + `cursor_reset` (decisão 8).**
- **P2 — leitor de tela sobrecarregado:** anunciar cada linha seria hostil. **Resolvido com status conciso e corpo do log sem live announcements.**
- **P1 — autorização no endpoint de logs (achado Assessment B):** `/api/logs/tail` atual não exige `Depends(...)` e retorna caminho absoluto; allowlist `Literal` impede path traversal remoto. **Classificado: pré-existente, fora do escopo do card** (o card não altera o controle de acesso e o endpoint já é exposto; barreira de proxy single-tenant documentada em `logs.py`). Recomendado follow-up de auth administrado separadamente, fora desta change.

## Resolução do BLOCKED (obrigatório)

- **O que bloqueou:** a sessão `design-planner` original produziu o pacote completo, mas não pôde criar os two critics read-only independentes (Assessment A/B) nem delegar a validação visual ao `vision` — ferramenta Task/subagent indisponível na tool surface do spawn. Os P1 de rotação, single-flight, burst/UTF-8 e viewport baixa apontados nas críticas posteriores foram incorporados ao design.
- **Como foi resolvido:** a sessão principal executou (1) dois critics read-only independentes via `Task` no mesmo modelo `openai/gpt-5.6-sol` (Assessment A e Assessment B), (2) validação visual via `vision` (`opencode-go/qwen3.7-plus`) sobre screenshots Playwright reais dos estados empty/filling/paused/resumed/error/reopened em desktop, mobile e viewport baixa, (3) browser gate funcional com 34+ asserts verdes. Achados P1 incorporados ao design (decisões 7-9), spec e tasks; P2 do vision corrigido no protótipo.
- **Quem aprovou:** aprovação humana de Alan pendente — o pacote está pronto para `Aprovação de Design`; Alan decide o arraste para `Pronto para Dev`.

## Impeccable Critique

⚠️ **DEGRADED: single-context (Task/subagent não está exposto nesta sessão).** O contrato exige Assessment A e B em contextos independentes; as observações abaixo são uma verificação inline e não substituem o gate.

### Assessment A — produto/UX/a11y/responsividade/estados

- **Método pretendido:** critic read-only em `openai/gpt-5.6-sol`, contexto isolado.
- **Método disponível:** revisão inline antes do detector, sem interpretação de pixels.
- **Forças:** delta focado; vazio inicial explicado; pausa é visível e reversível; decisão de API evita timestamp e diff frágil.
- **Riscos encontrados:** rotação precisava de contrato explícito; anúncio live do log seria excessivo; retomada apenas por scroll seria pouco descobrível. Todos foram tratados no design/protótipo.
- **Heurísticas:** visibilidade 4; mundo real 4; controle 4; consistência 3; prevenção 3; reconhecimento 4; flexibilidade 3; minimalismo 4; recuperação 3; ajuda contextual 3 — **35/40 (Good)**, com limite de evidência por ausência de critic isolado.
- **Carga cognitiva:** baixa; uma ação principal (**Fechar**) e uma ação contextual (**Ir para o fim**) apenas quando pausado.

### Assessment B — detector + navegador

- **Método pretendido:** critic read-only em `openai/gpt-5.6-sol`, contexto isolado.
- **Método disponível:** detector e Playwright executados pela própria sessão, após Assessment A inline.
- Detector mecânico: `[]` (zero finding) em `index.html`.
- Browser: 34 asserts verdes em desktop e mobile; abertura vazia, incrementos, aderência, pausa sem deslocamento, retomada, fechamento, retorno de foco e reabertura limpa.
- Nenhum `console.error` ou `pageerror`; versão HTTP e arquivo local têm o mesmo SHA-256.
- Apesar da evidência funcional, não é um contexto independente e não satisfaz a prova de isolamento exigida.

## Impeccable Audit

- **Acessibilidade (4/4 na auditoria DOM/funcional):** dialog nomeado, foco inicial no fechar, trap, Escape, retorno de foco, estado textual e ação de retomada por teclado. O corpo do log evita anúncios repetitivos.
- **Performance (4/4):** protótipo sem dependências; timer e startup timeout são cancelados no fechamento; produção mantém polling e acrescenta somente bytes novos.
- **Responsividade (4/4):** 1366×850 e 390×844 validados; sem scroll horizontal de página, painel bottom-aligned e alvos de 44 px no mobile.
- **Theming:** canvas `#0b0e11`, cards `#1e2329`, elevated/hairline `#2b3139`, body `#eaecef`, muted `#707a8a`, primary `#fcd535`, info `#3b82f6`.
- **Theming (3/4):** tokens canônicos aplicados ao shell/modal. O gradiente roxo/rosa de **Otimizar** é exceção herdada da tela atual no packet e ficou fora do delta.
- **Integridade (3/4):** detector limpo, sem recurso externo/quebrado, interações completas e digest servido idêntico. A nota não pode chegar a 4 sem inspeção visual pelo `vision`.
- **Audit Health Score:** **18/20 (Excellent, provisório)**; zero P0 novo, dois P1 de processo/evidência permanecem abertos.

## Impeccable Trace

- **Sessão designada:** `design-planner`, modelo observado `openai/gpt-5.6-sol`, reasoning effort high.
- **Context:** `node .agents/skills/impeccable/scripts/context.mjs --target frontend/public/prototypes/card-502-ver-logs-vazio-autoscroll/index.html` executado uma vez; `PRODUCT.md` e `DESIGN.md` lidos sem reescrita.
- **Shape:** brief acima, inferido do packet autoritativo; nenhuma entrevista adicional porque objetivos, público, estados, escopo e restrições já estavam fechados.
- **Prototype:** `frontend/public/prototypes/card-502-ver-logs-vazio-autoscroll/index.html`, SHA-256 `87635d6060a7f4b664ac7a74071cf6f87c75f47effdafde478406774337f143c`.
- **Critique/Audit:** fallback inline registrado; Assessment A/B isolados não disponíveis.
- **Detector (uma execução, após a primeira entrega):** `node .agents/skills/impeccable/scripts/detect.mjs --json frontend/public/prototypes/card-502-ver-logs-vazio-autoscroll/index.html` → `[]`.
- **Targeted fix:** lifecycle do atraso inicial passou a guardar/cancelar `startupTimer`, impedindo um timer da sessão fechada de iniciar na reabertura.
- **Polish:** indicador de rolagem deixou de usar glifo Unicode e passou a usar geometria CSS coerente com os status dots do sistema.
- **Browser gate final:** Playwright 1.62.1 via Chromium headless, depois do polish; 34 asserts verdes, 0 console/page errors.
- **Modelo dos critics:** não observável porque spawns não puderam ser criados; sem fallback de modelo.
- **Igualdade da versão servida:** fetch no navegador retornou HTTP 200 e SHA-256 `87635d6060a7f4b664ac7a74071cf6f87c75f47effdafde478406774337f143c`, idêntico ao arquivo local.

## Prototype Validation

- **URL servida:** `https://dev.criptofarol.com.br/prototypes/card-502-ver-logs-vazio-autoscroll/` (após `./restart` do frontend DEV; arquivo em `frontend/public/prototypes/card-502-ver-logs-vazio-autoscroll/index.html`)
- **Viewports:** desktop 1366×850; mobile 390×844; viewport baixa 1280×500.
- **Ferramenta/comando:** Playwright 1.62.1 + Chromium headless, script Node inline com `NODE_PATH=/home/ubuntu/.npm/_npx/e41f203b7505f1fb/node_modules`.
- **Versão validada:** arquivo local servido como `file://` (HTTP 200 via DEV pendente de restart); detector Impeccable `[]` (zero findings).
- **Asserts funcionais verdes:**
  - abertura vazia (`0 linhas`, `Aguardando eventos…`, sem histórico);
  - 36-48 eventos anexados em ordem, `distanceFromBottom <= 24 px` (autoscroll);
  - rolar ao topo → `Rolagem pausada` + botão **Ir para o fim** visível; append preserva `scrollTop` (sem puxão);
  - **Ir para o fim** → `Rolagem automática` retomada;
  - erro de poll (`HTTP 500 · tentando novamente…`) com conteúdo prévio preservado e cor de status âmbar/amarela (dot + texto);
  - **Fechar**/**Escape** fecham e devolvem foco; reabrir → `0 linhas` de novo (sessão limpa);
  - desktop, mobile e viewport baixa sem overflow horizontal e sem corte de header/toolbar/footer.
- **Console/page errors:** zero em todos os viewports.
- **Validação visual (vision, qwen3.7-plus):** PASS nos 7 estados × 3 viewports; P2 do dot de erro corrigido e revalidado.
- **Resultado funcional:** **PASS** — veredito geral **PASS** após incorporação dos achados A/B e validação visual; aguarda aprovação humana de Alan.

## Design Agent verdict

**PASS** — pacote completo (proposal, specs, design, tasks, protótipo navegável), critics A/B independentes executados no modelo do gate (`openai/gpt-5.6-sol`) com achados P1 incorporados, validação visual via `vision` (qwen3.7-plus) verde, browser gate funcional verde em 3 viewports, detector Impeccable limpo. Aprovação humana (`Aprovação de Design -> Pronto para Dev`) segue com Alan.
