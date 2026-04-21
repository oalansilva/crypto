# Fluxo OpenSpec + Codex CLI (Solo)

Este projeto usa o fluxo oficial do OpenSpec via **changes** com operação simplificada (um único operador).

Schema atual: `spec-driven` (proposal → specs → design → tasks)

## Atalho no chat
Use pedidos diretos no chat, por exemplo:
- `crie uma change openspec para <sua feature>`
- `continue a change <change_id>`
- `aplique a change <change_id>`
- `archive a change <change_id>`

## Passo a passo

### 1) Criar change
```bash
openspec new change <change_id> --schema spec-driven --description "<resumo>"
```

Padrão de branch:
- Trabalhar em `main` com commits curtos.
- Para revisão formal, usar `feature/<slug>` e PR para `main`.

### 2) Preencher artefatos do change
Arquivos típicos:
- `openspec/changes/<change_id>/proposal.md`
- `openspec/changes/<change_id>/specs/**/*.md`
- `openspec/changes/<change_id>/design.md`
- `openspec/changes/<change_id>/tasks.md`

(Use `openspec instructions <artifact> --change <change_id>` para obter instruções enriquecidas.)

### 3) Validar change
```bash
openspec validate <change_id>
```

### 4) Apply (implementação)
- Implementar tasks do `tasks.md`.
- Rodar testes.

```bash
openspec instructions apply --change <change_id> --json
```

No Codex CLI deste repo, a aplicação pode ser feita por pedido em linguagem natural no chat, usando as skills locais de OpenSpec, ou manualmente a partir das tasks do change.

### 5) Verify
```bash
openspec validate <change_id>
./backend/.venv/bin/python -m pytest -q
```

### 6) Archive
Após deploy/teste manual OK:
```bash
openspec archive <change_id>
```

## Notas
- Este repo usa o workflow oficial de `changes`, sem camada de coordenação por agente.
- Atualize as instruções do OpenSpec do projeto com `openspec update` quando necessário.
- Os artefatos principais permanecem: `proposal.md`, `specs/**/*.md`, `design.md`, `tasks.md`.
