# Design

## Step 1, Required outputs
- Domain: Monitor de sinais para cripto com estado de portfólio derivado da Carteira Binance.
- Color world: base escura já usada no Monitor, com âmbar para o estado de portfolio, azul/ciano para origem automática e laranja suave para fallback de sync.
- Signature: toggle visualmente igual ao atual, mas travado com texto de procedência logo abaixo, para comunicar regra sem parecer erro.
- Defaults to reject:
  - cadeado isolado sem explicação
  - esconder o toggle e trocar por texto solto
  - liberar edição manual no fallback de sync

## Step 2, Proposal
### Direction
Manter o botão `Portfolio` no mesmo lugar do card do Monitor, preservando reconhecimento do usuário, mas transformá-lo em um controle read-only quando o ativo for cripto e houver Binance válida. O estado continua usando o mesmo shape visual do toggle atual, com três reforços:
1. desabilitação perceptível no próprio botão
2. label contextual curto abaixo do controle
3. fallback explícito para sync indisponível ou desatualizado

### Rationale
- Preserva memória visual, porque o usuário continua vendo `Portfolio` no ponto em que já espera.
- Evita sensação de bug, porque o bloqueio sempre vem acompanhado da origem do dado.
- Mantém consistência com a regra de produto, porque mesmo sem posição ou sem sync o controle não volta a ser editável.

### Explicit rejections
- Não esconder o controle, porque isso apaga a relação entre o estado atual e a antiga ação manual.
- Não trocar por badge passiva, porque o card perderia comparabilidade com ativos fora da regra.
- Não usar erro vermelho no fallback, porque o problema é indisponibilidade operacional, não falha do usuário.

## Step 3, Implementation brief
### Intent
Mostrar que `Portfolio` agora é um estado derivado da carteira para ativos cripto elegíveis, com leitura imediata de ativo, inativo ou indisponível, sem abrir espaço para ambiguidade sobre edição manual.

### Palette rationale
- Âmbar preenchido: ativo em carteira, mantém associação com favorito/portfolio já conhecida.
- Neutro escuro com borda suave: sem posição comprada, ainda derivado.
- Azul/ciano no texto auxiliar: origem automática confiável.
- Laranja suave no fallback: atenção sem semântica de erro fatal.

### Depth and surfaces
- O botão continua com superfície compacta no cabeçalho do card.
- A mensagem de sync fica abaixo, em camada secundária, para não competir com o sinal principal.
- O estado travado usa opacidade reduzida e cursor bloqueado, mas preserva contraste suficiente.

### Typography
- Label do botão permanece curta, em peso médio.
- Mensagem auxiliar em 11px a 12px, alinhada à direita no desktop, para leitura rápida sem poluir o card.
- Copy sempre orientada à origem do dado, não ao bloqueio puro.

### Spacing system
- Manter gap atual entre ações do card.
- Reservar uma linha abaixo do toggle para estados derivados.
- Evitar empilhar múltiplos avisos longos, priorizando uma frase única por estado.

## Copy proposta
### Estado derivado com posição
- Tooltip: `Portfolio sincronizado pela Carteira Binance para ativos cripto`
- Mensagem auxiliar: `Sincronizado com a Carteira Binance (BTC).`

### Estado derivado sem posição
- Tooltip: `Portfolio sincronizado pela Carteira Binance para ativos cripto`
- Mensagem auxiliar: `Sem posição comprada de BTC na Carteira Binance.`

### Fallback de sincronização
- Loading: `Sincronizando carteira Binance...`
- Indisponível: `Carteira Binance indisponível. Portfólio bloqueado até a sincronização voltar.`
- Sem retorno elegível: `Sem posição elegível na Carteira Binance.`

## Visual QA notes
- Validar distinção clara entre toggle editável e toggle derivado sem depender só de tooltip.
- Validar contraste do estado desabilitado no tema dark do Monitor.
- Validar que o fallback continua bloqueado e não parece CTA quebrada.
- Validar alinhamento da mensagem auxiliar em cards com títulos longos e em mobile.
- Validar consistência entre ativo cripto elegível, ativo cripto sem holdings e ativo não cripto.
