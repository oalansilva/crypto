# Funil Social → Site → Leads Implementation Plan

> **For Hermes:** Use `alan-workflow` + `alan-workflow-ambientes`. Ambiente padrão: **DEV**. Não alterar PROD sem pedido explícito do Alan.

**Goal:** Criar rastreamento confiável do funil Cripto Farol desde posts no Buffer até navegação no site e cadastro/lead.

**Architecture:** Usar UTMs como chave de atribuição, capturar UTMs no frontend, persistir atribuição no backend junto ao lead/audit log e medir eventos de navegação com PostHog. Depois consolidar social/site/leads em dashboard simples.

**Canonical workspace:** `/srv/apps/dev/criptofarol/source` para implementação/validação em DEV. Não usar `/root/crypto` para novas mudanças de runtime; essa pasta é clone/branch auxiliar de material social.

**Tech Stack:** React/Vite frontend, FastAPI backend, SQLAlchemy, PostgreSQL em runtime/QA, Buffer, PostHog, Metabase opcional.

---

## Contexto atual verificado

- Backend de leads existe em `backend/app/routes/leads.py`.
- Payload atual de lead aceita `name`, `email`, `whatsapp`, `profile`, `pain`, `origin`.
- Serviço de criação de acesso beta fica em `backend/app/services/beta_access.py`.
- Hoje `_metadata_for_lead()` grava apenas flags e `origin` em `BetaAccessAuditLog.metadata_json`.
- Modelo `User` não tem campos UTM próprios; `BetaAccessAuditLog.metadata_json` já é bom ponto inicial para atribuição sem mexer pesado no schema de usuários.
- Não encontrei implementação atual de PostHog/analytics/UTM no frontend.

## Princípio de decisão

Primeiro resolver **atribuição**. Dashboard vem depois.

Se links e leads não carregarem UTM, qualquer relatório será fraco.

---

## Fase 1 — Atribuição mínima confiável

### Task 1: Definir contrato de UTMs dos posts

**Objective:** Criar padrão único para links usados no Buffer.

**Files:**
- Create: `docs/analytics/utm-social-contract.md`
- Update when scheduling posts: `docs/redes-sociais/**/texto.md`

**Padrão:**

```text
utm_source=<instagram|linkedin|whatsapp|telegram|direct>
utm_medium=social
utm_campaign=criptofarol_semana_<n>
utm_content=<canal>_<formato>_<yyyy_mm_dd>_<slug>
```

**Exemplos:**

```text
https://criptofarol.com.br/?utm_source=instagram&utm_medium=social&utm_campaign=criptofarol_semana_1&utm_content=ig_empresa_carrossel_2026_06_10_comprar_no_escuro
```

```text
https://criptofarol.com.br/?utm_source=linkedin&utm_medium=social&utm_campaign=criptofarol_semana_1&utm_content=linkedin_pessoal_2026_06_11_beta_clareza
```

**Validation:**
- Todo rascunho Buffer precisa ter link com `utm_source`, `utm_medium`, `utm_campaign`, `utm_content`.
- Ao alterar texto/link de post, atualizar Buffer no mesmo ciclo.

---

### Task 2: Criar utilitário frontend para capturar e persistir UTMs

**Objective:** Guardar UTMs/referrer no navegador para que o formulário de lead envie a atribuição mesmo se o usuário navegar antes de cadastrar.

**Files:**
- Create: `frontend/src/lib/attribution.ts`
- Modify: `frontend/src/main.tsx` ou componente raiz equivalente

**Implementation sketch:**

```ts
export type AttributionPayload = {
  utm_source?: string
  utm_medium?: string
  utm_campaign?: string
  utm_content?: string
  utm_term?: string
  referrer?: string
  landing_path?: string
  first_seen_at?: string
}

const STORAGE_KEY = 'criptofarol_attribution'
const UTM_KEYS = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term'] as const

export function captureAttributionFromUrl(now = new Date()): AttributionPayload | null {
  const url = new URL(window.location.href)
  const params = url.searchParams
  const utms: AttributionPayload = {}

  for (const key of UTM_KEYS) {
    const value = params.get(key)
    if (value) utms[key] = value.slice(0, 160)
  }

  const hasUtm = Object.keys(utms).length > 0
  const existing = getStoredAttribution()

  if (!hasUtm && existing) return existing
  if (!hasUtm && !document.referrer) return null

  const payload: AttributionPayload = {
    ...existing,
    ...utms,
    referrer: document.referrer || existing?.referrer,
    landing_path: `${url.pathname}${url.search}`.slice(0, 500),
    first_seen_at: existing?.first_seen_at || now.toISOString(),
  }

  localStorage.setItem(STORAGE_KEY, JSON.stringify(payload))
  return payload
}

export function getStoredAttribution(): AttributionPayload | null {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    return raw ? (JSON.parse(raw) as AttributionPayload) : null
  } catch {
    return null
  }
}
```

