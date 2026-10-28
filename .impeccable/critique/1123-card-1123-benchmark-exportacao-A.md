`proveniência: Assessment A (design review produto/UX/a11y/fidelidade) → Opus 5.5 (claude-opus-5-5, effort high)` — captura `/tmp/claude-1001/-srv-apps-dev-criptofarol-source/9da083da-1d07-4a6e-9eb6-dddd4afcad74/scratchpad/cf-assess-a-1123.json` (attempt `8cf72f82-79aa-4d6f-9794-9cce22b57067`, band `juizo`, role `assessment-a`, capture_sha256 `57c472ae6c984c4b5bf0f93f735a2730e629c218ef683f38b7be1a7d5fa0bdbf`, arquivo sha256 `4a6c520969453065c2220ec8baca0be8098c49cfb61b956d59941ac38dc9ca2a`). Wave capture: o mesmo arquivo. Birth: `.cursor/tmp/claude-evidence/8cf72f82-79aa-4d6f-9794-9cce22b57067.birth.json`.

# Assessment A: card 1123, change card-1123-benchmark-exportacao

> Avaliador A isolado (produto, UX, acessibilidade e fidelidade do clone). Onda dupla com-tela. Não li o transcript do pai nem nada do Assessment B. Não spawnei filho, não chamei `process_event`, não arrastei Status e não comentei no issue. Não editei `design.md`, OpenSpec, o protótipo nem código. Única escrita no repo: este arquivo.

## Metadata

- card: 1123, "Comparar estratégias com benchmark escolhido e exportar resultados completos"
- change: `card-1123-benchmark-exportacao`
- cwd: `/srv/apps/dev/criptofarol/crypto-worktrees/card-1123-benchmark-exportacao`
- branch / q_git: `card-1123-benchmark-exportacao` @ `9b83d25e` (pacote untracked: change e protótipo `??`)
- tupla: `bound_card=1123` · Status = Design (dado no prompt; não arrastado)
- data: 2026-10-27
- cliente: Claude Code (adapter cooperativo, sem modo Auto)
- Issue: REST `gh api repos/oalansilva/crypto/issues/1123` e `/comments` ("card nítido; sem grill"; "grill-card: fronteira vazia…"). Briefing = body grelhado; as 4 decisões de Alan de 27/10 estão em Entra. Não as reabri.
- sha256:
  - `design.md` `9a6235f5ef0b841a0af758cfc06085da61f8e54833a78afb3056ca7a7917faaa`
  - `proposal.md` `56690071…62b0` · `tasks.md` `d7356862…5172`
  - specs: `benchmark-reference-choice` `a9f56803…74ee`, `result-context-export` `68d7e17d…2c2f`, `discovery-leaderboard` `6edd303b…d5f`
- Ignore list: `.impeccable/critique/ignore.md` não existe.
- Ferramentas: Playwright Python, Chromium headless shell 1243 (arm64, `executable_path` explícito), `pt-BR`, tema escuro, fuso São Paulo, **na URL pública**, contexto novo por viewport: 1440×900 e 390×844 (`isMobile`, `hasTouch`). Contraste pela cor computada contra o fundo efetivo (compondo os ancestrais), sem axe-core. Segui `.agents/skills/impeccable/reference/critique.md` (Assessment A) e `.cursor/skills/design-critic/SKILL.md` (D4). Scripts, JSON e 56 PNGs em `/tmp/claude-1001/-srv-apps-dev-criptofarol-source/9da083da-1d07-4a6e-9eb6-dddd4afcad74/scratchpad/c1123A/` (não versionados).

## Digest (disco == servido)

| Arquivo | sha256 disco | HTTP | servido |
|---|---|---|---|
| `index.html` (também a pasta `/`) | `a739f5787d80dbf521d315a5cb637552e1ccd61e314ca234867e891104866df4` | 200 | IDENTICAL |
| `favorite.html` | `378044d31488b108c3aa51dacd66bb1d3aa7d5a727e332d351514e1bb18fe769` | 200 | IDENTICAL |
| `favorites.html` | `f34ce6026aeebd627e528c95e2c4ffc28fc37218635273399dbbbf75c862c38e` | 200 | IDENTICAL |
| `discovery.html` | `d4642588271663f27249874ee3e524de1397c19fc1f5dc89d3fce8ff078cb42e` | 200 | IDENTICAL |
| `live.css` | `353ac045db2df0a13512af6bc3268d64eb4ad256a821969eb7c8118b1ba832f6` | 200 | IDENTICAL |
| `delta.css` | `6893f4308bc2270b33c712ceb115ba4041e38c345f83baf6f68fb5c7c1950718` | 200 | IDENTICAL |
| `delta.js` | `ac7ef49362e953c5725f676c63465ebaf95d898fd7d6bfaa5c192369e9ea1a67` | 200 | IDENTICAL |

