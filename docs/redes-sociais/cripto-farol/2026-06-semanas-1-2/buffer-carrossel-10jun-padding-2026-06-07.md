# Cripto Farol — Correção de padding do carrossel 10/06 — 2026-06-07

Estado: ajuste visual aplicado nos assets públicos e sincronizado no Buffer. Nada publicado.

## Pedido

Alan apontou que, no carrossel do Instagram empresa de quarta-feira 2026-06-10, o texto dentro do painel/quadrado estava muito próximo da borda inferior. Exemplo recebido: slide 3/8, onde a frase menor encostava/ultrapassava visualmente a borda do painel.

## Ajuste aplicado

Escopo: Instagram empresa `criptofarol`, carrossel de 2026-06-10.

Arquivos atualizados em `public` e `dist`:

- `semana-1/2026-06-10/instagram-carrossel/slide-01.png`
- `semana-1/2026-06-10/instagram-carrossel/slide-02.png`
- `semana-1/2026-06-10/instagram-carrossel/slide-03.png`
- `semana-1/2026-06-10/instagram-carrossel/slide-04.png`
- `semana-1/2026-06-10/instagram-carrossel/slide-05.png`
- `semana-1/2026-06-10/instagram-carrossel/slide-06.png`
- `semana-1/2026-06-10/instagram-carrossel/slide-07.png`
- `semana-1/2026-06-10/instagram-carrossel/slide-08.png`

Mudança visual:

- painel ampliado com maior padding inferior;
- número/badge mantido em coluna própria;
- texto reposicionado sem encostar na borda;
- painel tornou-se opaco para eliminar ghost/sombra de texto antigo;
- elementos antigos parcialmente expostos foram cobertos.

## Buffer sincronizado

Post ID: `6a2561c474031f4964cff088`

Resultado verificado via API:

- `status`: `draft`
- canal: `criptofarol`
- `dueAt`: `2026-06-10T15:00:00.000Z`
- assets: 8
- link obrigatório presente: sim
- versionamento/cache-buster nos assets: `?v=padding-20260607`
- `version_ok`: `True`

## Observação de sincronização

Como o script também regenerou os Stories sem sticker para manter consistência dos assets, o draft de Story também foi sincronizado no Buffer conforme a regra nova de não deixar Buffer apontando para asset antigo.

Story ID: `6a241a308490187966a0b206`

Verificação:

- `status`: `draft`
- canal: `o.alan.silva`
- assets: 3
- cache-buster: `?v=padding-20260607`
- link obrigatório presente: sim
- `schedulingType`: `notification` retornado pelo Buffer

## QA visual

QA visual executado nos slides 03, 05 e 08:

- texto inferior com espaço confortável até a borda;
- número/badge separado do texto;
- sem sobreposição;
- sem ghost de texto antigo;
- sem elemento amarelo cortado aparente.

## Backup

Backup anterior preservado em:

```text
/srv/apps/dev/criptofarol/source/frontend/public/redes-sociais/cripto-farol/2026-06-semanas-1-2/_backup_2026-06-07-before-autopost-fixes
```
