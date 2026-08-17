# Design: seleção sem rolagem na Discovery

## Status do gate

- Change: `card-469-selection-redesign`
- Card de origem: `#469` (mesmo card da Discovery — decisão de Alan: o redesign pertence ao tema do card, sem issue separada).
- Status observado no packet: `Design` para esta nova change; o card original está em Done técnico/homologação.
- **UI impact: affected** — o configurador de `/combo/discovery` muda a interação e a composição visual usadas para selecionar 30 templates e 126 símbolos; shell e superfícies operacionais adjacentes permanecem.
- Aprovação humana: **aprovada por Alan em 2026-08-15** ("aprovado"), registrada abaixo na seção "Aprovação de Alan".

## Problema

A seleção atual apresenta opções de Templates e Símbolos dentro do fluxo vertical do formulário. Em escala real, 30 × 126, o usuário alterna busca, páginas e uma sequência de itens que domina a altura do rascunho. A interface faz a pessoa navegar pelo catálogo em vez de montar um escopo, desloca timeframes/direção/preflight para longe e transmite a sensação descrita por Alan: “uma rolagem”.

## Usuário e contexto

Administrador do beta fechado preparando uma varredura swing. Ele conhece tickers e estratégias, frequentemente procura um item específico, mas também precisa explorar por famílias e executar ações em lote sem perder a contagem nem o impacto no preflight. O modo é `Operate`, desktop-first e completo no mobile.

## Hipótese

Se o formulário mostrar apenas um resumo persistente e mover a edição para um workbench de foco único — busca instantânea, categorias, uma página curta de resultados, adição explícita e “todos + exceções” — o usuário alcançará qualquer item sem rolar uma lista longa, reduzirá erros de seleção e retornará ao preflight com o escopo ainda compreensível.

## Resultado esperado

- O rascunho ocupa altura estável independentemente de o catálogo ter 30, 126 ou mais itens.
- Qualquer opção é alcançável por busca, filtro ou paginação sem scroll vertical do catálogo.
- Desktop mostra até 6 resultados; mobile, até 4.
- Adicionar/remover atualiza estado e contagem imediatamente.
- `Selecionar todos` representa o universo inteiro; remoções viram exceções, evitando 126 cliques.
- `Aplicar` recalcula o preflight; `Cancelar` e Escape descartam a edição e restauram foco.
- Histórico, preflight lateral, sweep ativo, leaderboard e regras de limite não mudam.

## Base visual e fidelidade

- Base funcional/visual: protótipo aprovado `card-469-varredura-backtest`, rota atual `DiscoveryPage.tsx` e shell autenticado de Combo.
- Preservados: sidebar 224 px, header 80 px, grid principal + rail de 330 px, dark canvas, cards, hairlines, breadcrumb, título, histórico, preflight, sweep ativo e leaderboard.
- Tokens: canvas `#0b0e11`, superfícies `#181a20`/`#1e2329`/`#2b3139`, CTA `#fcd535`, foco `#3b82f6`, texto secundário `#eaecef`, muted forte `#929aa5`, raios 4–12 px, escala de 4 px, Inter e números tabulares IBM Plex Sans.
- `DESIGN.md` permaneceu read-only. Nenhum código de produção foi editado.
- Julgamento de pixels/screenshots não foi realizado nesta sessão; a fidelidade foi verificada por estrutura, tokens e asserts de DOM/computed style, sem interpretar imagens.

## Alternativas consideradas

1. **Grid denso sempre aberto:** reduz altura por item, mas continua exigindo varredura/rolagem e compete com o preflight.
2. **Combobox simples multiselect:** ótimo para busca conhecida, fraco para explorar famílias, revisar muitos selecionados e escolher tudo com exceções.
3. **Dois painéis permanentes com lista + selecionados:** melhora revisão, mas mantém uma área rolável como centro da tarefa.
4. **Workbench transacional paginado (escolhido):** mantém o rascunho compacto, oferece foco protegido, limita o conjunto visível, permite busca direta, exploração categorizada e seleção em lote sem rolagem.

## Decisões

### 1. Resumos compactos substituem catálogos abertos

Templates e Símbolos viram cards-resumo com contagem, até três chips representativos e `Editar`. A altura do formulário não cresce com o catálogo; Timeframes, Direção, Período e Ranking permanecem no mesmo bloco e o rail de preflight não muda.

### 2. Um workbench, duas abas

Um dialog concentra a decisão de catálogo. As abas mantêm as contagens `n/30` e `n/126`; o usuário pode configurar os dois e aplicar uma única transação. O modal é apropriado porque protege uma edição provisória que precisa de aplicar/cancelar e focus trap.