Os hashes batem com a tabela "Bytes por página" do `design.md`. Nos fluxos clicados (4 páginas, 2 larguras) não houve `console.error`, `pageerror` nem resposta ≥ 400.

## Tokens parseáveis (rubrica, D4)

`design.md` L1–L3, cada um em linha própria:

```
UI impact: affected
live_route: /combo/results
surface: existing
```

O bloco D4 (L5) é idêntico ao da skill; L7 marca só as regiões clonadas. Rodado por mim no HEAD: `design_token_gap` = None; `parse_live_route` = `/combo/results`; `parse_surface` = `existing`; `classify(index.html, /combo/results)` = PASS; `copied_utf8_sum` = 56.249; `clone_gate_ok` = True. Marcadores pareados: index 7 COPIED / 6 DELTA, favorite 7/6, favorites 8/7, discovery 7/6. Nenhum painel ANTES/DEPOIS (as 3 ocorrências de "antes/depois" são copy, como "depois do fim da estratégia"). **ok.**

## Cobertura do body (Entra)

| Item do Entra | Protótipo (visível) |
|---|---|
| Referência à escolha (qualquer ativo do catálogo; coleta na escolha) | Seletor com busca, Todas/Cripto/Ações/ETFs, "Próprio ativo · Padrão", 7 ativos das 3 classes, situação do histórico; QQQ "Sem histórico guardado: coleta ao escolher" → "Coletando histórico de QQQ na Binance…" → comparação. Ativo desabilitado do catálogo: sem exemplo (P2-4) |
| Escolha depois de rodar, gravada no resultado ou favorito, vai à planilha | Rodada: "Gravada neste resultado em …" + "Ao salvar nos Favoritos, a referência vai junto". Favorito: "Gravada no favorito NVDA Trend em …"; aba Contexto se atualiza com a escolha; Favoritos mostra "Ref.: SPY" |
| Janela comum visível + o que ficou de fora | SPY: "02 jan. 2019 – 31 dez. 2024 · 2.190 dias" e "01 jan. 2019 (sem pregão em Nova York) · 0 trades"; SOL: "… · 3 trades fora" em âmbar; favorito × BTC: "2 trades fora" |
| Histórico insuficiente com motivo, nunca zero | CRCL: "Sem comparação" + motivo com as duas datas; números, período e aviso somem. Só `no_overlap` tem tela; `short_overlap` (30 dias) não (P2-1) |
| Aviso USDT/USD | Faixa âmbar com ícone, "USDT tratado como USD, sem conversão." + "BTC/USDT em USDT, SPY em USD" (e o inverso no favorito NVDA × BTC/USDT). Some com moedas iguais. Planilha: coluna "Aviso de moeda" |
| Retorno de preço sem dividendos | "Tipo de retorno · Retorno de preço, sem dividendos" para SPY, QQQ, NVDA; Legenda explica. Falta na planilha da Descoberta (P1-1) |
| Três planilhas com contexto completo | Trades: 22 campos na aba Contexto + Legenda. Favoritos: 22 colunas + Legenda. **Descoberta: 16 colunas, faltam 8 dos 22 campos** (P1-1) |
| Sem recálculo escondido | "Abrir ou exportar de novo não recalcula." + versão da amostra. O único recálculo (refresh do favorito) não está dito na tela do favorito (P2-2) |
| Favoritos antigos: "deduzido" / "não registrado" | Favorito: "Comparação não registrada… Nada é calculado ao abrir" + "Comparar com o próprio ativo". Planilha: "BTC antigo" com "Cripto (deduzido)", "USDT (deduzido)" (âmbar) e "não registrado" (itálico) |
| Ranking da Descoberta e do lote no próprio ativo | Decidir: "Referência do ranking: o próprio ativo (buy-and-hold, long-only). Trocar a referência num resultado ou favorito não muda este ranking."; planilha com "Próprio ativo (buy-and-hold, long-only)" por linha. Lote sem tela (correto: nada muda) |
| Verificação | NVDA × SPY (favorite), BTC × próprio e × SPY (index), insuficiente (CRCL), troca no favorito, 3 planilhas, favorito antigo. "ETF × próprio ativo" não tem tela própria, mas o render é o mesmo do NVDA próprio (P3) |

