# Cripto Farol — Redes sociais — Semanas 1 e 2

Estado: material de revisão. Nada publicado ou agendado.

## Objetivo

Preservar dentro do projeto `crypto` os materiais de divulgação recorrente do Cripto Farol para Instagram e LinkedIn.

## Direção aprovada

- Visual editorial humano.
- Imagens base geradas via `openai-codex` OAuth/Device Code no Hermes.
- Uma arte final = uma base visual única.
- Sem reaproveitamento da mesma foto entre posts, stories ou slides.
- Logo com fundo em degradê translúcido.
- Blocos de texto com degradê/transparência, sem cartões chapados.
- Texto aplicado deterministicamente fora da geração de imagem.
- Guardrail: conteúdo educacional; sem promessa de lucro, sinal, call ou recomendação individual.

## Arquivos

- `semana-1-editorial-humana.zip` — pacote completo da Semana 1.
- `semana-1-contact-sheet.jpg` — prévia visual geral da Semana 1.
- `semana-2-editorial-humana.zip` — pacote completo da Semana 2.
- `semana-2-contact-sheet.jpg` — prévia visual geral da Semana 2.

## Estrutura preservada dentro de cada ZIP

Cada pacote semanal preserva a estrutura:

```text
<semana>/
  00-calendario.md
  manifest.json
  contact-sheet-*.jpg
  YYYY-MM-DD/<rede>/<publicacao>/texto.md
  YYYY-MM-DD/<rede>/<publicacao>/imagem.png
```

Stories e carrosséis mantêm as imagens ao lado do respectivo `texto.md`.

## Releases externas de revisão

- Semana 1: https://github.com/oalansilva/crypto/releases/tag/criptofarol-semana1-editorial-humana-20260605
- Semana 2: https://github.com/oalansilva/crypto/releases/tag/criptofarol-semana2-editorial-humana-20260606

## Processo semanal definido

A partir desta entrega, toda semana de redes sociais do Cripto Farol deve ser arquivada neste padrão dentro do projeto:

```text
docs/redes-sociais/cripto-farol/<campanha-ou-periodo>/
```

Com, no mínimo:

- README/índice;
- ZIP completo da semana;
- contact sheet para revisão rápida;
- referência clara de estado: revisão, aprovado, publicado ou agendado.
