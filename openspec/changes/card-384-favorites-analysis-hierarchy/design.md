## Context

O card #361 tornou o manifesto canônico da estratégia visível, mas a composição atual distribui a mesma informação entre `ComboResultsPage`, `StrategyTransparencyPanel` e `StrategyChartSurface`. Para o exemplo BTC 1D Long, `EMA 16`, `SMA 17`, `SMA 33`, participação, função, indisponibilidade da série e parâmetros efetivos aparecem mais de uma vez. A descrição longa também compete com blocos técnicos e pode ser percebida como cortada.

A tela atende investidores do beta fechado que saem de Favoritos para compreender uma estratégia antes de decidir se devem acompanhá-la. O visitante está em modo de avaliação: precisa primeiro entender identidade, tese, resultado e risco; depois confirmar regras e evidências no gráfico; por fim consultar configuração completa e operações.

Restrições:

- `UI impact: affected`.
- `DESIGN.md` e a interface autenticada atual são a autoridade visual.
- Nenhum cálculo, dado, permissão ou contrato de API será redefinido.
- O status deve permanecer em `Design` até as evidências e críticas exigidas; código de produção só pode começar após Alan mover o card de `Aprovação de Design` para `Pronto para Dev`.
- A sessão não expõe prova observável do LLM/modelo e versão para dois critics independentes. Portanto, as avaliações locais ajudam a refinar o protótipo, mas não podem produzir `PASS` no gate Codex.

## Impeccable Brief

- **Job and audience:** investidor do beta fechado abre uma favorita para entender rapidamente a tese, o desempenho histórico, o risco e a evidência antes de decidir acompanhar a estratégia.
- **Outcome and proof:** em poucos segundos deve localizar nome, par, timeframe, direção, retorno, taxa de acerto, drawdown e regras; o gráfico e as operações comprovam a leitura, e a configuração completa continua acessível sem repetição.
- **Selected direction:** leitura vertical decision-first. Um cabeçalho sóbrio apresenta identidade e métricas; regras permanentes vêm em seguida; o gráfico é a evidência dominante; detalhes técnicos ficam em uma única divulgação progressiva; sinais e operações fecham a análise.
- **Scope and boundaries:** redesenhar apenas a análise `/combo/results` aberta por Favoritos, desktop e mobile. Preservar shell, tokens, gráfico, dados, exportação, permissões e fluxos existentes. Não criar recomendações financeiras, novos indicadores, novas métricas ou endpoints.
- **States and ranges:** descrição curta ou longa; zero ou vários indicadores; séries disponíveis ou indisponíveis; direção Long ou Short; com ou sem candles, sinais ou operações; conteúdo de 320 px até desktop largo.
- **Interaction and layout:** ação de retorno permanece secundária; gráfico usa toda a largura útil; detalhes técnicos abrem por botão com `aria-expanded`; tabelas refluem em mobile; texto sempre quebra sem truncamento; controles mantêm alvo de toque e foco visível.

## Goals / Non-Goals

**Goals:**

- Eliminar a repetição dos mesmos indicadores e parâmetros.
- Dar prioridade à decisão: identidade, desempenho, risco, regras e evidência.
- Tornar a descrição completa legível em qualquer viewport.
- Preservar transparência completa com divulgação progressiva acessível.
- Tornar responsabilidades de apresentação explícitas entre os componentes.

**Non-Goals:**

- Alterar manifesto, séries, cálculos, backtest, trades ou sincronização com Monitor.
- Redesenhar a lista de Favoritos, o Monitor ou o shell global.
- Adicionar recomendação automática, score ou promessa de resultado.
- Implementar código de produção durante o gate de Design.

## Decisions

### 1. Um único fluxo vertical, sem painel técnico concorrente

`ComboResultsPage` será o orquestrador da hierarquia: cabeçalho/resumo, regras, gráfico, detalhe técnico, histórico de sinais e operações. A alternativa de manter a configuração campeã acima do painel de transparência foi rejeitada porque preserva a duplicação e desloca o gráfico para baixo.

### 2. Donos visuais separados por propósito

