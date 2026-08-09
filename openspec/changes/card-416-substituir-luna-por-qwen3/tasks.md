## 1. Validação de pré-requisito

- [x] 1.1 Confirmar disponibilidade de `opencode-go/qwen3.7-plus` no provider opencode-go (`opencode models`)
- [x] 1.2 Validar suporte a imagens (`attachment: true`) do `qwen3.7-plus` via delegação real de uma imagem ao subagent `vision`; se falhar, bloquear e reportar a Alan

## 2. Implementação

- [x] 2.1 Atualizar `.opencode/agent/vision.md`: `model: opencode-go/qwen3.7-plus` e descrição
- [x] 2.2 Atualizar `.opencode/plugin/vision-router.ts`: constante `VISION_MODEL_ID` e textos de delegação
- [x] 2.3 Atualizar `.opencode/commands/vision.md`: descrição e instruções do `/vision`
- [x] 2.4 Atualizar `AGENTS.md` e `rules.md`: exceção de roteamento visual com `opencode-go/qwen3.7-plus`
- [x] 2.5 Garantir zero referências ativas a `gpt-5.6-luna` (grep; histórico em archive/ é permitido). Classificação: restam referências apenas nos artifacts da própria change (proposal/design/tasks, descritivas do estado anterior) e em `openspec/specs/visual-analysis-routing/spec.md` (spec de requirements; sync no archive do fechamento, fluxo canônico OpenSpec)

## 3. Validação

- [x] 3.1 Rodar unit/plugin do vision-router com o novo ID (testes de roteamento, se existirem). Unit do card-399 não é versionado → N/A com justificativa; validação por smoke real (3.3)
- [x] 3.2 Validar change verde: `openspec validate --changes card-416-substituir-luna-por-qwen3` (47/47 OK)
- [x] 3.3 Smoke real: `/vision <imagem>` respondendo com julgamento visual no novo modelo (evidência runtime: sessão `ses_01c1359bbffeJNVd62K09W11t9`, agent=vision, model=`opencode-go/qwen3.7-plus`, análise real de pixels da home desktop; confirma `attachment: true`)
- [x] 3.4 Revisar diff completo antes de commit (Code Review). Veredito reviewer: APROVADO COM RESSALVAS; 4 achados (M1 AGENTS.md:317, B1 vision-router.ts:14, B2 sintaxe tasks.md, B3 proposal.md sync archive) corrigidos na mesma rodada; revalidação OpenSpec verde
