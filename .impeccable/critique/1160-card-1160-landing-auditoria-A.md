# Assessment A — card 1160 · change card-1160-landing-auditoria · onda 1160-d1

> Avaliador A isolado (produto / escopo / UX / a11y / fidelidade ao card e à página viva). Onda dupla com-tela; o B cobre detector, gate e navegador. Única escrita: este arquivo. Sem edição de design.md, protótipo, specs, tasks ou código; sem commit, `process_event`, Gist ou filho.

## Metadata

- card: #1160 (oalansilva/crypto), Status informado pelo pai: Design, com-tela. Briefing lido por REST (`gh api repos/oalansilva/crypto/issues/1160`).
- change: `openspec/changes/card-1160-landing-auditoria/` (proposal, design, 6 specs, tasks).
- protótipo: `frontend/public/prototypes/card-1160-landing-auditoria/` (index, privacidade, termos, styles.css = v4, delta.css, assets/).
- data: 2026-10-29.
- modelo: Opus 5.5 (`claude-opus-5-5`), effort high, role assessment-a (capture `capture-assessment-a-1160-d1.json`, attempt `02aaa54f-…`).
- Conferências feitas por este avaliador:
  - URL pública do protótipo `https://dev.criptofarol.com.br/prototypes/card-1160-landing-auditoria/` → 200, sha256 `7fd112f7d53a…` = `index.html` do worktree; `privacidade.html` → 200. (design.md ainda diz "responde 404 por enquanto": evidência velha.)
  - `https://criptofarol.com.br/` → sha256 `da9459593d1c…` = `cripto-farol-landing-v4/index.html` do repo (a fonte do clone é a página viva).
  - Leitura do HTML do protótipo sem marcadores e diff de copy contra a v4 (nav, hero, produto, benefícios, confiança, FAQ, cadastro, script).
  - Imagens: hero-1600.webp, tabela e gráfico (inteiros e recortes) convertidos e vistos.
  - Código atual: `backend/app/routes/leads.py` (`LeadAccessRequest.name` obrigatório; extra ignorado), `frontend/src/lib/analytics.ts` (PostHog do app sem `disable_session_recording`), nenhuma página de privacidade/termos no app (`frontend/src`), `docs/brand-system.md` (texto corrido = IBM Plex Sans).

## Rubrica

### Tokens do gate (L1–L3 do design.md)

`UI impact: affected` / `live_route: landing` / `surface: existing`, cada um em linha própria nas 3 primeiras linhas. OK. A seção "Regiões clonadas" lista só as regiões com delta. OK.

### Cobertura do Entra (1–12)

| # | Item | Protótipo | Contrato (design/specs/tasks) | Nota |
|---|---|---|---|---|
| 1 | Lead no passo 1, passo 2 opcional, tudo guardado, aviso ao Alan, sucesso honesto | passo 1 salva, passo 2 "(opcional)" + "Pular esta etapa", erro passo 1 e passo 2, final "Recebemos seu cadastro." | D1–D4, spec landing-lead-capture, tasks 1.1–1.6 | OK; furo só no corte (P1-1) |
| 2 | Funil medido | `data-cta` hero/nav/footer, `lead_step1_completed`, `lead_step2_skipped` | D5, spec product-analytics, 2.2 | OK; páginas legais têm `data-cta="nav"` sem script (P3) |
| 3 | Rodapé + páginas reais + consentimento | rodapé nas 3 páginas, sem nome/CNPJ/contato/redes; linha de consentimento | D6, spec landing-legal-pages, 2.4 | OK; textos com incoerências (P2-1..P2-4) |
| 4 | Aviso de risco no hero | `.hero-risk` após a linha de confiança | D6, spec | OK |
| 5 | Copy enxuta | `<dl>` de métricas visível, benefício 04 e confiança 3 sem nomes internos, POL, tabela uma vez | D7, spec conversion-copy | OK |
| 6 | Prints limpos e legíveis | gráfico/tabela limpos, BR, recortes ≤560px | D8 | OK; eixo do gráfico mostra "2" no lugar de "mar." (P3); alt da tabela no celular cita a coluna de risco que o recorte não tem (P2-6) |
| 7 | SEO técnico | título, descrição com acento, canonical, OG/Twitter, JSON-LD Organization + FAQPage | D9, spec seo, 2.5 | OK |
| 8 | www → apex | — (infra) | D11, 6.3 | OK |
| 9 | Performance | WebP srcset 9,6/20/36 KB, 2 famílias | D10, 2.3, 5.3, 6.6 | OK; troca IBM Plex Sans → Inter no texto corrido é decisão visível (juízo do Alan) |
| 10 | Cabeçalhos | — (infra) | D11, 6.3 | OK |
| 11 | Sem contador | frase de levas, sem número nem "--" | D4, spec | OK |
| 12 | Landing no repo `cripto-farol-landing` | — | D12, spec landing-publication, tasks 2/3/4/6 | **ordem do corte com furo (P1-1)** |

