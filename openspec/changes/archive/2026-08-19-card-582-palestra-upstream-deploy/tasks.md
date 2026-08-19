## 1. Deck e enquete

- [x] 1.1 Criar `docs/palestra-upstream-deploy.md` transcrevendo o roteiro do `design.md` (7 pontos, mermaid, três trilhas, enquete com contagem ao vivo mão/chat)
- [x] 1.2 Referenciar `docs/palestra-upstream-deploy-slide-skills.md` no bloco 11–14 min sem duplicar os 13 slides nem usar fluxo `Todo → In Progress`
- [x] 1.3 Incluir as 12 colunas atuais, os 4 gates humanos e a distinção Done / Homologado / Pronto; sanitizar canônico para `.cursor/skills/` (não `~/.codex/skills/`)
- [x] 1.4 Abrir o deck como palestra do **Agile Brazil 2026** (Foz, 12–13 nov); tom de relato de experiência; sem pitch comercial; sem submissão Even3
- [x] 1.5 Incluir tese HITL: tabela dos 4 gates com *porquê*, frase “automatize o verificável / humano no irreversível”, falhas de bypass ligadas aos gates

## 2. Evidência de board e card real

- [x] 2.1 Versionar o mapa das colunas reais do Project 1 com destaque a Em Refinamento (screenshot autenticado ou mapa explícito se captura falhar)
- [x] 2.2 Incluir walkthrough de um card Pronto real (candidato #585) com URLs de Gist OpenSpec e comentário de evidência, sem inventar links

## 3. Verificação

- [x] 3.1 Grep/assert textual: skills mínimas, 6 papéis + Alan, Cursor Agent, `inherit`, release-guard, human-in-the-loop / HITL / quatro gates com porquê
- [x] 3.2 Confirmar diff sem `frontend/src`, `backend/` ou `DESIGN.md`; ensaio cronometrado e Google Slides não marcados como feitos pelo agente
- [x] 3.3 `openspec validate --change card-582-palestra-upstream-deploy` verde
