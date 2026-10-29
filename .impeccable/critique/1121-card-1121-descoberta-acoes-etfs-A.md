`proveniência: Assessment A (design review produto/UX/a11y/fidelidade) → Opus 5.5 (claude-opus-5-5, effort high)` — captura `.cursor/tmp/claude-evidence/assessment-a-1121-a2.capture.json` (attempt `81596a8d-2c6c-4f0f-88b0-e4f7c80fa91a`, band `juizo`, role `assessment-a`, capture_sha256 `339d178582b88a23184047f87af0ef718cabd3e86894bb9aca79ac1ca58ea645`, arquivo sha256 `0d8b59dc81c1401c8a51ed569cd6b2b917efe3e4d09ade4b656c4327846ed693`). Birth: `.cursor/tmp/claude-evidence/81596a8d-2c6c-4f0f-88b0-e4f7c80fa91a.birth.json`.

# Assessment A: card 1121, change card-1121-descoberta-acoes-etfs

> Avaliador A isolado (produto, UX, acessibilidade e fidelidade do clone). Onda dupla com-tela. Não li o transcript do pai nem o snapshot do Assessment B. Não spawnei filho, não chamei `process_event`, não arrastei Status e não comentei no issue. Não editei `design.md`, OpenSpec, o protótipo, `backend/` nem `frontend/src/`. Única escrita: este arquivo.

## Metadata

- card: 1121, "Descobrir estratégias para ações e ETFs com amostras reproduzíveis"
- change: `card-1121-descoberta-acoes-etfs`
- cwd: `/srv/apps/dev/criptofarol/crypto-worktrees/card-1121-descoberta-acoes-etfs`
- branch / q_git: `card-1121-descoberta-acoes-etfs` @ `5bd1695f` (pacote untracked: só as duas pastas `??`)
- tupla: `bound_card=1121` · Status = Design (dado no prompt; não arrastado)
- data: 2026-10-26
- cliente: Claude Code (adapter cooperativo, sem modo Auto), superfície claude-desktop
- Issue: REST `gh api repos/oalansilva/crypto/issues/1121`. A fronteira é o body grelhado (Problema / História / Entra / Não entra), com as 4 decisões de Alan de 26/10/2026 dentro de Entra. Não reabri as decisões.
- sha256:
  - `design.md` `cbb94a72ebf03e5b28e3278bc656de4788d2171ef84d6c410510ecb6980f80c3`
  - `proposal.md` `a32c5d85…6548`
  - `tasks.md` `42f69c3a…28ed`
  - specs: `multiclass-discovery` `7111cc70…2d42`, `discovery-multiclass-ranking` `7c907691…23bc`, `discovery-promotion` `1ae5c22a…e86`, `crypto-only-mvp` `49aa1e3c…2b1`
- Ignore list: `.impeccable/critique/ignore.md` não existe.
- Ferramentas: Playwright Python com Chromium headless shell 1243 (arm64), `pt-BR`, tema escuro, 1440×900 e 390×844 (`isMobile`, toque), **na URL pública**. A skill `playwright-cli` não existe neste repo (`.cursor/skills/playwright-cli/` está ausente), então usei Playwright direto. Medi o contraste pela cor computada contra o fundo efetivo (compondo os ancestrais), sem axe-core. Scripts e PNGs de trabalho ficam em `/tmp/claude-1001/-srv-apps-dev-criptofarol-source/a6864850-8db3-4162-8fa9-5cbe144d5d69/scratchpad/c1121A/` (não versionados).

## Digest (disco == servido)

| Arquivo | sha256 disco | HTTP | servido |
|---|---|---|---|
| `index.html` (também a pasta `/`) | `46f32c0f17d787a13552235d75d15946a10fa79baa1f51b107f6d7a65e5204d2` | 200 | IDENTICAL |
| `live.css` | `876e5fe61e1b444bbf20e81ba5b05aeaf01577ef260b228df9a2eddcf0424b2a` | 200 | IDENTICAL |
| `delta.css` | `1e920760eda8c3c0ad2fdbc4f9eed10742c3d07ab6dd7e0a6fc7612a9964767d` | 200 | IDENTICAL |
| `delta.js` | `5e162462943c0f2ca3296c5129107d10327e2f874aa6a018a29b39aa72eaf904` | 200 | IDENTICAL |

