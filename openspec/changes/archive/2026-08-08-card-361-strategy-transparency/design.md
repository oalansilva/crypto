## Context

O Cripto Farol já calcula um manifesto seguro em `backend/app/services/strategy_transparency.py` e já o utiliza no gráfico de estratégia e no resumo permanente de regras. Porém, os endpoints de Favoritos/Monitor ainda usam `can_view_strategy_secrets` como autorização para o detalhe funcional: usuários autenticados comuns recebem `is_strategy_protected=true`, parâmetros vazios e a copy `Estratégia protegida`. No Monitor, `OpportunityCard` também omite controles e detalhes; em Favoritos/Resultados, a tela mostra “Parâmetros técnicos protegidos para este perfil”.

O card #361 altera a decisão de produto: transparência funcional é permitida para todo trader autenticado. Isso não autoriza exposição de credenciais, tokens, código-fonte, colunas diagnósticas ou controles administrativos. O shell, os tokens visuais e as regras de execução permanecem os atuais.

Superfícies de referência:

- Monitor autenticado: `frontend/src/components/monitor/OpportunityCard.tsx` e `ChartModal.tsx`.
- Favoritos autenticado: `frontend/src/pages/FavoritesDashboard.tsx`, `ComboResultsPage.tsx` e `StrategyChartSurface.tsx`.
- Contrato canônico compartilhado: `backend/app/services/strategy_transparency.py`, `backend/app/schemas/strategy_transparency.py` e `frontend/src/lib/strategyTransparency.ts`.
- Copy atual a revisar: `backend/app/services/strategy_descriptions.py`.

## Goals / Non-Goals

**Goals:**

- Entregar um manifesto funcional único e seguro para cada estratégia ativa, com nome e descrição específicos ao comportamento executado.
- Mostrar o mesmo nome, descrição, direção, timeframe, indicadores, parâmetros, regras de entrada/saída e risco em Favoritos e Monitor.
- Remover a experiência de ocultação para o usuário autenticado comum sem transformar segredo técnico em dado público.
- Usar rótulos de trader em português, preservando valores e unidades exatos do manifesto.
- Dar ao usuário uma hierarquia legível: identidade e tese primeiro; regras, indicadores e parâmetros em detalhe progressivo; indisponibilidade explícita quando não houver prova.
- Cobrir catálogo, payloads e superfícies com testes determinísticos e E2E desktop/mobile.

**Non-Goals:**

- Alterar regras de entrada, saída, sinais, backtests, trades, indicadores calculados ou otimização.
- Expor source code, credenciais, tokens, colunas internas, IDs de execução ou controles de mutação.
- Liberar endpoints públicos ou remover autenticação/ownership das rotas de Favoritos e Monitor.
- Redesenhar o shell, navegação, gráficos ou layout inteiro das páginas.
- Inventar uma explicação quando template, indicador, série ou timeframe não puder ser comprovado.

## Decisions

### 1. Separar detalhe funcional de segredo administrativo

Adicionar uma decisão explícita de autorização para `strategy_details` (usuário autenticado) e manter `can_view_strategy_secrets` para permissões administrativas e fluxos que realmente dependem de segredo. Os redactors não devem mais usar `include_secrets=false` para apagar o manifesto funcional do usuário autenticado. O redactor continuará aplicando uma allowlist: manifesto, parâmetros efetivos e campos operacionais necessários entram; código, credenciais, tokens, diagnósticos e controles ficam fora.

Alternativas consideradas:

- Tornar todo usuário administrador: rejeitado, pois amplia permissões de catálogo/gestão além do card.
- Enviar tudo e filtrar no React: rejeitado, pois dados proibidos chegariam ao cliente e poderiam vazar por export/telemetria.
- Manter a proteção e criar uma segunda API paralela: rejeitado, pois duplicaria o contrato e permitiria divergência entre Favoritos e Monitor.

### 2. Manifesto como fonte única de identidade e detalhe

Consolidar a superfície de detalhe em um componente/adaptador reutilizável que consuma `StrategyTransparency`. O Monitor usará a variante compacta no card e o gráfico/modal usará a variante completa; Favoritos/Resultados usará a mesma variante completa. A copy de `strategy_descriptions.py` será a identidade canônica, mas o texto deve ser coerente com o template efetivamente resolvido.

O componente terá quatro grupos:

1. Identidade: nome, tese, direção, timeframe e quantidade de indicadores.
2. Regras: par permanente “Quando compra” / “Quando vende”, mais risco quando declarado.
3. Indicadores: nome legível, tipo/configuração, função, painel/escala e participação.
4. Parâmetros efetivos: direção, timeframe, thresholds, períodos, stops e filtros allowlisted.

`status=unavailable` e `timeframe_mismatch` serão estados de primeira classe, com mensagem clara e sem fallback genérico.

Alternativas consideradas:

- Renderizar apenas os campos brutos de `parameters`: rejeitado, pois não explica função/participação e não garante paridade.
- Criar cópia de manifestos dentro de cada tela: rejeitado, pois nomes e regras divergiriam com o tempo.
- Mostrar todos os detalhes sempre no topo do card: rejeitado, pois aumenta carga cognitiva; identidade fica visível e detalhe usa disclosure acessível.

