# Design — card-1036-pin-sqlalchemy (rework: driver explícito, sem pin)

## Context

Card **#1036**, Status=Design. **Rework completo**: o âmbito mudou por decisão do dono. O Design anterior (pin `sqlalchemy>=2.0,<2.1`) está **obsoleto** e foi substituído por este. Briefing = issue grelhado/reenquadrado (Problema, História, Entra/Critérios, Não entra, Evidência de 24/09), copiado **verbatim** em `proposal.md`. Sem reentrevista. **SEM-TELA**: é infraestrutura de backend — sem painel/Monitor, sem rota, sem HTML, sem protótipo.

> **Slug histórico:** o ramo `card-1036-pin-sqlalchemy` e o `change` `card-1036-pin-sqlalchemy` mantêm o nome **histórico** (nasceram com o âmbito do pin). O nome deixou de corresponder ao âmbito actual («driver explícito»), mas **não** é renomeado: o `change` tem de continuar igual ao nome do ramo. Registe-se a divergência aqui e no handoff.

UI impact: none
live_route: N/A driver de base de dados no CI e nos testes; não há tela de produto neste card
surface: new

Sem rota autenticada, sem landing, sem HTML, sem protótipo. Nunca emprestar `/monitor`, `/favorites`, `/combo/discovery`, `/combo/select`, `landing`. Prototype **N/A**. Impeccable **N/A** (não há superfície visual).

> **Design fecha em 1+1+1 (teto):** sem-tela = 1 autor + 1 crítico + 1 rework; com-tela = autor + dupla + 1 rework. Segundo rework só com P0 novo de produto justificado no prompt; fora disso o pai publica a seção de crítica com os P3 aceitos e submete. **Classificação:** só produto/escopo/contrato visível (tela, estados, acessibilidade, escopo furado) gera P0/P1; detalhe de implementação é P3 "detalhe de Apply", aceito em `design.md` e resolvido no Apply — nunca reaberto como P0/P1. **Gate no autor:** o primeiro autor já entrega `UI impact` / `live_route` / `surface` em linha própria parseável; sem-tela declara ausência + justificativa curta (nunca rota de catálogo emprestada); com-tela marca só as regiões clonadas. O crítico/dupla verifica esses tokens como item da rubrica.

### Causa (confirmada no código do worktree)

- O SQLAlchemy **2.1** mudou o driver **implícito** de `postgresql://` de `psycopg2` para `psycopg` (v3). O projecto só instala `psycopg2-binary` (`backend/requirements.txt:10`) e **não** tem `psycopg` v3. Logo uma URL bare passa a rebentar na construção do engine com `ModuleNotFoundError: No module named 'psycopg'`.
- O import que falha está no build do engine do workflow DB: `backend/app/workflow_database.py:146` (`engine = create_engine(...)`), que sob 2.1 resolve o dialeto `psycopg` v3.
- Os helpers de guarda **aceitam as duas formas**: `backend/app/database.py:51` (`_is_postgres_url`) e `backend/app/workflow_database.py:116` fazem `startswith("postgresql://") or startswith("postgresql+psycopg2://")`. Isto é a base da distinção ligação-vs-asserção (abaixo).

### Cascata do `combo_templates` (confirmada)

Leitura do issue confirmada no código:

- `backend/tests/integration/test_ai_dashboard_dynamic.py:19-24` cria o engine e corre `Base.metadata.create_all(bind=engine)`. É o **primeiro** ficheiro de teste de integração por ordem alfabética (`conftest.py` não é teste; a seguir vêm `test_ai_dashboard_dynamic.py`, `test_binance_latest_buy_trade_rule.py`, `test_combo_backtest_data_source_inference.py`).
- Com a URL bare a rebentar em 2.1, esse `create_all` **nunca corre** → nenhuma tabela é criada na base partilhada.
- `backend/tests/integration/test_combo_backtest_data_source_inference.py:76-79` monta uma app **local** (`_build_app` / `_build_public_app` constroem um `FastAPI()` só com o router), **sem `lifespan`** — logo não corre `create_all` nem as migrações de runtime que criam/seedam `combo_templates`.
- `combo_templates` é um modelo `Base` (`backend/app/models.py:195-196`, `class ComboTemplate`), criado pelo `create_all` do primeiro ficheiro. Sem ele, o teste do combo falha com `UndefinedTable: combo_templates`.
- Logo as 3 falhas do combo são **cascata**, não incompatibilidade própria do 2.1: corrigir as URLs (o `create_all` volta a correr) deve resolvê-las. As 61 restantes são o próprio `ModuleNotFoundError: psycopg`.

