## Context

O Cripto Farol já possui um gate obrigatório de Design, o contrato canônico `.agents/skills/design-critic/SKILL.md`, protótipos HTML versionados e validação em navegador real. O repositório ainda não possui a skill Impeccable, `PRODUCT.md` ou hook Codex.

Esta change integra o Impeccable somente ao Codex. O Cursor permanece usando o contrato atual de `design-critic`. O `DESIGN.md` existente continua sendo a fonte de verdade visual do produto e não pode ser sobrescrito pelo setup do Impeccable.

## Goals / Non-Goals

**Goals:**

- Instalar uma versão local, reproduzível e pinada do Impeccable para o Codex.
- Acrescentar brief estruturado, crítica independente, detector técnico e polish ao gate de Design.
- Fazer os dois critics usarem exatamente o mesmo LLM/modelo e versão da sessão principal.
- Preservar a aprovação humana de Alan e os gates de navegador, OpenSpec e Kanban existentes.
- Registrar evidência suficiente para reproduzir o resultado e distinguir achados bloqueantes de riscos aceitos.

**Non-Goals:**

- Alterar UI de produção, API, banco, runtime ou comportamento de cards existentes.
- Instalar ou alterar o provider Cursor.
- Reabrir ou reutilizar os cards cancelados 362 e 369.
- Substituir o `design-critic`, o `DESIGN.md` ou a aprovação humana por uma pontuação automática.
- Criar fallback para outro LLM quando a herança do modelo principal não puder ser comprovada.

## Decisions

### Instalação e versionamento

Usar instalação project-local do provider Codex (`--providers=codex --scope=project`), versionar `.agents/skills/impeccable/` e `.codex/hooks.json`, e registrar separadamente o pacote CLI npm `impeccable@3.5.0`, o payload da skill `4.0.4` e o `gitHead` npm `9a949fb543d44cfb406f61bcab99d95d7f12cf1d`. O hook será informativo durante edição; o gate final continua sendo executado pelo `design-critic` com evidência explícita.

### Contexto e fontes de verdade

Criar `PRODUCT.md` como contexto resumido para o Impeccable, derivado de `docs/project-hub.md`, `docs/mvp-scope.md` e `docs/brand-system.md`. O arquivo apontará para o `DESIGN.md` canônico, sem duplicar tokens. Se `impeccable init` tentar reescrever `DESIGN.md`, aceitar somente o contexto de produto e rejeitar a alteração visual gerada.

### Pipeline para UI impact: affected

O `design-critic` executará, nesta ordem:

1. `context.mjs` uma vez por sessão e leitura da superfície atual.
2. `$impeccable shape` antes de escolher ou editar a direção visual.
3. Protótipo versionado fiel ao shell existente.
4. `$impeccable critique` com Assessment A de UX/produto e Assessment B de detector/navegador.
5. `$impeccable audit` para acessibilidade, responsividade e performance.
6. `harden`, `adapt` ou `clarify` somente quando houver achado correspondente.
7. Correção em uma única rodada agrupada.
8. `$impeccable polish` como última alteração do protótipo.
9. Nova validação de navegador real desktop/mobile e asserts após a última alteração.

O fluxo terá no máximo uma rodada adicional de confirmação após a correção agrupada, seguindo a abordagem de passes limitados do Impeccable.

### Subagents e herança de modelo

Assessment A e Assessment B serão subagents separados, read-only e sem compartilhar resultados antes da síntese. Cada um deverá herdar exatamente o identificador e a versão do LLM/modelo da sessão principal do Codex. O effort acompanha a sessão principal por padrão. Se a igualdade do modelo ou a disponibilidade do subagent não puder ser observada, a etapa fica `BLOCKED` e não emite `PASS`.

### Evidência e critérios de PASS

O `design.md` da change/card terá `Impeccable Brief`, `Impeccable Critique`, `Impeccable Audit` e `Impeccable Trace`, além das seções existentes `Prototype`, `Prototype Validation` e `Design Critique`. `PASS` exige zero achado P0/P1 aberto, findings determinísticos resolvidos ou classificados, browser gate verde, asserts críticos verdes, console/page errors sem impacto no fluxo e digest da versão validada.

Para `UI impact: none`, Impeccable será registrado como `N/A` com justificativa, sem reduzir os gates de Design, Aprovação de Design ou aprovação de Alan.

## Risks / Trade-offs