### Não entra

Nada entrou: sem redesenho (o delta visual é rodapé, CTA na nav, aviso, `<dl>`, frase de levas — todos pedidos pelo Entra), sem prova social, sem listagem de leads no app, sem mudança de código do app (cabeçalhos valem para o domínio, sem código), sem nome/CNPJ/contato/redes. Ponto de atenção: troca da fonte do texto corrido (Plex → Inter) toca o `docs/brand-system.md`; está dentro do Entra 9 ("no máximo 2 famílias"), mas a escolha de qual família sai é do Alan.

### Estados do formulário

Passo 1 salvo (status "Pronto, seu cadastro está salvo." + título do passo 2), passo 2 opcional (três campos "(opcional)", nível começa em "Prefiro não dizer"), pular, erro passo 1 (fica no passo 1), erro passo 2 (cadastro já salvo, tentar de novo ou pular), sucesso honesto (sem e-mail, sem vaga garantida). WhatsApp de fato opcional no protótipo e no contrato (D1 + Node sai em D2). Lacunas: foco após o passo 1 vai para o campo WhatsApp (teclado abre no celular e esconde "Pular") — P2-7; mensagem de status repetida ("salvo" duas vezes) — P3.

### Acessibilidade

Rótulos envolvem os campos; `role=status` existente; foco programático no estado final; `.form-skip` e links do rodapé com 44px; contraste dos tokens da v4 alto (muted ~13:1, subtle ~7:1 sobre `--night`). Lacuna nova: `.nav a.nav-cta` herda `min-height: 36px` da v4 — alvo < 44px no celular (P2-5). Os outros links da nav (36px) são da v4, fora do delta (P3). Erro com `role=status` (polite) em vez de `alert` — P3.

### Fidelidade

Clone byte a byte confirmado: página viva = v4 do repo; protótipo publicado = worktree; `styles.css` inteiro; delta só em DELTA. Página inteira como o visitante vê, sem painel antes/depois. OK.

### Páginas legais × o que é coletado

- PostHog: `persistence: "localStorage"` e `autocapture: false` batem com a Política. Mas o projeto é o mesmo do app e o init não desliga gravação de sessão; se o projeto ligar replay/surveys, a Política fica falsa sem ninguém mexer na landing (P2-2).
- Google Fonts: a página pede fontes a `fonts.googleapis.com` (IP vai ao Google); a Política não cita. Fonte local em `/lp/` resolve e ajuda o Entra 9 (P2-2).
- Telegram: dados do formulário vão ao Telegram (empresa fora do Brasil); a Política só fala em transferência internacional para o PostHog (P2-2).
- "O aplicativo, depois do login, tem regras próprias": não existe política do app (`frontend/src` sem privacidade/termos). Frase falsa (P2-3).
- Termos: "Ao usar o Cripto Farol ou entrar na lista do beta, você concorda com estes termos", mas a linha do formulário só fala da Política (P2-4).
- Regras novas inventadas no texto: "maiores de 18 anos" (só na Política, não nos Termos nem no formulário) e "se não assinar, o acesso termina" (Termos) — juízo do Alan.

### Migração de repo (Entra 12)

Ordem do Migration Plan / tasks 6: 6.2 deploy da landing → 6.3 Caddy (sai `@prodLeadSubmit`) → 6.4 Node off → 6.5 deploy do `crypto` (backend novo + migração + remoção da v4 do `dist`).