Não entra: nenhum campo de referência antes de rodar, ranking intocado, sem fonte nova, sem dividendos. **Sem escopo furado.**

## Decisões de Alan de 27/10

1. **Qualquer cripto/ação/ETF do catálogo, coleta na escolha:** respeitada. ok.
2. **Troca no resultado ou no favorito, gravada, vai à planilha; Descoberta/lote no próprio ativo:** respeitada. ok.
3. **USDT/USD em percentual com aviso, nunca em silêncio:** respeitada na tela e na planilha. ok.
4. **Planilhas com o contexto listado:** respeitada em Trades e Favoritos; **a prévia da Descoberta contradiz a decisão e o próprio spec** (P1-1).
5. **Favoritos antigos com "deduzido" e "não registrado":** respeitada. Ver P2-6 (tela × planilha).

## Decisão aberta: mínimo de 30 dias corridos

Não decido. A tela **não comunica** esse mínimo: nenhum estado `short_overlap` aparece no protótipo, e a frase de apoio do insuficiente ("Escolha outra referência com histórico no período da estratégia.") só serve para `no_overlap`. O texto do spec ("Período comum de N dias: o mínimo é 30.") existe só no spec. Alan aprova o número sem ver como ele aparece (P2-1). O `design.md` registra a pergunta em Open Questions com clareza.

## Estados

- **Válido:** 3 números (estratégia, referência, diferença em p.p. com "a favor da estratégia/da referência"), período comum, fora, tipo de retorno, aviso, linha de gravação. Tom de alta/queda sempre com sinal e texto, nunca só por cor. ok.
- **Gravando / coletando:** `role=status` polite, spinner com `prefers-reduced-motion`, sem números. ok. O cabeçalho já mostra a referência nova antes de gravar (P3).
- **Insuficiente:** ok para `no_overlap`; `short_overlap` sem tela (P2-1).
- **Falha na coleta:** alerta com motivo, "Nada foi gravado: a referência continua SPY.", comparação anterior visível, "Tentar de novo" 44 px que grava QQQ. ok.
- **Não registrada (favorito antigo):** ok; o cabeçalho diz "Referência: Próprio ativo (NVDA)" enquanto nada está registrado (P3).
- **Exportação:** status polite com arquivo e abas nas 3 páginas. ok.

## Fidelidade

- O canônico clona `/combo/results`: cabeçalho da estratégia, "Dados e execução", convenções, regras, gráfico, lista de operações. A seção nova fica entre o cabeçalho/análise e "Dados e execução", na moldura `r19-data` e com o `r19-precision` vivo em tom de alerta. Nenhuma grade de estados; cada Demonstração fica no fim, no fluxo, e se declara "Só no protótipo".
- Fora do delta, 1440 e 390 sem rolagem horizontal em todas as páginas (`scrollWidth == clientWidth`).
- No Decidir a 1440, "Promover"/"Excluir" aparecem cortados na borda direita da tabela. A região é COPIED e o delta não toca a tabela, então trato como incumbente (P3: o Apply confere que o botão novo no cabeçalho não piora isso).

## Acessibilidade (medida)

- **Contraste (menor razão no delta):** rótulos 12 px da seção 6,12; placeholder da busca 4,61; "USDT"/histórico no seletor 5,39; nota da referência do ranking 5,56; cabeçalho da prévia 5,56; texto do alerta de falha 7,35; "Fora do período comum" em âmbar 10,42; "Ref.: SPY" 16,35. **Tudo ≥ 4,5:1.**
- **Estado só por cor:** não há. Aviso com triângulo e texto; insuficiente com ícone e "Sem comparação"; diferença com "a favor da…"; células "deduzido"/"não registrado" com o próprio texto.
- **Diálogo:** `role=dialog aria-modal aria-labelledby aria-describedby`; foco inicial na busca (com rótulo `sr-only` "Buscar ativo"); Tab percorre Todas → Cripto → Ações → ETFs → rádio marcado → Cancelar → Usar referência → Fechar → busca (preso); setas trocam o rádio (`radiogroup` nativo, foco no rótulo com contorno 2 px); Esc fecha e devolve o foco a "Trocar referência"; busca sem resultado mostra "Nenhum ativo do catálogo com esse texto."; a 390 ocupa a tela inteira com botões de largura dividida.
- **Alvos:** "Trocar referência", "Usar referência", "Cancelar", "Fechar", "Tentar de novo", "Comparar com o próprio ativo", "Exportar planilha" com 44 px; rádios com 88 px. Os filtros de classe têm **36 px** também no toque (P2-5). "Exportar" de Favoritos tem 40 px (incumbente).
- **Live regions:** o alerta de falha (`role=alert`) fica dentro do `role=status` polite da seção. As live regions aninhadas podem anunciar duas vezes ou nenhuma (P3).
- **Foco depois de "Usar referência":** volta a "Trocar referência". ok.

