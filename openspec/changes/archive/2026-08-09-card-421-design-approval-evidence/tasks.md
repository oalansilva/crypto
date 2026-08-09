## 1. Regras de processo

- [x] 1.1 Adicionar em `AGENTS.md`/`rules.md`: nenhum código é aplicado sem evidência registrada de aprovação de Design (comentário de Alan ou arraste `Aprovação de Design -> Pronto para Dev`), inclusive UI impact none, remoções e tooling
- [x] 1.2 Adicionar regra: veredito `BLOCKED` exige seção de resolução no `design.md` (causa, correção, aprovador) antes de `Pronto para Dev`/implementação

## 2. Checklist de gates

- [x] 2.1 Adicionar checklist de gates no template/fluxo de PR/commit de integração: `design.md`/verdict + evidência de aprovação, mesmo para tooling
- [x] 2.2 Adicionar validação do gate no `/opsx:verify` (design.md presente, verdict registrado, evidência de aprovação)

## 3. Auditoria kaizen

- [x] 3.1 Adicionar sinal "sem evidência de aprovação de Design" na auditoria de cards fechados (subagent kaizen)
- [x] 3.2 Adicionar sinal "BLOCKED sem resolução registrada" na auditoria

## 4. Validação

- [x] 4.1 Validar regras/checklist em um card de teste (foco) e registrar evidência
- [x] 4.2 Rodar validação OpenSpec da change
