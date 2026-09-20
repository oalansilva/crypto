⚠️ DEGRADED: single-context (Assessment A/B not spawned — parent MUST NOT spawn design-critic / Assessment A/B; spawn-count 0)

# Impeccable Operate — card-995-monitor-retry-rede

Change: `card-995-monitor-retry-rede` · issue #995  
Mode: **Operate** · `DESIGN.md` not overwritten  
UI impact: affected  
live_route: /monitor  
surface: existing  

Method: single-context author critique + CLI detector + Playwright browser gate. Dual-agent Assessment A/B is the parent's T5 job, not this author child.

Canonical proto: `https://dev.criptofarol.com.br/prototypes/card-995-monitor-retry-rede/`  
Path: `frontend/public/prototypes/card-995-monitor-retry-rede/index.html`  
Siblings (same surface, not extra catalog routes): `carga.html`, `erro.html`, `sessao.html`

## Shape (Qs already A — not re-interviewed)

- Job: operator on a corporate proxy opens Monitor with a valid session and favorites on the server.
- Outcome: a transient cut is absorbed; signals appear; loading waits tens of seconds with «Carregando sinais...» and KPIs that are not a true 0; persistent failure keeps #975; dead session goes to login.
- Direction: clone live `/monitor`, apply only the state delta. No redesign.
- Boundaries: no Caddy/backend/Zscaler/TTL; no Favoritos/Início/Carteira extras (Q4=A).

## Design Health Score

Operate scoring. n/a only where the heuristic does not apply to this authenticated task surface.

| # | Heuristic | Score | Key Issue |
|---|-----------|-------|-----------|
| 1 | Visibility of System Status | 4 | Loading, list, persistent error, and login are distinct XOR states. |
| 2 | Match System / Real World | 4 | Copy stays #975 / login vivo; no invented error wording. |
| 3 | User Control and Freedom | 4 | «Tentar de novo» rereads; «Atualizar» still recomputes. |
| 4 | Consistency and Standards | 4 | Clone of AppNav + MonitorStatusTab; DESIGN.md tokens. |
| 5 | Error Prevention | 4 | First `Failed to fetch` is not the last word; wait tens of seconds. |
| 6 | Recognition rather than Recall | 4 | Same board landmarks; pending KPIs use incumbent hyphen, not a new glyph system. |
| 7 | Flexibility and Efficiency | n/a | No power-user path in this delta. |
| 8 | Aesthetic and Minimalist Design | 3 | Incumbent clip of Operar at 1280 and truncated search at 390 — clone, not this card. |
| 9 | Help Users Recognize, Diagnose, Recover | 4 | Persistent #975 + retry; dead session → login instead of a lying error card. |
| 10 | Help and Documentation | n/a | Task surface; no new help copy. |

**Design specificity:** grounded. This is the Cripto Farol Monitor, not a generic empty-state kit. The delta is state/time/recovery, not a new visual world.

## Cognitive load

- Decision points on the happy board remain the incumbent filters + row actions (unchanged).
- Loading has one message («Carregando sinais...»).
- Error has one recovery («Tentar de novo»).
- Login is the existing auth card.
- No >4 new options introduced.

## Emotional journey

- Valley of the incident (false «lista não chegou» + KPIs at 0 + prefs toast) is the thing this card removes.
- Peak: list appears after the wait, same opening, no network change.
- End: either signals, a honest #975 after tens of seconds, or login if the session died.

## Strengths

1. Canonical URL is the live `/monitor` clone with signals — not an ANTES/DEPOIS panel.
2. Four required states exist as siblings of the same surface (carga / lista / erro / sessão).
3. KPIs during wait/error do not paint `0` as a completed count; prefs toast is absent when load succeeds.

## Priority issues (author)

**P0:** none  
**P1:** none  

**P3 (Apply, accepted):**

- Clip of «Ver Trades» / «Operar» at 1280×800 — incumbent board, do not redesign.
- Search placeholder truncates at 390 («Buscar par, est»).
- Empty `thead` under the #975 card (`erro.html`) — XOR of live error vs table; kept for cloned landmarks.
- Mobilebar still shows «SOL/USDT 1d» on carga/erro (clone chrome).
- Detector `flat-type-hierarchy` on `sessao.html` (12/14/20px login clone).
- Exact retry count / backoff ms; `authFetch` vs Monitor queue; toast suppress vs dismiss.

## Audit (technical)

| Dimension | Score | Notes |
|---|---|---|
| Accessibility | 3 | `role=status` on loading; `role=alert` on #975; retry 44px; pending KPIs `aria-busy`. Login labels present. |
| Performance | 4 | Static HTML proto; no motion beyond incumbent. |
| Theming | 4 | DESIGN.md tokens; dark canvas; yellow CTA. |
| Responsive | 3 | Desktop + mobile structural collapse is the live Monitor; clip/truncate are clone P3. |
| Implementation integrity | 3 | CLI detector: 1 warning (`flat-type-hierarchy` on login clone). Em-dash advisory fixed to hyphen. |

Detector JSON: `.impeccable/critique/995-detect.json`

## Browser gate

Command: `python3 .impeccable/critique/995-autor-gate.py`  
Chromium `/usr/bin/chromium-browser --no-sandbox`, viewports 1280×800 and 390×844, `colorScheme: dark`.  
Evidence: `.impeccable/critique/995-autor-gate.json`  
Shots: `995-{index,carga,erro,sessao}-{desktop,mobile}-*.png`

| State | Desktop | Mobile | Contract |
|---|---|---|---|
| lista (`index.html`) | PASS | PASS | SOL/USDT + ETH/USDT; landmarks; no #975; no toast; no empty catalog |
| carga (`carga.html`) | PASS | PASS | «Carregando sinais...»; KPI 0-as-truth absent; no #975 |
| erro (`erro.html`) | PASS | PASS | #975 copy + Tentar de novo; stays on proto; no empty catalog |
| sessão (`sessao.html`) | PASS | PASS | Bem-vindo de volta + Entrar; no #975 card |

FAIL 0 / 8. Console errors 0.

## Polish applied

- Replaced pending KPI em-dashes with incumbent hyphen `-` (detector `em-dash-overuse` advisory).
- `a.monitor-retry` keeps 44px yellow target and `text-decoration:none`.
- No DESIGN.md rewrite. No product `frontend/src/**` or `backend/**` writes.

## Bytes (UTF-8)

| File | sha256 | bytes | copied | generated | COPIED pairs |
|---|---|---|---|---|---|
| index.html | `5c80aa4a01efa5fab1ca1a56cdc3461e0213b22d3bfd1056fa7762407c617b9a` | 31568 | 22008 | 9560 | 7/7 |
| carga.html | `00f523eb23752b39ab27e439ccfad82b00da98097a671c5878696060209e5fd4` | 23657 | 20719 | 2938 | 4/4 |
| erro.html | `86d863acbb9318dfe9d5439a6e91d5fc5d1d6fde9a57065e1c464b69d40f6223` | 24773 | 21328 | 3445 | 5/5 |
| sessao.html | `7879cd2630a22d2929db07cdfc7c0da5e1ba4f37e22261782a3ac7547d09c584` | 4933 | 4169 | 764 | 3/3 |

T5 measures canonical `index.html` only.

## Verdict

**Design Agent verdict: PASS** (author + browser gate).  
Assessment A/B not run here. Parent submits Design (T5) after critics.

`proxy modelo: design-autor → Grok 4.6 (cursor-grok-4.6-high)`  
spawn-count: 0