O disco é igual ao servido. Na avaliação do autor, a URL pública ainda dava 404 (Risks, último item); agora responde 200, então o serviço foi reiniciado. `live.css` é igual, byte a byte, a `https://dev.criptofarol.com.br/assets/index-BKQOezYM.css`, a folha que `/combo/discovery` serve hoje. Nos fluxos clicados (2 larguras) não houve erro de console nem `pageerror`.

## Tokens parseáveis (rubrica 6, D4)

`design.md`, L1–L3, cada um em linha própria:

```
UI impact: affected
live_route: /combo/discovery
surface: existing
```

O bloco D4 em L5 é idêntico ao da skill. `design_clone_gate` (HEAD): `design_token_gap` = None; `parse_live_route` = `/combo/discovery`; `classify(index.html, /combo/discovery)` = PASS; `clone_gate_ok` = True. As regiões clonadas declaradas em §Context (AppNav, cabeçalho e abas, Montar, Acompanhando, Decidir, modal e fim da página) são as marcadas `COPIED`, com 38/38 pares; o delta fica só em `DELTA`, também 38/38. A rota é a página viva do catálogo, não uma rota emprestada. **ok.**

## Cobertura do body (rubrica 1)

| Item do Entra | Decisão / spec | Protótipo (visível) |
|---|---|---|
| Três classes na mesma varredura; cada ativo com classe, fonte, sessão, ajuste e moeda | d2, d3 · `multiclass-discovery` R1/R2 · `crypto-only-mvp` | "Pronto para iniciar", "Vão rodar 3 ativos: 1 cripto (USDT) · 1 ação · 1 ETF (USD)", nota do seletor nova. Os textos "a Descoberta vem depois", "rodam só com cripto" e "ações e ETFs fora" sumiram (grep = 0) |
| Mesma amostra, sem vazamento (70/30) | d4 · R3 | Comportamento sem tela. Visível: "Amostra 8b41d7e2 · guardada enquanto o favorito existir" no modal e "amostra até …" na linha (vivo) |
| Precisão diária visível; sem candles = estado explícito | d6, d7 · R4/R5 | Âmbar "Precisão diária · sem 15m de 2 jan. 2003 a 31 dez. 2025" nas Parciais, no Decidir, no modal e no Por ativo. No Preflight: "Precisão diária prevista em 1d". Período passado: "Sem candles prováveis em 4h", 2 linhas "Sem candles de 4h de NVDA/SPY…" sem rank e "6 processadas = 4 sucesso + … + 2 amostra insuficiente" |
| Teto de 1.000 recusa e pede para estreitar | d8 · R7 | "Bloqueado — veja o que falta", "2.433 combinações válidas passam do limite de 1.000: … (1 cripto · 2.431 ações · 1 ETF)", "Estreite a seleção … Nenhuma varredura foi criada.", `role=alert`, Iniciar `disabled` |
| Orçamento, progresso, cancelamento, retomada; falha não vira aprovada | d9 · R8 | "Coletando histórico · 1d · página 3 de 6"; "Pausado na coleta · … · retoma daqui" → Retomar; Cancelar → "Não rodou · varredura cancelada" e "1 sucesso + 2 ignoradas"; "tentativa 2 de 3" → "Falha: a Binance não respondeu ao histórico de SPY nas 3 tentativas", e SPY sai do ranking |
| Lista única com classe, moeda e convenções por linha + filtro por classe; USD ≠ USDT | d11 · `discovery-multiclass-ranking` | Cada linha mostra "NVDA · 1d · Long · Ação · USD", convenções e período efetivo. Filtro Classe "Todas (3) / Cripto (1) / Ações (1) / ETFs (1)"; Ações deixa o rank 2 e anuncia "1 de 3 candidatos". A nota diz "USD e USDT não se somam nem se convertem" |
| Candidato vira favorito como no lote; aceite depende do #1122 | d10 · `discovery-promotion` | Título "Promover a favorito", identidade completa e destino "Favoritos · sem nível de estrela … Monitor, Telegram e Revalidar: ainda não para ações e ETFs". Depois: "Favorito · sem estrela" e "Ver em Favoritos" (`/favorites`, 44 px). BTC continua "tier 3" |
| Viés de sobrevivência | d12 · R9 | Preflight e Decidir, em tom neutro, com a janela |
| Verificação | tasks 5.1–5.4 | Os três cenários do card estão no painel Demonstração (misto, NVDA em todo o histórico, teto) |