### 3. Busca é o caminho rápido; categorias e páginas são o caminho exploratório

Busca instantânea encontra nome amigável, código ou ticker. Sem query, um filtro de categoria e páginas de 6/4 itens tornam todo o catálogo navegável. Paginação troca o conjunto no mesmo espaço e mantém `scrollTop=0`.

### 4. A ação primária é adicionar, não marcar uma parede de checkboxes

Cada resultado usa `Adicionar`; quando selecionado, a mesma ação vira `Remover` (ou `Excluir` no modo catálogo inteiro). O estado usa `aria-pressed`, contagens e live region. Isso torna a intenção explícita e reduz ruído visual.

### 5. Catálogo inteiro usa exceções

`Selecionar todos` muda para modo universo. Em vez de materializar 126 chips, o resumo mostra total e número de exceções. Remover um item cria uma exclusão explícita; `Limpar` retorna ao modo manual vazio.

### 6. Edição é transacional

O workbench opera sobre uma cópia. `Aplicar seleção` exige ao menos um item em cada eixo, grava os arrays e recalcula o preflight; `Cancelar`, backdrop ou Escape descartam alterações. Foco retorna ao gatilho.

### 7. “Sem rolagem” vale para a tarefa de seleção

O objetivo não é remover a rolagem natural da página longa da Discovery. É eliminar a necessidade de rolar um catálogo para alcançar opções. O dialog bloqueia o body, usa viewport fixa sem overflow vertical e mantém busca, resultados, paginação e ações simultaneamente acessíveis.

## Riscos e mitigação

| Risco | Severidade | Mitigação/decisão |
| --- | --- | --- |
| Selecionar todo o catálogo excede 1.000 combinações | P2 | Preflight existente permanece autoritativo, recalcula após aplicar e bloqueia start; implementação pode antecipar a projeção sem duplicar regra server-side. |
| Categoria artificial diverge da taxonomia real | P2 | Protótipo usa famílias representativas; produção deve consumir metadados do catálogo/API e oferecer `Todas`. |
| Usuário mobile quer revisar muitos selecionados | P2 | Contagem permanece visível; remoção ocorre pela busca/resultado para preservar o requisito sem scroll. Validar se dois itens recentes devem aparecer numa rodada futura. |
| Modo “todos + exceções” ser confundido com seleção manual | P2 | Copy explícita “Catálogo inteiro · N exceções”, ação muda para `Excluir` e `Limpar` volta ao modo manual. |
| Modal perder foco ou permitir interação no fundo | P1 técnico | `aria-modal`, focus trap, Escape e restauração de foco foram implementados e assertados no protótipo; produção deve também neutralizar background conforme o componente modal do app. |
| Critics independentes não disponíveis neste spawn | P1 de gate | Manter `Status=Design` e `BLOCKED` até dois contexts read-only `openai/gpt-5.6-sol` serem observados. |

## Prototype

- URL local validada: `http://127.0.0.1:4173/prototypes/card-469-selection-redesign/`
- URL canônica esperada após publicação pela sessão principal: `https://dev.criptofarol.com.br/prototypes/card-469-selection-redesign/`
- Caminho: `frontend/public/prototypes/card-469-selection-redesign/index.html`
- SHA-256 validado: `42fabbd3a1010349aa535c4b99a3fcf6c13cee72b13037ab114335f658da2abe`
- Viewports: desktop `1440×900`; mobile `390×844`.
- Estados/fluxos: default, abrir por Templates/Símbolos, abas, busca com/sem resultado, categoria, paginação, add/remove, selecionar todos, exceção, limpar, aplicar, cancelar, Escape, contagens e preflight recalculado.
- Delta: somente seleção de catálogos; demais superfícies são preservadas como contexto da Discovery.

## Impeccable Brief

- **Job/audiência:** administrador monta rapidamente o universo de uma varredura extensa; modo `Operate`.
- **Outcome/prova:** alcançar qualquer um dos 30/126 itens sem scroll de catálogo, manter contagem correta e aplicar um escopo que o preflight reconhece.
- **Direção:** workbench denso e sóbrio sobre o shell atual; busca como acelerador, páginas como exploração, seleção por adição e universo com exceções.
- **Escopo:** refatorar só Templates/Símbolos; não mudar shell, lifecycle, histórico, preflight, ranking ou promoção.
- **Estados/ranges:** 0/1/poucos/todos, busca vazia/sem resultado, páginas, exceções, apply/cancel, desktop/mobile, teclado e draft futuro congelado.
- **Restrições:** 30 templates, 126 símbolos, sem scroll vertical na tarefa de seleção, targets ≥44 px, focus trap, live regions, dark tokens canônicos, `DESIGN.md` read-only.
- **Assunções substituídas pelo packet:** a solicitação já fixou problema, público, superfície, escala, fidelidade e critério “sem rolagem”; não foi necessária nova entrevista de Shape.

