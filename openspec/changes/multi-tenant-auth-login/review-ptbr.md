# Review PO — Card #69: [MT-1] Autenticação — Login, Registro e JWT

## Revisão de Produto (PT-BR)

**Data:** 2026-03-30
**Card:** #69 — [MT-1] Autenticação — Login, Registro e JWT
**Stage:** PO → DESIGN

---

## Avaliação do Proposal

| Item | Status | Comentário |
|------|--------|------------|
| Problema claro | ✅ | Identificado corretamente |
| Solução proporcional | ✅ | Escopo justo para este card |
| User Stories relevantes | ✅ | 3 US cobrindo registro, login, proteção |
| Critérios de aceitação testáveis | ✅ | Todos são verificáveis |
| Escopo bem definido (inclui/exclui) | ✅ | Limites claros |

## Pontos de Atenção

1. **Segurança** — Refresh tokens em blocklist (revokedAt) é correto. Não usar apenas JWT signed para logout ( stateless por si só não permite revoke).

2. **Expired tokens** — Certificar que middleware retorna 401 (não 403) para token expirado — padrão REST.

3. **Email uniqueness** — A validação de email duplicado deve ser feita em nível de banco (unique constraint) E em nível de aplicação.

4. **Refresh token storage** — Armazenar hash do refresh token, não o token em texto plano (proteção contra leak de DB).

## Decisão

✅ **Aprovado para avançar para DESIGN.**

O escopo está correto. Não há dependências bloqueantes. O design pode ser detalhado pela equipe de DESIGN respeitando o proposal.

**Próximo passo:** DESIGN — detalhar protótipos de API e layout de tabelas Prisma.
