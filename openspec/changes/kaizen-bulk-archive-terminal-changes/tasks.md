## 1. Bulk archive

- [x] 1.1 Levantar lista de changes ativas com 4/4 artifacts done via `openspec status --change <name> --json` para todas em `openspec/changes/`
- [x] 1.2 Mapear card vinculado (nome `card-<id>-*`/`issue-<id>-*` ou referência no proposal) e confirmar status terminal (`Pronto`/`Cancelado`) via `gh project item-list 1 --owner oalansilva`
- [x] 1.3 Para cada change elegível, rodar archive via CLI/skill `openspec` (sync de delta specs quando aplicável) movendo para `openspec/changes/archive/YYYY-MM-DD-<change>/` — 33 changes arquivadas em 2026-08-11; issue-71 com --skip-specs (deltas obsoletos vs main spec evolvido); fix-saldo-usdt-compra REATIVADA após review (card #463 Homologado, em fluxo — archive indevido corrigido); sync de specs de monitor/opportunity-monitor/strategy-template-descriptions revertido para HEAD (deltas antigos sobrescreviam conteúdo mais novo de card-278) e reaplicado só o delta novo (5 ADDED de monitor)
- [x] 1.4 Changes sem card vinculado ou não concluídas: classificação manual (integrar/arquivar com evidência) e registro
- [x] 1.5 Se CLI/skill falhar em alguma change, archive manual com registro da exceção operacional e evidência (regra AGENTS.md)

## 2. Guard: check de changes terminais

- [x] 2.1 Adicionar seção "OpenSpec terminal changes" ao `scripts/release-guard` (post/audit): detecta changes ativas com 4/4 done cujo card é `Pronto`/`Cancelado`; audit → warn, post → blocker exigindo archive/classificação
- [x] 2.2 Fail-closed: se `gh` falhar na consulta do board, reportar issue em post
- [x] 2.3 Atualizar `AGENTS.md` (regra de validação OpenSpec global) com a nova checagem

## 3. Validação

- [x] 3.1 `openspec validate --all` verde após o archive
- [x] 3.2 `bash -n scripts/release-guard` sem erros
- [x] 3.3 Rodar `scripts/release-guard audit` e confirmar que não reporta mais as changes arquivadas
