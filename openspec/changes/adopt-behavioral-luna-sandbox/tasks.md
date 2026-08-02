## 1. Contrato local do Cripto Farol

- [x] 1.1 Atualizar `AGENTS.md` e `rules.md` para tornar a opção 2 padrão e remover bloqueios baseados somente na igualdade do sandbox.
- [x] 1.2 Atualizar os três perfis Luna para declarar o contrato comportamental, a propriedade de escopo e as proibições específicas de cada função.
- [x] 1.3 Atualizar `$stage-model-routing` com preflight, inventário antes/depois, critérios de aceitação e risco residual por lane.

## 2. Evidência automatizada

- [x] 2.1 Atualizar os testes de contrato para manter agente/modelo/effort/thread fail-closed e validar a contenção comportamental.
- [x] 2.2 Adicionar ou ajustar validações que rejeitem mutação fora do escopo e review com qualquer alteração de estado.
- [x] 2.3 Validar que nenhuma regra ativa reintroduz a opção 1 ou exige alteração da segurança do host.

## 3. Processo global e superfícies operacionais

- [x] 3.1 Atualizar a skill global `alan-workflow` em branch própria com a opção 2 e a mesma linguagem de risco residual.
- [x] 3.2 Atualizar a descrição do GitHub Project e documentação operacional aplicável sem mudar o fluxo Kanban nem a autoridade humana.
- [ ] 3.3 Registrar no card os diffs/SHAs das duas camadas e confirmar que local e global não divergem.

## 4. Validação e handoff

- [x] 4.1 Rodar os testes focados dos perfis/skills, parse TOML e validação OpenSpec da change e global.
- [ ] 4.2 Executar Code Review independente no diff exato com prova de estado idêntico antes/depois.
- [ ] 4.3 Em QA, verificar uma lane Luna natural com metadata observável e auditoria de escopo, sem iniciar agente somente para smoke test.
- [ ] 4.4 Publicar evidências finais no card e manter explícito que a opção 2 não oferece isolamento forte do sistema operacional.
