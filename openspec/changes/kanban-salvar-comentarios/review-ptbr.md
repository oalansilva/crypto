# Proposal Review — kanban-salvar-comentarios

## Resumo

**Problema:** O botão "Comentar" fica desabilitado — usuário não consegue salvar comentários.

**Causa:** Campo "author" está vazio (não carrega do localStorage) e o botão exige author + body preenchidos.

**Solução:** Preencher o campo author com valor padrão.

**Próximo passo:** Aprovação → DEV → QA → Homologação.
