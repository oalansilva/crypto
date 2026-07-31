---
name: design-critic
description: Preparar ou refatorar protótipos de cards com impacto de UI, executar crítica independente de produto, UX, acessibilidade, responsividade e estados do sistema, registrar evidência e veredito no design.md e entregar o card para aprovação humana. Use durante Status=Design, antes de solicitar Aprovação de Design, tanto no Codex quanto no Cursor.
---

# Designer/Critic Agent

Conduzir a entrega de design sem substituir a aprovação humana de Alan.

## Preflight

1. Confirmar o card/change e ler `AGENTS.md`, `rules.md`, `DESIGN.md` e todos os `contextFiles` retornados por `openspec instructions apply --change <change> --json`.
2. Confirmar `UI impact: affected` e `Status=Design`. Se o impacto for `none`, usar o bypass documentado do workflow em vez desta skill.
3. Não editar código de produção. Limitar a execução a artefatos OpenSpec, documentação de design e protótipos/wireframes explicitamente vinculados à entrega.

## Produzir a solução

1. Explicitar no `design.md` o problema, o usuário afetado, a hipótese de produto e o resultado esperado.
2. Produzir ou refatorar um protótipo verificável. Aceitar Figma versionado, HTML navegável, arquivo versionado ou wireframe Markdown quando proporcional ao card.
3. **HTML nunca fica no Gist OpenSpec.** Gist renderiza fonte, não a tela. Para protótipo HTML neste repo:
   - publicar em `frontend/public/prototypes/<change-or-card-slug>/` (entrada preferencial `index.html`);
   - servir na URL DEV navegável `https://dev.criptofarol.com.br/prototypes/<change-or-card-slug>/` (rebuild/restart do frontend DEV se o preview usar `dist/`);
   - opcionalmente manter cópia espelho em `openspec/changes/<change>/prototype/` para o pacote da change (não publicar esse HTML no Gist);
   - no comentário do card: bloco OpenSpec = só Markdown do Gist; bloco separado **Protótipo navegável** = link HTTP da tela;
   - usar `publish-openspec-card-artifacts.sh --prototype-url <url>` (o script não envia `prototype/**` ao Gist).
4. Registrar em `## Prototype`:
   - **URL HTTP navegável** (obrigatória para HTML; Figma/Markdown usam URL ou caminho verificável);
   - caminho versionado no repo (`frontend/public/prototypes/...`);
   - versão, commit ou digest;
   - escopo desktop e mobile;
   - fluxos e estados representados.
5. Aplicar os tokens, componentes e padrões do `DESIGN.md`. Registrar qualquer exceção e sua justificativa.

## Criticar de forma independente

Depois do primeiro protótipo, assumir postura crítica e procurar problemas concretos antes de emitir o veredito. Cobrir:

- **Produto:** problema, usuário, hipótese, valor e aderência ao escopo.
- **UX:** hierarquia, fluxo, carga cognitiva, clareza de ações e prevenção/recuperação de erro.
- **Acessibilidade:** teclado, foco, nomes acessíveis, contraste, semântica e equivalência ao drag-and-drop.
- **Responsividade:** desktop, mobile, touch, conteúdo longo e densidade.
- **Estados:** loading, vazio, erro, sucesso, permissão negada, dado obsoleto e rework.

Corrigir no protótipo e no `design.md` todo achado bloqueante que estiver no escopo. Não marcar como resolvido um achado sem evidência correspondente.

## Registrar a entrega

Adicionar ou atualizar `## Design Critique` no `design.md` com:

- achados por dimensão e correções realizadas;
- riscos ou pendências não bloqueantes;
- referências exatas do design e do protótipo avaliados;
- `Design Agent verdict: PASS` ou `Design Agent verdict: BLOCKED`.

Usar `PASS` somente quando `design.md`, protótipo versionado/verificável (com URL HTTP navegável quando for HTML) e crítica estiverem completos, coerentes e sem achado bloqueante. Publicar novamente os artefatos OpenSpec no card quando a entrega mudar; o comentário de handoff MUST incluir o link da tela prototipada.

## Handoff permitido

- Com `BLOCKED`, manter `Status=Design`, registrar o motivo e parar.
- Com `PASS` e evidência completa, mover somente `Design -> Aprovação de Design` e registrar handoff com change, design digest, protótipo/versão, resumo da crítica e pendências aceitas.
- Nunca mover `Aprovação de Design -> Pronto para Dev`, nunca autoaprovar, nunca enviar `actor=Alan` nem alegar identidade humana. Essa transição pertence exclusivamente a Alan autenticado.
- Se o design ou protótipo mudar depois da aprovação, considerar a aprovação obsoleta e bloquear desenvolvimento até nova aprovação humana.
- Não mover nenhum outro status. Desenvolvimento começa somente depois que o card estiver em `Pronto para Dev`.

## Saída

Reportar de forma curta:

- card/change e status observado;
- protótipo e versão/digest;
- resultado da crítica;
- veredito;
- movimento realizado ou bloqueio;
- próximo passo humano.
