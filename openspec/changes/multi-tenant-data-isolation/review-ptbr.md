# Review — Card #70: [MT-2] Multi-tenant Data Isolation

## Resumo

Card para implementar isolamento de dados por `user_id` em todas as tabelas e queries do sistema. Cada usuário só vê seus próprios dados (sinais, portfolio, histórico, etc.).

## Pontos Positivos

- ✅ Design claro: todas as tabelas com dados de usuário terão `user_id` como FK
- ✅ dependency `get_current_user_id()` reutilizável em todos os endpoints
- ✅ Validação de ownership em update/delete (403 se tentar acessar recurso de outro)
- ✅ Índices compostos criados para queries por `user_id` + data (performance)
- ✅ Segue o padrão do Card #69 (JWT authentication)

## Riscos Identificados

- ⚠️ **Monitor Preferences**: a tabela usa `symbol` como PK. Precisa reestruturar para ter `user_id` como parte da PK ou usar `user_id` sozinho como PK. Reestruturar pode quebrar queries existentes.
- ⚠️ **Dados existentes**: se houver dados sem `user_id` no banco, queries filtradas retornarão vazio. Pode precisar migration ou marcar como `user_id = NULL` para dados globais existentes.
- ⚠️ **Monitor Preferences**: com `user_id` como PK único, um usuário só pode ter uma preferência de monitor por vez. Isso pode ser limitante se o frontend espera múltiplas preferências por símbolo.

## Decisões de Design

1. **`user_id` como FK obrigatória**: todas as tabelas listadas devem ter `user_id` não-nulo. Não há dados globais compartilhados neste sistema.

2. **Monitor Preferences**: mudar de `symbol` como PK para `user_id` como PK. Um usuário = uma preferência de monitor (por enquanto). Se precisar de múltiplas, pode ser扩展 num card futuro.

3. **Índices**: `user_id` isolado + índices compostos `(user_id, created_at/recorded_at)` para queries de lista ordenadas.

4. **Validação de ownership**: reuso de validação `validate_ownership()` em todos os endpoints de update/delete.

## Checklist de Implementação

- [ ] Adicionar `user_id` nas 6 tabelas (signal_history, portfolio_snapshots, favorite_strategies, monitor_preferences, backtest_runs, combo_templates)
- [ ] Criar índices em `user_id`
- [ ] Implementar `get_current_user_id()` dependency
- [ ] Atualizar todos os endpoints GET para filtrar por `user_id`
- [ ] Atualizar todos os endpoints POST para incluir `user_id`
- [ ] Atualizar todos os endpoints PUT/PATCH/DELETE para validar ownership
- [ ] Testar: GET retorna só dados do usuário, 403 em acesso cruzado

## Dependências

- Card #69 (multi-tenant-auth-login) ✅ — precisa estar homologado antes

## Estimativa

- **Complexidade**: Média — muda muitas tabelas e endpoints, mas padronizado
- **Impacto**: Alto — segurança e privacy dos dados
- **Risk**: Baixo-Mediano — reestruturar monitor_preferences pode causar breaking change