- Entre 6.3 e 6.5 a landing nova fala com o backend **antigo**: passo 1 (`step`, `name`, `email`) dá 202, mas só o e-mail + marcas vão para a auditoria — nome perdido, nenhum aviso ao Alan; passo 2 manda `step`, `lead_ref`, `email`, WhatsApp, nível, dificuldade **sem `name`** → 422 no `LeadAccessRequest` → o visitante vê "Seu cadastro já está salvo, mas estas respostas não foram" e as respostas se perdem. A conferência de 6.3 ("um POST /api/leads com o e-mail do Alan") roda contra o backend velho e não prova nada do contrato novo.
- Se o 6.5 falhar e for revertido, a landing nova fica indefinidamente contra o backend velho (passo 2 sempre falha), e voltar à v4 exige reverter o `crypto` também.
- O "commit anterior" do repo da landing para rollback (`deploy.sh prod <commit anterior>`) é a landing **antiga de maio/2026**, não a v4: no primeiro deploy não há alvo de reversão válido dentro do repo da landing.
- A circularidade (o Caddy precisa do backend novo antes; o `crypto` remove a v4 do `dist` e precisa do Caddy trocado antes) nasce de pôr a remoção da v4 no mesmo deploy do backend.
- Links antigos: assets antigos com 301 para `/lp/` e `/prototypes/cripto-farol-landing-v4/` → `/` mantidos. `/prototypes/cripto-farol-landing/` (página da 1ª variante) e v3/skill-v2 viram shell da SPA (200) depois da remoção — P3.

## Achados

### P0

Nenhum.

### P1

- **P1-1 — Corte em PROD com janela de leads perdidos e sem rollback dentro do repo da landing.** Onde: design.md D12 + Migration Plan 3–4 + Risks "[O corte troca quem serve /]"; tasks 6.2–6.5; spec landing-publication. Correção proposta: (a) primeiro commit do `cripto-farol-landing` = v4 viva sem delta, já com caminhos `/lp/` (alvo de rollback independente do `crypto`); (b) ordem: deploy da landing "v4 como está" + troca do Caddy para servir `/` e assets do checkout novo **mantendo** `@prodLeadSubmit` → Node (mudança invisível) → deploy do `crypto` (backend novo + migração; agora remover a v4 do `dist` não quebra nada) → Caddy sem `@prodLeadSubmit`, www → apex, cabeçalhos, Node desligado → `deploy.sh prod <commit com o delta>`; (c) a conferência por POST (lead salvo no passo 1, enriquecido no passo 2, aviso no Telegram) roda **depois** do backend novo; (d) rollback documentado por fase (landing = `deploy.sh prod <commit v4>`). Se o commit "v4 como está" ainda chamar `/api/leads/stats`, ou esse commit já tira o contador ou o endpoint sai só depois do corte (senão aparece "--" por alguns minutos). Alternativa equivalente: deixar a remoção da v4/`ops/landing-leads/` do `crypto` para um commit/release posterior ao corte.

### P2

- **P2-1 — Canal do titular e identificação do controlador.** Onde: privacidade.html item 7 (placeholder "⟨canal do titular…⟩"), Open Question 1. Correção: a pergunta vai ao Alan no T7 junto com "quem é o controlador" (dentro da Política, não no rodapé); a aprovação do T7 precisa trazer a resposta, senão a task 2.4 fica sem texto final.
- **P2-2 — Política incompleta sobre terceiros.** Onde: privacidade.html itens 2 e 4; D5/D10. Correção: (a) fontes servidas de `/lp/` em vez do Google Fonts (tira um terceiro, ajuda Lighthouse e uma futura CSP) ou citar o Google na Política; (b) citar o Telegram como serviço de fora do Brasil no item 4; (c) init do PostHog da landing com `disable_session_recording: true` (e surveys off) para a Política não depender de chave do projeto do app.
- **P2-3 — Frase falsa sobre o app.** Onde: privacidade.html abertura ("O aplicativo, depois do login, tem regras próprias"). Correção: "Esta política cobre só a página pública e o formulário do beta." e registrar follow-up de política do app (fora deste card).
- **P2-4 — Aceite dos Termos que o formulário não colhe.** Onde: termos.html abertura × linha "Ao enviar, você concorda com a Política de Privacidade." Correção: Termos passam a valer "ao usar o Cripto Farol" (não "ao entrar na lista"), ou o Alan decide estender a linha do formulário aos Termos (o texto da linha veio do issue).
- **P2-5 — Alvo do CTA novo da navegação < 44px no celular.** Onde: delta.css `.nav a.nav-cta` (herda `min-height: 36px` da v4). Correção: `min-height: 44px` no `.nav-cta` até 920px.
- **P2-6 — Alt da tabela não bate com o recorte do celular.** Onde: index.html hero `<picture>` (alt cita "risco até o stop"; o recorte ≤560px não tem a coluna). Correção: alt sem a coluna de risco, ou recorte que mantenha o risco (o card de confiança promete "sinal, contexto e risco").
- **P2-7 — Foco no WhatsApp depois do passo 1.** Onde: script do protótipo (`form.elements.whatsapp.focus()`). Correção: foco no título do passo 2 (`tabindex=-1`), para o leitor de tela ler "Cadastro salvo… É opcional" e o teclado do celular não cobrir "Pular esta etapa".
- **P2-8 — Rótulo do CTA da navegação.** Onde: nav "Entrar no beta" × form "Entrar na lista do beta" × Termos "entrar na lista não garante vaga". Correção: "Entrar na lista" na nav (mesma honestidade do botão do passo 1).
- **P2-9 — Link da Política no formulário tira a pessoa da página.** Onde: `.form-consent a` (mesma aba). Correção: abrir em nova aba (`target="_blank" rel="noopener"`) só nesse link, para não perder nome e e-mail digitados.