Não entra: não há execução de ordens nem família nova de estratégia. **Sem escopo furado.**

## Decisões de Alan (rubrica 2)

1. **Favorito com aceite dependente do #1122:** respeitada. Proposal (Impact), design d10 e Risks registram a dependência, e o modal diz o que ainda não vale. **ok.**
2. **Precisão diária com marca:** respeitada. A marca âmbar aparece com o trecho em 4 superfícies e é prevista no Preflight; a previsão nunca substitui a marca da execução. **ok.**
3. **Teto de 1.000 que recusa e pede para estreitar:** respeitada (antes de começar, servidor também recusa). **ok.**
4. **Lista única com classe, moeda, convenções e filtro por classe:** respeitada. O rank global sobrevive ao filtro e as moedas nunca aparecem juntas. **ok.**

## Estados (rubrica 3)

- **Carregando / em curso:** Na fila, Coletando histórico (série + página), Rodando · tempo, com uma linha viva só para a etapa em curso. ok.
- **Pausado / retomado:** "Varredura pausada", "Pausado na coleta · … · retoma daqui" e Retomar, que volta ao estado anterior. ok.
- **Cancelado:** a confirmação viva (`alertdialog`, foco em "Confirmar cancelamento"), "Varredura cancelada", "Não rodou · varredura cancelada" e o contador com ignoradas. O que já tinha resultado fica no Decidir. ok.
- **Erro:** "Varredura concluída com falhas", a linha "Falha: … nas 3 tentativas" com "Nenhum resultado…". ok no Acompanhando, mas ver P2-2 (o Decidir não mostra).
- **Amostra insuficiente:** está no Decidir e no detalhe do Por ativo. Ver P2-1 sobre o estado principal.
- **Vazio:** a seleção vazia e o rascunho são incumbentes vivos. O vazio novo (Classe com 0) aparece sem mensagem: ver P2-3.

## Fidelidade (rubrica 5)

- O canônico `index.html` clona `/combo/discovery`, com os três modos e o modal na mesma página, um por vez, como o React faz. Não há painel ANTES/DEPOIS nem grelha de N estados: o grep de "ANTES/DEPOIS/6 estados" só acha prosa como "antes de hoje" e "depois da coleta". O painel Demonstração fica no fim, no fluxo.
- `live.css` é o CSS vivo inteiro e confere com o bundle servido. O delta é local: chips de classe com as cores do `.ap-fact.cls-*` vivo e, fora isso, só os tokens do produto.
- Não fazer URL extra de `/favorites` está justificado (d1): o favorito usa as chaves `analysis_*` que Favoritos já renderiza desde o #1120, então ali não há copy nova. Concordo.
- A tabela do Decidir a 1440 é 1240 px num contêiner de 1175 px com `overflow-x:auto`, o que corta Promover/Excluir até rolar. **É incumbente:** sem os blocos DELTA a largura continua 1240 px, então o delta não causa isso. Fica registrado, sem achado do card.

## Acessibilidade (rubrica 4, medida)