## Responsividade

390: grade de 3 células vira uma coluna; "Trocar referência" ocupa a largura toda; aviso e linha de gravação quebram sem corte. "Ref.: SPY · comparação gravada 27/10" no cartão de NVDA, legível. Decidir: "Exportar planilha" e status acima das notas, sem corte. 1440: seção em 3 colunas, aviso em largura cheia.

## Heurísticas Nielsen (0–4), só neste snapshot

| # | Heurística | Nota | Nota curta |
|---|---|---|---|
| 1 | Visibilidade do estado | 3 | Gravando/coletando/falha/gravada claros; `short_overlap` sem tela |
| 2 | Linguagem do usuário | 3 | "Período comum", "o que ficou de fora", "a favor da estratégia"; "p.p." e "buy-and-hold" são do público |
| 3 | Controle e liberdade | 3 | Cancelar, Esc, voltar ao próprio ativo; uma escolha sem período comum substitui a válida |
| 4 | Consistência | 2 | Prévia da Descoberta com outras colunas (P1-1); SPY Trend sem "Ref." (P2-3); tela × planilha do favorito antigo (P2-6); ÷365 × 365,25 na mesma tela (P3) |
| 5 | Prevenção de erro | 2 | O seletor não avisa antes que a referência não cobre a estratégia (P2-4) |
| 6 | Reconhecer em vez de lembrar | 3 | Classe, moeda e histórico em cada opção; referência sempre nomeada |
| 7 | Flexibilidade | 3 | Busca, filtro, teclado completo |
| 8 | Estética e minimalismo | 3 | Seção densa, mas cada linha responde uma pergunta |
| 9 | Recuperar de erros | 4 | Falha diz o motivo e o que ficou; "Tentar de novo" |
| 10 | Ajuda | 3 | Legenda e linha de gravação; falta a regra do refresh (P2-2) |
| | **Total** | **29/40** | Good |

## Design specificity / cognitive load

O desenho é do produto: o exemplo canônico (01/01/2019, feriado em NY, 0 trades fora) mostra o problema real de comparar cripto 24/7 com pregão de NY, e o aviso de moeda escreve as duas moedas em vez de um alerta genérico. A carga cognitiva está na seção válida: 3 números, 3 fatos, aviso e linha de gravação. Fica aceitável porque a ordem segue a pergunta do pesquisador (quanto, contra o quê, em que período, com que ressalva, de quando). O ponto de decisão mais pesado é o seletor: 7 opções + 4 filtros, mitigado pela busca.

## Emotional journey

O pico é trocar para SPY e ver, sem pedir, o dia que ficou de fora e o aviso de moeda: dá confiança de que o número não engana. O vale é escolher CRCL e perder a comparação válida sem aviso prévio (P2-4), e, no favorito, ver números diferentes no dia seguinte depois de ler "não recalcula" (P2-2).

## What's working

- O "sem recálculo escondido" virou uma linha concreta: data, dono (resultado ou favorito), versão da amostra e a frase "Abrir ou exportar de novo não recalcula".
- Falha na coleta é honesta: diz o motivo, que nada foi gravado e qual referência continua, e mantém os números anteriores.
- Insuficiente nunca vira zero: números, período e aviso somem juntos, e o motivo cita as duas datas.

## Findings

### P0: bloqueante (produto / escopo / contrato visível)

Nenhum.

### P1: deve corrigir antes de PASS