## Impeccable Critique

⚠️ DEGRADED: single-context (a ferramenta Task/subagent não está exposta neste spawn; Assessment A/B independentes não puderam ser criados).

### Assessment A — revisão de produto/UX/a11y

- Contexto: passagem read-only sequencial no contexto autor; não independente.
- Modelo do autor observado no runtime: `openai/gpt-5.6-sol`, reasoning effort `high`.
- Modelo de um critic separado: **não observável**, pois nenhum spawn foi possível.
- Especificidade: proposta usa a escala real 30/126, preflight e shell da Discovery; não é um multiselect genérico isolado.
- Forças: altura estável do rascunho; dois caminhos claros (busca/exploração); universo com exceções; apply/cancel; preflight preservado.
- Carga cognitiva: uma decisão por dialog, duas abas, no máximo 6/4 opções; seleção e contagem permanecem no mesmo contexto.
- Personas: Alex ganha busca, Enter e lote; Sam recebe semântica/foco/live region; Casey recebe 4 opções e ações sempre no viewport.

| Heurística | Score | Evidência/limite |
| --- | ---: | --- |
| Visibilidade do status | 4/4 | Contagens nas abas/cards, `aria-pressed`, live region e preflight. |
| Compatibilidade com o domínio | 4/4 | Templates, tickers, categorias e escopo de varredura. |
| Controle e liberdade | 4/4 | Remove, limpa, cancelar, backdrop e Escape. |
| Consistência | 4/4 | Tokens, cards, botões e shell atuais. |
| Prevenção de erro | 3/4 | Eixo vazio não aplica; excesso é bloqueado pelo preflight após aplicar. |
| Reconhecimento vs memória | 3/4 | Desktop mostra selecionados; mobile prioriza contagem e busca para caber sem scroll. |
| Flexibilidade/eficiência | 4/4 | Busca, Enter, categorias, páginas, lote e exceções. |
| Estética/minimalismo | 4/4 | Catálogo sai do formulário e o conjunto visível é limitado. |
| Recuperação de erro | 3/4 | Empty state e cancel preservam estado; mensagem visual de eixo vazio precisa do componente final. |
| Ajuda/documentação | 3/4 | Copy contextual e atalho no footer; não há ajuda extensa necessária. |
| **Total** | **36/40** | Estruturalmente excelente; independência do assessment continua bloqueante. |

### Assessment A — revalidação final (spawn independente)

- Contexto: spawn read-only separado via Task, `design-planner`, modelo observado `openai/gpt-5.6-sol`.
- Veredito da primeira revalidação: **FAIL** com 5 P1s (exceções ilimitadas, alertdialog sem isolamento, foco pós-aplicar, apply só aba ativa, busca perdendo foco, digest desatualizado).
- Após targeted fixes: **FAIL residual** com 1 P1 (fallback de foco sempre para `#edit-templates` ao aplicar pela aba Símbolos).
- Após correção do fallback por eixo: **PASS**.

### Assessment B — revalidação final (spawn independente)

- Contexto: spawn read-only separado via Task (contexto distinto do A), `design-planner`, modelo observado `openai/gpt-5.6-sol`.
- Veredito da primeira revalidação: **FAIL** com 5 P1s convergentes.
- Após targeted fixes: **PASS** — "Os 5 P1s estão resolvidos; não identifiquei novo P0/P1. Resumos compactos e workbench transacional resolvem convincentemente a rolagem longa."

### Findings consolidados

