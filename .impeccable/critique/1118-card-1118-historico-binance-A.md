# Assessment A — card 1118 · change card-1118-historico-binance

> Avaliador A isolado (produto / UX / acessibilidade / fidelidade do clone). Onda dupla com-tela. Sem transcript do pai. Sem resultados do Assessment B. Sem nested-spawn. Sem `process_event`. Sem arraste de Status. Sem edição de `design.md`, HTML proto, OpenSpec, `backend/` ou `frontend/src/`. Única escrita: este arquivo.

`proxy modelo: Assessment A → Opus 5.5 (claude-opus-5-5, effort high)` — captura `cf-assess-a-1118.json` (attempt `037f7771-07fe-4f28-a805-c1929e37b7ff`, band `juizo`, role `assessment-a`).

## Metadata

- card: 1118 — Consultar histórico Binance confiável e reutilizável para cripto, ações e ETFs
- change: `card-1118-historico-binance`
- cwd: `/srv/apps/dev/criptofarol/crypto-worktrees/card-1118-historico-binance`
- branch / q_git: `card-1118-historico-binance` @ `a1a699d3` (pacote untracked)
- tuple: `bound_card=1118` · Status esperado = Design (MUST NOT arrastar)
- data (UTC): 2026-10-22T23:48Z
- cliente: Claude Code (adapter cooperativo, não oficial; sem modo Auto), superfície claude-desktop
- Issue: REST `gh api repos/oalansilva/crypto/issues/1118 --jq .body`. Fronteira = body grelhado (Problema / História / Entra / Não entra + 5 decisões de Alan de 22/10/2026). Sem reentrevista.
- `design.md` sha256 `5aee2b40701cad7936c362e5a00d4d10247a03e89a746c1b2dfe63a22b0f1fd0` (== prompt)
- Ignore list: `.impeccable/critique/ignore.md` ausente
- Tooling: `python3 -m http.server 53291 --bind 127.0.0.1` (cwd `frontend/public`, encerrado no fim); Playwright Python + Chromium `/usr/bin/chromium-browser` headless, `pt-BR`, 1440×900 e 390×844. Screenshots de trabalho em `/tmp/1118-A-shots/` (não versionados). Sem axe-core local: contraste medido por cor computada.
- Mode: Impeccable **critique** sobre Operate (refinamento do seletor vivo do #1117). `DESIGN.md` autoridade visual, não sobrescrito.

## Digest (disco == servido)

| Arquivo | sha256 disco | HTTP local | servido |
|---|---|---|---|
| `index.html` (canônico; também `…/card-1118-historico-binance/`) | `5db21b21c59f4fd41df36c916ed1ba737bd2bfef637834722a03fa7bdeb811ff` | 200 | IDENTICAL |
| `combo.html` | `c14805cf76af3c46f5f86a86eef361b354b0c30ebfbe8f764d593b739404d804` | 200 | IDENTICAL |
| `optimize.html` | `a0e8e60daa6cf0981aae433bee66d127dc251ee46ea89a0e8f25c0dc9885e72e` | 200 | IDENTICAL |
| `live.css` | `03835ef5c21e5a086823248e0656944b120d26c8c44b724cb36dc35df2316674` | 200 | IDENTICAL |
| `cobertura.css` | `324ab1db187d4cde5272822c645a6a546b96f455a7b385db4ed3a65bbd74cfc3` | 200 | IDENTICAL |
| `cobertura.js` | `55f15658aabf0704f45c484fbb7dab227f0f04cd7769591749e9f94d2237418b` | 200 | IDENTICAL |

Disco == servido == prompt == `design.md` §Prototype Validation. Único 404 da sessão: `/favicon.ico` (fora do proto). Sem `pageerror`.

## Tokens parseáveis (rubrica D4)

`design.md` L1–L3, linhas próprias:

```
UI impact: affected
live_route: /combo/discovery
surface: existing
```

`design_clone_gate.design_token_gap` = None; `parse_ui_impact` = `affected`; `parse_live_route` = `/combo/discovery`; `parse_surface` = `existing`. `copied_utf8_sum(index.html)` = 43.646 B de 47.342 (9/9 pares `COPIED`), `DELTA` 5/5. Landmarks do catálogo para `/combo/discovery` (`Descoberta de estratégias swing`, `Preflight`, `Rascunho de varredura`) presentes no Montar padrão. Regiões clonadas declaradas uma a uma no §Context; extras `combo.html` (`/combo/configure`) e `optimize.html` (`/combo/optimize`) nunca canônicos. Index não é painel ANTES/DEPOIS nem grelha de N estados; Demonstração no fim, no fluxo. **ok.**

## Cobertura do body (Entra / Não entra)

| Item do body | OpenSpec | Protótipo (dentro do clone) |
|---|---|---|
| Mesma série em todo lugar | `market-history`, `market-candles`, decisões 2–4, tarefa 4.4 | n/a (sem tela) |
| Sem download repetido / catálogo não coleta | `market-history` "Selecionar todos os ETFs", decisão 5, 7.3 | "Todos do filtro (3.112)" sem efeito de coleta |
| Período honesto (pedido, coberto, lacunas, atualização, insuficiente, falha) | `market-history` req. 3, `binance-equity-history` | coberto (BTC/NVDA), lacunas (SPY), parcial/insuficiente (IBIT), falha (QQQ, Demonstração), atualizado em toda linha |
| Coleta que retoma | decisão 6, 3.2 | "Coletando histórico · 1d, página 2" (`role=status`); falha diz "a coleta continua do ponto em que parou" |
| Calendário de bolsa | decisão 8, 3.3 | nota "Mercado fechado não conta como lacuna" |
| Amostra estável + proveniência | `execution-data-snapshot` | Decidir: "Binance Spot · 1d nativo · v7" |
| Correções / eventos corporativos | decisões 10–11 | "ajustado" na linha de série |
| Apagar cache não perde histórico | decisão 12, 3.6 | n/a |
| Verificação NVDA / SPY ou QQQ / BTC | tarefas 7.1–7.2 | n/a |
| Cobertura no seletor (sem "não coletado") | `asset-history-coverage` | 0 ocorrências de "Histórico não coletado" nas 3 telas; botão "Cobertura" + tabela por timeframe |
| Coleta sob demanda | decisão 5 + Open Question | AAPL/MSFT/TSLA "Histórico sob demanda" |
| Só pregão regular | decisão 8 | "pregão regular de Nova York" na nota da série |
| 15m montado do 5m, marcado derivado | decisão 9 | 15m com selo "derivado" e origem "montado do 5m" |
| Reprodução enquanto favoritado / prazo fixo | decisão 14 (30 dias), `execution-data-snapshot` | Decidir: "amostra guardada até 21 nov. 2026", "favorito: amostra mantida", "não reproduzível exatamente" (evidência e resultado) |

Não entra — nada vazou: sem gráfico de ação/ETF, sem pré/pós-mercado, sem botão de coletar nem coleta em segundo plano/lote, sem "refazer igual" na tela, sem escolha de estratégia, provedores legados mantidos (#1126). Varredura de texto nas 3 telas + `cobertura.js` por pré/pós-mercado, gráfico, refazer, coletar, segundo plano, lote diário, reproduzir: 0 ocorrências.

## Fidelidade (clone da página viva)

- Sem sessão autenticada nesta avaliação; a fidelidade usa o catálogo de landmarks, a fonte viva (só leitura) e a captura declarada do autor (DEV com `/api/**` simulado, mocks do `card-1117-asset-selector.spec.ts`).
- `AssetPicker.tsx` vivo: `ap-facts` → `ap-fact cls-*`, `ap-fact st-*`, `ap-fact hist` (`historyText`), linha `<label class="ap-row">`, marcado `div.ap-row.marked` + `ap-reason`. O protótipo mantém exatamente essa estrutura e muda só o conteúdo de `ap-fact hist`, mais o botão e o painel. Nota de classe idêntica ao `classNote`.
- `DiscoveryPage.tsx` vivo: evidência `… candles ${candle_source} v${candle_version}` → o delta troca a fonte pela série e anexa a amostra, no mesmo lugar.
- AppNav desktop (224 px, grupos Principal/Estratégias/Carteira/Admin, item ativo âmbar), AppNav móvel (hambúrguer + DEV + avatar), densidade e tokens `--bg`/`--text-tertiary` idênticos nas três telas. Combo e Otimização mantêm o chrome vivo (Template Information, Parameter Optimization Ranges, "Ready to Optimize").
- Delta restrito ao seletor (3 telas) e ao Decidir (index). **ok.**

## Acessibilidade (medida)

- Contraste (cor computada sobre fundo efetivo): fato de histórico `#929aa5`/`#0b0e11` 6,81:1; âmbar lacuna/parcial 11,59:1; azul coletando 10,73:1; vermelho falha 8,18:1; rótulos do painel 6,12:1; valores 14,69:1; botão "Cobertura" 13,36:1; Decidir "não reproduzível exatamente" 6,68–7,35:1; "favorito: amostra mantida" 7,44–8,18:1. Tudo ≥ AA 4,5:1.
- Alvos: "Cobertura" 101×32 px nas 3 telas e nos 2 viewports (≥ 24 px).
- Teclado: ordem Tab = filtros → checkbox → "Cobertura" de cada linha; `:focus-visible` com contorno 2 px `#3b82f6`; Space no botão abre (`aria-expanded=true`) e **não** marca BTC; Enter em SPY abre e SPY continua fora da seleção; foco volta ao botão depois do re-render.
- Nome acessível "Cobertura de <símbolo>" (`sr-only`), `aria-controls` → `role=region` com `aria-label`. Coleta em andamento em `role=status`.
- Sem rolagem horizontal do documento em nenhuma tela/viewport, com painéis abertos e no Decidir (tabela do Decidir rola dentro do `overflow-x-auto` incumbente). Painel na Otimização (coluna de 320 px) reorganiza em 2 colunas; a 390 px idem.

## Heurísticas Nielsen (0–4) — só neste snapshot

| # | Heurística | Score | Nota |
|---|---|---|---|
| 1 | Visibility of system status | 4 | coletando / falha / parcial / atualizado visíveis na linha |
| 2 | Match between system and real world | 3 | "página 2", "há 1d desde", horas sem fuso |
| 3 | User control and freedom | 3 | painel abre/fecha sem afetar seleção; nenhum controle de coleta (por escopo) |
| 4 | Consistency and standards | 4 | mesmo fato e mesmo painel nas 3 telas |
| 5 | Error prevention | 3 | "Todos do filtro" não coleta; a promessa "sob demanda" sem caminho na UI para ação/ETF |
| 6 | Recognition rather than recall | 3 | resumo "desde 2014 · 3 timeframes" esconde que 5m/15m começam em 2026 |
| 7 | Flexibility and efficiency | 3 | disclosure por linha; sem resumo de cobertura dos selecionados |
| 8 | Aesthetic and minimalist design | 3 | linha fica com 3 linhas de texto a 390 px |
| 9 | Recognize, diagnose, recover | 3 | falha diz motivo e o que já há; lacuna diz data/hora |
| 10 | Help and documentation | 3 | nota da série explica mercado fechado |
| **Total** | | **32/40** | Good |

## Cognitive load

Single focus por linha; detalhe em progressive disclosure; 4 fatos no máximo por linha (classe, estado, histórico, botão). Falhas: (1) contagem de lacunas que soma o 15m derivado à lacuna do 5m; (2) período resumido que mistura timeframes com inícios diferentes. Carga baixa-média.

## Findings

### P0 — bloqueante (produto / escopo / contrato visível)

- nenhum.

### P1 — deve corrigir antes de PASS

- nenhum.

### P2 — residual visível, não bloqueia o teto 1+1+1

- **[P2 · mecânico] Seletor, linha SPY (3 telas): "2 lacunas" conta duas vezes o mesmo buraco.** O painel mostra 1 lacuna no 5m (14 out., 10:05–10:40) e o mesmo trecho "herdado do 5m" no 15m derivado; o resumo soma as duas. Corrigir: contar só lacunas de séries nativas (ou "1 lacuna (repete no 15m derivado)").
- **[P2 · mecânico] Seletor, linha NVDA/SPY: "Histórico desde 11 nov. 2014 · 3 timeframes" sugere 5m/15m desde 2014.** 5m e 15m começam em 19 mai. / 01 jul. 2026. Corrigir o resumo para não prometer o período mais longo para todos os timeframes (por exemplo "1d desde 11 nov. 2014 · 5m e 15m desde 19 mai. 2026"), em linha com "Período honesto".
- **[P2 · mecânico] Painel "Cobertura": horários sem fuso e fusos misturados.** Lacunas em hora de Nova York (10:05–10:40 só cabe no pregão se for ET; em Brasília seria 09:05 ET, pré-mercado), "atualizado 18:00" em hora local. Corrigir: rotular o fuso das lacunas ("horário de Nova York") ou converter tudo para um fuso declarado.
- **[P2 · mecânico] Linha QQQ em falha: "há 1d desde 05 jan. 2023" se lê como "há 1 dia".** Corrigir: "já coletado: 1d desde 05 jan. 2023".
- **[P2 · mecânico] Decidir, evidência: "amostra expirada em …: não reproduzível exatamente" fica na linha de 10 px**, o menor texto da tela, para o estado mais importante da amostra. Contraste ok (6,68:1). Corrigir: manter na evidência e dar peso/tamanho do resultado (11 px) ou um selo, sem novo componente.
- **[P2 · juízo leve] Favoritos com atualização automática diária (`favorite_backtest_refresh_service`) × "favorito mantém a sua amostra".** O design fixa `snapshot_id` na promoção, mas não diz o que acontece quando o backtest do favorito é atualizado todo dia com dados novos: a amostra mantida é a da promoção (e os números em `/favorites` deixam de corresponder a ela) ou a atualização troca a amostra fixada? O autor pode propor um default explícito no `design.md`/`execution-data-snapshot`; Alan confirma na Aprovação de Design. (O caminho de dados do refresh passa por `CcxtMarketDataProvider` → `IncrementalLoader`, então "mesma série" já está coberto.)

### P3 — detalhe de Apply (não reabrir como P0/P1)

- **[P3] `<button>` "Cobertura" dentro do `<label class="ap-row">`**: conteúdo de label com segundo elemento rotulável é HTML inválido; funciona (o `preventDefault` + nome via `aria-label` garantem), mas o Apply deve tirar o botão de dentro do label ou reestruturar a linha. Disposition: **aceito-P3-Apply**
- **[P3] `role=status` re-renderizado a cada filtro ou página** reanuncia a coleta. Apply: anunciar só quando o progresso muda. **aceito-P3-Apply**
- **[P3] Motivos de falha**: só "limite de requisições da Binance" demonstrado; o Apply escreve os textos para indisponibilidade, erro de negócio (sem expor `488006` cru) e "formato da Binance mudou". **aceito-P3-Apply**
- **[P3] "página 2" sem total** no estado coletando. Vocabulário do próprio body; total opcional no Apply. **aceito-P3-Apply**
- **[P3] Texto da Demonstração em `combo.html`/`optimize.html` cita "a aba Decidir"**, que não existe nessas telas. Texto de demonstração, não vai para o produto. **aceito-P3-Apply**
- **[P3] Nomes de tabelas/serviços/rotas, balde de fichas, 3 GiB, 1e-9, caminhos de cache/segmentos, formato de data, ordem dos fatos, seta do botão, números de amostra**: já listados como P3 no `design.md`. **aceito-P3-Apply**

## Open Question do autor (coleta de ação/ETF só via consulta até o #1119)

Parecer: **não é furo do Design, é ambiguidade real do body que pede decisão de Alan**, e o autor a expôs corretamente em vez de decidir. A leitura literal é coerente com as decisões de 22/10 (nada de tela nova além da cobertura, coleta sob demanda, nada de lote/segundo plano), e os specs ficam internamente consistentes com ela.

O que está em jogo para o operador:

- **Leitura do Design (análise recusada não coleta):** até o #1119, as ~7.900 ações e ETFs só saem de "Histórico sob demanda" por `GET /market/history` (API, sem botão na tela). Na prática, Alan vê cobertura só dos ativos da verificação (NVDA, SPY/QQQ); escolher NVDA na Descoberta e tentar iniciar não muda nada no seletor. O texto "sob demanda" promete um gatilho que a tela ainda não oferece para essas classes. Zero risco de coleta em massa.
- **Alternativa (incluir ação/ETF numa análise já dispara a coleta, mesmo recusada):** a cobertura aparece pela própria tela antes do #1119, mas "Todos do filtro" em ETFs + Iniciar poderia pedir 3.112 coletas; o Design precisaria de um teto (e de um texto na tela dizendo o que foi e o que não foi coletado), o que é mudança de escopo e de tela.
- Uma terceira via (botão "coletar" na linha) seria UI nova e conflita com a decisão "cobertura no seletor, sem tela nova"; só com aval explícito.

Recomendação ao pai: levar a pergunta a Alan **antes** do único rework (teto 1+1+1), para que a resposta caiba no rework se ele escolher a alternativa; se Alan mantiver a leitura literal, nada muda no protótipo.

## Disposition (resumo)

| Finding | Gravidade | Classe | Quem corrige | Disposition |
|---|---|---|---|---|
| (nenhum P0/P1) | — | — | — | n/a |
| Lacunas contadas 2×; resumo "desde 2014" para todos os tf; fuso das horas; "há 1d"; peso do "não reproduzível" na evidência | P2 | produto visível (copy/hierarquia) | autor (mecânico) | n/a — rework se o pai abrir |
| Favorito com atualização diária × amostra mantida | P2 | contrato de produto | autor propõe default; Alan confirma | n/a |
| Open Question (coleta só via consulta) | — | escopo / juízo | Alan | perguntar antes do rework |
| button-in-label, `role=status`, motivos de falha, "página 2", texto da Demonstração, internos | P3 | detalhe de Apply | Apply | aceito-P3-Apply |

## Bloco resumo

```
P0: 0
P1: 0
P2: 6
P3: 6
verdict: PASS
```

Design fecha em 1+1+1: sem `## Design Critique` aqui (o pai publica depois da dupla).

## Artefactos desta sessão

- `.impeccable/critique/1118-card-1118-historico-binance-A.md` (este arquivo; única escrita no repo)
- Screenshots de trabalho em `/tmp/1118-A-shots/` (não versionados)