### Factos do código (lidos no worktree, sem alterar nada)

- **CI — 4 valores de ligação com URL bare:** `.github/workflows/ci.yml:262` e `:263` (`DATABASE_URL` / `WORKFLOW_DATABASE_URL` do job `backend-unit-tests`), `:367` e `:368` (mesmas variáveis no job `backend-tests`). Todos `postgresql://postgres:postgres@127.0.0.1:5432/...`.
- **Instalação no CI:** `ci.yml:168`, `:292`, `:397` — `python -m pip install -r backend/requirements.txt`; `cache-dependency-path` em `:163`, `:287`, `:392`. `qa-gate` em `:511`, com `needs` a incluir `backend-unit-tests` e `backend-tests` (`:517-529`) e o passo «Require all QA checks to finish green» a exigir `success` de cada um (`:531-553`).
- **`backend/requirements.txt` NÃO muda:** `:9` permanece `sqlalchemy>=2.0.0` (sem limite superior) e `:10` permanece `psycopg2-binary>=2.9.9`.
- **Ligações reais em testes — 14 ficheiros / 15 valores** (URL que vai a `create_engine`, a `sessionmaker`/`bind`, ou a uma env `DATABASE_URL`/`WORKFLOW_DATABASE_URL`):
  1. `backend/tests/conftest.py:15,19` (defaults de env, 2 valores)
  2. `backend/tests/integration/test_ai_dashboard_dynamic.py:20`
  3. `backend/tests/integration/test_external_binance_spot_balances.py:18`
  4. `backend/tests/integration/test_workflow_audit_coordination.py:19`
  5. `backend/tests/integration/test_workflow_core_service.py:22`
  6. `backend/tests/integration/test_monitor_preferences_endpoints.py:19`
  7. `backend/tests/integration/test_system_preferences_admin.py:15`
  8. `backend/tests/integration/test_workflow_projects.py:57` (só a linha 57 deste ficheiro)
  9. `backend/tests/integration/test_user_profile_endpoints.py:20`
  10. `backend/tests/integration/test_user_binance_credentials.py:16`
  11. `backend/tests/integration/test_monitor_theme_preference.py:15`
  12. `backend/tests/integration/test_workflow_api.py:17`
  13. `backend/tests/integration/test_workflow_update_change_guards.py:37`
  14. `backend/tests/integration/test_workflow_kanban_manual_backlog.py:21`
  - Nota: `backend/tests/integration/test_discovery_service.py:75` (`create_engine(os.environ["DATABASE_URL"])`) e `backend/tests/unit/test_runtime_worker_and_workflow_db.py:98` (`unit_workflow_database_url`) são ligações reais, mas **não têm literal bare**: consomem env/fixture, cobertas pelo `conftest.py` e pelo `ci.yml`.