- **P1-1. A prévia da planilha da Descoberta não traz o contexto completo e contradiz o spec.**
  - gravidade P1 · classe **contrato**
  - Onde: `discovery.html`, `#b23-data.rows` / Demonstração "Planilha do ranking · colunas de contexto"; spec `result-context-export` ("the three workbooks carry the same context headers in the same order") e `discovery-leaderboard`; Apply contract ("os HTML … como spec de layout").
  - Problema: a prévia tem 16 colunas. Faltam Período pedido, Tipo de retorno da referência, Fora do período comum, Retorno da estratégia no período comum, Retorno da referência, Situação da comparação, Versão da amostra da referência e Comparação gravada em, e "CAGR anualizado" aparece no lugar de "CAGR da estratégia no período comum". As linhas de NVDA e SPY (referência ação/ETF) não dizem "retorno de preço, sem dividendos" em lugar nenhum, o que fere o item "Retorno de preço" do Entra. É uma decisão de Alan (27/10) que o Apply pode seguir pela prévia errada.
  - Correção: a prévia da Descoberta passa a ter os mesmos 22 campos, na ordem do spec (como Favoritos e Trades já têm). Valores da Descoberta: Período pedido = janela pedida na varredura, Tipo de retorno = "Preço, sem dividendos" em NVDA/SPY e "Preço" em BTC, Fora = "nada", Situação = "Válida", Comparação gravada em = data da varredura. Se algum campo não fizer sentido para a Descoberta, o spec diz qual e por quê, e a prévia mostra o mesmo.
  - Disposition: rework (pai/autor, no rework único da dupla).

### P2: residual visível, não bloqueia o teto 1+1+1

- **P2-1. O mínimo de 30 dias não aparece na tela.** classe **produto**
  - Onde: `index.html`/`favorite.html` (só `no_overlap`); spec "Common period too short"; Open Questions.
  - Problema: Alan decide o número na Aprovação sem ver o estado. A frase de apoio "Escolha outra referência com histórico no período da estratégia." não serve para um período comum curto.
  - Correção: uma opção no seletor de `favorite.html` (ou na Demonstração) que caia em `short_overlap`, com "Sem comparação · Período comum de 12 dias: o mínimo é 30." e uma frase de apoio própria. Assim a pergunta aberta fica visível.
- **P2-2. O favorito diz "não recalcula" e omite o único recálculo.** classe **produto**
  - Onde: `favorite.html`, linha de gravação; design d5 ("Refresh do favorito… É o único recálculo").
  - Problema: a comparação do favorito é refeita a cada atualização do backtest. Quem lê "Abrir ou exportar de novo não recalcula" e vê outros números no dia seguinte entende que houve recálculo escondido, justamente o que o Entra proíbe.
  - Correção: no favorito, acrescentar "Refeita só quando o backtest do favorito é atualizado, com a mesma referência." Na Legenda, o mesmo.
- **P2-3. SPY Trend tem referência BTC/USDT na planilha, mas a linha de Favoritos não mostra "Ref.".** classe **contrato**
  - Onde: `favorites.html`: linha e cartão de SPY Trend × `rows[2]` ("Referência: BTC/USDT", gravada 27/10 10:02); design d9.
  - Problema: pela regra d9, a linha deveria mostrar "Ref.: BTC/USDT · comparação gravada 27/10". A tela e a planilha divergem justamente no único favorito com aviso de moeda.
  - Correção: pôr a tag na linha e no cartão de SPY Trend (ou trocar o dado da prévia para o próprio ativo).
- **P2-4. O seletor não avisa antes de gravar uma referência sem período comum.** classe **produto**
  - Onde: diálogo "Escolher referência" (CRCL "Histórico desde 05 jun. 2025" numa estratégia que termina em 31/12/2024); spec "Marked or unavailable catalog assets SHALL be shown disabled with the catalog reason" sem exemplo.
  - Problema: escolher CRCL substitui uma comparação válida por "Sem comparação", e no favorito isso vai para a planilha. O dado para avisar antes já está na opção (início do histórico guardado). O estado "desabilitado com o motivo do catálogo" está no spec, mas não na tela.
  - Correção: na opção, "Sem período comum com esta estratégia" quando o histórico guardado começa depois do fim (ou termina antes do início), sem bloquear a escolha. Acrescentar um ativo desabilitado com o motivo do catálogo no protótipo.
- **P2-5. Filtros de classe com 36 px no toque.** classe **a11y**
  - Onde: `.b23-filters button` (`min-height: 36px`), também a 390.
  - Correção: 44 px a partir de `max-width: 639.98px` (convenção dos outros controles do delta).
