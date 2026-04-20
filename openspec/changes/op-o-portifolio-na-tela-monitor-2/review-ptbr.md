# Revisão (PT-BR) — op-o-portifolio-na-tela-monitor-2

## Resumo
- Na tela Monitor, quando o usuário tiver conexão Binance configurada e o ativo for do tipo criptomoeda, a opção de Portfólio não deve permitir edição manual.
- Nessa condição, o conteúdo do Portfólio deve vir da Carteira/holdings sincronizados da Binance.
- Para ativos que não forem criptomoedas, a regra não se aplica.

## Valor de negócio
- Evita divergência entre o que o usuário realmente possui na Binance e o que o Monitor deixa selecionar manualmente.
- Reduz configuração incorreta e melhora a confiança no Monitor para acompanhamento de cripto.
- Mantém o comportamento atual fora do cenário protegido, reduzindo risco de impacto lateral.

## Decisão necessária
- Confirmar que a fonte canônica para “ativos comprados” no cenário Binance conectado será a Carteira/holdings da integração.
- Confirmar o comportamento desejado quando a Binance estiver conectada, mas não houver holdings de cripto elegíveis.

## Trade-offs
- Prós: consistência de produto, menos erro manual, regra mais clara para cripto.
- Contras: menor flexibilidade manual nesse cenário e dependência maior da qualidade/atualização dos dados da Carteira.

## Critérios-chave definidos
- Binance conectada + ativo cripto = Portfólio bloqueado e sincronizado pela Carteira.
- Binance desconectada = comportamento manual atual pode permanecer.
- Ativo não cripto = regra não se aplica.
- Se não houver holdings de cripto, a UI deve mostrar estado vazio definido, sem liberar override manual.

## Próximo passo
- **Recomendação:** handoff para DESIGN, porque há mudança visível de comportamento/UI no estado bloqueado/read-only do Portfólio no Monitor.

## Ação necessária
- **Alan:** validar a regra de fonte canônica e o empty state sem holdings.
- **Scrum Master / Orchestrator:** mover o card para DESIGN quando considerar o pacote PO suficiente.
- **DESIGN:** definir protótipo do estado bloqueado/read-only e mensagens da UI.
- **DEV:** aguardar handoff de DESIGN + aprovação do fluxo.
- **QA:** aguardar implementação.