| Severidade | Finding | Disposição |
| --- | --- | --- |
| P1 | Exceções nominais sem limite podiam crescer a altura do resumo | **Corrigido**: review limitado a 8 chips + "+N na contagem"; resumo do shell com 3 chips + "+N"; detail com contagem de exceções. |
| P1 | Confirmação de descarte sem isolamento de foco | **Corrigido**: `role=alertdialog` movido para fora do picker; `#selection-picker.inert` durante exibição; foco inicial em "Continuar editando"; focus trap Tab. |
| P1 | Foco não restaurado após Aplicar | **Corrigido**: trigger capturado antes do apply; refocus no novo `#edit-<eixo>` após re-render (inclui fallback por eixo). |
| P1 | Apply validava apenas a aba ativa | **Corrigido**: bloqueia se QUALQUER eixo estiver `loading/stale/frozen/error`. |
| P1 | Busca perdia foco a cada tecla | **Corrigido**: foco e caret restaurados após render quando o input estava focado. |
| P2 | Projeção usa multiplicador fixo ×4 | Aceito: projeção informativa; servidor permanece autoritativo. |
| P2 | Proposal/spec descreviam descarte direto | Reconciliado: Cancelar/Escape pedem confirmação quando a edição está suja. |

## Impeccable Audit

| Dimensão | Score | Evidência |
| --- | ---: | --- |
| Acessibilidade | 4/4 | Dialog nomeado, tabs, labels, `aria-pressed`, live regions, focus trap/restore, Escape/Enter e targets 44 × 44 assertados. |
| Performance | 4/4 | Uma página de 6/4 opções no DOM; busca local instantânea; sem imagens pesadas/animações. |
| Responsividade | 4/4 | Dialog e regiões sem overflow vertical em `1440×900` e `390×844`; ações sempre alcançáveis. |
| Theming | 4/4 | Tokens do `DESIGN.md`, dark theme e amarelo reservado à ação primária. |
| Integridade | 4/4 | Catálogos 30/126, detector `[]`, preflight recalculado e superfícies vizinhas preservadas. |
| **Total técnico** | **20/20** | Sem finding determinístico; gate processual A/B permanece fora deste score. |

### Targeted fixes e polish

- Antes do detector/gate final, o protótipo substituiu o glyph móvel por SVG do mesmo sistema de ícones.
- A composição limita resultados a 6/4, mantém footer fixo, usa busca direta e paginação sem alterar `scrollTop`.
- Copy foi destilada para `Adicionar`, `Remover`, `Excluir`, `Selecionar todos`, `Limpar`, `Aplicar seleção` e `Cancelar`.
- Nenhum ornamento, gradiente, nova cor de marca ou card decorativo foi introduzido.

## Impeccable Trace

1. **Context:** `context.mjs` executado uma vez com target do protótipo; PRODUCT/DESIGN carregados; `DESIGN.md` read-only.
2. **Shape:** modo Operate; problema e limites definidos pelo packet; escolhida edição transacional paginada.
3. **Prototype:** shell da Discovery preservado e apenas seleção substituída pelo workbench.
4. **Critique:** Assessment A e B executados como spawns read-only separados (Task, `design-planner`, `openai/gpt-5.6-sol`), com três rodadas de revalidação até PASS em ambos.
5. **Audit:** cinco dimensões avaliadas; detector final retornou `[]`.
6. **Targeted fixes:** exceções limitadas, alertdialog isolado, foco por eixo, apply cross-aba, busca com caret, ícone móvel normalizado.
7. **Polish:** hierarquia, densidade, selected state, empty state, responsividade e tokens reconciliados.
8. **Browser gate:** versão final digest `349b6d70…`, 8/8 asserts de fixes + suíte de shell/estados verdes, 0 console errors, 0 page errors.

Metadados:

- Autor: `design-planner`, runtime declarado `openai/gpt-5.6-sol`, reasoning effort `high`.
- Assessment A: spawn read-only separado, `design-planner`, igualdade de modelo observada; PASS na revalidação final.
- Assessment B: spawn read-only separado (contexto distinto), `design-planner`, igualdade de modelo observada; PASS na revalidação final.
- Skill: `design-critic` + `impeccable` + `playwright-cli` carregadas.
- OpenSpec CLI: não executada, conforme proibição explícita do packet (`ff/new` e comandos OpenSpec fora do escopo).
- Screenshots/pixel judgment: subagent `vision` (`opencode-go/qwen3.7-plus`) — PASS na versão final desktop e mobile.
- Digest: `349b6d70d98e08da08ea2ec00c1a7c5e0df5fa02d9b9de6461ccd25b95963eea`.

## Prototype Validation

- Comando de servidor: `npm --prefix frontend run dev -- --host 127.0.0.1 --port 4173`.
- URL: `http://127.0.0.1:4173/prototypes/card-469-selection-redesign/`.
- Browser: Chromium real headless via `@playwright/test` com `--no-sandbox`.
- Viewports: desktop `1440×900`; mobile `390×844`.
- Resultado final: **8/8 asserts de fixes + suíte anterior, 0 falhas, 0 `console.error`, 0 `pageerror`**.
- Versão validada: SHA-256 `349b6d70d98e08da08ea2ec00c1a7c5e0df5fa02d9b9de6461ccd25b95963eea`.

