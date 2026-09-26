# card-1036-pin-sqlalchemy — Driver de base de dados explícito no CI e nos testes

> **Nota do que este card faz:** torna o driver **explícito** (`postgresql+psycopg2://`) em **todos** os sítios com URL de base de dados no CI e nos testes, para que a instalação deixe de depender do driver implícito de `postgresql://` que o SQLAlchemy 2.1 mudou para `psycopg` (v3). É uma alteração de ficheiros de configuração de CI e de testes: sem tela, sem rota/HTML, sem painel, sem base de dados de produto, sem PROD. `backend/requirements.txt` **não** muda (sem pin). O slug `pin-sqlalchemy` do ramo/change é **histórico** e não corresponde ao âmbito actual.
>
> As 5 secções abaixo são copiadas **verbatim** do body actual do issue #1036 (24/09).

Card reenquadrado em 24/09 (ver comentário de reenquadramento). **Bloqueia todos os PRs novos do repositório.**

## Problema

Quem manda trabalho para o repositório vê o CI do backend deixar de arrancar sem ninguém tocar no código: as URLs de base de dados do CI e de 14 ficheiros de teste dependem do **driver implícito** da URL `postgresql://`, e o SQLAlchemy 2.1 mudou esse implícito de `psycopg2` para `psycopg` (v3), que não está instalado. Uma publicação upstream partiu o CI por inteiro.

## História

Como dono do repositório, quero que todas as URLs de base de dados declarem o **driver explicitamente**, para que a configuração deixe de depender de um valor por omissão que o fornecedor pode mudar — e para que o CI teste a mesma configuração que o DEV e o PROD usam.

## Entra

- Tornar o driver **explícito** (`postgresql+psycopg2://`) em **todos** os sítios com URL de base de dados no CI e nos testes: os 4 valores do `.github/workflows/ci.yml` (jobs `backend-unit-tests` e `backend-tests`), os **14 ficheiros de teste** com ligação real (15 valores) (`backend/tests/integration/**`, `backend/tests/unit/**`, `backend/tests/contract/**`) e o `backend/tests/conftest.py`.
- **Sem pin e sem limite superior:** o `sqlalchemy>=2.0.0` fica como está e o CI passa a correr no **2.1**.
- Corrigir, no mesmo passo, qualquer teste que só falhava por **cascata** do driver (nomeadamente os que dependem de as tabelas serem criadas por outro teste).

Critérios observáveis:

- Dada uma URL de base de dados no CI ou nos testes, o driver está declarado explicitamente (nenhuma `postgresql://` sem driver em contexto de ligação).
- Dada uma instalação limpa, o SQLAlchemy resolvido é **2.1.x** (sem pin).
- Dado um PR novo, `backend-unit-tests` e `backend-tests` correm até ao fim **sem falhas** e o `qa-gate` fica verde.
- O DEV e o PROD não são alterados (já usam o driver explícito).

## Não entra

- Fixar / limitar a versão do SQLAlchemy ou de qualquer outra dependência (**é o #1037**; com o driver explícito o pin deixou de ser necessário).
- Migrar para o driver `psycopg` v3 ou adicionar `psycopg[binary]`.
- Alterar o código de aplicação, as migrações ou os modelos.
- Tocar em `frontend/**`, base de dados de produto, painel/Monitor ou PROD.

## Evidência (24/09)

- O SQLAlchemy **2.1.0** foi publicado a 24/09 **20:27 UTC**; o último run verde em `develop` (02:12 UTC, commit `94e6ef1c`) instalou **2.0.54** e passou com **0 falhas**.
- Nas 2.1 o driver implícito de `postgresql://` passou a `psycopg` (v3), ausente: `psycopg2-binary>=2.9.9` está instalado, `psycopg` não. Erro: `app/workflow_database.py:146` → `sqlalchemy/dialects/postgresql/psycopg.py:497` → `ModuleNotFoundError: No module named 'psycopg'`.
- Medido em venv descartável com SQLAlchemy 2.1.0 + `psycopg2`, **sem** `psycopg` v3: `postgresql://` → falha; `postgresql+psycopg2://` → **funciona** (`driver=psycopg2`); `postgresql+psycopg://` → falha.
- O **DEV e o PROD nunca estiveram em risco**: usam `postgresql+psycopg2://` explícito. Só o CI e os testes dependiam do implícito — o CI testava uma variante que ninguém usa.
- PR #1038 (fix do `ci.yml`) com as 2.1: a suíte **arrancou** (já não falhava na coleta) e falhou **59 + 5** — 61 por `ModuleNotFoundError: psycopg` (URLs hardcoded) e 3 por `UndefinedTable: combo_templates`, que são **cascata**: `backend/tests/integration/test_ai_dashboard_dynamic.py:19-24` (primeiro ficheiro de integração, ordem alfabética) é quem cria as tabelas (`Base.metadata.create_all`); com a URL bare a rebentar, o `create_all` nunca corre e o teste do combo — que monta uma app **local sem `lifespan`** — não as encontra.
- **14 ficheiros de teste** com ligação real (**15 valores**) e **66 ocorrências** do literal `postgresql://` no backend (em 24 ficheiros).
