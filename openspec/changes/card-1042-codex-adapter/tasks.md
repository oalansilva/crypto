## 1. Produto e mapa compartilhado

- [x] 1.1 No produto `oalansilva/covenant-flow`, inventariar os caminhos de instalação e os nomes de skills existentes; registrar a forma de preservar `.agents/skills/impeccable/` e hooks Codex alheios sem sobrescrita silenciosa.
- [x] 1.2 Estender `.cursor/model-map.yaml` de forma aditiva com `juizo.codex={label,slug:gpt-6-sol,effort:high}` e `execucao.codex={label,slug:gpt-6-luna,effort:max}`; ler `juizo.label/slug`, `execucao.label/slug` e `forbid` do destino vigente no ato do pin, preservá-los integralmente e não criar segundo mapa.
- [x] 1.3 Implementar resolução/validação do par Codex por faixa antes de cada spawn, com falha visível para arquivo, modelo ou esforço ausente, inválido, proibido ou recusado pelo host; provar que edição válida afeta o próximo spawn e não altera Cursor.
- [x] 1.4 Gerar pontes curtas `.agents/skills/` para as skills canônicas de `.cursor/skills/`, reconciliar `design-critic`, preservar Impeccable e adicionar checagem de cobertura/drift; comprovar cobertura/drift e descoberta em sessão nova CLI. IDE local fora do recorte #1042 por decisão de Alan; não alegada.

## 2. Adapter local e Guard

- [x] 2.1 Criar a configuração `.codex/` de projeto para `SessionStart`, `PreToolUse` de `Bash`/`exec_command` e `apply_patch`, `PostToolUse` e `Stop`, compondo hooks existentes e resolvendo scripts pela raiz git.
- [x] 2.2 Conectar `SessionStart` ao `paging.page()` compartilhado; verificar página para card bound em `Todo`, Design e Status unread, sem duplicar `context_file` ou inferir estado do chat.
- [x] 2.3 Normalizar envelopes Codex de shell/edição para `guard.decide()` antes da operação; garantir deny observável de produto em `develop`/`Todo`, permissão de artefatos em Design e permissão de produto só no card worktree após T8.
- [x] 2.4 Encaminhar `PostToolUse` com caminho de UI e `Stop` para o `hook.mjs` existente; comparar condição de disparo e classe de achado com os quatro adapters atuais, mantendo o detector advisory.
- [x] 2.5 Adicionar goldens de hook confiado, hook ausente/desabilitado, envelope sem path, overlay ausente e rota não coberta; documentar o limite cooperativo conforme resultado, sem alegar Auto.

## 3. Filhos, reviews e fluxo

- [x] 3.1 Codificar nos runbooks/agent prompts Codex os papéis por faixa, prompts autocontidos, isolamento de transcript e verificação de `completed`+payload; registrar modelo e esforço solicitados/observados em proxies.
- [x] 3.2 Fazer o pai materializar uma vez o diff exato e entregar o mesmo digest a `diff-reviewer` e `code-reviewer` Codex de somente leitura; testar dois pareceres separados, sem busca git pelo filho nem escrita. Evidência: `evidence/review-wave-1818-and-p1-fixes.md`.
- [x] 3.3 Assegurar que Status Codex só avance por `process_event`; testar recusa de `gh project item-edit` direto e preservação de T7/T15/T18 humanos e T16/release sem alteração.

## 4. Pin e regressões

- [x] 4.1 Expandir `install.sh --pin`, skill `implantar`, geração de `AGENTS.md` e specs do produto para copiar quinto adapter e pontes sem tabela paralela; testar pin repetido, conflito de hook e mapa Cursor local alterado: conflito gera recusa visível ou merge explícito, nunca overwrite silencioso.
- [ ] 4.2 Publicar tag do produto e aplicar o pin no worktree Cripto somente depois do gate humano de Design; antes de escrever, capturar o mapa **destino** vigente e, depois, comparar `juizo.label/slug`, `execucao.label/slug` e `forbid` byte a byte, além de inspecionar diff, overlay e quatro adapters existentes. <!-- covenant-flow:after-commit -->
- [x] 4.3 Rodar goldens do Codex e regressões de Cursor, Grok, OpenCode e dsh; corrigir quebra causada pelo mapa aditivo ou instalador antes do ensaio vivo.

## 5. Ensaio local e evidência

- [x] 5.1 No recorte CLI, provar skills, orientação por Status e OpenSpec em sessões novas; registrar host/versão, confiança do hook e resultados, sem usar Codex Cloud. IDE local fora do recorte #1042 por decisão de Alan; não alegada. Evidência: `evidence/cli-apply-validation.md`.
- [x] 5.2 No CLI, executar ensaio de deny em arquivos descartáveis: comando e edição em `develop` e `Todo`, readback de bytes intactos; verificar Design permitido e produto permitido apenas no card worktree depois de T8; registrar rotas cobertas e o limite de spawn nativo sem `PreToolUse`. Evidência: `evidence/cli-apply-validation.md`. IDE local fora do recorte #1042 por decisão de Alan; não alegada.
- [ ] 5.3 Provar no CLI em filhos reais o par `gpt-6-sol/high` e `gpt-6-luna/max`, falha sem fallback para par ausente/indisponível, isolamento de Design/Apply/QA e dois reviewers read-only com diff idêntico. A parte de isolamento/retorno de QA depende de T11 e dos checks. Limite cooperativo registrado: o spawn nativo real ficou fora de `PreToolUse`; Alan aceitou essa cobertura no comentário do #1042. A IDE local permanece pendente. <!-- covenant-flow:after-qa -->
- [ ] 5.4 Percorrer um card piloto pela FSM: Design, aprovação de Alan, Apply, dois reviews, QA e Done técnico; guardar eventos, proxies e evidência de cada gate sem pular etapa. <!-- covenant-flow:after-qa -->
- [ ] 5.5 Depois do ensaio documentado, atualizar a descrição do board para retirar apenas a afirmação de Codex inativo; registrar explicitamente a cobertura cooperativa e validar OpenSpec/estado final. <!-- covenant-flow:after-qa -->
