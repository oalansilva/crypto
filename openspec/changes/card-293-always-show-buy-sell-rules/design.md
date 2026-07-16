## Context

O card #290 criou explicações contextuais por evento (`entry_explanation`, `exit_explanation` e `current_state_explanation`). A UI escolhe blocos conforme o evento disponível; por isso um trade aberto pode mostrar apenas entrada/posição atual e um trade fechado prioriza o que aconteceu, sem um contrato visual fixo com as duas regras da estratégia.

## Goals / Non-Goals

**Goals:**

- Transportar um par público, tipado e direcional de regras permanentes de entrada/saída em toda explicação.
- Renderizar “Quando compra” e “Quando vende” antes dos detalhes contextuais, em qualquer posição.
- Manter linguagem correta para `long` e `short`, fallback seguro e responsividade.

**Non-Goals:**

- Alterar o motor de sinais ou interpretar o estado atual como regra permanente.
- Expor lógica bruta, código, nomes internos ou evidência histórica como condição universal.
- Criar take profit ou saída parcial.

## Decisions

### Decision: preservar os blocos tipados do manifesto no frontend

Alterar `normalizeStrategyTransparency` para preservar `participation`, `description`, `status`, `operator` e `condition_count` de cada `logic_block`, em vez de achatá-lo para texto. Um helper extrai `entry`, `exit` e `risk` e aplica os rótulos direcionais a partir de `direction`.

O backend já entrega esses blocos humanizados e protegidos para todas as estratégias; reutilizá-los evita duplicar regra por trade ou ampliar a API. Quando o manifesto estiver ausente/legado, a UI mostra as duas linhas com indisponibilidade explícita.

Alternativas rejeitadas: usar `entry.summary`/`exit.summary`, pois descrevem eventos ocorridos; ou duplicar o par dentro de cada `TradeExplanation`, aumentando payload sem necessidade.

### Decision: regras permanentes antes do contexto do trade

Criar um `StrategyRuleOverview` reutilizável. O card expandido do Monitor mostra sempre o grupo “Como funciona a estratégia”, com “Quando compra” e “Quando vende”. O disclosure de trades usa o mesmo grupo antes de “Por que entrou”, “Por que saiu” ou “Por que continua aberto”. Assim o usuário distingue contrato da estratégia de evento atual.

Para `short`, os rótulos continuam amigáveis, mas as ações informam “Venda/Short” na entrada e “Compra/Cobertura” na saída. Estado não depende apenas de verde/vermelho.

### Decision: fallback seguro e cobertura de catálogo

Quando os `logic_blocks` faltarem ou o manifesto não permitir tradução segura, os dois cards continuam presentes com mensagem de indisponibilidade. A cobertura backend existente continua garantindo regras para todo template ativo; testes frontend cobrem estados aberto, fechado e legado.

Aplicação do `DESIGN.md`: superfícies `#0b0e11/#1e2329`, hairline `#2b3139`, texto `#eaecef/#929aa5`, foco `#3b82f6`, radius 6–8px, gaps 8/12/16px, alvo de 44px e layout sem nova coluna.

## Risks / Trade-offs

- [Propagação do manifesto até a tabela] → adicionar uma prop tipada única em `StrategyTradesTable` e reutilizar o mesmo componente.
- [Payload legado sem `logic_blocks`] → renderizar ambos os cards como indisponíveis, sem usar valores atuais.
- [Confusão em estratégia short] → exibir ação direcional dentro de cada card e validar copy em testes.
- [Painel mais denso] → resumo em dois cards compactos; detalhes históricos continuam abaixo e colapsados pelo disclosure.

## Migration Plan

1. Preservar metadados de `logic_blocks` no normalizador frontend.
2. Criar e integrar o overview reutilizável no card e no disclosure.
3. Propagar o manifesto já disponível por `ChartModal` e `ComboResultsPage`.
4. Validar unidade, acessibilidade e Playwright desktop/mobile.
5. Rollback: remover o overview/prop; API, execução e dados persistidos permanecem inalterados.

## Open Questions

- Nenhuma.
