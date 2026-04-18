# Contributing

Este repositório usa um fluxo simples de contribuição para manter o monorepo previsível desde o início do projeto.

## Branches

- `main`: branch de release. Protegida. Não faça push direto.
- `develop`: branch de integração. Protegida. PRs de features e bugs entram aqui por padrão.
- `feature/<nome-curto>` ou `card-<id>-<nome-curto>`: branches de trabalho.
- `hotfix/<nome-curto>`: correções urgentes ligadas a produção.

## Fluxo recomendado

1. Atualize sua branch local a partir de `develop`.
2. Crie uma branch de trabalho.
3. Faça as mudanças com escopo pequeno e objetivo.
4. Rode os checks locais antes de abrir o PR.
5. Abra um Pull Request para `develop`.
6. Use `main` apenas para merges de release/hotfix aprovados.

## Setup local

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Frontend

```bash
cd frontend
npm install
```

## Checks locais

### Python

```bash
./backend/.venv/bin/python -m black backend
./backend/.venv/bin/python -m pytest -q
```

### Frontend

```bash
npm --prefix frontend run lint
npm --prefix frontend run build
```

## Pull Requests

- Escreva uma descrição curta com contexto, impacto e risco.
- Referencie o card/change quando existir.
- Inclua screenshot para mudanças de UI.
- Não misture refactor amplo com bugfix/feature no mesmo PR.

## Segurança

- Nunca commite `.env`, credenciais, tokens ou dumps locais.
- Revise mudanças de configuração antes de subir para `main` ou `develop`.