- **Rolagem horizontal da página:** nenhuma a 1440 nem a 390 (`scrollWidth == clientWidth` em Montar, Acompanhando, Decidir e no modal). A 390 a tabela vira cartão, que é o comportamento vivo, e o Por ativo empilha.
- **Foco:** Iniciar leva a `#progress-heading`; o fim leva a `#leaderboard-title`. No modal, o foco abre em `#confirm-promotion`, o Tab fica preso em Fechar → Voltar → Promover, e Esc devolve o foco a `promote-RS-NVDA1121B2`. Depois de confirmar, o foco vai para o `span.promoted-state[tabindex=-1]`. Cancelar abre o `alertdialog` com foco no confirmar, e Continuar devolve o foco. As abas respondem às setas (ArrowLeft seleciona Acompanhando).
- **ARIA:** o modal tem `role=dialog`, `aria-modal=true`, `aria-labelledby=modal-title` ("Promover a favorito") e `aria-describedby`. Por ativo é `<section aria-labelledby>` + `<ol>` + `role=status aria-live=polite` só com a etapa em curso ("NVDA: coletando histórico · 1d · página 3 de 6"). O filtro anuncia "1 de 3 candidatos". O teto é `role=alert`. O filtro Classe tem `<label>`.
- **Contraste** (texto novo, menor razão por classe): chips Cripto 11,1 · Ação 8,8 · ETF 7,4; precisão intrabar 8,8 e diária 9,5; convenções e detalhe 5,6; Por ativo, Concluído 7,4 e precisão diária 9,5; sobrevivência 5,6–6,1; teto 6,9; nota de calendário 5,6. **Tudo ≥ 4,5:1.**
- **Estado só por cor:** não há. Cada estado tem ícone + texto, e a marca âmbar tem ícone e texto.
- **Alvos de toque:** Promover, Excluir, "Ver em Favoritos" e os botões do Por ativo/Pausar/Cancelar têm ≥ 44 px. Os `select` do Decidir medem 18 px de altura a 390, Classe incluído: é o reset `*` vivo que zera padding, um incumbente já listado em P3 pelo autor. Ver P2-5 (mecânico).

## Responsividade

A 390, o Por ativo vira cartão (ativo e classe; combinações; estado; detalhe) e o modal cabe sem rolagem lateral. O painel Demonstração quebra em linhas. A 1440, a tabela incumbente rola dentro do contêiner, como descrito acima.

## Heurísticas Nielsen (0–4), só neste snapshot

| # | Heurística | Nota | Nota curta |
|---|---|---|---|
| 1 | Visibilidade do estado | 3 | Por ativo com página da coleta e tentativas. O Decidir diz "em execução" numa varredura terminada (P2-4) |
| 2 | Linguagem do usuário | 4 | "Precisão diária", "Estreite a seleção", "sem nível de estrela" |
| 3 | Controle e liberdade | 4 | Pausar, Retomar, Cancelar com confirmação; promoção reversível |
| 4 | Consistência | 4 | Rótulos iguais aos de Favoritos e do #1120 |
| 5 | Prevenção de erro | 4 | Teto antes de começar; previsão de precisão e de sem candles |
| 6 | Reconhecer em vez de lembrar | 3 | Linha com classe, moeda e convenções. A falha some do Decidir (P2-2) |
| 7 | Flexibilidade | 3 | Filtro Classe + Símbolo + Timeframe |
| 8 | Estética e minimalismo | 3 | A linha do candidato ficou alta (6 linhas de bloco), aceitável |
| 9 | Recuperar de erros | 3 | Motivo da falha e do sem candles explícitos; o filtro vazio fica sem mensagem (P2-3) |
| 10 | Ajuda | 3 | Notas de calendário e de moeda |

## Design specificity / cognitive load

O bloco do candidato soma 4 linhas novas por linha, o que é denso mas legível: símbolo e classe primeiro, marca de precisão em seguida. O Preflight ganhou até 4 parágrafos (vão rodar, coleta, precisão e sobrevivência). A sobrevivência em tom neutro evita fadiga de alerta. O risco de carga está no Por ativo com centenas de ativos (P2-6).

