# Landing Page - Cripto Farol

## Objetivo

Captar interessados para o beta fechado do Cripto Farol com uma pagina simples, clara e pronta para compartilhar por link.

## CTA Principal

**Entrar na lista do beta fechado**

## Estrutura da Pagina

1. Hero
2. Bloco de problema
3. Como funciona
4. Para quem e
5. O que entra no beta
6. Formulario de interesse
7. Guardrail etico

## Copy Base

### Hero

- Headline: **Enxergue melhor antes de decidir em cripto.**
- Subheadline: Veja quais ativos estao em posicao ativa e quais pedem saida com uma leitura simples de contexto e risco.
- CTA: **Entrar na lista do beta fechado**

### Problema

- O mercado cripto muda rapido; o dificil e saber o que realmente importa agora.
- O investidor pula entre moedas, graficos e opinioes sem saber onde concentrar atencao.
- Falta uma leitura simples para separar posicao ativa de saida acionavel.

### Como Funciona

- Monitor central com `HOLD` e `EXIT` como sinais visiveis na tela principal.
- Leitura visual para entender momento, oportunidade e risco.
- Fluxo de acompanhamento pensado para investidores que querem rotina, nao call.

### Perfil Ideal

- Investidor iniciante que quer saber onde concentrar atencao.
- Intermediario que precisa acompanhar oportunidades com mais consistencia.
- Trader que quer contexto objetivo para acompanhar posicoes ativas e saidas.

### O Que Entra no Beta

- Acesso controlado.
- Monitor como tela principal.
- Feedback direto com grupo pequeno.
- Evolucao orientada por uso real.

### Formulario

Campos minimos:

- nome;
- email;
- nivel com cripto;
- principal dificuldade hoje;

## Captacao Operacional

- Formulario da landing envia os leads para o endpoint VPS `http://72.60.150.140:5174/api/leads`.
- Os leads sao gravados em uma planilha `.xlsx` no Google Drive da Clara: `https://docs.google.com/spreadsheets/d/1cWFpAEfbTHcPJ8akzTf-oHRLRS-QmVNf/edit?usp=drivesdk&ouid=109602176178341361243&rtpof=true&sd=true`.
- A cada inscricao, o endpoint tambem envia aviso no topico Telegram do projeto cripto, e-mail para Alan em `o.alan.silva@gmail.com` e e-mail de boas-vindas para o lead com link de acesso.
- Se o e-mail ainda nao existir no sistema, o endpoint cria automaticamente um usuario ativo do beta com senha temporaria aleatoria, salva apenas o hash no banco e envia a senha somente no e-mail de boas-vindas com copia para Alan.
- Observacao tecnica: a API nativa do Google Sheets esta bloqueada no OAuth atual; por isso a integracao usa arquivo `.xlsx` no Drive, atualizado pela VPS.

## Disclaimer

O Cripto Farol e uma ferramenta de apoio a leitura de mercado.
As decisoes de investimento e os riscos continuam sendo do usuario.
Evitar no topo frases defensivas como "sem lucro garantido"; o guardrail deve aparecer de forma discreta no fim da pagina ou em contexto juridico/regulatorio.

## Entregavel Tecnico

Protótipo estatico em:

- `frontend/public/prototypes/cripto-farol-landing/index.html`
- `frontend/public/prototypes/cripto-farol-landing/styles.css`

## Regra Visual dos Prints

Nao usar screenshots que exponham parametros internos, valores de indicadores, medias moveis ou informacoes que o cliente beta nao tera acesso.

A landing deve mostrar uma previa sanitizada da experiencia: status, leitura de contexto, oportunidade e risco, sem detalhes tecnicos internos.

## Direcao Visual

A landing deve usar azul oceano como base visual, mantendo o amarelo como feixe/CTA. A metafora do farol precisa aparecer de forma clara, com sensacao de mar e um feixe de luz no hero, sem abandonar a percepcao de produto tecnico e confiavel.

## Regra de Status

Nao usar `WAIT`/`waiting` na landing. Verificacao no codigo em 2026-05-09 mostrou que o board principal do Monitor exibe `HOLD` e `EXIT`; `WAIT`, `NEUTRAL`, `BUY_SIGNAL` e `BUY_NEAR` ficam ocultos/nao acionaveis na tela principal. A landing deve comunicar dois sinais visiveis: acompanhamento/manutencao (`HOLD`) e saida/venda (`EXIT`).
