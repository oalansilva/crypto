## 1. Regra de fechamento

- [ ] 1.1 Documentar no AGENTS.md: no `Done`, título do board == título da issue; divergência exige comentário registrando aprovação
- [ ] 1.2 Documentar mecanismo de sync (`gh issue edit --title` ou edição do item do board) no fluxo de fechamento

## 2. Troca de modelo de subagent

- [ ] 2.1 Documentar no AGENTS.md: mudança de modelo/configuração de subagent exige nova sessão (spawns em voo continuam no modelo antigo)

## 3. Auditoria kaizen

- [ ] 3.1 Adicionar sinal "modelo antigo pós-merge" no subagent kaizen (comparar modelo reportado nas sessões da release com configuração vigente no HEAD)
- [ ] 3.2 Adicionar verificação de título board/issue divergente nos cards fechados da release

## 4. Validação

- [ ] 4.1 Validar o sinal em sessões da release anterior (evidência read-only)
- [ ] 4.2 Rodar validação OpenSpec da change