### 3. Catálogo distinto e testável

Revisar `PUBLIC_STRATEGY_DISPLAY_NAMES` e `PUBLIC_STRATEGY_DESCRIPTIONS` em conjunto com a matriz de templates ativos. Nomes devem diferenciar família, comportamento, direção e proteção/saída quando isso for parte da configuração; datas, `WINNER`, `chain`, IDs e frases genéricas isoladas não serão a identidade exibida. Testes detectarão duplicidade normalizada, indicadores mencionados sem configuração e ausência de explicação de entrada/saída/risco.

### 4. Protótipo baseado no shell atual

O protótipo usa o shell real do produto: canvas `#0b0e11`, superfície `#181a20`/`#1e2329`, borda `#2b3139`, Inter, amarelo `#fcd535`, verde/red semântico e sidebar de 224px no desktop. O delta é limitado ao bloco de estratégia transparente e à mesma leitura no quadro de Favoritos. No mobile a sidebar vira menu, a grade colapsa para uma coluna e os controles mantêm alvo mínimo de 40–44px.

## Risks / Trade-offs

- [Risco] Um template antigo pode não ter configuração ou série confiável → [Mitigação] estado `unavailable`/`timeframe_mismatch`, sem inventar dados; teste de cenário obrigatório.
- [Risco] Alterar a semântica de `is_strategy_protected` pode quebrar testes e consumidores legados → [Mitigação] introduzir `strategy_details` separado, atualizar contratos e manter compatibilidade de leitura sem usar o flag para ocultar detalhe funcional autenticado.
- [Risco] Parâmetros efetivos podem conter campos internos não destinados ao trader → [Mitigação] allowlist no backend e formatação/rótulos compartilhados no frontend.
- [Risco] Copy de catálogo pode prometer mais do que a regra executa → [Mitigação] revisão contra `template_data` e teste que cruza indicadores/regras declarados com o manifesto.
- [Risco] Detalhe completo aumenta altura do card e densidade mobile → [Mitigação] progressive disclosure, resumo sempre visível, grid responsivo e validação em 390px, 768px e desktop.
- [Risco] Mudança de UI aprovada pode ficar divergente do protótipo → [Mitigação] usar os mesmos tokens/componentes do shell e reexecutar browser gate após qualquer alteração.

## Migration Plan

1. Atualizar OpenSpec, catálogo e contrato de autorização/allowlist na branch do card.
2. Implementar o painel reutilizável e integrar Monitor/Favoritos sem alterar a lógica de execução.
3. Rodar testes backend/frontend focados, E2E visual desktop/mobile, `openspec validate --all` e `/opsx:verify`.
4. Integrar a branch em `develop`, reiniciar DEV e validar Monitor/Favoritos autenticados.
5. Rollback: reverter o commit da branch integrada; a mudança não exige migração de banco e não altera sinais ou dados persistidos.

## Open Questions

- Nenhuma decisão de produto pendente para iniciar: Alan já decidiu transparência total para trader autenticado e exclusão de segredos.
- A aprovação humana do design ainda é necessária antes de mover o card de `Aprovação de Design` para `Pronto para Dev`.

## Impeccable Brief

- **Problema:** o trader vê nomes genéricos e, em alguns perfis, não consegue auditar a configuração que gerou o sinal.
- **Usuário e modo:** trader autenticado em operação, alternando entre Monitor e Favoritos para confirmar contexto e risco.
- **Resultado:** em poucos segundos, identificar a tese, o lado, o timeframe, as regras, os indicadores e a proteção sem copiar nomes internos.
- **Direção:** transparência operacional em progressive disclosure; preservar shell escuro e denso do Cripto Farol, usando amarelo apenas para foco/ação e verde/vermelho para semântica de mercado.
- **Escopo:** card do Monitor, análise de Favoritos e componentes de detalhe compartilhados; desktop e mobile.
- **Estados:** disponível, detalhes recolhidos, detalhes expandidos, indisponível, timeframe incompatível, Long/Short, paridade BTC/ETH e menu móvel aberto/fechado.
- **Interações:** navegação Monitor/Favoritos, abrir/recolher detalhes, abrir análise, foco de teclado e leitura por tecnologia assistiva.
- **Restrições:** autenticado; sem source code, credenciais, tokens, diagnósticos ou redesign do shell; dados não comprovados não são inventados.

## Prototype

- **URL:** https://dev.criptofarol.com.br/prototypes/card-361-strategy-transparency/
- **Arquivo versionado:** `frontend/public/prototypes/card-361-strategy-transparency/index.html`
- **Versão:** 1.1.
- **Digest SHA-256:** `fc9b94a7c818d1daff9cbe9d97b3fec3e33ca52f9ebc602a4dd38f6f7a5924fe`.
- **Base:** shell de `AppNav`/`Layout`, tokens de `frontend/src/index.css` e estrutura de `OpportunityCard`/`StrategyChartSurface`.
- **Desktop:** sidebar 224px, header, card de oportunidade com identidade, regra, indicadores, risco e parâmetros.
- **Mobile:** menu móvel, uma coluna, detalhes e tabela responsivos, alvos de toque preservados.
- **Estados e delta:** disponível expandido, disclosure recolhido/expandido, indisponível com retry, mismatch 4H/1D com `aria-live`, Short com regra/stop/params, paridade de detalhe na tabela de Favoritos, drawer móvel com foco contido e conta expandível.

