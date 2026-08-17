# Design: kaizen-dedupe-card-comments

## Context

- Auditoria 2026-08-09 (release kaizen 421-440) e anterior (#438 F-5): cards receberam 2 comentários "Implementação concluída" para o mesmo commit/PR, variando apenas o formato de referência (URL vs "PR N (sha)").
- O fechamento é feito por agentes (opencode/Codex) que postam comentários manualmente via `gh issue comment`; não há hoje nenhum controle de unicidade.
- Os templates canônicos estão em `AGENTS.md` (Implementação concluída / Homologado por Alan / Publicado em main).

## Goals / Non-Goals

- Goals: 1 comentário de evidência por transição (Done/Homologado/Pronto) por card; dedupe por commit ref normalizado; zero duplicações na próxima release.
- Non-Goals: não alterar os templates canônicos de `AGENTS.md`; não criar UI; não mudar o board nem o fluxo de status.

## Decisions

- **D1 — Helper bash `scripts/post-card-evidence-comment.sh`**: novo script versionado no repo, chamado pelo agente no fechamento (Done/Homologado/Pronto) em vez de `gh issue comment` cru.
  - Rationale: bash é o padrão do repo (`scripts/release-guard`); sem nova dependência; testável.
  - Alternativa considerada: skill/plugin opencode — rejeitada por ficar fora do repo versionado (mais frágil para auditoria).
- **D2 — Dedupe por transição + commit ref normalizado**: o script busca comentários existentes do card (`gh issue view --comments`), extrai SHA/ref via regex dos formatos conhecidos (URL `github.com/.../commit/<sha>`, "PR N (sha)") e bloqueia postagem se já houver comentário da mesma transição (detectada pela linha-chave do template, ex.: "Implementação concluída.") com mesmo SHA.
  - Rationale: cobre exatamente o caso real (mesmo commit, formatos diferentes) e é determinístico.
  - Alternativa: dedupe só por transição, sem SHA — rejeitada (falso positivo quando o card passa 2x por Done de commits diferentes... não é o caso real, mas SHA evita colisão).
- **D3 — Fail-safe**: se `gh` falhar ao listar comentários (auth/rate limit), o script falha com mensagem clara e NÃO posta (fail-closed), evitando duplicação.
- **D4 — Modo `--dry-run`**: imprime o que seria postado sem postar, para o agente validar antes.

## Risks / Trade-offs

- [Regex de ref pode não casar formato futuro de comentário] → centralizar extração em função `extract_commit_ref` e manter a lista de padrões em variável documentada; se não casar, considera "sem ref" e dedupe cai para transição apenas com aviso.
- [Comentário de evidência legado não padronizado (já postado manualmente)] → o dedupe compara também por transição; se o legado não casar SHA, é aceito como evidência existente sem duplicar (o objetivo é evitar duplicação, não reescrever histórico).
- [Falha de gh no meio do fechamento em lote] → fail-closed: nenhum comentário duplicado; o agente diagnostica e reexecuta.

## Migration Plan

1. Criar `scripts/post-card-evidence-comment.sh` com suporte a `--transition done|homologado|pronto`, `--card <n>`, `--commit <sha>`, `--pr <n>` (opcional), `--dry-run`.
2. Atualizar `AGENTS.md` (seção "Comentários obrigatórios no Kanban") para exigir o uso do helper.
3. Rollback: reverter o commit do helper; o `AGENTS.md` volta ao manual.
4. Não há runtime/DB/migração envolvidos.

## Open Questions

- Nenhuma (decisões definidas; verificação de duplicação coberta pelo critério de aceite "0 duplicações na próxima release").

## Design Critique

- UI impact: **none** — mudança 100% tooling/processo (script bash + docs); nenhuma superfície visual do produto é criada ou alterada.
- Impeccable: **N/A** — sem UI; justificativa: não há interface, componente ou fluxo visual envolvido.
- Prototype Validation: **N/A** — sem protótipo HTML; superfície de validação é o próprio script/teste de dedupe.
- Critérios de aceite verificáveis: (1) helper existe e dedupe por transição+commit ref; (2) 1 comentário por transição por card; (3) zero duplicações na próxima release (medido na auditoria kaizen seguinte).
- Design Agent verdict: **PASS** — decisões D1-D4 definem implementação sem ambiguidade; nenhum achado bloqueante em produto/UX/a11y (não aplicável) ou escopo.

