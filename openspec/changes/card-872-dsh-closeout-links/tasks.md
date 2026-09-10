## 1. Contrato e verificação

- [x] 1.1 Definir o checklist de verificação textual da regra geral (qualquer ligação local vira clicável; ausência de `xdg-open`/erro/caminho de servidor sozinho) derivado dos cenários da spec `closeout-links`
- [x] 1.2 Validar o checklist contra os três critérios de aceite do card #872 em mensagens de exemplo (fictícias, sem reabrir lote): (1) regra geral, (2) fechamento com docs+PRs, (3) sem erro visível com substituto clicável

## 2. Conformidade de escopo

- [x] 2.1 Confirmar que nenhum arquivo do harness (`xdg-open`, opener, closeout) foi criado ou alterado neste repo consumidor
- [x] 2.2 Confirmar não-regressão dos não-objetivos: sem servir doc na porta do painel, sem instalar navegador, sem mudar acesso remoto, sem reabrir lote
- [x] 2.3 Rodar `openspec validate --change "card-872-dsh-closeout-links"` e corrigir pendências de artefato (detalhes de formato são P3 "detalhe de Apply")

## Verificação textual (Apply — contrato observável, sem código neste repo)

### Checklist 1.1 — regra geral (derivado da spec `closeout-links`)

Aplicar sobre o texto da mensagem do chat. Falha em qualquer item = entrega inválida.

- C1 (Req 1): para cada ligação local citada (caminho, `file://`, porta do painel), a mensagem contém a URL `https://...` clicável equivalente — regex: `https://[^\s)]+` ou `\[[^\]]+\]\(https://[^)]+\)`.
- C2 (Req 2, fechamento/docs): mensagem de fechamento contém a URL clicável do doc do lote E a do diário de melhorias (2 URLs blob em main, inteiras).
- C3 (Req 3, fechamento/PRs): mensagem de fechamento contém a URL clicável do PR de código E a do PR de docs.
- C4 (Req 4, sem abertura/erro): a mensagem NÃO contém `xdg-open`, `canOpenNativePath`, caminho de navegador, `open `/`start ` como comando, nem erro visível (`exit code`, `Traceback`, `xdg-open: ...`, `no browser`) — regex: `xdg-open|canOpenNativePath|no browser|exit code|Traceback`.
- C5 (Req 5, SÓ link): nenhum caminho de servidor (`/srv/...`, caminho de worktree), `file://` ou `localhost:porta`/`127.0.0.1:porta` aparece como apoio, mesmo com os links presentes — regex: `/srv/|file://|localhost:\d+|127\.0\.0\.1:\d+`.
- C6 (Req 6, formato): cada URL exigida aparece inteira, em linha própria nua ou como `[texto](url)`; URL quebrada/truncada = requisito não atendido.

### Validação 1.2 — três aceites em mensagens de exemplo FICTÍCIAS (sem reabrir lote)

URLs abaixo são inventadas (`ORG/REPO`) só para exercitar o checklist.

Aceite (1) regra geral — mensagem fictícia:
> Painel do dia (abre no seu dispositivo):
> https://painel.exemplo.test/dia/2026-09-08
Veredito: PASSA C1/C4/C5/C6 (link equivalente, sem caminho local, sem abertura, formato em linha própria).

Aceite (2) fechamento docs+PRs — mensagem fictícia:
> Fechamento do lote:
> Doc do lote: https://github.com/ORG/REPO/blob/main/docs/lote-2026-09-08.md
> Diário de melhorias: https://github.com/ORG/REPO/blob/main/docs/diario-2026-09-08.md
> PR código: https://github.com/ORG/REPO/pull/100
> PR docs: https://github.com/ORG/REPO/pull/101
Veredito: PASSA C2 (2 docs) + C3 (2 PRs) + C4/C5/C6.

Aceite (3) sem erro visível — mensagem fictícia (abertura direta indisponível no servidor):
> Doc do lote (abre no seu dispositivo):
> https://github.com/ORG/REPO/blob/main/docs/lote-2026-09-08.md
Veredito: PASSA C4 (nenhum erro/exit code) — substituto é o link clicável.

Caso negativo (discrimina C5) — mensagem fictícia INVÁLIDA:
> Doc: https://github.com/ORG/REPO/blob/main/docs/lote-2026-09-08.md (também em /srv/apps/dev/criptofarol/docs/lote.md)
Veredito: FALHA C5 (caminho de apoio acompanha o link) — corretamente rejeitada.

### Conformidade 2.1/2.2 (evidência do Apply)

- 2.1: `git status --porcelain` limpo exceto artefatos untracked do próprio change; `git grep -i "xdg-open|canOpenNativePath"` em `scripts/ backend/ frontend/` = sem match; menções a `closeout` em `scripts/process-fsm/*` e `scripts/release-guard` são pré-existentes (T14/T16/guard) e intocadas. Nenhum arquivo do harness criado/alterado neste repo consumidor.
- 2.2: nenhum código alterado → não-objetivos intactos por construção (sem servir doc na porta do painel, sem instalar navegador, sem mudar acesso remoto, sem reabrir lote).