## Design Critique

Status: PASS no digest `fc9b94a7c818d1daff9cbe9d97b3fec3e33ca52f9ebc602a4dd38f6f7a5924fe`.

- **Assessment A — Hegel (`019fc7cb-81d6-71d1-b05f-559945dbb69a`):** auditoria independente read-only, Chromium em `1440x900`/`390x844`, Nielsen `36/40`, nenhum P0/P1/P2. Confirmou Combo oculto para trader comum, rotas reais, drawer `role=dialog` com trap/restauração de foco, DEV mobile, Conta, rail/Menu, estados e paridade. O relatório marcou `BLOCKED` somente porque este `design.md` ainda estava pendente no momento da leitura e porque o subagent não expõe o registro de spawn; ambos estão resolvidos/registrados nesta versão.
- **Assessment B — Russell (`019fc7cb-8206-7381-b991-e2fcef7c4e37`):** browser gate independente read-only, PASS em desktop/mobile; confirmou disclosure, Short, BTC/ETH, indisponível/retry, mismatch/`aria-live`, Conta, links, Combo ausente, colapso/rail, foco e zero erros.
- Nenhum critic alterou arquivos, Git, board, produção ou dados.

## Prototype Validation

Rodada local final executada em `http://127.0.0.1:8401/prototypes/card-361-strategy-transparency/` com Chromium real (`/usr/bin/chromium-browser`) em `1440x900` e `390x844`. Asserts: Monitor e disclosure; Short com `Short`, `4H`, stop e foco; paridade de regra BTC Monitor/Favoritos; detalhe ETH com Volume e foco; indisponível substitui todo detalhe e retry restaura; mismatch anuncia `4H`/`1D`; sidebar colapsa para `Menu`; Conta abre/fecha com `aria-expanded`; DEV permanece visível no mobile; drawer recebe foco, mantém Tab, fecha com Escape e restaura foco; navegação mobile; overflow horizontal. Resultado: PASS, sem console errors, page errors ou failed requests. Evidência visual: `/tmp/card-361-final-v3-mobile.png` e screenshots canônicos registrados na rodada HTTPS final.

URL canônica também validada em `https://dev.criptofarol.com.br/prototypes/card-361-strategy-transparency/` antes da remoção do artefato temporário e do restart de restauração do DEV; resultado PASS nos dois viewports, sem console/page/request errors. A evidência canônica é vinculada à mesma versão/digest publicado temporariamente e foi removida antes do fechamento.

## Impeccable Critique

O detector local reportou somente `overused-font` para `Inter` na linha 27. Classificação: aviso não bloqueante/false positive de identidade visual, pois `Inter` é a tipografia canônica do produto em `DESIGN.md`/shell atual. Nenhum erro de semântica, foco, estado ou responsividade ficou aberto após a rodada de correções.

## Impeccable Audit

Checklist final: shell preservado com sidebar/header, tokens e gradiente atuais; hierarquia de identidade antes de regras; progressive disclosure; estados disponível/indisponível/mismatch; Long/Short; paridade de manifestos; foco visível e foco contido no drawer; alvos móveis; zero overflow; account menu com `aria-expanded`; disclaimer de apoio educacional. O único aviso do detector foi classificado como advisory.

## Impeccable Trace

- Skills usadas: `design-critic`, `impeccable` (`shape`, `critique`, `audit`, `polish`, `operate`, `craft-floor`), `playwright` e OpenSpec (`openspec-new-change`, `openspec-ff-change`).
- Comandos: `openspec new change`, `openspec status --change ... --json`, `openspec instructions ... --json`, `node .agents/skills/impeccable/scripts/detect.mjs --json ...`, browser Chromium real local/DEV e `sha256sum`.
- Digest auditado: `fc9b94a7c818d1daff9cbe9d97b3fec3e33ca52f9ebc602a4dd38f6f7a5924fe`.
- Delegação: critics finais foram criados read-only com `model`, `reasoning_effort` e `service_tier` omitidos para herdar o modelo da sessão principal; `fork_context=false`; nenhum override de modelo foi usado. O cliente não expõe um inspector separado de runtime para imprimir o identificador efetivo, então a evidência disponível é a configuração de spawn por herança e a ausência de override.
- Vínculo final: Hegel (`019fc7cb-81d6-71d1-b05f-559945dbb69a`) e Russell (`019fc7cb-8206-7381-b991-e2fcef7c4e37`) auditaram o mesmo digest; o detector tem somente o advisory `Inter`; os browsers local/canônico passaram.

Design Agent verdict: PASS — design aprovado por Alan ao mover o card de `Aprovação de Design` para `Pronto para Dev`; implementação autorizada.
