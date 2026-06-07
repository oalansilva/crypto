# Cripto Farol — Redes sociais — Semanas 1 e 2

Estado: material de revisão. Nada publicado.

Atualização Buffer: rascunhos dos dias 2026-06-09 a 2026-06-12 foram criados no Buffer pessoal para revisão do Alan. Ver `buffer-drafts-2026-06-09-a-12.md` e `x-drafts-2026-06-09-a-12.md`.

Atualização editorial: com a nova configuração em Buffer único, os rascunhos foram reorganizados por 3 canais em `rascunhos-buffer-unico-3-canais-2026-06-09-a-12.md`.

Regra vigente: descrições/textos públicos das postagens do Cripto Farol devem incluir `https://criptofarol.com.br` no texto/descrição.

Modelo operacional vigente: usar um único Buffer com 3 canais — LinkedIn pessoal do Alan, Instagram pessoal `o.alan.silva` e Instagram empresa Cripto Farol. X/Twitter sai do ciclo imediato. Ver `modelo-dois-buffers.md` para histórico e atualização da decisão.

Grade aprovada para este pacote:

- 2026-06-09 terça — X/Twitter 09h30; Instagram Stories 20h.
- 2026-06-10 quarta — X/Twitter 10h; Instagram carrossel 12h.
- 2026-06-11 quinta — LinkedIn 09h; X/Twitter 10h.
- 2026-06-12 sexta — Instagram feed 09h; LinkedIn 09h30; X/Twitter 11h.

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

- `rascunhos-buffer-unico-3-canais-2026-06-09-a-12.md` — organização atual dos rascunhos no modelo de Buffer único com LinkedIn pessoal, Instagram pessoal e Instagram empresa.
- `buffer-ajustes-aplicados-2026-06-07.md` — evidência dos canais localizados e dos ajustes aplicados no Buffer, mantendo tudo como rascunho.
- `buffer-stories-sem-sticker-e-carrossel-2026-06-07.md` — evidência da remoção de stickers/enquetes nos Stories, atualização do rascunho no Buffer e correção visual do carrossel de 10/06.
- `buffer-carrossel-10jun-padding-2026-06-07.md` — evidência da segunda revisão visual do carrossel de 10/06, corrigindo padding inferior dos painéis e sincronizando o Buffer.
- `imagem-perfil-instagram-criptofarol/` — imagem de perfil/avatar para o Instagram oficial do Cripto Farol, com PNG final, SVG fonte e README.
- `primeira-postagem-instagram-criptofarol/` — primeira postagem sugerida para estrear o Instagram oficial do Cripto Farol, com `texto.md` e `imagem.png`.
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