## What's working

- As 4 decisões aparecem como texto concreto e testável, não como intenção.
- O caminho do card (BTC/USDT + NVDA + SPY → ranking → favorito) e os três cenários da Verificação podem ser clicados.
- Falha e amostra insuficiente nunca chegam a Promover; o contador soma certo nos 4 desfechos.
- O fato divergente do issue (período padrão de 15 dias, não "todo o histórico") foi conferido no código e declarado, sem mudar escopo.

## Findings

### P0: bloqueante (produto / escopo / contrato visível)

Nenhum.

### P1: deve corrigir antes de PASS

Nenhum.

### P2: residual visível, não bloqueia o teto 1+1+1

**Produto**

- **P2-1. O estado principal do Por ativo esconde a amostra insuficiente parcial.**
  - Onde: período passado, linhas NVDA e SPY (Acompanhando, `delta.js assetLine`; design d7).
  - Problema: o Estado diz "Concluído · precisão diária · 2 de 2 combinações", mas uma das duas (4h) é amostra insuficiente; isso só aparece na coluna Detalhe, que a 390 fica no fim do cartão.
  - Correção: com desfecho misto, o estado mostra o pior caso junto ("Concluído com 1 amostra insuficiente") ou separa as contagens ("1 concluída · 1 amostra insuficiente"). Registrar a regra em d7 e no spec "Per-asset state".
- **P2-2. A falha não aparece no Decidir.**
  - Onde: cenário "SPY: coleta falha" (Decidir; design d7 / Apply contract "falha fora do ranking").
  - Problema: o operador cai no Decidir automaticamente e vê "2 de 2 candidatos" e "ETFs (0)", sem nada dizendo que SPY falhou; só o Acompanhando mostra.
  - Correção: uma linha de nota no cabeçalho do Decidir ("1 ativo com falha, fora do ranking: SPY — ver Por ativo"), no mesmo tom da nota de sobrevivência.
- **P2-3. O filtro Classe com 0 resultados deixa a tabela vazia sem mensagem.**
  - Onde: Decidir, `#d21-class-filter`, opção "ETFs (0)".
  - Problema: a tela mostra só o cabeçalho da tabela e a paginação; "0 de 2 candidatos" é anunciado, mas não há texto visível de vazio.
  - Correção: desabilitar a opção com contagem 0, ou mostrar "Nenhum candidato de ETF nesta varredura" + "Limpar filtros". Pôr no spec "Class filter".
- **P2-6. Por ativo não tem limite visível para varreduras grandes.**
  - Onde: design d7, spec "Per-asset state".
  - Problema: o teto aceita até 1.000 ativos (1 template × 1 tempo), e o quadro lista todos.
  - Correção: como no #1120, "Mostrar mais 50", com o ativo em curso, as falhas e as amostras insuficientes no topo. Registrar em d7.

**Mecânico**

- **P2-4. O cabeçalho do Decidir diz "em execução" numa varredura terminada, cancelada ou com falha.**
  - Onde: `index.html`, Decidir, linha "Varredura #c1121mix · em execução · 3 classes…". O trecho é COPIED da captura feita durante a execução.
  - Correção: o protótipo segue o estado (`concluída` / `cancelada` / `concluída com falhas`), ou o design declara que o Apply usa o estado real.
- **P2-5. Os `select` do Decidir têm 18 px de altura a 390, Classe incluído.**
  - Onde: o reset `*` vivo (incumbente, já em P3 do autor).
  - Correção: como o Classe é DELTA, dar a ele `min-height:44px` no Apply, sem esperar o incumbente.
- **P2-7. O spec não traz estados que o design e o protótipo já mostram.**
  - Onde: `specs/multiclass-discovery` "Per-asset state while the sweep runs".
  - Problema: a lista de estados não tem "Não rodou · varredura cancelada" nem "Pausado na coleta · … · retoma daqui", e diz "Rodando" onde o design diz "Rodando · <tempo>".
  - Correção: alinhar a lista ao d7 para que o E2E (5.3) tenha a fonte certa.
