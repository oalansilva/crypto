---
target: análise gráfica de Favoritos
total_score: 34
max_score: 40
na_heuristics: ""
p0_count: 0
p1_count: 0
timestamp: 2026-08-06T18-33-56Z
slug: s-card-384-favorites-analysis-hierarchy-index-html
---
⚠️ DEGRADED: single-context (independent critics could not be started with observable proof of the exact primary LLM/model and version)

## Design Health Score

| # | Heuristic | Score | Key Issue |
| --- | --- | --- | --- |
| 1 | Visibility of System Status | 3 | Candle de referência e sincronização são explícitos; estados assíncronos ficam para a implementação. |
| 2 | Match System / Real World | 4 | A ordem identidade → risco → regras → evidência → operações acompanha a decisão do trader. |
| 3 | User Control and Freedom | 4 | Voltar, reset do gráfico, disclosure e menu com Escape/fechar são claros. |
| 4 | Consistency and Standards | 4 | Shell, tokens, termos e semântica Long/Compra/Venda são consistentes. |
| 5 | Error Prevention | 3 | A superfície é majoritariamente de leitura; estados indisponíveis não inventam valores. |
| 6 | Recognition Rather Than Recall | 4 | Contexto permanece visível e o disclosure informa antecipadamente seu conteúdo. |
| 7 | Flexibility and Efficiency | 3 | Mouse, toque e teclado funcionam; não há aceleradores adicionais no protótipo. |
| 8 | Aesthetic and Minimalist Design | 4 | O detalhe técnico aparece uma vez e fica fora do caminho principal. |
| 9 | Error Recovery | 2 | O estado principal está completo, mas erro de candles e falha de sincronização não foram materializados no HTML. |
| 10 | Help and Documentation | 3 | Regras, função dos indicadores e disclaimer dão contexto; a ajuda global permanece no shell real. |
| **Total** |  | **34/40** | **Good** |

## Design Specificity Verdict

**LLM assessment:** a composição é específica para uma análise de estratégia do Cripto Farol. Ela não depende de uma grade genérica de métricas: tese, direção, stop, regras permanentes, candles, sinais e operações formam uma narrativa de decisão própria do produto. A maior melhoria sobre a tela atual é a separação clara entre resumo, evidência temporal e ficha técnica.

**Deterministic scan:** zero achados no arquivo `frontend/public/prototypes/card-384-favorites-analysis-hierarchy/index.html`. Os desvios iniciais de tipografia, raio e cor foram corrigidos com os tokens de `DESIGN.md`.

**Visual overlay:** a injeção foi confirmada em navegador real e registrou `[impeccable] No anti-patterns found`. Não havia marcações visuais a exibir.

## Overall Impression

A tela agora oferece uma leitura calma e verificável: o usuário entende primeiro o que está analisando e só abre a ficha técnica quando precisa. A maior oportunidade restante é garantir que a implementação trate estados sem candles, sincronização falha e payload parcial com a mesma disciplina.

## What's Working

- O nome e a descrição completa têm espaço editorial e não são cortados em 390 px.
- O gráfico é a superfície dominante; métricas e regras apoiam a interpretação sem competir com ele.
- Indicadores e parâmetros têm um único dono visual, e a indisponibilidade foi consolidada em um aviso contextual.
- A tabela vira linhas rotuladas no mobile, evitando rolagem horizontal.

## Priority Issues

### [P2] Estados degradados ainda não estão materializados no protótipo

**Why it matters:** candles ausentes, sincronização falha ou manifesto parcial são estados reais da análise; uma implementação que improvisar esses estados pode reintroduzir blocos concorrentes.

**Fix:** implementar os estados previstos no OpenSpec dentro das mesmas regiões, sem inserir uma nova ficha técnica global.

**Suggested command:** `$impeccable harden`.

### [P2] Estado do disclosure não é persistido

**Why it matters:** um usuário especialista que sempre consulta a ficha técnica precisa reabri-la a cada visita.

**Fix:** durante implementação, avaliar preferência local por sessão sem tornar o detalhe aberto o padrão para todos.

**Suggested command:** `$impeccable polish`.

### [P3] Legenda do gráfico permanece densa no mobile

**Why it matters:** três séries com valores cabem, mas uma estratégia futura com mais indicadores pode ocupar uma área relevante do gráfico.

**Fix:** manter quebra controlada e definir limite com acesso ao restante pela ficha técnica, sem esconder as séries ativas.

**Suggested command:** `$impeccable adapt`.

## Persona Red Flags

**Alex (power user):** encontra retorno, risco, regras e gráfico em menos de um viewport desktop, e os controles permanecem diretos. Red flag residual: a preferência do detalhe técnico não persiste.

**Sam (keyboard/screen reader):** controles têm nomes, foco visível, alvo mínimo de 44 px e o menu fechado sai da árvore de foco. Red flag residual: a implementação React deverá anunciar carregamento e falha assíncrona, estados que o HTML estático não simula.

**Casey (mobile):** não há overflow horizontal; ações do gráfico têm 44 px; descrição e operações refluem. Red flag residual: uma legenda com mais de três indicadores precisará de contenção responsiva.

## Cognitive Load

Carga baixa: os oito critérios passam. Há um único foco, grupos de até quatro elementos, uma sequência vertical clara e divulgação progressiva. Nenhum ponto de decisão apresenta mais de quatro opções visíveis.

## Minor Observations

- A paleta é deliberadamente sóbria e usa amarelo apenas para marca/ênfase, verde/vermelho para semântica de mercado.
- A configuração técnica usa siglas reconhecidas, mas explica a função em linguagem comum.
- O disclosure informa `3 indicadores · 4 parâmetros efetivos`, reduzindo custo de descoberta.

## Questions to Consider

- A preferência de detalhe técnico aberto deve durar apenas na visita atual ou entre visitas?
- Quando houver mais de três indicadores, quais valores merecem permanecer na legenda do gráfico?

Questions skipped: a direção principal já foi definida pelo relato do usuário; as pendências restantes são critérios de implementação e estados de robustez, não escolhas que bloqueiem o design.
