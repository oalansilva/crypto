## Why

No Cursor, o modelo de cada filho segue o picker de quem abriu o chat. Quem abre em Grok 4.6 paga Grok no Apply inteiro; quem abre em Composer barateia também a grelha e o Design, onde a qualidade decide. Não há lei por papel; cada operador improvisa.

## What Changes

- Os filhos no Cursor deixam de herdar o picker do pai. O spawn pede o modelo do papel nos dois caminhos (tipo nomeado ou genérico com o texto do agente colado). A lei é o parâmetro `model` do Task; o cabeçalho dos ficheiros de revisor, se mudar, é pin redundante.
- **Mapa:** grelha e Design (autor, crítico e A/B) → Grok 4.6. Apply, QA, os dois revisores, busca/exploração no mesmo card e o filho de fecho de lote → Composer normal. Não entra: revisores no Grok; `composer-2.5-fast`.
- Isolamento intacto nos filhos já existentes (sem transcript do pai; destape, nomes curtos, sidecar, pasta/comando/filho nos dois modos, teto 1+1). Este card não os redesenha.
- Só o cliente Cursor. Stubs Grok Build, OpenCode e dsh continuam a herdar; stub ≤8 linhas; sem copiar a tabela.
- Slug que o Cursor já não aceita: falha visível; o filho **não** herda o picker em silêncio; sem retry inventado. Troca de modelo = sessão nova (#430). Atualizar o nome = card novo.
- O git não força o picker do chat pai. O runbook **não** recomenda picker ao pai nos chats normais do card. **Exceção D10:** release/lote (fechar lote / subir a release / T16 + filho `fecho-lote`) exige chat pai `composer-2.5`; se não for, recusa visível (sessão nova em Composer); MUST NOT forçar picker via git / `AGENTS.md` / overlay `clients.*.auto`. Ensaio do pai em Composer **não** entra.
- Filho isolado de fecho de lote no Composer normal quando o operador pede fechar o lote / subir a release. O pai continua a chamar `process_event fechar_release`. Sem aresta nova na FSM.
- Os dois revisores ficam no Composer normal **neste card, sem reversão escrita**.
- Handoff de Design, Apply ou Review registra, por spawn, o proxy papel→modelo. `/kaizen release` lê esse proxy. Sem parser de fatura e sem dashboard.
- `harness.mdc` (4–12 linhas) deixa de dizer que todo filho herda; aponta juízo/execução (ou o runbook); não vira runbook. `AGENTS.md` always-on não cresce.
- Specs Cursor que hoje exigem inherit nos filhos recebem delta. Prova viva: Apply Composer + grill ou Design Grok, dois modos Cursor, host `completed`. Cloud e Auto fora.

**Não muda / não entra:** código de serviço / ecrã fonte; HTML / protótipo; aresta/estado/evento/hook/`enabled_tools` novos; parser de usage Cursor; redesenhar destape/needles/sidecar/Q2–Q6/teto 1+1 dos filhos já existentes; spawn na nuvem / Auto / versão rápida do Composer; forçar picker do pai; tabela de modelos nas peles Grok/OpenCode/dsh; deixar o fecho de lote só no pai; reversão escrita do ensaio de review.

## Capabilities

### New Capabilities

- (nenhuma) — o contrato vive nas specs de harness/emissão/review/kaizen já existentes. Este card não inventa coluna nem capability.

### Modified Capabilities

- `cursor-harness`: filhos Cursor usam o modelo do papel (juízo Grok 4.6 / execução Composer 2.5), não o picker; `harness.mdc` aponta juízo/execução e o runbook; slug inválido recusa visível; filho de fecho de lote no Composer; prova viva nos dois modos; stubs dos outros clientes continuam inherit.
- `cursor-code-review`: os dois revisores pedem Composer normal nos dois caminhos de spawn; o cabeçalho deixa de mandar herdar; isolamento/intervalo colado/onda no mesmo turno intactos.
- `developer-tooling`: os dois agent files deixam de declarar `model: inherit`; pin redundante do slug de execução; a lei continua a ser o parâmetro do spawn.
- `covenant-flow`: runbook Cursor deixa de mandar inherit de modelo; mapa papel→modelo; filho de fecho de lote (pai chama T16); stubs curtos sem copiar a tabela; `AGENTS.md` always-on não cresce.
- `llm-flow-emission`: críticos e revisores usam o modelo do papel, não o do pai; handoff ganha o proxy papel→modelo; sem parser/dashboard.
- `impeccable-design-gate`: Assessment A/B são juízo (Grok 4.6), iguais ao Design-autor, e MUST NOT herdar o picker do pai.
- `kaizen-continuous-improvement`: `/kaizen release` lê o proxy papel→modelo nos handoffs do pacote e compara com a tabela vigente.

## Impact

- Cursor skins: `.cursor/rules/harness.mdc` (orçamento 4–12; texto exacto no `design.md`); `.cursor/skills/covenant-flow/SKILL.md` (spawn por papel; filho de fecho de lote; prompts autocontidos); `.cursor/agents/diff-reviewer.md` e `.cursor/agents/code-reviewer.md` (cabeçalho deixa de mandar inherit); `.cursor/skills/kaizen/SKILL.md` (lê o proxy).
- Specs acima. Sem produto (`backend/` / UI). Sem `.cursor/process-fsm.yaml`. Sem aresta/evento/hook/`enabled_tools` novos. Destape classifier / FOLLOWUP / sidecar dos filhos já existentes intactos.
- Pin overlay vigente `v1.1.15`: Apply = peles Cursor. Núcleo `scripts/process-fsm/` só se goldens existentes partirem (`model: inherit` nos agent files / `Task inherit` no harness); isso não sobe o pin. Sem dual-write `.dsh/` / `.grok/` / `.opencode/` (stubs continuam inherit, ≤8 linhas).
- `AGENTS.md` always-on não cresce. Overlay `clients.*.auto` intocado. Sem HTML proto. Sem `CONTEXT.md`. Sem `docs/adr/`.
- `UI impact: none`. Prototype N/A. Cliente desta sessão é Cursor; Grok/OpenCode/dsh fora da tabela.