- **P2-8. O Por ativo não tem os cabeçalhos de coluna que d7 promete.**
  - Onde: `#d21-asset-list` (d7 diz "colunas Ativo · Combinações · Estado · Detalhe").
  - Problema: a 1440 as colunas não têm cabeçalho visível nem `aria` de coluna.
  - Correção: uma linha de cabeçalho visual (ou `aria-label` por célula) a partir de 620 px; ou ajustar o texto de d7.

### P3: detalhe de Apply (aceito; não reabrir como P0/P1)

- Os itens da subseção "P3 aceitos" do autor, incluindo: formato de data misto ("2 de jan. de 2003" no modal × "2 jan. 2003" na linha), números de amostra, os 3 chips do cenário do teto, a estimativa "~81h" e o logo por caminho absoluto.
- `discovery-promotion`: o payload continua exigindo `tier: 3` e o servidor grava `tier` nulo para ação e ETF. A redação do requisito ("Any payload that supplies a tier other than 3 SHALL be rejected") está coerente com d10, mas é contraintuitiva; o Apply documenta no teste.
- O texto de "Precisam de coleta" e de "Precisão diária prevista" com centenas de ativos (truncar com "+N").
- A tabela incumbente do Decidir a 1440 rola dentro do contêiner (largura igual com e sem o delta).

## Persona red flags

- **Alan pesquisador, varredura de 300 ações:** o Por ativo fica longo (P2-6) e as falhas se perdem no Decidir (P2-2).
- **Leitor de tela:** a linha viva é boa. O filtro vazio só anuncia "0 de 2" (P2-3).
- **Celular a 390:** sem rolagem lateral; os selects são baixos (P2-5, incumbente).

## Questions to consider

- Com "Todo o histórico", BTC (desde 2017) e NVDA (desde 2003) disputam o mesmo ranking com janelas diferentes. O card pede uma lista só e o período efetivo por linha está visível, então isso não é achado. Um aviso "janelas diferentes por ativo" no cabeçalho ajudaria a ler o Calmar.
- O padrão de 15 dias faz o 1d de ação cair sempre em amostra insuficiente (10 velas). O autor declarou isso fora do escopo; o Preflight poderia prever "poucas velas" como já prevê "sem candles".

## Perguntas para Alan (rubrica 7)

- **Quando aparece o aviso de viés de sobrevivência?**
  - **A (recomendada; concordo com o autor):** em toda varredura. O "todos" e a seleção usam o catálogo de hoje, então qualquer janela no passado, mesmo 15 dias, pode não ter um ativo removido no meio dela. O tom neutro (cinza, ícone de histórico) evita fadiga de alerta.
  - **B:** só quando a janela termina antes de hoje (Personalizado no passado). O aviso fica mais raro, mas perde o caso comum (todo o histórico até hoje), que é exatamente onde o viés pesa mais.
  - Nota: o spec `multiclass-discovery` R9 já está escrito como A ("SHALL appear in every sweep"). Se Alan escolher B, o requisito e o d12 mudam juntos.

## Disposition (resumo)

- Tokens L1–L3 ok; o gate do clone passa; o clone é fiel (`live.css` igual ao bundle vivo); não há ANTES/DEPOIS.
- Os 9 itens do Entra têm tela, estado, texto e requisito. As 4 decisões de Alan foram respeitadas. Sem escopo furado nem item de Não entra.
- A11y medida: foco, ARIA, contraste ≥ 4,5 e 390 px sem rolagem horizontal; alvo de 44 px falha só nos selects, por causa do incumbente.
- P0 = 0 · P1 = 0 · P2 = 8 (4 produto, 4 mecânico) · P3 = aceitos.
- **Verdict: PASS.** Os P2 cabem no rework único da dupla, se o pai abrir um; senão ficam como residual registrado na seção de crítica do `design.md`.
