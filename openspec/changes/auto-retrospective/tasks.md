# Tasks — Card #77: Auto-Retrospective após cada Feature

## Tasks Técnicas

### 1. Hook de Trigger — Homologação
**Descrição:** Adicionar trigger no endpoint/fluxo de homologação do orchestrator para disparar pipeline de retrospective quando uma feature for marcada como `homologada`.
**Critério de Done:** Ao marcar qualquer card como homologado no Kanban, o pipeline de retrospective é disparado sem bloquear o retorno.
**Dependências:** nenhuma
**Estimativa:** 2h

### 2. Coletor de Dados Contextuais
**Descrição:** Criar módulo que consulta runtime/tasks API e Kanban API para extrair: tempo total, tempo por stage, quantidade de ciclos de revisão, blockers, bugs abertos.
**Critério de Done:** Módulo retorna objeto estruturado com todos os dados coletados para uma feature específica.
**Dependências:** task 1
**Estimativa:** 4h

### 3. Classificador de Risco
**Descrição:** Implementar lógica de classificação: `sem_problemas` / `com_ressalvas` / `problemática` baseada em thresholds (ex: >3 ciclos revisão = com ressalvas, blocker >48h = problemático).
**Critério de Done:** Dado o objeto de dados da task 2, retorna classificação coerente com thresholds configuráveis.
**Dependências:** task 2
**Estimativa:** 2h

### 4. Gerador de Insights via LLM
**Descrição:** Usar `acpx codex` para gerar insights textuais (o que funcionou, o que não funcionou, recomendações) a partir dos dados estruturados da retrospective.
**Critério de Done:** Dados os dados + classificação, gera markdown legível com insights acionáveis.
**Dependências:** tasks 2 e 3
**Estimativa:** 4h

### 5. Persistência em Markdown
**Descrição:** Gravar relatório de retrospective em `/root/.openclaw/workspace/crypto/docs/retrospectives/YYYY-MM-DD-{feature-slug}.md` com estrutura padronizada.
**Critério de Done:** Arquivo criado com campos: feature, data, dados coletados, classificação, insights.
**Dependências:** task 4
**Estimativa:** 1h

### 6. Endpoint de Consulta
**Descrição:** Criar endpoint `GET /retrospectives/{feature-slug}` para consultar retrospectiva de uma feature específica.
**Critério de Done:** Endpoint retorna markdown do relatório persisted, ou 404 se não existir.
**Dependências:** task 5
**Estimativa:** 2h

### 7. Execução Assíncrona (não bloqueante)
**Descrição:** Garantir que o trigger de retrospective não bloqueie o retorno de homologação — usar background job/queue.
**Critério de Done:** Homologação retorna imediatamente; retrospective é processada em background.
**Dependências:** task 1
**Estimativa:** 2h

### 8. Testes End-to-End
**Descrição:** Criar teste E2E que marca uma feature como homologada e verifica se a retrospective foi gerada e persistida corretamente.
**Critério de Done:** Playwright test passa: feature homologada → retrospective existe em arquivo e endpoint.
**Dependências:** tasks 1-7
**Estimativa:** 4h

---

## Resumo de Estimativa

| Task | Estimativa |
|------|-----------|
| 1. Hook de Trigger | 2h |
| 2. Coletor de Dados | 4h |
| 3. Classificador de Risco | 2h |
| 4. Gerador de Insights | 4h |
| 5. Persistência | 1h |
| 6. Endpoint | 2h |
| 7. Execução Assíncrona | 2h |
| 8. Testes E2E | 4h |
| **Total** | **21h** |

---

## Ordem de Execução

```
1 → 2 → 3 → 4 → 5 → 6 → 7 (7 pode paralelizar com 2-6)
8 (QA, após todas as outras)
```

---

## Dados Mínimos para Análise (Definição Pré-implementação)

Antes de iniciar, definir os campos mínimos:
- `started_at` (primeiro commit)
- `homologated_at`
- `stage_times: {po, design, dev, qa}`
- `review_cycles_count`
- `blocker_events: [{start, end, duration}]`
- `open_bugs_at_homologation`
- `card_type` (feature, bugfix, etc.)

Esses campos precisam existir na runtime/tasks API.
