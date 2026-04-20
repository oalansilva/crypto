# Review PT-BR — #66 Análise Técnica Onchain + Fundamentos + Git

## Resumo

Card **#66** em **DEV**: "Fazer uma análise técnica onchain, fundamentos e repositório git para compor sinais"

Objetivo: construir um motor de sinais que combina dados onchain, fundamentos de repositório e composição de score para gerar sinais `BUY` / `SELL` / `HOLD` com confiança explicável.

## Reconciliação de Aprovação

Este card foi reconciliado para refletir o estado operacional atual do workflow:

- o runtime/Kanban já posiciona o card em **DEV**
- a aprovação para implementação do **MVP backend-first** deve ser tratada como concedida
- o frontend visual continua parte do card, mas o detalhamento de DESIGN do `SignalCard` não bloqueia o início das fases de backend

## Escopo Aprovado para MVP

As decisões abaixo foram congeladas a partir do escopo já documentado nos artefatos existentes:

1. **Provedor inicial onchain:** começar pelo caminho mais simples de integração pública
2. **Modelo de scoring:** soma ponderada interpretável
3. **Entrega inicial:** endpoint e pipeline independentes, sem depender de unificação imediata com todos os sinais existentes
4. **Cobertura MVP:** conjunto inicial de chains definido em `tasks.md`
5. **Validação:** backtesting e histórico continuam no escopo, mas não bloqueiam o começo do desenvolvimento das fases 1 e 2

## Observação de DESIGN

- Existe UI prevista para o card
- o artefato [design.md](/root/.openclaw/workspace/crypto/openspec/changes/fazer-uma-analise-tecnica-onchain/design.md) passa a registrar a direção mínima do frontend
- a ausência anterior desse artefato foi uma inconsistência de processo, não um motivo para apagar a aprovação já refletida no board

## Próximo Passo

- DEV pode executar as **fases 1 e 2** imediatamente
- ao entrar na **fase 3**, deve seguir o direcionamento mínimo de `design.md`
- se o frontend completo ficar grande demais para o mesmo turno, o card permanece em **DEV** até haver fechamento end-to-end do escopo visível

## Artefatos

- `proposal.md` — proposta base
- `tasks.md` — plano executável reconciliado
- `design.md` — direção mínima de UI para a fase 3
- `review-ptbr.md` — resumo e registro de aprovação reconciliada