- O resumo apresenta somente identidade e métricas decisórias.
- `StrategyRuleOverview` apresenta as regras permanentes de entrada, saída e proteção.
- `StrategyChartSurface` apresenta candles, sinais, controles e legenda de valores no candle de referência, sem repetir a ficha técnica completa abaixo do gráfico.
- `StrategyTransparencyPanel` é a única ficha técnica detalhada: indicadores, função, participação, configuração, parâmetros efetivos e indisponibilidade.

A alternativa de condensar tudo dentro do gráfico foi rejeitada porque prejudica mobile, leitura por tecnologia assistiva e o estado sem candles.

### 3. Detalhes técnicos fechados por padrão

O bloco técnico usa divulgação progressiva com título, resumo de quantidade e estado. Abrir/fechar não oculta as regras essenciais nem o contexto de risco. A alternativa de abas foi rejeitada porque criaria navegação paralela e esconderia informação atrás de estados mutuamente exclusivos.

### 4. Métricas em faixa editorial, não em coleção de cards aninhados

Retorno recebe ênfase numérica; taxa de acerto, drawdown e operações usam divisores e alinhamento, evitando uma grade de cartões dentro de outro cartão. Verde e vermelho ficam reservados à semântica de mercado. A alternativa de repetir seis cards iguais foi rejeitada por aumentar ruído sem melhorar comparação.

### 5. Responsividade por reflow, nunca por corte

O cabeçalho passa de duas colunas para uma; métricas formam uma grade de duas colunas; regras empilham; o gráfico mantém largura total e altura adequada; operações viram linhas rotuladas. `line-clamp`, elipse e overflow horizontal na página são proibidos para identidade e descrição.

## Information Architecture

1. Voltar aos favoritos.
2. Identidade: `BTC/USDT`, `1D`, `Long`, nome e descrição completa.
3. Resultado e risco: retorno total, taxa de acerto, drawdown, operações e stop.
4. Regras da estratégia: condições de entrada, saída e proteção.
5. Gráfico da estratégia: candles, indicadores, sinais e valores no ponto selecionado.
6. Detalhes técnicos: única fonte visual de indicadores e parâmetros efetivos.
7. Histórico de sinais, quando existir.
8. Operações e exportação.
9. Aviso educacional.

## Component Ownership

| Informação | Dono visual | Apresentação permitida fora do dono |
| --- | --- | --- |
| Identidade, timeframe e direção | Cabeçalho da análise | Contexto compacto no cabeçalho do gráfico |
| Métricas agregadas | Resumo da análise | Resumo de operações, sem parâmetros |
| Regras de entrada/saída/risco | `StrategyRuleOverview` | Nenhuma repetição; operações mostram apenas seus motivos contextuais |
| Série e valor no candle | `StrategyChartSurface` | Nenhuma lista técnica duplicada |
| Função, participação e configuração de indicador | `StrategyTransparencyPanel` | Nome/cor/valor compacto na legenda |
| Parâmetros efetivos | `StrategyTransparencyPanel` | Referência em linguagem natural nas regras, sem nova grade |
| Indisponibilidade técnica | Contexto técnico correspondente | Estado vazio do gráfico apenas quando o próprio gráfico não existe |

### Refinamento após feedback de uso

- O bloco permanente usa o título `Regras da estratégia` e o apoio `Condições usadas para entrada, saída e proteção da operação.`. A frase sobre as regras não mudarem com a posição atual foi removida porque não acrescenta uma decisão útil ao contexto.
- Nas operações, o acionador passa a se chamar `Ver decisão da operação`, descrevendo o resultado da ação em vez de repetir uma explicação genérica da estratégia.
- O conteúdo expandido de cada operação mostra somente as evidências daquele evento — motivo da entrada, da saída ou do estado aberto. Ele não renderiza novamente `StrategyRuleOverview`, pois as regras permanentes já possuem um único dono visual acima do gráfico.
- O comportamento do Monitor permanece inalterado; o refinamento é opt-in no fluxo de análise completa para evitar regressão no componente compartilhado.

## Accessibility and Content

