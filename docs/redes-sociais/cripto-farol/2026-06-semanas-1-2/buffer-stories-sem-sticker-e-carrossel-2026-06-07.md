# Cripto Farol — Ajuste Stories automáticos e carrossel 10/06 — 2026-06-07

Estado: ajustes aplicados em assets públicos DEV/dist e rascunhos do Buffer. Nada publicado.

## Pedido

- Remover dependência de stickers/enquetes/caixa de pergunta nos Stories para reduzir necessidade de ação manual.
- Atualizar o carrossel de 2026-06-10 porque os números/badges estavam sobrescrevendo palavras.

## Ajuste visual aplicado

Arquivos atualizados em:

```text
/srv/apps/dev/criptofarol/source/frontend/public/redes-sociais/cripto-farol/2026-06-semanas-1-2/
/srv/apps/dev/criptofarol/source/frontend/dist/redes-sociais/cripto-farol/2026-06-semanas-1-2/
```

### Stories 09/06

Atualizados:

- `semana-1/2026-06-09/instagram-stories/story-01.png`
- `semana-1/2026-06-09/instagram-stories/story-02.png`
- `semana-1/2026-06-09/instagram-stories/story-03.png`
- `semana-1/2026-06-09/instagram-stories/texto.md`

Mudança:

- Removidos textos que pediam enquete, resposta ou caixa de pergunta.
- Substituídos por CTAs visuais não interativos:
  - `Menos impulso. Mais clareza.`
  - `Olhe o risco antes.`
  - `criptofarol.com.br`

### Carrossel 10/06

Atualizados:

- `semana-1/2026-06-10/instagram-carrossel/slide-01.png`
- `semana-1/2026-06-10/instagram-carrossel/slide-02.png`
- `semana-1/2026-06-10/instagram-carrossel/slide-03.png`
- `semana-1/2026-06-10/instagram-carrossel/slide-04.png`
- `semana-1/2026-06-10/instagram-carrossel/slide-05.png`
- `semana-1/2026-06-10/instagram-carrossel/slide-06.png`
- `semana-1/2026-06-10/instagram-carrossel/slide-07.png`
- `semana-1/2026-06-10/instagram-carrossel/slide-08.png`

Mudança:

- Número/badge movido para uma coluna própria.
- Texto redesenhado com afastamento do número.
- Painel escurecido para remover sobra/ghost do texto antigo.

## Buffer atualizado

### Story Instagram pessoal

Post ID: `6a241a308490187966a0b206`

Resultado da API após `editPost`:

- `status`: `draft`
- `channel`: `o.alan.silva`
- `dueAt`: `2026-06-09T23:00:00.000Z`
- assets: 3
- imagens com cache-buster: `?v=autopost-20260607`
- link obrigatório presente: sim
- textos de sticker/enquete removidos: sim

Limitação observada:

Mesmo enviando `schedulingType: "automatic"`, o Buffer retornou o Story como:

```text
schedulingType: notification
```

Interpretação: o conteúdo não depende mais de sticker manual, mas o Buffer não confirmou publicação 100% automática para Story; ele preservou o modo de notificação.

### Carrossel Instagram empresa

Post ID: `6a2561c474031f4964cff088`

Resultado da API após `editPost`:

- `status`: `draft`
- `channel`: `criptofarol`
- `dueAt`: `2026-06-10T15:00:00.000Z`
- assets: 8
- imagens com cache-buster: `?v=autopost-20260607`
- link obrigatório presente: sim

## QA visual

Verificação visual feita nas imagens revisadas:

- Story 01: não pede enquete/sticker; adequada como peça não interativa.
- Carrossel slide 01: número não sobrescreve palavras.
- Carrossel slide 02: número não sobrescreve palavras.

## Backup

Antes de sobrescrever os assets públicos, backup criado em:

```text
/srv/apps/dev/criptofarol/source/frontend/public/redes-sociais/cripto-farol/2026-06-semanas-1-2/_backup_2026-06-07-before-autopost-fixes
```
