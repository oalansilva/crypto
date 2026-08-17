## Context

A tela `/combo/discovery` já existe. O start usa `idempotency_key` derivado de `snapshot_hash`. Payload hash não canonicaliza a ordem dos eixos. “Novo rascunho” só descongela o form e não gera chave nova. WIP em `origin/card-469-idempotency-normalization-wip`. #469 permanece Pronto.

## Goals / Non-Goals

**Goals:**
- Hash canônico no servidor.
- UUID por rascunho na UI; Novo rascunho rotaciona a chave.
- Retry equivalente = mesmo sweep, não 409.
- Reaplicar WIP em `card-567-*` a partir de `develop`.
- e2e + spec `discovery-sweep`.

**Non-Goals:**
- Workers PROD (#566).
- Redesign do catálogo/leaderboard/promoção.
- Reabrir #469.

## Decisions

1. **Servidor canonicaliza.** Sort estável de templates/symbols/timeframes/directions antes do hash. Cliente não é fonte de verdade da ordem.
2. **Chave = UUID de rascunho**, não snapshot_hash. Snapshot continua no token/hash de preflight.
3. **Protótipo = tela atual + delta.** Clonar o protótipo #469 e mostrar chave, retry equivalente e novo rascunho.
4. **UI impact: affected.**

## UI impact

`affected` — start/retry/novo rascunho na Discovery existente.

## Impeccable Brief

- Problema: retry/rascunho colidem por chave e hash não canônicos.
- Usuário: admin que dispara varredura.
- Resultado: mesma chave + payload equivalente retorna o sweep; novo rascunho começa limpo.
- Direção: shell atual; chip “Chave do rascunho”; botões de laboratório só no protótipo.
- Escopo: preflight/start/progress; não redesenhar leaderboard.
- Estados: rascunho novo, start criado, retry idempotente, eixos reordenados, draft após Novo rascunho.
- Interação: Iniciar, Retry, Reordenar eixos, Novo rascunho.
- Restrições: tokens DESIGN.md; sem layout paralelo.

## Prototype

- URL: `https://dev.criptofarol.com.br/prototypes/card-567-discovery-idempotency/`
- Path: `frontend/public/prototypes/card-567-discovery-idempotency/index.html`
- Base: protótipo `card-469-varredura-backtest` (shell 224px, Combo, Discovery).
- Delta: `data-testid="draft-key"`, `canonical-hash`, `reorder-axes` (LAB), `new-draft`, `start-result`. Retry no produto = segundo **Iniciar**, sem botão Retry.
- Desktop e mobile.

## Impeccable Critique

Assessment A (Task inherit, read-only): BLOCKED inicial — lab parecia produto, chave truncada, retry só no lab, retry vazio mentia estado. P1 corrigidos: faixa “Somente protótipo”, UUID real, segundo Iniciar = retry, hash canônico estável, botão Retry de produto ausente.

Assessment B (Task inherit, read-only, isolado): mesmos P1 de lab vs produto e retry vazio. Corrigidos no HTML. P2 de copy/jargão aceitos (toast de lab).

Follow-up: P1 do Iniciar disabled após o primeiro clique corrigido (botão vira “Retry do mesmo rascunho” e permanece clicável). Zero P0/P1 aberto.

## Impeccable Audit

- a11y: botões 44px, `aria-live` na chave/resultado, lab com `aria-label` de demonstração, `:focus-visible`.
- Responsivo: shell 1080/720 herdado; lab com wrap; Novo rascunho visível depois do start (igual à tela atual).
- Theming: tokens do #469 / DESIGN.md.
- Integridade: clone do shell Combo/Discovery; delta só preflight + lab tracejado.

## Impeccable Trace

- Target: `frontend/public/prototypes/card-567-discovery-idempotency/index.html`
- Digest sha256: `1529989d568e64fbad11382a4bf183b1790909d50dda20a04ce7e2339851ae52`
- Critics: Task inherit (Assessment A, B, follow-up), instruídos a não editar.
- Browser gate: `node /tmp/card-567-prototype-gate.mjs` contra a URL servida; 28/28 PASS.

## Risks / Trade-offs

- [WIP desatualizado vs develop] → rebase; resolver só conflitos de discovery_service/DiscoveryPage.
- [UUID no cliente perdido no refresh] → sessionStorage do rascunho; aceitável no MVP.
- [Protótipo tem lab buttons que o produto não terá] → no apply, só UUID + Novo rascunho; Reordenar é demonstração.

## Migration Plan

1. Aprovação de Design.
2. Rebase WIP; testes.
3. QA visual Discovery (baseline se o chip aparecer no produto — preferir chave só em debug/`aria` se Alan não quiser chip permanente; default: chave visível no preflight como no protótipo, texto discreto).

## Open Questions

Exibir a chave completa no produto ou só garantir o UUID interno? Default do protótipo: visível no preflight (auditável). Alan pode pedir para esconder na aprovação.

## Design Critique

- Fidelidade: shell Combo/Discovery clonado do #469 (sidebar 224px, tokens, leaderboard).
- Delta: chave UUID, hash canônico, segundo Iniciar = retry, Novo rascunho rotaciona UUID. Lab tracejado “somente protótipo”.
- Achados P1 (lab como produto, UUID falso, retry desabilitado) corrigidos e revalidados no navegador.
- Apply: no produto só UUID interno + Novo rascunho + hash canônico no servidor; Reordenar não entra.

## Prototype Validation

- URL: `https://dev.criptofarol.com.br/prototypes/card-567-discovery-idempotency/`
- Comando: `node /tmp/card-567-prototype-gate.mjs` (Playwright Chromium, headless)
- Viewports: 1440×900 e 390×844
- Asserts: lab visível; UUID; hash estável após reordenar; 1º Iniciar cria sweep; progress visível; Novo rascunho após start; 2º Iniciar = retry idempotente; Novo rascunho troca UUID; `retry-start` count=0; 0 erros de console
- Resultado: 28/28 PASS
- Screenshots: `/tmp/card-567-gate/desktop-1440x900.png`, `/tmp/card-567-gate/mobile-390x844.png`
- Digest da versão validada: `1529989d568e64fbad11382a4bf183b1790909d50dda20a04ce7e2339851ae52`

Design Agent verdict: PASS
