## 1. Helper com --gist-id

- [ ] 1.1 Adicionar flag `--gist-id <id>` ao `publish-openspec-card-artifacts.sh`
- [ ] 1.2 Ao receber `--gist-id`, validar `gh gist view <id>` e atualizar arquivos do Gist existente (`gh gist edit`); sem `--gist-id`, manter comportamento atual (criar novo)
- [ ] 1.3 Evitar novo comentário duplicado na republicação; manter 1 comentário OpenSpec por card (atualizar quando possível, senão reportar gist atualizado)

## 2. Retrigger de CI

- [ ] 2.1 Documentar comando real de retrigger via `workflow_dispatch` (`gh workflow run --repo <repo> <workflow> --ref <ref>`) no AGENTS.md
- [ ] 2.2 Registrar proibição de commit vazio como retrigger de CI

## 3. Docs/fluxo

- [ ] 3.1 Documentar no AGENTS.md o uso do helper com `--gist-id` em republicações
- [ ] 3.2 Documentar orientação de agrupar ajustes pós-review em um único commit/PR por card

## 4. Validação

- [ ] 4.1 Testar: primeira publicação cria Gist; republicação com `--gist-id` atualiza sem criar novo
- [ ] 4.2 Rodar validação OpenSpec da change