- Semântica `main`, seções rotuladas, `button` real e `aria-expanded` no disclosure.
- Foco de teclado de 2 px com contraste; alvo mínimo de 44 px para ações móveis.
- Contraste mínimo 4.5:1 para texto corrente e 3:1 para texto grande.
- Números tabulares; siglas EMA/SMA preservadas; rótulos de interface em português.
- A indisponibilidade comum às séries aparece uma única vez dentro do detalhe aberto; motivos diferentes permanecem localizados no indicador afetado.
- O disclaimer esclarece apoio educacional, sem competir com a evidência principal.

## Prototype

- Caminho versionado: `frontend/public/prototypes/card-384-favorites-analysis-hierarchy/index.html`
- URL canônica: `https://dev.criptofarol.com.br/prototypes/card-384-favorites-analysis-hierarchy/`
- Conteúdo representativo: `BTC 1D Long — Médias: Virada Inicial`, EMA 16, SMA 17, SMA 33 e stop de 8,50%.
- Interações: abrir/recolher detalhes técnicos, alternar referência do gráfico e abrir menu móvel.

## Design Critique

### Assessment A — produto e hierarquia

Executado em-thread antes de introduzir achados determinísticos no julgamento. A composição é específica do Cripto Farol: tese, direção, stop, regras permanentes, gráfico, sinais e operações formam uma narrativa de decisão que não poderia ser aplicada sem alterações a um dashboard genérico. A ordem de leitura está clara e a carga cognitiva é baixa. Achados: materializar estados degradados na implementação e considerar persistência da preferência do disclosure para especialistas.

### Assessment B — UX, acessibilidade e responsividade

Executado em-thread após Assessment A. O detector final retornou `[]`; a injeção no navegador registrou `[impeccable] No anti-patterns found`. O browser gate confirmou desktop 1440×900 e mobile 390×844 sem overflow, descrição completa, um único heading de parâmetros, controles de zoom visíveis, disclosure operável, menu móvel fora da árvore de foco quando fechado, foco transferido/restaurado e zero erros de console/página.

### Design Agent verdict

`BLOCKED`: a sessão atual não oferece evidência observável de que dois critics independentes herdariam exatamente o mesmo LLM/modelo e versão da sessão principal. O protótipo e as avaliações locais podem ser concluídos, mas o card não será movido para `Aprovação de Design` sem satisfazer esse contrato.

## Impeccable Critique

`⚠️ DEGRADED: single-context` porque a igualdade exata de modelo/versão dos critics independentes não pôde ser observada. Score em-thread: `34/40 (Good)`, sem P0/P1. Pontos fortes: hierarquia decision-first, gráfico dominante, transparência sem duplicação e reflow móvel. Pendências P2: estados degradados devem respeitar a mesma arquitetura; avaliar persistência do disclosure. Snapshot: `.impeccable/critique/2026-08-06T18-33-56Z__s-card-384-favorites-analysis-hierarchy-index-html.md`.

## Impeccable Audit

Audit Health Score: `19/20 (Excellent)`.

| Dimensão | Score | Evidência |
| --- | --- | --- |
| Accessibility | 4/4 | Contrastes mínimos medidos: texto 16.35:1, auxiliar 6.12:1, verde 8.18:1, vermelho 4.93:1; nomes acessíveis, headings, alt text, foco e targets verificados. |
| Performance | 4/4 | HTML/SVG local, sem dependências, loops, requests de dados ou efeitos caros. |
| Responsive | 4/4 | 1440×900 e 390×844 com `scrollWidth - innerWidth = 0`; controles e conteúdo preservados. |
| Theming | 4/4 | Tokens alinhados a `DESIGN.md`; hook e detector sem findings. |
| Implementation Integrity | 3/4 | Solução coerente e específica; estados assíncronos/degradados permanecem como contrato para a implementação React. |

Checklist básico de acessibilidade: contraste `PASS`; alternativas de texto `PASS`; teclado e foco `PASS` após remover o drawer fechado da árvore; labels de controles `PASS`; formulários `N/A`.

## Impeccable Trace