### Asserts críticos

- shell desktop/mobile e estado padrão com picker fechado;
- catálogos exatos de 30 templates e 126 símbolos;
- 6 opções desktop e 4 mobile;
- picker, workbench e resultados sem overflow vertical; body bloqueado durante edição;
- todos os controles visíveis do picker com pelo menos 44 × 44 px;
- focus trap, Escape e retorno de foco ao gatilho;
- busca alcança o último template (`breakout_retest`) e o símbolo `ZRX/USDT` sem scroll;
- paginação alcança página 2 preservando `scrollTop=0`;
- adicionar/remover atualiza `4/30`, `5/126` e retorna às contagens anteriores;
- selecionar todos produz `126/126`; excluir ZRX produz `125/126`;
- limpar + adicionar volta ao modo manual;
- aplicar atualiza o resumo e recalcula preflight para 12; cancelar descarta edição provisória;
- empty search visível no mobile;
- console/page errors: zero.

### Asserts de regressão dos fixes (rodada final)

- busca preserva foco e caret durante digitação;
- exceções limitadas: 9 exceções mostram `+1 exceções na contagem`; resumo do shell mostra `Catálogo inteiro · N exceções`;
- descarte: `alertdialog` com foco inicial em "Continuar editando" e foco contido no Tab;
- aplicar com eixos vazios exibe erro visível e foca o notice;
- aplicar pela aba Símbolos restaura foco em `#edit-symbols`; pela aba Templates em `#edit-templates`.

Qualquer alteração posterior no HTML/CSS/JS invalida digest e browser gate.

## Design Critique

### Síntese

A proposta resolve a fricção central sem redesenhar a Discovery: o catálogo deixa de definir a altura do formulário, cada decisão mostra no máximo 6/4 opções, busca e paginação alcançam qualquer item sem rolagem e o caso de uso em lote vira "todos + exceções". O protótipo está funcional, o gate de navegador está verde e os dois assessments independentes aprovaram a versão final.

### Aprovação formal

- Assessment A (spawn read-only, `openai/gpt-5.6-sol`): **PASS** após correção do fallback de foco por eixo.
- Assessment B (spawn read-only, `openai/gpt-5.6-sol`): **PASS** — "Os 5 P1s estão resolvidos; não identifiquei novo P0/P1."
- Julgamento de pixels (`vision`, qwen3.7-plus): **PASS** em desktop e mobile.

**Design Agent verdict: PASS**

## Aprovação de Alan

- Alan aprovou a proposta em 2026-08-15 (chat): "aprovado".
- Aprovação registrada também neste artefato e no card/issue correspondente da change.
- Próximo passo após o arraste `Aprovação de Design -> Pronto para Dev`: implementar conforme tasks.md.

## Resolução dos achados (BLOCKED → PASS)

1. Rodada 1: veredito `BLOCKED` por A/B não executáveis no spawn autor (sem tool Task). Sessão principal executou A/B como spawns independentes `design-planner` (`openai/gpt-5.6-sol`).
2. Rodada 2: A e B retornaram `FAIL` com 5 P1s convergentes (exceções ilimitadas, alertdialog, foco pós-aplicar, apply cross-aba, busca/caret, digest).
3. Targeted fixes aplicados no protótipo e validados com 5 asserts de regressão + suíte completa (8/8 verdes).
4. Rodada 3: A `FAIL` residual (fallback de foco por eixo), B `PASS`. Fallback corrigido e validado com assert dedicado (`#edit-symbols`).
5. Rodada 4 (final): A **PASS**, B **PASS**, vision **PASS**. Digest atualizado `349b6d70…`.
6. Alan decide exclusivamente `Aprovação de Design -> Pronto para Dev`; a sessão principal move no máximo `Design -> Aprovação de Design`.

## Handoff

- Decisão-chave: resumos compactos + workbench transacional paginado + busca + universo com exceções.
- Findings: todos os P1s resolvidos; P2s aceitos (projeção informativa e copy de revisão mobile).
- Protótipo: `https://dev.criptofarol.com.br/prototypes/card-469-selection-redesign/` após publicação; local validado no caminho acima.
- Evidência: detector `[]`; Playwright 8/8 + suíte anterior; erros zero; digest `349b6d70…`; vision PASS; assessments A/B PASS.
- Próximo passo: publicar o protótipo em DEV e mover `Design -> Aprovação de Design` para revisão de Alan.