- **P2-6. Favorito antigo: a tela diz "Binance Spot · 24/7", a planilha diz "não registrado".** classe **produto**
  - Onde: `favorites.html` "BTC antigo" (linha COPIED com a convenção da classe) × `rows[3]` (Fonte/Sessão "não registrado").
  - Problema: a decisão de Alan está certa e não a reabro. O leitor da planilha, porém, vê na tela uma fonte que a planilha diz não ter.
  - Correção: na Legenda, uma linha "A tela de Favoritos mostra a convenção da classe; a planilha só traz o que foi gravado."

### P3: detalhe de Apply (aceito; não reabrir como P0/P1)

- Os itens da subseção "P3 aceitos" do autor.
- **Anualização na mesma tela:** a seção usa 365,25, e "Convenções desta execução", logo abaixo, diz "dias corridos ÷ 365". Já é P3 do autor. Sugestão: "CAGR por dias corridos ÷ 365,25" no subtítulo da seção.
- **Cabeçalho durante a coleta** já mostra a referência nova antes de gravar; "Trocar referência" segue ativo durante a coleta. Sugestão: "Trocando para QQQ…" e botão `aria-disabled` até terminar.
- **Live regions aninhadas:** `role=alert` dentro do `role=status`. Mover o alerta para fora da região polite.
- **Insuficiente na planilha:** células vazias com Estado "registrado"; "Tipo de retorno da referência" vazio para CRCL (ação), embora o spec peça o rótulo para toda referência ação/ETF; "Amostra da referência: CRCL versão 2" sem período comum que a defina.
- **Não registrada:** o cabeçalho diz "Referência: Próprio ativo (NVDA)" sem nada registrado. Sugestão: "Referência: não registrada".
- **Dado de mock:** NVDA "Todo o histórico" começa em 11/11/2014 no favorito, mas o seletor e a Descoberta dizem "desde 02 jan. 2003".
- **Descoberta:** "Versão da amostra" mostra só um id; o spec pede `candle_version` + `snapshot_id`. Com o ranking ordenado por Calmar, "Referência do ranking" pode ser lido como critério de ordem; "Referência do B&H e do Δ" é mais exato.
- **Sem tela para:** ETF × próprio ativo e short ("buy-and-hold long-only"). Copy no spec, render igual ao NVDA próprio.
- **Decidir a 1440:** "Promover"/"Excluir" cortados na borda (região COPIED, incumbente).
- **Busca do seletor:** o contorno de foco aparece no `input` interno, dentro da moldura `.b23-search` (borda dupla).

## Persona red flags

- **Alan pesquisador (BTC × SPY):** lê o aviso e o dia fora; ok. Na planilha da Descoberta, não acha "retorno de preço" nem o retorno da referência (P1-1).
- **Alan no favorito, dia seguinte:** os números mudaram depois de "não recalcula" (P2-2).
- **Teclado/leitor de tela:** diálogo completo e preso; alerta de falha numa live region aninhada (P3).
- **Celular:** tudo em uma coluna, sem corte; os filtros de classe são o único alvo pequeno (P2-5).

## Questions to consider

- Uma escolha que dá "Sem comparação" deveria mesmo substituir a comparação válida gravada, ou ficar como tentativa até Alan confirmar?
- Com a referência gravada mudando a cada refresh, vale guardar o histórico das comparações do favorito (a anterior fica consultável), ou só a última basta?

## Disposition (resumo)

- Tokens L1–L3 ok; gate do clone PASS (rodado por mim); disco = servido nos 7 arquivos; sem ANTES/DEPOIS.
- Os itens do Entra têm tela, salvo o estado `short_overlap` (P2-1) e a planilha da Descoberta incompleta (P1-1). Decisões de Alan respeitadas; sem escopo furado.
- A11y medida: contraste ≥ 4,5 no delta, estado nunca só por cor, diálogo com foco preso, Esc e retorno do foco, 1440/390 sem rolagem horizontal; filtros com 36 px.
- P0 = 0 · P1 = 1 · P2 = 6 · P3 = aceitos.
- **Verdict: PASS com rework.** O P1-1 cabe no rework único da dupla (dados da prévia em `discovery.html`, sem mudança de spec). P2-1 e P2-3 são baratos no mesmo rework; os outros P2 podem ficar como residual na seção de crítica do `design.md`.