- **Ocorrências que são asserção / valor esperado / fixture (NÃO mudam):**
  - `backend/tests/unit/test_database_and_auth.py:81,88,90,91,94,101,102,154,192,1089` — asserts sobre `_is_postgres_url` (aceita `postgresql://`), `monkeypatch.setenv("DATABASE_URL", ...)` para routing, e `monkeypatch.setattr(database_module, "DB_URL", ...)` com o `engine` substituído por um falso.
  - `backend/tests/contract/test_backend_unit_harness.py:82,174,177,180,202,207,208,209,210,221` — :82 é texto sintético escrito num ficheiro-fixture (não é engine); as restantes são inputs de `unit_conftest._assert_safe_unit_database` / `database_guard.assert_safe_test_database_url` (guardas puras).
  - `backend/tests/integration/test_workflow_projects.py:50` (`assert "postgresql://" not in body`), `:129,146,165,247,266` — `workflow_database_url` é **metadado** de `Project` (payload/assert), nunca vai a `create_engine`.
  - `backend/tests/integration/test_user_profile_endpoints.py:255` — assert `_is_postgres_url`.
  - `backend/tests/integration/test_discovery_service.py:112` — `monkeypatch.setenv("DATABASE_URL", ...)` para o guard (a linha 108 já usa o explícito).
  - `backend/tests/test_bootstrap_env.py:27,49,58,67,105` — conteúdo textual de ficheiros `.env` de fixture.
  - `backend/tests/unit/test_ohlcv_storage.py:124,161,176,197` — `monkeypatch.setattr(..., "DB_URL", ...)` com `engine` falso.
  - `backend/tests/unit/test_runtime_status.py:14` — env para teste de máscara.
  - `backend/tests/unit/test_runtime_worker_and_workflow_db.py:34,65,68,75,78,80,87,114,137` — asserts de `_is_postgres_url` e strings de registry/metadado de teste.
  - `backend/app/database.py:51`, `backend/app/workflow_database.py:116`, `backend/scripts/cleanup_beta_test_users.py:58,162` — código de produto que aceita as duas formas; **fora do escopo** (não se altera app).
- **DEV usa o explícito:** `/srv/apps/dev/criptofarol/source/backend/.env` tem `postgresql+psycopg2://` nos **4** valores (`DATABASE_URL`, `WORKFLOW_DATABASE_URL`, `CRYPTO_DATABASE_URL`, `CRYPTO_WORKFLOW_DATABASE_URL`). O overlay confirma DEV (`dev.criptofarol.com.br`, db `crypto_app_dev`) e PROD (`criptofarol.com.br`, db `crypto_app`).
- **O `restart` não reinstala dependências:** `/srv/apps/dev/criptofarol/source/restart` corre `alembic upgrade head`, build do frontend e (re)instalação de units systemd; **não** há `pip install`. O risco do 2.1 materializa-se no CI e numa reconstrução de venv, não no arranque corrente.
- **Venv de DEV:** `sqlalchemy-2.0.50.dist-info` e `psycopg2_binary-2.9.12.dist-info` presentes, **sem** `psycopg` v3. Instalar o 2.1 aqui para «reproduzir a falha» partiria o DEV.
- **Relação com o #1037:** o pin/limites saem deste card; o **#1037** continua a tratar limites e indirectos. Não é editado aqui.

## Goals / Non-Goals

**Goals:**

- Uma instalação limpa resolve SQLAlchemy **2.1.x** (sem pin) e o CI corre nessa versão, provando que o 2.1 não tem incompatibilidades conhecidas para além do driver implícito.
- Todos os sítios de **ligação** no CI e nos testes declaram o driver explicitamente (`postgresql+psycopg2://`), sem depender de um valor por omissão do fornecedor.
- `backend-unit-tests` e `backend-tests` correm até ao fim sem `ModuleNotFoundError: psycopg` e sem `UndefinedTable`; `qa-gate` verde.

**Non-Goals:**

