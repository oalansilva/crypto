# Crítica independente de Design — #1087

## Metadata

- Data: 2026-10-13 UTC.
- Papel: design-critic; rodada sem-tela, 1 autor + 1 crítico + até 1 rework.
- Card: https://github.com/oalansilva/crypto/issues/1087.
- Estado e branch informados: Design; card-1087-calendario-mensal.
- Escopo de escrita: somente este snapshot; nenhum código, artefato OpenSpec, evento ou status modificado.
- Skill lida: `.cursor/skills/design-critic/SKILL.md` no worktree.
- Modelo/esforço solicitado: `gpt-6-astra` / `medium`.
- Captura lida: `/tmp/card-1087-design-critic-20261013.json`.
- attempt_id: `67d9f323-158e-4756-aeeb-8a3d9d9a20e4`.
- capture_sha256: `53ce1d6929973699f27cb4adcea21ace05eac573e5757cd11cf18a84a1d6545e`.
- Payload observado de runtime: unavailable. A captura registra seleção e argumentos solicitados; não observa independentemente o modelo/esforço efetivo.

## Evidências consultadas

Leitura integral de proposal, design, tasks e `specs/sweep-calendar-parity/spec.md` em `openspec/changes/card-1087-calendario-mensal/`. Body atual do card consultado por `gh api repos/oalansilva/crypto/issues/1087`. Esta revisão avalia o contrato documental; não afirma execução de testes funcionais.

## Avaliação de produto, escopo e contrato

O problema e os limites do card estão refletidos na proposta. O contrato define as cinco opções `1m`, `3m`, `6m`, `1y` e `2y` como deslocamentos diretos de 1, 3, 6, 12 e 24 meses da referência UTC original. Preserva o dia quando válido e limita ao último dia do mês de destino quando necessário. O deslocamento direto evita encurtamento cumulativo.

Todos os exemplos do card estão cobertos: 2026-05-15 → 2026-04-15, 2026-03-31 → 2026-02-28, 2026-05-31 → 2026-04-30, 2024-03-31 → 2024-02-29, 2024-02-29 → 2023-02-28 e 2026-05-15 → 2025-05-15. A matriz contempla todas as opções, fevereiro bissexto e virada de ano, preservando a data final.

A paridade abrange apresentação existente, payloads e janela consumida. O plano reconhece que a Descoberta recebe datas explícitas do frontend: corrigir somente o fallback do backend seria insuficiente. As tasks cobrem relógio controlado, preflight/criação, envio do Combo, fallback e precedência das datas explícitas, sem reinterpretar snapshots antigos.

O contrato preserva `15d`, personalizado e todo o histórico, incluindo nulos, campos vazios e impedimentos existentes, assim como opções, labels e defaults. Ranking e execução do backtest permanecem fora do escopo. Igualdade depende da mesma referência UTC, conforme o card; sincronização de relógios não vira requisito novo.

## Gate de superfície

- `UI impact: none` presente em linha própria.
- `live_route: N/A correção de aritmética de calendário; sem alteração de apresentação` presente em linha própria.
- `surface: none` presente em linha própria.
- Classificação sem-tela coerente: valores corrigidos usam a apresentação existente, sem novo layout, texto, controle, estado ou navegação. Não há rota de catálogo emprestada nem protótipo necessário.

## Achados e disposition

- P0: nenhum.
- P1: nenhum.
- P2: nenhum.
- P3: formato/local da matriz compartilhada de testes é detalhe de Apply; disposition: aceito, já previsto no design. Não exige rework ou decisão de produto.
- Disposition geral: contrato atende ao card; nenhuma pendência de produto, escopo ou contrato visível encontrada.
- Verdict: PASS para conclusão da crítica e encaminhamento pelo orquestrador ao gate humano de Design. Não constitui aprovação humana, mudança de Status ou autorização de implementação.

## Limites

Revisão documental independente, sem navegação ou auditoria visual porque a mudança é sem-tela. Correção e regressões serão demonstradas no Apply conforme as tasks; esta crítica não substitui essa evidência. Nenhuma segunda rodada solicitada e nenhum P0 novo identificado.
