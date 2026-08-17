## 1. Documentação do fluxo de rename

- [x] 1.1 Documentar no `AGENTS.md` o fluxo de rename de issue com card no board: nota de divergência obrigatória no card (motivo + aprovação) quando o título do board não puder ser sincronizado
- [x] 1.2 Definir formato canônico da nota (`Nota de divergência` + `Motivo:` + `Aprovado por:`)

## 2. Check de divergência no guard

- [x] 2.1 Adicionar bloco `board_issue_title_sync` ao `scripts/release-guard` no modo `audit`
- [x] 2.2 Comparar `title` do card (board) vs `content.title` da issue e procurar nota de divergência nos comentários
- [x] 2.3 Emitir warn quando divergência sem nota; não emitir quando nota presente
- [x] 2.4 Aplicar check somente a itens vinculados a issues; itens sem issue fora de escopo
- [x] 2.5 Validar com o #463 (com nota, sem warn) e com caso sem nota (warn) via `release-guard audit`

## 3. Testes e validação

- [x] 3.1 Executar `release-guard audit` e confirmar saída esperada sem regressão em pre/post
- [x] 3.2 Validação OpenSpec da change
