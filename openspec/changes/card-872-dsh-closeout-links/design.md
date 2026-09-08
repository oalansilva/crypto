## Context

Card #872 — regra geral de ligações locais no chat (fechamento como caso primário). Status=Design (rework único do teto sem-tela). Este repo é o CONSUMIDOR (criptofarol); o comportamento `xdg-open`/`canOpenNativePath`/closeout vive no HARNESS dsh (outro checkout). Este Design especifica o CONTRATO observável exigido das mensagens de chat, não a implementação do harness. História grelhada (body do issue, fonte da verdade) sintetizada na proposal; rework amplia o escopo por reversão do Alan pós-T5 (Q2 revertida: regra geral, fechamento caso primário). Sem-tela: nenhuma superfície visual muda; a evidência é conferida no GitHub, no dispositivo do operador.

UI impact: none
live_route: none (sem-tela — mensagem de chat, sem rota)
surface: N/A (sem superfície; nunca emprestar rota de catálogo)

## Goals / Non-Goals

**Goals:**
- QUALQUER endereço de máquina local que chegue ao chat é entregue como endereço clicável equivalente, abrível no dispositivo do Alan.
- Caso primário fechamento: docs do dia (doc do lote + diário de melhorias) já publicados chegam clicáveis.
- Caso primário fechamento: pedidos de integração do pacote (código e docs) chegam clicáveis.
- Quando abertura direta não existe, o substituto é endereço clicável, sem erro visível e sem tentativa de abertura direta na mensagem.
- Caminho do servidor sozinho nunca conta como entrega; a entrega traz endereço clicável, sem caminho de apoio.

**Non-Goals:**
- Servir documento na porta do painel.
- Instalar navegador no servidor.
- Mudar o acesso remoto.
- Reabrir lote já fechado.
- Implementar ou alterar o harness dsh neste repo (nenhum arquivo do harness aqui; mecanismo referenciado só como *como* em Riscos).

## Decisions

- **Decisão 1 — SÓ endereço clicável, sem caminho de apoio:** segue decisão fechada do operador (Q1). Caminho de servidor (`/srv/...`, `file://`, caminho de worktree) ou porta local na mensagem não satisfaz o aceite mesmo acompanhado de links. Alternativa (link + caminho de apoio) rejeitada: reintroduz dependência do servidor, que é exatamente a dor.
- **Decisão 2 — Regra geral, fechamento como caso primário (Q2 REVERTIDA por Alan pós-T5):** a regra vale para QUALQUER ligação local no chat (caminho, `file://`, porta do painel); o fechamento (docs do dia + PRs do pacote) é o caso primário, não o escopo total. Alternativa anterior (valer SÓ para documentos de fechamento) superada pela reversão do operador.
- **Decisão 3 — Contrato observável, sem implementação do harness aqui:** este repo não contém `xdg-open`, opener nem closeout; o Apply futuro verifica o texto da mensagem (regex de links / ausência de marcadores de abertura). Alternativa (implementar opener neste repo) rejeitada: aresta inventada entre repos.
- **Decisão 4 — Fallback silencioso:** indisponibilidade de abertura direta nunca vaza erro visível (exit code, stack, "xdg-open: ...", "no browser") para o chat; o substituto é o endereço clicável. Alternativa (avisar o erro + link) rejeitada: viola o aceite.

## Risks / Trade-offs

- [Risco — *como* do harness, não decisão] A sessão dsh tentou `xdg-open` nos docs; o opener declara `canOpenNativePath` falso em Linux headless; o substituto é URL clicável equivalente (no fechamento: URL blob em main + PRs). Este repo apenas exige o resultado observável; se o harness mudar o mecanismo, o contrato aqui continua válido → Mitigação: aceite escrito sobre a mensagem, não sobre chamadas internas.
- [Risco] Docs ainda não publicados (sem URL blob em main) no momento do fechamento → Mitigação: sem publicação, sem fechamento válido; o fechamento só é reportado após push/publicação.
- [Risco] URL colada mas não clicável (quebra de linha, formatação) → Mitigação: spec exige URLs inteiras em linhas próprias, formato markdown `[texto](url)` ou URL nua.
- [Trade-off] Sem caminho de apoio, debug posterior exige abrir o GitHub em vez do disco → aceito pelo operador (decisão fechada).

## Migração / Rollout

N/A — change de contrato, sem migração de dados nem deploy. Verificação: inspeção textual da mensagem do chat contra os critérios de aceite.

## Open Questions

Nenhuma — decisões do operador estão fechadas (Q2 revertida por Alan: regra geral, fechamento caso primário); este é o rework único do teto sem-tela (1+1+1).

## Design Critique

Rework único do teto sem-tela (1 autor + 1 crítico + 1 rework): APROVADO sem P0/P1. Gate verificado (tokens em linha própria, sem-tela sem rota emprestada); fidelidade ao issue verificada (Entra geral + fechamento primário / Não entra / Q1 + Q2 revertida / aceite geral + fechamento, sem escopo além do decidido). Justificativa do rework: Alan reverteu a decisão Q2 pós-T5 e ampliou o escopo — a regra agora vale para QUALQUER ligação local no chat, com o fechamento como caso primário.

P3 anteriores (mantidos ou superados pelo rework — detalhe de Apply, resolver no Apply, nunca reabrir como P0/P1):

- Checklist via regex textual em `tasks.md` — mantido pelo rework, só ampliado para cobrir qualquer ligação local além do fechamento; detalhar regex/checklist no Apply.
- Formato "URL nua em linha própria ou `[texto](url)`" — mantido pelo rework, inalterado na essência e estendido à regra geral; fixar exemplos canónicos no Apply.
- Concretização "URL blob em main" — mantida pelo rework como concretização do caso primário (fechamento), sem limitar a regra geral; confirmar padrão de URL no Apply.
- Menção `canOpenNativePath`/opener do harness em Riscos — mantida pelo rework só como contexto do *como*, sem implementar neste repo.

> **Design fecha em 1+1+1 (teto):** sem-tela = 1 autor + 1 crítico + 1 rework; com-tela = autor + dupla + 1 rework. Segundo rework só com P0 novo de produto justificado no prompt; fora disso o pai publica a seção de crítica com os P3 aceitos e submete. **Classificação:** só produto/escopo/contrato visível (tela, estados, acessibilidade, escopo furado) gera P0/P1; detalhe de implementação é P3 "detalhe de Apply", aceito em `design.md` e resolvido no Apply — nunca reaberto como P0/P1. **Gate no autor:** o primeiro autor já entrega `UI impact` / `live_route` / `surface` em linha própria parseável; sem-tela declara ausência + justificativa curta (nunca rota de catálogo emprestada); com-tela marca só as regiões clonadas. O crítico/dupla verifica esses tokens como item da rubrica.