- `context`: `node .agents/skills/impeccable/scripts/context.mjs --target frontend/src/pages/ComboResultsPage.tsx` — executado uma vez; resolveu `PRODUCT.md`, `DESIGN.md` e o alvo real.
- `shape`: brief registrado acima com base no relato detalhado, na inspeção da interface atual e nas restrições do card.
- `prototype`: criado em `frontend/public/prototypes/card-384-favorites-analysis-hierarchy/index.html`; SHA-256 final `21fa15496e3334f5930c08c6e97c77a25d847564c4e05f5af76beb62854cb50f`.
- `critique`: Assessment A foi concluído antes do detector; Assessment B usou detector e navegador em contexto único. Resultado degradado `34/40`, sem P0/P1; dual-agent permanece bloqueado.
- `audit`: detector final `[]`; overlay injetado em navegador real retornou nenhum antipadrão; audit manual `19/20`.
- `targeted fixes`: tokens fora da rampa corrigidos; indisponibilidade consolidada; controles de zoom preservados no mobile; contraste auxiliar elevado; drawer fechado removido da árvore de foco; ação de fechar e restauração de foco adicionadas.
- `polish`: copy, espaçamento, reflow, alvos de toque, tabela mobile, legenda, disclaimer e fidelidade ao shell revisados na tela completa.
- `browser gate`: servidor local `http://127.0.0.1:4174`; Chromium Playwright existente; viewports 1440×900 e 390×844; asserts de descrição completa, ocorrências únicas, disclosure, referência, zoom, drawer, foco, overflow e console todos verdes. Capturas em `output/playwright/card-384-desktop.png` e `output/playwright/card-384-mobile.png` (não versionadas).

## Prototype Validation

- Versão validada: SHA-256 `21fa15496e3334f5930c08c6e97c77a25d847564c4e05f5af76beb62854cb50f`.
- URL local: `http://127.0.0.1:4174/prototypes/card-384-favorites-analysis-hierarchy/`.
- Desktop 1440×900: descrição completa; `Parâmetros efetivos = 1`; `Detalhes técnicos = 1`; aviso comum de séries indisponíveis = 1; disclosure e referência do candle funcionais; overflow 0.
- Mobile 390×844: descrição completa; zoom −/+/reset e referência visíveis; menu abre/fecha com foco correto e Escape; drawer fechado não possui links visíveis/focáveis; disclosure funcional; overflow 0.
- Console e page errors: `[]`.
- URL canônica validada: `https://dev.criptofarol.com.br/prototypes/card-384-favorites-analysis-hierarchy/`; o conteúdo HTTP e o arquivo versionado têm o mesmo SHA-256 `21fa15496e3334f5930c08c6e97c77a25d847564c4e05f5af76beb62854cb50f`.
- Gate HTTPS repetiu todos os asserts de desktop/mobile e retornou `errors=[]` e `failed requests=[]`; capturas em `output/playwright/card-384-canonical-desktop.png` e `output/playwright/card-384-canonical-mobile.png` (não versionadas).
- Ferramenta: o wrapper Playwright CLI não pôde iniciar porque procurou `/opt/google/chrome/chrome`; foi usado o Chromium Playwright já instalado em `/home/ubuntu/.cache/ms-playwright/chromium-1234/chrome-linux/chrome` pelo runtime Playwright do projeto.
- Qualquer alteração posterior ao HTML invalida esta validação e exige nova rodada.

## Risks / Trade-offs

- [Detalhes fechados podem reduzir descoberta por usuários especialistas] → mostrar contagem/resumo e rótulo explícito no controle.
- [Remover duplicação pode apagar contexto útil do gráfico] → manter legenda compacta com nome, cor e valor no candle; remover apenas ficha completa repetida.
- [Payload legado pode não oferecer todas as métricas] → manter estado indisponível localizado sem inventar valores.
- [Descrição e tabela podem estourar em mobile] → validar copy real em 390 px e reflow rotulado das operações.
- [Responsabilidade compartilhada pode regredir em mudanças futuras] → testes por ocorrência de rótulos e contrato de ownership.

## Migration Plan

1. Após aprovação humana, implementar a nova composição em componentes existentes sem alterar API.
2. Adaptar testes unitários para ownership e ausência de duplicação.
3. Atualizar Playwright desktop/mobile e baselines visuais intencionais.
4. Integrar em `develop`, executar restart e validar a URL antes de `Done`.
5. Rollback: reverter o único commit da mudança, pois não há migração de dados.

## Open Questions

- Gate operacional: como fornecer evidência observável do mesmo LLM/modelo e versão aos dois critics independentes exigidos pelo processo Codex.