**Validation:**
- Abrir DEV com UTMs.
- Verificar `localStorage.criptofarol_attribution` no navegador.
- Navegar para outra rota e confirmar que a atribuição continua.

---

### Task 3: Enviar atribuição no payload de lead

**Objective:** Quando o usuário solicitar beta/cadastro, enviar UTMs junto com `origin`.

**Files:**
- Modify: componente/formulário que chama `/api/leads`
- Import: `getStoredAttribution` de `frontend/src/lib/attribution.ts`

**Payload esperado:**

```ts
const attribution = getStoredAttribution()
await fetch(apiUrl('/leads'), {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    name,
    email,
    whatsapp,
    profile,
    pain,
    origin: attribution?.utm_source || 'landing',
    ...attribution,
  }),
})
```

**Validation:**
- Testar submissão no DEV com `utm_source=instagram`.
- Backend deve receber campos UTM no JSON.

---

### Task 4: Expandir schema Pydantic do endpoint de leads

**Objective:** Aceitar UTMs/referrer sem quebrar payload atual.

**Files:**
- Modify: `backend/app/routes/leads.py`
- Test: `backend/tests/unit/test_leads_attribution.py` ou teste unitário equivalente

**Fields to add:**

```py
utm_source: str | None = Field(default=None, max_length=120)
utm_medium: str | None = Field(default=None, max_length=120)
utm_campaign: str | None = Field(default=None, max_length=160)
utm_content: str | None = Field(default=None, max_length=200)
utm_term: str | None = Field(default=None, max_length=160)
referrer: str | None = Field(default=None, max_length=500)
landing_path: str | None = Field(default=None, max_length=500)
first_seen_at: str | None = Field(default=None, max_length=80)
```

**Validation:**
- `pytest backend/tests/unit/test_leads_attribution.py -v`
- Endpoint continua aceitando payload antigo.
- Endpoint aceita payload com UTMs.

---

### Task 5: Persistir atribuição no audit log do lead

**Objective:** Gravar atribuição em `BetaAccessAuditLog.metadata_json` para análise posterior.

**Files:**
- Modify: `backend/app/services/beta_access.py`
- Modify: `backend/app/routes/leads.py`
- Test: `backend/tests/unit/test_leads_attribution.py`

**Approach:**
- Adicionar argumento `attribution: dict | None = None` em `create_beta_access_for_lead()`.
- Atualizar `_metadata_for_lead()` para mesclar campos de atribuição sanitizados.
- Não criar coluna nova ainda; usar `metadata_json` reduz risco e acelera entrega.

**Metadata desejado:**

```json
{
  "origin": "instagram",
  "utm_source": "instagram",
  "utm_medium": "social",
  "utm_campaign": "criptofarol_semana_1",
  "utm_content": "ig_empresa_carrossel_2026_06_10_comprar_no_escuro",
  "referrer": "https://instagram.com/",
  "landing_path": "/?utm_source=instagram...",
  "first_seen_at": "2026-06-07T...Z",
  "has_whatsapp": true,
  "has_profile": true,
  "has_pain": false
}
```

**Validation:**
- Submeter lead teste no DEV.
- Consultar audit log no banco DEV.
- Confirmar UTM em `metadata_json`.

---

## Fase 2 — Eventos de navegação com PostHog

### Task 6: Configurar variáveis PostHog no frontend

**Objective:** Permitir ativar PostHog por ambiente sem hardcode.

**Files:**
- Modify: `frontend/.env.example` ou docs de env
- Modify DEV env se Alan aprovar a chave/projeto PostHog

**Vars:**

```text
VITE_POSTHOG_KEY=
VITE_POSTHOG_HOST=https://app.posthog.com
```

**Validation:**
- Build frontend sem chave não quebra.
- Com chave, eventos aparecem no PostHog DEV.

---

### Task 7: Criar wrapper de analytics no frontend

**Objective:** Centralizar eventos e evitar chamadas espalhadas.

**Files:**
- Create: `frontend/src/lib/analytics.ts`
- Modify: `frontend/src/main.tsx` ou roteador

**Events mínimos:**

```text
landing_view
cta_click
lead_form_start
lead_form_submit
lead_created
```

**Properties comuns:**

```text
utm_source
utm_medium
utm_campaign
utm_content
referrer
landing_path
path
```

**Validation:**
- Abrir landing em DEV e confirmar `landing_view`.
- Clicar CTA e confirmar `cta_click`.

---

### Task 8: Identificar lead no PostHog após cadastro

**Objective:** Conectar jornada anônima ao lead sem expor dados sensíveis desnecessários.

**Files:**
- Modify: formulário de lead
- Modify: `frontend/src/lib/analytics.ts`

