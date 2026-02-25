# Proposal — LangGraph Studio integration (Strategy Lab)

## One-liner

Tornar a spec **`crypto.lab.langgraph.studio.v1`** compatível com o workflow oficial do **OpenSpec (Fission-AI)**, com artefatos completos (proposal/specs/design/tasks), validação via **`openspec validate`**, e link do viewer para revisão do Alan antes de implementar.

## Why

Porque precisamos padronizar o nosso processo de specs e validação no **OpenSpec oficial** (Fission-AI), garantindo que:
- validação seja feita via CLI (`openspec validate`),
- artefatos (proposal/specs/design/tasks) existam para reduzir ambiguidade,
- o Alan revise via link do viewer antes de qualquer implementação.

## Motivation / Problem

- Hoje temos uma spec para integrar o **Strategy Lab** com **LangGraph Studio**, mas ela foi criada/validada fora do fluxo oficial do OpenSpec.
- No nosso workflow padrão, a validação deve ser feita via **CLI** (`openspec validate`) e só depois compartilhamos o link do viewer para revisão.

## Scope

### In scope

- Recriar a proposta como uma **OpenSpec Change** usando o schema `spec-driven`:
  - `proposal.md`
  - `specs/**/spec.md` com requisitos + cenários testáveis
  - `design.md` (decisões/arquitetura, linkagem run_id↔trace)
  - `tasks.md` (checklist de implementação)
- Após `openspec validate` passar:
  - Atualizar (ou consolidar) a spec principal em `openspec/specs/crypto.lab.langgraph.studio.v1.md` para refletir os requisitos finais.
  - Manter o ID da spec: **`crypto.lab.langgraph.studio.v1`**.

### Out of scope

- Implementar a feature agora (isso só acontece depois do Alan mandar **"implementar"**).
- Expor o LangGraph Studio publicamente na internet.
- Criar um builder visual do grafo.

## Stakeholders

- **Alan**: reviewer e aprovador (gate antes de implementar).

## Success criteria

- `openspec validate redo-langgraph-studio-integration --strict` passa.
- Link do viewer `http://31.97.92.212:5173/openspec/crypto.lab.langgraph.studio.v1` abre e mostra a spec atualizada.
- A spec tem requisitos e cenários que guiam implementação e testes.
