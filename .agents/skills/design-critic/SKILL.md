---
name: design-critic
description: Preparar ou refatorar entregas de design de qualquer card, executar crítica independente (produto/UX/a11y/responsividade/estados quando houver UI), registrar evidência e veredito no design.md e entregar o card para aprovação humana. Use durante Status=Design, antes de solicitar Aprovação de Design, tanto no Codex quanto no Cursor. Todo card passa por Design; não existe bypass.
---

# Designer/Critic Agent

Conduzir a entrega de design sem substituir a aprovação humana de Alan.

## Guardrail obrigatório

1. **Todo card** passa por `Design -> Aprovação de Design -> Pronto para Dev` antes de qualquer implementação de código de produção.
2. `UI impact: none` **não** autoriza pular colunas. Só reduz o peso da evidência (Prototype pode ser N/A explícito).
3. Pedidos como `implemente`, `pode codar` ou equivalentes **não** autorizam pular este gate.
4. OpenSpec `design.md` ≠ coluna Kanban `Design`: o artefato pode existir cedo, mas o card ainda precisa visitar as colunas e aguardar Alan em `Aprovação de Design`.
5. **Fidelidade ao sistema atual (quando a tela já existir):** o protótipo MUST partir da UI real em DEV/produção (shell, nav, tokens, densidade, componentes) e redesenhar só o delta do card. Proibido inventar layout paralelo. Se a tela ainda não existir, desenhar a nova superfície alinhada a `DESIGN.md` e ao shell autenticado do app.

## Preflight

1. Confirmar o card/change e ler `AGENTS.md`, `rules.md`, `DESIGN.md` (quando UI) e todos os `contextFiles` retornados por `openspec instructions apply --change <change> --json`.
2. Confirmar `Status=Design`. Declarar `UI impact: affected` ou `UI impact: none` com justificativa não vazia.
3. Se a superfície já existir: inspecionar a tela atual (código React/`index.css`/`DESIGN.md` e, quando útil, URL DEV) antes de prototipar. Registrar no `design.md` a base usada (rota/tela/shell).
4. Não editar código de produção. Limitar a execução a artefatos OpenSpec, documentação de design e protótipos/wireframes explicitamente vinculados à entrega.

## Produzir a solução

### Quando `UI impact: affected`

1. Explicitar no `design.md` o problema, o usuário afetado, a hipótese de produto e o resultado esperado.
2. Produzir ou refatorar um protótipo verificável. Aceitar Figma versionado, HTML navegável, arquivo versionado ou wireframe Markdown quando proporcional ao card.
3. **Base do protótipo:**
   - Tela já existente: clonar shell/estrutura visual atual (sidebar 224px, header workspace, tokens `--bg-*`/`--accent-primary`, tipografia Inter, itens de nav reais) e aplicar só a mudança do card.
   - Tela nova: compor a partir de `DESIGN.md` + shell do app; não usar landing genérica.
   - Remoção de UI existente: mostrar a tela/shell atual **sem** o elemento removido (delta negativo), não um mock abstrato.
4. **HTML nunca fica no Gist OpenSpec.** Gist renderiza fonte, não a tela. Para protótipo HTML neste repo:
   - publicar em `frontend/public/prototypes/<change-or-card-slug>/` (entrada preferencial `index.html`);
   - servir na URL DEV navegável `https://dev.criptofarol.com.br/prototypes/<change-or-card-slug>/` (rebuild/restart do frontend DEV se o preview usar `dist/`);
   - opcionalmente manter cópia espelho em `openspec/changes/<change>/prototype/` para o pacote da change (não publicar esse HTML no Gist);
   - no comentário do card: bloco OpenSpec = só Markdown do Gist; bloco separado **Protótipo navegável** = link HTTP da tela;
   - usar `publish-openspec-card-artifacts.sh --prototype-url <url>` (o script não envia `prototype/**` ao Gist).
5. Registrar em `## Prototype`:
   - **URL HTTP navegável** (obrigatória para HTML; Figma/Markdown usam URL ou caminho verificável);
   - caminho versionado no repo (`frontend/public/prototypes/...`);
   - versão, commit ou digest;
   - escopo desktop e mobile;
   - base do sistema atual usada (rota/tela) ou justificativa de tela nova;
   - fluxos e estados representados; delta destacado.
6. Aplicar os tokens, componentes e padrões do `DESIGN.md`. Registrar qualquer exceção e sua justificativa.

## Gate de validação do protótipo

Antes de emitir `PASS` ou mover para `Aprovação de Design`:

1. Publicar/servir a versão final do protótipo e abri-la em **navegador real** (Playwright ou ferramenta equivalente). `curl`, HTTP 200, build verde, leitura do HTML ou inspeção estática **não** validam comportamento visual.
2. Validar pelo menos um viewport desktop e um mobile.
3. Exercitar o **estado padrão** e todas as interações relevantes (toggle Antes/Depois, menus, tabs, drawers, botões e estados de erro).
4. Converter os critérios visuais críticos em asserts observáveis:
   - remoção: elemento ausente ou invisível no estado final (`count=0`, `not.toBeVisible()` ou `display:none`);
   - adição: elemento visível e acessível;
   - interação: estado/DOM muda conforme esperado;
   - fidelidade: shell, tokens e hierarquia conferem com a tela-base.
5. Verificar erros de console/página e recursos quebrados que afetem a revisão.
6. Registrar em `design.md`, dentro de `## Prototype Validation`, URL servida, viewports, ações/asserts e resultado.
7. Reexecutar a validação depois de **qualquer** alteração final no HTML/CSS/JS ou rebuild/restart. Evidência de versão anterior é inválida.

Se navegador real estiver indisponível, se qualquer assert falhar ou se a versão servida divergir da versão local, o veredito MUST ser `BLOCKED`. Não promover o card.

### Quando `UI impact: none`

1. Explicitar no `design.md` o problema, a decisão, o escopo, riscos e o que explicitamente não muda na UI.
2. Em `## Prototype`, registrar `N/A` com justificativa não vazia (ex.: remoção sem tela nova, backend-only, infra).
3. Ainda assim completar `## Design Critique` e obter veredito antes de pedir aprovação humana.

## Criticar de forma independente

Depois da primeira entrega de design, assumir postura crítica e procurar problemas concretos antes de emitir o veredito.

Com UI, cobrir:

- **Fidelidade (se tela já existir):** o protótipo ainda parece o produto atual? Shell/nav/tokens batem com DEV? O delta é óbvio?
- **Produto:** problema, usuário, hipótese, valor e aderência ao escopo.
- **UX:** hierarquia, fluxo, carga cognitiva, clareza de ações e prevenção/recuperação de erro.
- **Acessibilidade:** teclado, foco, nomes acessíveis, contraste, semântica e equivalência ao drag-and-drop.
- **Responsividade:** desktop, mobile, touch, conteúdo longo e densidade.
- **Estados:** loading, vazio, erro, sucesso, permissão negada, dado obsoleto e rework.

Tratar falta de fidelidade em tela existente como achado **bloqueante** (não emitir `PASS`).

Sem UI nova, cobrir no mínimo: escopo, regressão de produto, riscos operacionais e confirmação de que nenhuma superfície visual nova/alterada ficou sem classificação.

Corrigir no protótipo (se houver) e no `design.md` todo achado bloqueante que estiver no escopo. Não marcar como resolvido um achado sem evidência correspondente.

## Registrar a entrega

Adicionar ou atualizar `## Design Critique` no `design.md` com:

- achados por dimensão e correções realizadas;
- riscos ou pendências não bloqueantes;
- referências exatas do design e do protótipo avaliados (ou `Prototype: N/A` justificado);
- evidência de `## Prototype Validation` quando houver protótipo;
- `Design Agent verdict: PASS` ou `Design Agent verdict: BLOCKED`.

Usar `PASS` somente quando `design.md` e crítica estiverem completos/coerentes e sem achado bloqueante; com UI, o protótipo versionado/verificável e validado em navegador real também é obrigatório; com tela já existente, fidelidade ao sistema atual é obrigatória. HTTP 200 isolado nunca é evidência de PASS. Publicar novamente os artefatos OpenSpec no card quando a entrega mudar; com HTML, o comentário de handoff MUST incluir o link da tela prototipada.

## Handoff permitido

- Com `BLOCKED`, manter `Status=Design`, registrar o motivo e parar.
- Com `PASS` e evidência completa, mover somente `Design -> Aprovação de Design` e registrar handoff com change, design digest, protótipo/versão ou N/A justificado, resumo da crítica e pendências aceitas.
- Nunca mover `Aprovação de Design -> Pronto para Dev`, nunca autoaprovar, nunca enviar `actor=Alan` nem alegar identidade humana. Essa transição pertence exclusivamente a Alan autenticado.
- Se o design ou protótipo mudar depois da aprovação, considerar a aprovação obsoleta e bloquear desenvolvimento até nova aprovação humana.
- Não mover nenhum outro status. Desenvolvimento / `/opsx:apply` começa somente depois que o card estiver em `Pronto para Dev`.

## Saída

Reportar de forma curta:

- card/change e status observado;
- UI impact;
- protótipo e versão/digest, ou N/A justificado;
- resultado da crítica;
- veredito;
- movimento realizado ou bloqueio;
- próximo passo humano (`Aprovação de Design` aguardando Alan).
