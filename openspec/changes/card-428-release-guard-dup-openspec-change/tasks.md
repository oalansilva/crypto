## 1. Detecção no release-guard post

- [x] 1.1 Adicionar check no modo `post`: nenhuma change ativa em `openspec/changes/` com correspondente em `openspec/changes/archive/*/`
- [x] 1.2 Em duplicação, emitir blocker com instrução de correção (verificar conteúdo/digest e remover pasta ativa duplicada, ex.: `git rm -r`)

## 2. Fluxo de sync main -> develop

- [x] 2.1 Documentar no AGENTS.md que o fluxo de sync `main -> develop` pós-publicação roda o `release-guard post` (ou check equivalente) e falha em duplicação

## 3. Validação

- [x] 3.1 Criar cenário de teste com duplicação simulada (ativa + arquivada) e confirmar blocker; limpar cenário após o teste
- [x] 3.2 Rodar `scripts/release-guard post` sem duplicação e confirmar PASS
- [x] 3.3 Rodar validação OpenSpec da change