- [Ruído do detector] → Findings P2/P3 podem ser classificados com justificativa e link para a decisão; nenhum finding fica sem estado.
- [Sobrescrita do DESIGN.md] → Validar o diff do `init` e rejeitar qualquer alteração não explicitamente aprovada.
- [Custo de dois subagents por card] → Usar contexto read-only, passes limitados e executar apenas em `UI impact: affected`.
- [Modelo do subagent não observável] → Bloquear o `PASS` em vez de usar fallback.
- [Hook incompatível] → Preservar entradas existentes, validar JSON e permitir desabilitar somente o alerta do hook; o gate documentado permanece obrigatório.

## Migration Plan

1. Instalar e pinar a skill em branch própria, preservando as alterações já pendentes de `AGENTS.md` e `rules.md`.
2. Criar `PRODUCT.md`, regras de `.impeccable` e hook Codex.
3. Atualizar `design-critic`, `openspec/config.yaml`, `AGENTS.md`, `rules.md` e o decision log.
4. Executar smoke test do detector em um protótipo existente e uma validação completa em um próximo card de UI do Codex.
5. A partir do merge da change, exigir o fluxo Impeccable para novos cards Codex com `UI impact: affected`.

Rollback: remover o hook e o provider Impeccable, mantendo `design-critic`, `DESIGN.md`, protótipos e gates de navegador. A remoção não altera código de produto nem status de cards.

## Open Questions

Nenhuma. A integração é Codex-only, obrigatória para UI affected e não modifica o provider Cursor.

## Design Gate Classification

- `UI impact: none`: esta change altera somente tooling, contexto, processo e documentação; não altera tela, rota, componente, token de produção ou protótipo de produto.
- A aprovação humana de Alan continua obrigatória para qualquer card futuro e não é simulada por este artifact.

## Prototype

`N/A`: a integração não cria nem altera uma superfície visual de produto. O smoke test usa um protótipo existente somente como alvo técnico do detector.

## Prototype Validation

`N/A`: não há versão de protótipo desta change para abrir em navegador. Cards futuros com `UI impact: affected` continuam obrigados a validar a versão final em desktop e mobile.

## Impeccable Brief

`N/A` para esta change sem UI. O contrato para cards com UI exige brief de problema, usuário, resultado, direção, escopo, estados, interação e restrições antes do protótipo.

## Impeccable Critique

`N/A` para esta change sem UI. O contrato futuro exige Assessment A de produto/UX/a11y/responsividade/estados e Assessment B de detector/navegador em contextos independentes e read-only.

## Impeccable Audit

`N/A` para esta change sem UI. O audit futuro cobre acessibilidade, performance, responsividade, theming e integridade da implementação.

## Impeccable Trace

- CLI: `impeccable@3.5.0`.
- Payload da skill: `4.0.4` (`.agents/skills/impeccable/SKILL.md`).
- `gitHead` npm: `9a949fb543d44cfb406f61bcab99d95d7f12cf1d`.
- Contexto executado: `node .agents/skills/impeccable/scripts/context.mjs --target frontend/public/prototypes/improve-wallet-screen/index.html`.
- Smoke target: `frontend/public/prototypes/improve-wallet-screen/index.html`.
- Detector executado: `node .agents/skills/impeccable/scripts/detect.mjs --json frontend/public/prototypes/improve-wallet-screen/index.html`.
- Resultado do detector: `[]` (zero findings; não houve finding para classificar ou resolver).
- Hook validado: `.codex/hooks.json` contém apenas os hooks oficiais `PostToolUse` e `Stop` do Impeccable nesta branch; não havia entrada não relacionada para preservar.
- `DESIGN.md` permaneceu sem alteração; digest validado: `sha256 02e3d8f4aa25bb1ce1e51b40c9070f3a619c9583c587751cc77e1f04b82f3072`.
- Crítica dual-agent: `N/A` nesta change sem UI; não houve spawn. Para UI affected, ausência de evidência observável de igualdade entre a sessão principal e os dois critics mantém o veredito `BLOCKED`.

## Design Critique

- Escopo: tooling e processo somente; não há superfície visual nova ou alterada.
- Produto/UX/a11y/responsividade/estados: N/A, com justificativa registrada acima.
- Risco de regressão: mitigado pela preservação explícita de `DESIGN.md`, do contrato base e do provider Cursor.
- Evidência: contexto carregado, hook JSON parseado e detector executado com resultado vazio.
- `Design Agent verdict: PASS` para a classificação `UI impact: none` desta change; isso não representa aprovação humana de nenhum card.