- Pinar/limitar o SQLAlchemy ou qualquer outra dependência (é o #1037).
- Migrar para o driver `psycopg` v3 ou adicionar `psycopg[binary]`.
- Alterar código de aplicação, migrações ou modelos; alterar `backend/requirements.txt`.
- Alterar strings de asserção/esperadas que continuam válidas; tocar em `frontend/**`, PROD, base de dados de produto, painel/Monitor.

## Decisions

1. **Formato fixado: `postgresql+psycopg2://`.** Mantém o `psycopg2`, que já está instalado (`psycopg2-binary>=2.9.9`), e é a forma que o DEV/PROD já usam. É a substituição textual de `postgresql://` por `postgresql+psycopg2://` em cada sítio de ligação.
   *Alternativa rejeitada —* **`postgresql+psycopg://`**: obrigaria a instalar o `psycopg` v3, que não está no `requirements.txt`; alargaria o escopo e misturar-se-ia com a migração de driver (Non-Goal).
   *Alternativa rejeitada —* **pinar o SQLAlchemy `<2.1`** (o âmbito antigo): o dono decidiu sem pin; o #1037 trata limites e o pin só esconderia o problema em vez de o resolver.
2. **Âmbito de ficheiros: os 4 valores do `ci.yml` + 14 ficheiros de teste (incluindo o `conftest.py`) = 19 valores em 15 ficheiros.** As **ocorrências de asserção/esperadas/fixture não mudam** — só se altera uma string se ela for **usada como** URL de ligação (passada a `create_engine`, a `sessionmaker`/`bind`, ou a uma env `DATABASE_URL`/`WORKFLOW_DATABASE_URL`). Exclusões justificadas em §Factos (ex.: `test_database_and_auth.py` e `test_backend_unit_harness.py` são asserts de guarda; as `workflow_database_url` de `Project` são metadado).
   *Alternativa rejeitada —* **trocar as 66 ocorrências indiscriminadamente**: mexeria em asserts que testam exactamente as formas aceites (`_is_postgres_url` aceita ambas) e em fixtures de texto, sem ganho e com risco de quebrar testes.
   *Alternativa rejeitada —* **mudar só o `ci.yml`** (o fix do PR #1038): deixa 61 falhas por URLs hardcoded nos testes; não fecha o card.
3. **Prova: CI do próprio PR, com `sqlalchemy-2.1.x` no log de instalação.** O PR da mudança tem de mostrar `backend-unit-tests` e `backend-tests` a **correr até ao fim sem falhas** (sem `ModuleNotFoundError: psycopg` e sem `UndefinedTable`) e o `qa-gate` verde, com a linha `Successfully installed ... sqlalchemy-2.1.x` no log. Não se instala o 2.1.0 no venv de DEV.
   *Alternativa rejeitada —* **reproduzir instalando `sqlalchemy==2.1.0` no venv de DEV**: partiria o DEV, que o `restart` reusa sem reinstalar; o card não autoriza tocar no DEV.
   *Alternativa rejeitada —* **aceitar o último run verde de `develop`**: é pré-publicação do 2.1.0 e corre 2.0.54; não executa a configuração nova.
4. **Relação com o #1037: o pin/limites saem daqui.** Com o driver explícito, o pin deixou de ser necessário; o #1037 continua a tratar limites e indirectos. Regista-se a relação, **sem** editar o outro card.
   *Alternativa rejeitada —* **incluir lock file / limites neste card**: alargaria o escopo e duplicaria o #1037.
5. **Nota de processo (honestidade).** O âmbito anterior (pin de 1 linha) nasceu de uma diagnoze **incompleta**: viu-se o sintoma (o 2.1 mudou o driver implícito) e não se perguntou *«porque é que o CI difere do DEV/PROD?»*. O `## Não entra` original chegava a **proibir** tocar no CI — ou seja, o card estava desenhado para não poder fazer a correcção certa. O DEV/PROD sempre usou o driver explícito e nunca correu risco. Este rework corrige o âmbito.

## Risks / Trade-offs

- [Risco] O 2.1 pode trazer outras incompatibilidades reais que só apareçam ao correr a suíte completa. Mitigação: é precisamente o que o CI do PR mede; **se** surgirem falhas que não sejam o `psycopg` implícito nem a cascata do `create_all`, são defeito real e param o Apply como P0 visível (não residual).
- [Risco] Alguma ocorrência de asserção ser, afinal, usada como ligação e ficar por converter. Mitigação: o contrato exige classificar cada ocorrência como ligação vs asserção; as ligações indirectas usam env/fixture e são cobertas pelo `conftest.py`/`ci.yml`.
- [Risco] O `conftest.py` usa `setdefault` e no CI o valor do job ganha. Mitigação: **os dois** sítios (job env e default) mudam, logo não há divergência de configuração.
- [Trade-off] O DEV continua em 2.0.50 e o 2.1 não é testado localmente. Aceite: o 2.1 é testado no CI do PR; testar localmente exigiria instalar o 2.1 no venv de DEV (rejeitado).
- [Trade-off] Sem pin, uma futura 2.1.x/2.2.x pode voltar a mudar comportamento. Aceite: é o objectivo do card (não depender de implícitos); o CI passa a detectar isso em vez de o esconder.
- [Trade-off] `requirements.txt` fica intacto, logo a chave de cache do pip não é invalidada. Aceite: a resolução do pip continua a escolher o último candidato (`2.1.x`), que é o pretendido.

## Apply contract

**Contrato visível (não P3):**

- **Formato exacto do driver:** substituir `postgresql://` por `postgresql+psycopg2://` em cada sítio de ligação. Sem outra forma (`+psycopg` v3, `+asyncpg`, etc.).
- **Distinção ligação-vs-asserção (o que muda e o que não muda):**
  - **Muda** — URL de ligação real: passada a `create_engine`, a `sessionmaker`/`bind`, ou a uma env `DATABASE_URL` / `WORKFLOW_DATABASE_URL`. São os **4** valores do `ci.yml:262,263,367,368` e os **15** valores dos **14** ficheiros de teste listados no Context.
  - **Não muda** — string de asserção, valor esperado, conteúdo de fixture ou entrada de guarda (ex.: `assert _is_postgres_url("postgresql://db")`, `monkeypatch.setattr(..., "DB_URL", "postgresql://unit")` com engine falso, `assert "postgresql://" not in body`, `workflow_database_url` de `Project`). `_is_postgres_url` (`backend/app/database.py:51` / `backend/app/workflow_database.py:116`) aceita as duas formas, logo essas asserções continuam válidas sem tocar. Se uma string de teste for usada **como** URL de ligação, conta como ligação.
- **`backend/requirements.txt` NÃO muda:** `:9` fica `sqlalchemy>=2.0.0` (sem limite superior) e `:10` fica `psycopg2-binary>=2.9.9`. Sem `psycopg` v3.
- **Escopo de ficheiro:** só `.github/workflows/ci.yml` (4 valores) e os 14 ficheiros de teste (incluindo `backend/tests/conftest.py`). Sem `backend/app/**`, `backend/alembic/**`, `backend/Dockerfile`, `frontend/**`, base de dados de produto, PROD.
- **Prova obrigatória:** CI do **próprio PR** verde, com `sqlalchemy-2.1.x` no log de instalação; `backend-unit-tests` e `backend-tests` correm até ao fim **sem falhas** (sem `ModuleNotFoundError: No module named 'psycopg'`, sem `UndefinedTable`) e `qa-gate` verde.
- **DEV/PROD inalterados:** nenhuma alteração em `.env`, units systemd, `restart`, migrações ou base de dados; já usam `postgresql+psycopg2://`.

**P3 — detalhe de Apply (aceito aqui, resolvido no Apply — não reabrir como P0/P1):**

- Comandos exactos de verificação local (pytest/integração) e onde fica a evidência (comentário do card e/ou `evidence/`).
- Ordem mecânica das edições e eventual uso de `sed`/script de substituição limitado aos ficheiros listados.
- Se o Apply regista uma nota de rastreio para o **#1037** (sem comentar/editar o outro card).

## Open Questions

Nenhuma. A história veio reenquadrada no issue e o *como* fecha nas decisões 1–5. O que resta (comandos exactos, ordem mecânica) é detalhe de Apply (P3). Novas falhas reais do 2.1 que a suíte exponha não são questão de Design: tratam-se no Apply como P0 visível.

## Design Critique

Publicada pelo pai após a onda de crítica (excepção prevista no runbook). Sem-tela: o crítico é **um**; sem onda A/B, sem protótipo, sem clone de página viva e sem Snapshot Impeccable.

**Onda desta entrada (teto 1+1+1, sem-tela):** 1 autor (rework completo) → 1 crítico → **sem rework**. `rework: nao`, `p0_p1_count: 0`. A coluna segue para `Aprovação de Design`.

**Crítico (ronda do rework):** rubrica **10/10 `ok`** — tokens do gate, briefing verbatim, **âmbito completo**, causa e cascata confirmadas, formato fixado, `requirements.txt` inalterado, escopo, cobertura dos critérios observáveis, tasks e a nota de processo. Cinco achados, todos **P3** com `bloqueia_merge: nao` — gravidade e classe copiadas do dump, sem reclassificação:

| id | gravidade | classe | bloqueia_merge | achado | fecho |
| --- | --- | --- | --- | --- | --- |
| A1 | **P3** | mecanico | nao | `design.md` cita uma linha que já usa o explícito como se fosse bare (drift de número de linha). | **Aceito** (detalhe de Apply): resolvido ao editar. |
| A2 | **P3** | mecanico | nao | Duas referências de linha com drift (`test_discovery_service.py`, `test_runtime_worker_and_workflow_db.py`). | **Aceito** (detalhe de Apply). |
| A3 | **P3** | juizo | nao | `surface: new` num card sem tela. | **Aceito**: tokens parseáveis e coerentes com a convenção do repo; não é defeito. |
| A4 | **P3** | mecanico | nao | Reconciliação `16 ficheiros` (body) vs `14 de ligação` (Design) só implícita. | **Fechado pelo pai**: body e `proposal.md` alinhados para **14 ficheiros / 15 valores / 66 ocorrências** e reconfirmados verbatim. |
| A5 | **P3** | mecanico | nao | Wording do `spec.md` sobre o que conta como «ligação». | **Aceito**: já resolvido pelo carve-out dos *guard inputs*. |

**Âmbito completo?** **SIM** — veredicto explícito do crítico: **nenhum sítio de ligação ficou de fora**. Os **19 valores em 15 ficheiros** (4 do `ci.yml` + 15 em 14 ficheiros de teste, incl. `conftest.py`) cobrem todos os `create_engine`/`sessionmaker`/`bind` com literal bare e todas as env `DATABASE_URL`/`WORKFLOW_DATABASE_URL` que vão a engine. Os deixados de fora estão bem classificados: asserções de guarda (`test_backend_unit_harness.py`, `test_database_and_auth.py`), metadado de `Project` (`test_workflow_projects.py`), fixture/texto (`test_bootstrap_env.py`) e configs com engine falso (`test_ohlcv_storage.py`, `test_runtime_status.py`). O erro de contrato que este rework corrigia — ligação tratada como asserção — **não ocorre**.

**Cascata confirmada?** **SIM**: `test_ai_dashboard_dynamic.py:19-23` cria o engine bare e corre `Base.metadata.create_all`; com a URL a rebentar em 2.1, o `create_all` não corre → sem tabelas; `combo_templates` é `ComboTemplate(Base)` (`backend/app/models.py:195`) e o teste do combo monta app local **sem `lifespan`** (`test_combo_backtest_data_source_inference.py:76-79`) → `UndefinedTable`.

**Factos verificados pelo crítico** (bate certo): `ci.yml:262,263,367,368` (URLs bare), `:168,292,397` (installs), `:511,517-529,531-553` (`qa-gate` e `needs`); `backend/requirements.txt:9-10` **sem pin**; `conftest.py:15,19` + `:21-22`; os 14 ficheiros/15 valores de ligação; `database.py:49-51` e `workflow_database.py:116` (`_is_postgres_url` aceita ambas as formas); `workflow_database.py:146`; `models.py:195`; `test_combo_backtest_data_source_inference.py:76-79`; `validate --strict` verde; `restart` **sem** `pip install`.

**Sem achados de produto/escopo:** confirmado — nenhum P0/P1; sem pin, sem `psycopg` v3, sem código de aplicação/migrações, sem `frontend/**`, sem PROD.

**Proxies desta entrada:** spawns = **2** (autor do rework, crítico; sem rework). HTML generated vs copied = **N/A vs N/A**. Prototype **N/A**. Impeccable **N/A**. Cliente Cursor: os dois filhos de juízo correram com o slug `juizo` do `.cursor/model-map.yaml`.

### Ronda anterior — Design original (pin), substituída

O primeiro Design fixava o **pin** `sqlalchemy>=2.0,<2.1` e foi aprovado pelo dono (T7). Ficou **obsoleto**: a experiência do PR #1038 mostrou que o CI arrancava com o 2.1 e falhava por **URLs hardcoded** (61) e por **cascata** (3), não por incompatibilidade do SQLAlchemy. Essa onda (1 autor + 1 crítico, `rework: nao`, `p0_p1_count: 0`, 2 P3) foi substituída por este rework por decisão do dono — **sem pin**, driver explícito. O registo do evento está no comentário de reenquadramento do card.
