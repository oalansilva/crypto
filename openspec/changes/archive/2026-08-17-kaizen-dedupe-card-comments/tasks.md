## 1. Helper script

- [x] 1.1 Criar `scripts/post-card-evidence-comment.sh` com flags `--transition done|homologado|pronto`, `--card <n>`, `--commit <sha>`, `--pr <n>` (opcional), `--dry-run`
- [x] 1.2 Implementar extração de commit ref de comentários existentes (URL commit, "PR N (sha)", "Commit/merge: <ref>") via `gh issue view <card> --comments`
- [x] 1.3 Implementar dedupe: bloqueia postagem se já existir comentário da mesma transição com mesmo SHA normalizado; senão posta com template canônico do `AGENTS.md`
- [x] 1.4 Fail-closed: se `gh` falhar ao listar comentários, não posta e sai com erro claro
- [x] 1.5 Modo `--dry-run` imprime o que seria postado sem postar
- [x] 1.6 Testar manualmente: card sem comentário (posta), card com comentário idêntico (não posta), card com formato divergente URL vs PR N (sha) (não posta)

## 2. Documentação

- [x] 2.1 Atualizar `AGENTS.md` seção "Comentários obrigatórios no Kanban" para exigir o uso do helper no fechamento Done/Homologado/Pronto
- [x] 2.2 Registrar uso do helper no comentário de Pronto/Done com evidência

## 3. Validação

- [x] 3.1 Rodar `shellcheck`/`bash -n` no script (se disponível) e corrigir achados
- [x] 3.2 Validar change OpenSpec com `openspec validate --all` sem novos blockers