### P3 (detalhe de Apply)

- Prototype Validation diz que a URL pública dá 404; hoje dá 200 com o mesmo sha — atualizar a evidência.
- Eixo do gráfico com "2" entre "fev." e "abr." (deveria ser "mar."); recorte do gráfico corta "Venda"/"Compra" na borda esquerda.
- `data-cta="nav"` nas páginas legais sem script de evento: o clique de lá não entra no funil.
- Mensagem de erro em `role=status` (polite); `role=alert` ou `aria-describedby` no erro.
- Status "Pronto, seu cadastro está salvo." repete o título do passo 2 e fica abaixo dos botões.
- Passo 2 enviado vazio pode ser tratado como "pular" (sem request).
- Linha de consentimento acima do botão (ler antes de enviar).
- Links da nav da v4 com 36px (fora do delta).
- `/prototypes/cripto-farol-landing/` e v3/skill-v2 viram shell da SPA depois da remoção: 301 para `/` ou 410.
- `$pageview` com `capture_pageview: false` precisa de captura manual para cumprir o spec product-analytics.
- `route-landmarks.yaml` `landing.source` velho e futuros cards de landing clonando do repo novo: card de motor no covenant-flow (já em 4.5).

## Open Questions do autor

1. Controlador / canal do titular — não bloqueia a submissão ao T7; vai como pergunta ao Alan no T7 e a resposta é condição para o Apply fechar a 2.4. Acrescentar a identificação do controlador dentro da Política.
2. Leads antigos da planilha/Drive — não bloqueia; pergunta no T7. Acrescentar: destino/apagamento da planilha local e da cópia no Drive da Clara (dado pessoal sem Política), e confirmar que ninguém (Clara, tópico do grupo) dependia da planilha/Drive/tópico que somem com o Node.
3. Prazo de guarda — não bloqueia; pergunta no T7.

## Juízos do Alan

- Canal do titular e identificação do controlador dentro da Política (OQ1).
- Leads antigos: importar ou só arquivar; o que fazer com a planilha e a cópia no Drive da Clara; aviso que hoje sai no tópico do grupo / e-mail passa a ser só DM do bot (OQ2).
- Prazo de guarda (OQ3).
- Qual família sai: Plex (texto corrido vira Inter, proposta do autor) ou Inter (títulos viram Plex).
- Regras novas nos textos: "maiores de 18 anos" (se fica, entra também nos Termos) e "se não assinar, o acesso termina".
- Linha do formulário só com a Política (texto do issue) ou também com os Termos.
- Base legal do formulário: consentimento "ao enviar" (rascunho) ou procedimento preliminar a pedido do titular (art. 7º, V) — tema da revisão jurídica, que está fora; só registrar.

## Disposition

Delta visível: a v4 com rodapé (Política, Termos, aviso, CTA), aviso de risco no hero, CTA na navegação, métricas explicadas, copy de carteira/confiança/FAQ sem nomes internos, POL, tabela só no hero, prints limpos e recortes no celular, frase de levas no lugar do contador, passo 1 que salva com consentimento, passo 2 opcional com pular, erros e sucesso honestos, mais as páginas `/privacidade` e `/termos`. Clone fiel; cobertura dos itens 1–11 completa. O furo é o plano de corte do item 12 (ordem Caddy × backend × remoção da v4 e falta de alvo de rollback), mais ajustes de texto nas páginas legais e pequenos ajustes de a11y.

## Verdict

**PASS com rework** — um rework resolve o P1-1 (reordenar o corte e criar o commit-base v4 no repo da landing) e os P2 de texto/a11y; as Open Questions e os juízos vão ao Alan no T7.
