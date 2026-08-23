## 1. Spec e contrato

- [x] 1.1 Atualizar main specs via apply: `kaizen-continuous-improvement` (Em Refinamento + requirement de materialização) e `release-worktree-hygiene` (post valida materialização)
- [x] 1.2 Atualizar `.cursor/skills/kaizen/SKILL.md`: orquestrador materializa cards/dedupe antes do `post`; skill permanece read-only na auditoria
- [x] 1.3 Atualizar template/nota no topo de `docs/kaizen-log.md` ou skill sobre tabela obrigatória + marcador `Sem achados acionáveis`

## 2. release-guard post

- [x] 2.1 Após o check do heading canônico, parsear todas as seções `## RELEASE_DATE — Kaizen release` e tabelas cujo `###` **começa com** `Cards kaizen criados` (sufixo livre)
- [x] 2.2 Classificar linhas (após header/separador): created (`#N`), dedupe (`(não criado)` + todos `#N` após `coberto por`), invalid (resto)
- [x] 2.3 Validar Status de **todos** os `#N` de dedupe no snapshot do board (fail-closed se board indisponível e há dedupe)
- [x] 2.4 Aplicar precedência PASS/FAIL do design (invalid/dedupe terminal primeiro; depois 1–3 created; 0+dedupe; marcador; senão FAIL)
- [x] 2.5 Mensagens de blocker explícitas (sem tabela, linha inválida, dedupe Pronto, board down, >3, etc.)

## 3. Testes

- [x] 3.1 Integrar em `backend/tests/integration/test_release_guard.py`: FAIL sem tabela/materialização
- [x] 3.2 PASS com 1–3 cards listados (heading com sufixo `(máx. 3/release)`)
- [x] 3.3 PASS com 0 cards + dedupe multi-ID (`coberto por #625 / #631`) e board em fluxo
- [x] 3.4 FAIL com dedupe e Status Pronto/Cancelado/ausente; FAIL board down + dedupe
- [x] 3.5 FAIL com >3 cards; PASS com marcador `Sem achados acionáveis`; FAIL marcador + linha inválida; FAIL created + `(não criado)` sem cobertura / `observação; sem card novo`
- [x] 3.6 Atualizar `_post_ready` e o teste que hoje aceita só o heading para incluir tabela ou marcador (suite existente não regressa em falso PASS)

## 4. Verificação

- [x] 4.1 `pytest backend/tests/integration/test_release_guard.py` verde (91 passed)
- [x] 4.2 `openspec validate` da change verde
- [x] 4.3 UI impact: none — sem mudança de frontend
