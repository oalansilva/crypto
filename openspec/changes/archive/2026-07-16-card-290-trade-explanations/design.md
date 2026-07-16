## Context

O backend já constrói um `StrategyTransparency` a partir do template executável e devolve séries timestampadas dos indicadores. Os trades salvos contêm horários/preços e motivo de saída, mas não contêm evidência de entrada/saída. O frontend exibe a tabela em `StrategyTradesTable`, enquanto o Monitor usa `signal_history` e o endpoint de trades do Favorito.

A mudança atravessa schema, serviço de transparência, rotas de Favoritos/Oportunidades e UI do Monitor. A explicação pública deve permanecer útil para usuário comum sem expor código-fonte, diagnósticos ou controles internos.

## Goals / Non-Goals

**Goals:**

- Explicar entrada e saída de cada trade de todas as estratégias ativas usando a configuração executada e valores históricos do evento.
- Distinguir regra da estratégia, stop, objetivo real e posição aberta, com semântica correta para `long` e `short`.
- Expor um contrato aditivo e seguro para Monitor/Favoritos.
- Oferecer uma experiência acessível “Entenda este trade” em desktop e mobile.
- Falhar de forma explícita quando a evidência histórica não puder ser comprovada.

**Non-Goals:**

- Alterar sinais, métricas, parâmetros, execução, stop ou resultado financeiro.
- Criar take profit, saída parcial ou múltiplas saídas onde o motor não oferece essas funções.
- Reconstruir um trade antigo usando valores atuais ou configuração divergente.
- Expor expressão bruta, código-fonte ou payload diagnóstico como explicação pública.

## Decisions

### Decision: contrato de explicação tipado e aditivo no backend

Adicionar modelos `TradeExplanation`, `TradeExplanationEvent` e `TradeEvidenceItem`. Cada trade terá `entry_explanation`, `exit_explanation` e `current_state_explanation` opcionais; sinais do Monitor poderão carregar `explanation`. O contrato registra status (`available`, `partial`, `unavailable`, `inconsistent`), direção, timeframe, ação pública, gatilho, resumo, candle de decisão, execução, preço e evidências históricas.

Alternativa rejeitada: gerar texto somente no frontend. Isso não consegue provar valores históricos, motivo do stop nem defasagem entre confirmação no candle N e execução no N+1.

### Decision: explicações derivadas do manifesto canônico e séries timestampadas

O manifesto ganhará resumos públicos específicos das regras de entrada/saída/risco, derivados da configuração executada. O serviço de explicação selecionará apenas indicadores cuja `participation` corresponda ao evento e localizará os pontos no candle de decisão. Para regras executadas na abertura seguinte, o candle de decisão será o ponto confiável anterior à execução; stop usa o instante/preço registrado.

Quando não houver séries ou alinhamento temporal confiável, o status será `unavailable`/`partial` com motivo explícito. Nunca usar o último valor atual para explicar evento histórico.

Alternativa rejeitada: persistir imediatamente uma nova estrutura em todos os trades legados. Isso exigiria migração e poderia congelar explicações inconsistentes; o contrato aditivo permite regenerar com o contexto canônico disponível e marcar legado sem prova como indisponível.

### Decision: um serviço único atende Favoritos e Monitor

Criar um builder puro de explicações, reutilizado por `GET /favorites/{id}/trades` e pelo payload de Oportunidades. Isso mantém a mesma linguagem, direção e evidência nas duas superfícies. A redaction pública preservará somente o contrato curado da explicação e continuará removendo segredos.

### Decision: disclosure acessível sem ampliar a tabela horizontal

`StrategyTradesTable` exibirá um botão “Entenda este trade” por operação, com `aria-expanded`, `aria-controls`, foco visível e painel de detalhes em uma linha própria. O Monitor apresentará resumo curto no detalhe e a explicação completa em `Ver Trades`. Não serão adicionadas colunas técnicas, reduzindo overflow mobile.

Aplicação do `DESIGN.md`: canvas `#0b0e11`, card `#1e2329`, hairline `#2b3139`, texto `#eaecef/#929aa5`, foco `#3b82f6`, trading up/down apenas para semântica, radius 6–8px, espaçamento 8/12/16px e números em fonte monoespaçada/BinancePlex existente. Estado nunca dependerá só de cor.

### Decision: cobertura de catálogo bloqueia drift

Testes tabulares usarão o catálogo exportado para exigir nome, regras públicas de entrada/saída e explicação segura para cada estratégia ativa. Testes focados cobrirão `long`, `short`, saída lógica, stop, posição aberta e indisponibilidade histórica. Playwright validará disclosure, teclado, desktop e mobile.

## Risks / Trade-offs

- [Lógicas heterogêneas e complexas] → humanizar somente tokens/operadores allowlisted; manter estrutura booleana em PT-BR e marcar parcial quando algo não puder ser traduzido.
- [Candle de decisão ausente em cache legado] → não inferir com valor atual; retornar indisponibilidade explícita.
- [Manifesto salvo desatualizado] → preferir manifesto recalculado no mesmo timeframe/contexto quando disponível e validar timestamps.
- [Vazamento de lógica protegida] → expor resumo funcional curado e evidências allowlisted; nunca expressão bruta, identificadores internos ou diagnósticos.
- [UI densa no mobile] → disclosure empilhado dentro da operação, sem novas colunas e com alvos de 44px.

## Migration Plan

1. Publicar schema e builders de forma retrocompatível.
2. Enriquecer respostas de trades e oportunidades sem remover campos atuais.
3. Consumir campos novos no frontend com fallback explícito para payloads antigos.
4. Validar catálogo, API, build e Playwright desktop/mobile.
5. Rollback: remover consumo da UI e campos aditivos; nenhum dado ou regra de execução é migrado.

## Open Questions

- Nenhuma decisão de produto pendente. Saídas parciais/objetivo permanecem ausentes quando o motor não os executa.
