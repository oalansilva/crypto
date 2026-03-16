# Proposal Review — sincronismo e registro de tasks

## Resumo

**Problema real:** As tasks definidas no tasks.md não aparecem no card — nem quando abre o drawer. Apenas 1 task aparece, mas o tasks.md tem 12.

**Causa raiz:** Não existe sincronização entre o tasks.md (OpenSpec) e o banco de dados (workflow DB).

**Solução:**
1. Implementar sync: tasks.md → workflow DB
2. Corrigir API para retornar todas as tasks sincronizadas
3. Frontend exibe as tasks corretamente

**Próximo passo:** Aprovação → DEV implementa → QA → Homologação.
