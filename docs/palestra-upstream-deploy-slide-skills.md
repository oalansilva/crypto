# Slide — Skills como runbooks (projetor)

> **Palestra:** Do upstream ao deploy  
> **Card:** #582  
> **Uso:** copiar cada bloco `--- SLIDE ---` para um slide no Google Slides / Keynote  
> **Fonte:** `AGENTS.md`, `.cursor/skills/` (canônico GitHub), `.agents/skills/`

---

## SLIDE 1 — Título

**Skills como runbooks**

Cada etapa crítica tem instrução versionada — não prompt ad hoc

Cripto Farol · Cursor Agent · agosto/2026

---

## SLIDE 2 — Insight (frase única)

**O board decide SE avançou.**  
**A skill decide COMO executar.**

Skill ≠ gate humano.

---

## SLIDE 3 — Onde ficam (3 camadas)

| Camada | Onde |
| --- | --- |
| Workflow (canônico GitHub) | `.cursor/skills/alan-workflow` (+ ambientes, github-project-board) |
| OpenSpec + kaizen | `.cursor/skills/` |
| Design + QA | `.agents/skills/` |
| Always-on curto | `.cursor/rules/harness.mdc` |

Comandos: `/opsx-*` · `/kaizen`

---

## SLIDE 4 — Workflow global (1 linha por skill)

**`alan-workflow`** → contrato operacional: cards, status, gates, evidência, review, release

**`alan-workflow-ambientes`** → mapa DEV/PROD: paths, services, deploy, guardrails de produção

**`github-project-board`** → operar Project v2: Status, Prioridade, Responsável

---

## SLIDE 5 — OpenSpec: especificação (1 linha por skill)

**`/opsx:new`** → criar scaffold da change OpenSpec

**`/opsx:ff`** → gerar artifacts até apply-ready (proposal, specs, design, tasks)

**`/opsx:explore`** → explorar escopo e riscos **sem implementar código**

**publicar no card** → Gist secreto + comentário (Markdown only; protótipo separado)

---

## SLIDE 6 — OpenSpec: implementação e fechamento (1 linha por skill)

**`/opsx:apply`** → implementar tasks — **somente após `Pronto para Dev`**

**`/opsx:verify`** → confrontar artifacts × código × testes × protótipo

**`/opsx:archive`** → arquivar change + sincronizar specs (fechamento de card/release)

**`/opsx:bulk-archive`** → arquivar várias changes de um lote de release

---

## SLIDE 7 — Design e qualidade (1 linha por skill)

**`design-critic`** → gate Design: design.md, protótipo (se UI), crítica isolada, veredito

**`impeccable`** → pipeline UI: context → prototype → audit → browser gate

**`playwright-cli`** → browser real: protótipo, QA visual, asserts desktop/mobile

**`kaizen`** → auditoria read-only pós-card/release; propõe melhorias de processo

---

## SLIDE 8 — Pipeline compacto (diagrama textual)

```
Em Refinamento ──Alan──► Todo
    │ opsx:new/ff + publicar
    ▼
Design ──design-critic [+ impeccable]──► Aprovação de Design
    │ Alan
    ▼
Pronto para Dev ──opsx:apply──► Em desenvolvimento → Code Review → QA
    │ opsx:verify
    ▼
Done ──Alan──► Homologado ──release──► Pronto
         kaizen + release-guard + deploy PROD
```

---

## SLIDE 9 — Agentes no processo (1 linha por papel)

**Não são 6 modelos.** São 6 papéis no mesmo Cursor Agent (`inherit`).

| Papel | Faz | Coluna |
| --- | --- | --- |
| **main** | Orquestra, fala com Alan, aciona o próximo | Todo o fluxo |
| **PO** | OpenSpec: proposal, specs, tasks | Todo → Design |
| **DESIGN** | `design.md`, protótipo, crítica isolada | Design |
| **DEV** | Código + review do diff **antes** do commit | Em desenvolvimento → Code Review |
| **QA** | Testes, qa-gate, Playwright visual | QA → Done técnico |
| **Kaizen** | Audita processo (read-only); propõe, não implementa | Pós-card / release |
| **Alan** | 4 gates humanos — o agente nunca cruza | Triagem, design, homologação, produção |

Skill = *como* executar. Agente = *quem* é dono da etapa. Board = *se* avançou.

---

## SLIDE 10 — Skill × coluna do board

| Coluna | Skills que entram |
| --- | --- |
| Em Refinamento → Todo | `github-project-board` · **Alan** |
| Todo → Design | `openspec-new` · `openspec-ff` |
| Design | `design-critic` · `impeccable` · `playwright-cli` |
| Pronto para Dev → QA | `openspec-apply` · review diff · CI |
| Antes de Done | `openspec-verify` · Playwright CI |
| Release | `openspec-archive` · `alan-workflow-ambientes` · `kaizen` · release-guard |

---

## SLIDE 11 — O que a skill NÃO faz (limites)

**`openspec-apply`** → não roda antes de `Pronto para Dev`

**`design-critic`** → não autoaprova Design (Alan arrasta)

**`kaizen`** → não corrige código nem move card sozinho

**`alan-workflow-ambientes`** → merge em main ≠ Pronto sem deploy PROD

---

## SLIDE 12 — Falha típica vs. correção

| Falha | Correção |
| --- | --- |
| Chat disse "implemente" | Voltar ao board: Design → Aprovação → Pronto para Dev |
| Agent codou sem skill | Carregar `openspec-apply` + evidência de gate |
| Protótipo no Gist | HTML em `dev.criptofarol.com.br/prototypes/` |
| Release sem audit | `/kaizen release` antes de `Pronto` |

---

## SLIDE 13 — Pergunta para o público

**Quais etapas do seu fluxo ainda dependem de prompt no chat — e deveriam virar skill/runbook versionado?**

---

## Notas para o apresentador

- Slides 4–7 são o núcleo: **uma linha por skill**, leia devagar (~15 s/slide).
- Slide 8 pode virar diagrama visual (mermaid no issue #582).
- Slide 9 lista os **6 papéis + Alan** — reforça que não são 6 modelos, e sim papéis no mesmo harness.
- Slide 10 conecta skill ao **campo Status** — reforça fonte única de estado.
- Tempo sugerido deste bloco: **3–4 min** (11–14 min da palestra; slide 9 também cabe no bloco Anatomia 7–11 min).

## Versão compacta (1 slide só — backup)

Se faltar tempo, use apenas esta lista:

1. **alan-workflow** — contrato global  
2. **alan-workflow-ambientes** — DEV/PROD e deploy  
3. **github-project-board** — operar o Kanban  
4. **opsx:new/ff** — especificar  
5. **opsx:apply** — implementar (após Pronto para Dev)  
6. **opsx:verify/archive** — validar e arquivar  
7. **design-critic** — gate Design  
8. **impeccable** — qualidade UI  
9. **playwright-cli** — browser gate  
10. **kaizen** — auditar processo pós-release  
11. **main / PO / DESIGN / DEV / QA / Kaizen** — papéis no mesmo Cursor Agent (`inherit`); Alan nos 4 gates  
