# Candidato inativo #1130

Este pacote é concreto e reviewável; não foi aplicado ao adapter ativo. `nucleus/` contém o delta autorado a partir dos arquivos canônicos do checkout nucleus #1098 (HEAD `14aa9d6` com alterações locais #1098). `provenance-base.json` guarda os hashes das origens; esse HEAD sozinho não contém a base dirty. `package.json` guarda inventário e digests finais. Não foi criada tag, revisão publicada, pin ou confiança.

Os patches gerados ficam em `.cursor/tmp/card-1130-delivery/`, com paths/digests no manifesto versionado. `nucleus.patch` aplica sobre a base nucleus identificada. `consumer.patch` representa a entrega correspondente no consumidor e exclui `install.sh`, que pertence ao nucleus. Ambos passaram `git apply --check`; nenhum foi aplicado. A fonte única do comportamento está no candidato nucleus; não editar as cópias ativas em paralelo. Mudança futura nos arquivos-base recusa regeneração em vez de sobrescrever trabalho alheio. Patches derivam dos mesmos bytes de `nucleus/`; a revisão lê o candidato versionado, sem duplicar todo o código em arquivos patch.

Arquivos de execução: `codex_qualification_index.py`, `codex_qualification.py`, `codex_terminal.py`, `codex_terminal_review.py` e delta em `codex_evidence.py`. Entrega também testes, installer, runbook e quatro docs. O índice é localizador privado; nascimentos guardam referência/identidade originais e revalidam fontes. Refinamento em source aceita card explícito apenas para grill-card, com Estado vivo revalidado antes do spawn; produto não adota outro card. Nenhuma aresta, estado, trust, cliente Auto ou aprovação humana foi criada.

## Reprodução sem ativação

Na raiz do worktree deste card:

```bash
python3 openspec/changes/card-1130-codex-cli-fluxo-completo/implementation/prepare_test_tree.py
python3 -m pytest -q .cursor/tmp/card-1130-candidate-test/scripts/process-fsm/test_codex_qualification_index.py .cursor/tmp/card-1130-candidate-test/scripts/process-fsm/test_codex_terminal.py .cursor/tmp/card-1130-candidate-test/scripts/process-fsm/test_codex_terminal_review.py .cursor/tmp/card-1130-candidate-test/scripts/process-fsm/test_codex_terminal_install.py .cursor/tmp/card-1130-candidate-test/scripts/process-fsm/test_codex_refinement_binding.py
python3 openspec/changes/card-1130-codex-cli-fluxo-completo/implementation/build_package.py
openspec validate card-1130-codex-cli-fluxo-completo --strict
```

`prepare_test_tree.py` monta cópia descartável em `.cursor/tmp/card-1130-candidate-test` a partir do nucleus e sobrepõe o candidato. Não lê `.impeccable/critique`, instala conta ou altera o consumidor ativo. Installer e módulos são exercitados em destinos descartáveis dos testes. A tag `v1.2.0` desses fixtures é somente dado de teste, nunca publicação real. As suites existentes de evidence/context/Review/probes/process_event/release/checklist completam a regressão; resultados e negativos vivos estão em `../evidence/apply-report.md`.

## Operações seguintes do pai

**Implementação aplicável a precommit concluída; aceitação pendente, 19/26.** Não foi identificado P0 de produto. As tasks 3.4/3.5/4.3/4.4 permanecem abertas em after-pin para exercitar o novo código no consumidor instalado, conforme [resolução fundamentada de fases](../evidence/phase-resolution.md). A dependência circular anterior foi resolvida pelo contrato aprovado do Design/checklist; não se marcou ensaio ausente. Inspeção técnica e faseamento não liberam T9 automaticamente: o pai precisa dos gates reais de preparação/Status e da onda canônica.

O pai pode inspecionar `package.json`, patches e matriz e conduzir diagnósticos pela implementação integrada sem esperar tag nova. Ensaios de produto precisam de sessões/cards/etapas elegíveis e do novo comportamento ativado pelo mecanismo suportado, com revisão humana A/R e `/hooks` aplicáveis. Executar o candidato na árvore descartável não substitui esse caminho de hooks.

A entrega posterior exige reconciliar a base dirty #1098 em contexto/binding real do nucleus e aplicar o patch ali pelos gates autorizados, preservando alterações existentes. Instalação canônica usa `install.sh --pin <tag-real> --source <checkout-real> --target <consumidor-autorizado>` somente após existir a revisão/tag factual; o comando aqui tem placeholders, não é uma tag publicada. Não usar pin antigo para rotular bytes novos. Trust pertence ao operador, não é gravado pelo installer ou pelo agente.

Onda canônica, verify-wave e checklist precommit pertencem ao pai e vencem **antes** de commit; fechamento pós-commit, pin real, ensaios after-pin, QA e atos humanos seguem as fases próprias. Postpin/strict bloqueiam enquanto os ensaios anotados continuarem abertos. Checkboxes vivos pendentes não foram promovidos por fixtures.