**Approach:**
- Após resposta aceita do `/api/leads`, disparar `lead_created`.
- Usar email normalizado como propriedade apenas se política de privacidade permitir; alternativa: hash/email_id gerado no backend.

**Validation:**
- Funil PostHog mostra `landing_view → cta_click → lead_form_submit → lead_created`.

---

## Fase 3 — Base interna para posts e métricas sociais

### Task 9: Criar catálogo interno de posts planejados/publicados

**Objective:** Ter uma fonte local que relacione Buffer, canal, data e UTM.

**Files:**
- Create: `docs/analytics/social-post-catalog.md` inicialmente
- Later optional DB table: `social_posts`

**Campos mínimos:**

```text
date
channel
profile
format
buffer_post_id
status
utm_source
utm_campaign
utm_content
public_url
asset_path
texto_md_path
```

**Validation:**
- Cada rascunho Buffer da semana tem uma linha no catálogo.

---

### Task 10: Coleta semanal manual/semi-automática de métricas sociais

**Objective:** Começar a medir social sem depender imediatamente de APIs difíceis.

**Files:**
- Create: `docs/analytics/social-metrics-weekly.md`
- Later optional script: `scripts/collect_buffer_metrics.py`

**Métricas por post:**

```text
impressions
reach
likes
comments
shares
saves
clicks
profile_visits
followers_delta
```

**Validation:**
- Relatório semanal cru com 3 canais: LinkedIn pessoal, Instagram pessoal, Instagram empresa.

---

## Fase 4 — Dashboard executivo

### Task 11: Criar visão semanal simples

**Objective:** Responder “o que funcionou?” sem dashboard pesado no início.

**Files:**
- Create: `docs/analytics/weekly-funnel-report-template.md`

**Blocos:**

```text
Posts publicados
Visitas por UTM source
Leads por UTM content
Taxa visita → lead
Melhor post por lead
Melhor post por engajamento
Posts com engajamento alto e conversão baixa
```

**Validation:**
- Gerar primeiro relatório depois de uma semana de dados.

---

### Task 12: Avaliar Metabase depois de dados reais

**Objective:** Só montar dashboard quando a atribuição já estiver entrando.

**Trigger:**
- Pelo menos 1 semana com UTMs + PostHog + leads auditados.

**Views sugeridas:**
- Canal → visitas → leads.
- Post → visitas → leads.
- Campanha semanal → conversão.
- Social engagement vs conversão.

---

## Testes e validação técnica

### Backend

```bash
cd /srv/apps/dev/criptofarol/source/backend
pytest tests/unit/test_leads_attribution.py -v
```

Depois rodar suíte proporcional existente de rotas/leads:

```bash
cd /srv/apps/dev/criptofarol/source/backend
pytest tests/unit/test_database_and_auth.py tests/unit/test_api_coverage.py -v
```

### Frontend

```bash
cd /srv/apps/dev/criptofarol/source/frontend
npm run build
```

Se houver testes frontend configurados:

```bash
cd /srv/apps/dev/criptofarol/source/frontend
npm test -- --run
```

### DEV runtime

- Reiniciar apenas serviços DEV afetados:
  - backend alterado: `criptofarol-dev-backend.service`
  - frontend alterado: `criptofarol-dev-frontend.service`
- Validar `https://dev.criptofarol.com.br`.
- Testar URL com UTM.
- Submeter lead teste controlado.
- Consultar audit log DEV.
- Confirmar eventos no PostHog se chave estiver configurada.

---

## Riscos e decisões pendentes

1. **PostHog Cloud vs self-hosted:** recomendo Cloud no início para velocidade, salvo restrição de privacidade/custo.
2. **Email no analytics:** evitar mandar email cru para PostHog até definir política; preferir lead_id/hash.
3. **LinkedIn pessoal:** métricas podem exigir coleta manual; não prometer automação completa agora.
4. **Instagram Stories:** Buffer pode continuar como notification; medir link/click depende do formato disponível.
5. **Banco:** começar com `BetaAccessAuditLog.metadata_json`; criar tabela dedicada só quando o volume justificar.

---

## Ordem recomendada de execução

1. UTM contract.
2. Captura frontend de atribuição.
3. Payload de lead com atribuição.
4. Backend aceitando e gravando attribution metadata.
5. Teste ponta-a-ponta em DEV.
6. PostHog events.
7. Atualizar links dos rascunhos Buffer com UTMs.
8. Primeiro relatório semanal manual.
9. Dashboard Metabase só depois de dados reais.

## Definição de pronto em DEV

- Link com UTM abre DEV/PROD e grava atribuição no navegador.
- Lead criado pelo formulário gera audit log com UTM/referrer/landing_path.
- Eventos principais aparecem no PostHog, se configurado.
- Buffer drafts da campanha usam links UTM padronizados.
- Nenhuma publicação direta foi feita sem aprovação do Alan.
