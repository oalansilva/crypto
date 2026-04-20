# Design - Opção Portifolio na tela Monitor - 1

## Step 1 - Required outputs
- **Domain:** monitor de ativos com decisão rápida sobre presença em Portfólio
- **Color world:** manter dark trading UI já reconhecível, com destaque âmbar para estado derivado e azul para mensagens informativas
- **Signature:** mesmo toggle/botão de `Portfolio` no topo do card, porém em modo somente leitura quando vier da Carteira Binance
- **Defaults to reject:** esconder o controle, trocar por texto solto, ou bloquear sem explicar a origem

## Step 2 - Proposal
- **Direction:** preservar o controle visual de `Portfolio` no card do Monitor e transformá-lo em estado derivado para criptomoedas com Binance configurada
- **Rationale:** o usuário continua reconhecendo o ponto de decisão, mas entende que naquele cenário a origem é automática e não manual
- **Explicit rejections:**
  - não substituir o toggle por label estática, porque perde comparabilidade com ativos editáveis
  - não usar aparência de campo desabilitado genérico sem mensagem, porque parece erro
  - não reabrir edição manual em fallback de sincronização, porque quebraria a regra de produto

## Step 3 - Implementation brief
- **Intent:** deixar claro, no primeiro olhar, quando o Portfólio vem da Carteira e quando continua editável
- **Palette rationale:**
  - âmbar para `estado derivado` e atenção leve
  - azul para mensagens de contexto e ausência de posição
  - neutro escuro para manter continuidade com o Monitor existente
- **Depth and surfaces:** cards com superfície única, borda sutil e helper text logo abaixo do controle
- **Typography:** título do ativo em destaque, metadado curto abaixo, helper text pequeno e direto
- **Spacing system:** bloco superior com ativo + status, controle alinhado à direita, mensagem imediatamente abaixo para não exigir busca visual

## Decisions
1. O controle `Portfolio` permanece no cabeçalho do card.
2. Para cripto com Binance configurada, o controle fica bloqueado visualmente e semanticamente.
3. A mensagem explicativa é obrigatória logo abaixo do controle.
4. O protótipo cobre quatro estados:
   - cripto com holding encontrada
   - cripto sem holding encontrada
   - cripto com sincronização indisponível
   - ativo não cripto editável
5. A regra é explicitamente restrita a criptomoedas.

## Copy guidance
- **Com holding:** `Sincronizado com a Carteira Binance.`
- **Sem holding:** `Sem posição comprada na Carteira Binance.`
- **Fallback de sync:** `Carteira Binance indisponível. Portfólio bloqueado até a sincronização voltar.`
- **Fora da regra:** `Fora da regra nova. Toggle continua editável.`

## Visual QA notes
- Validar contraste visível entre estado editável e derivado
- Validar que o bloqueio não parece erro de permissão genérico
- Validar leitura clara de origem automática em viewport desktop e mobile
- Validar que ativo não cripto continua com affordance de clique
- Validar que fallback de sincronização mantém bloqueio, mas muda o tom da mensagem
