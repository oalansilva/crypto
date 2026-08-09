## 1. Todos completos no fechamento

- [ ] 1.1 Documentar no AGENTS.md/fluxo: `/opsx:verify`/Done exige 0 todos `in_progress`/`pending` nas sessões associadas ao card (leitura read-only do `opencode.db`)
- [ ] 1.2 Implementar/validar o check no fluxo `/opsx:verify` com fonte indisponível declarada quando aplicável

## 2. Título de sessão descritivo

- [ ] 2.1 Documentar regra: sessões com custo > $0.10 (ou produção relevante) têm título descritivo (card/contexto)
- [ ] 2.2 Adicionar validação na auditoria kaizen (título descritivo em sessões caras)

## 3. Publicação única OpenSpec (sinergia #423)

- [ ] 3.1 Confirmar que o helper `publish-openspec-card-artifacts` com `--gist-id` atualiza gist/comentário existente sem duplicação (implementado no #423, validar aqui)
- [ ] 3.2 Registrar no fluxo: 1 comentário OpenSpec por card

## 4. Priorização

- [ ] 4.1 Elevar o card #423 de P2 para P1 (label/prioridade no board, ação PO)

## 5. Validação

- [ ] 5.1 Validar o check de todos completos em sessões da release anterior (read-only)
- [ ] 5.2 Rodar validação OpenSpec da change
