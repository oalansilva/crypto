## MODIFIED Requirements

### Requirement: Full-history default period (ajuste Alan 2026-09-07)

O preset default do seletor de período na Descoberta SHALL ser `15 dias` (janela «últimos 15 dias» a contar de hoje). As opções SHALL ser a lista partilhada: `15 dias`, `1 mês`, `3 meses`, `6 meses`, `1 ano`, `2 anos`, `Personalizado`, `Todo o histórico`. O preflight default SHALL refletir essa janela (`N combinações · ~T estimado · 15 dias + datas da janela`). O rótulo do CTA default SHALL ser `Iniciar varredura — N, ~T` dessa janela. Trocar o preset SHALL atualizar preflight, CTA e rascunho congelado. Restore de uma varredura gravada SHALL reidratar o período do snapshot e SHALL NOT aplicar o default de 15 dias por cima. A marca inicial do Combo não faz parte deste requisito.

#### Scenario: Default is 15 days

- **WHEN** abro o modo `Montar` sem tocar no seletor de período
- **THEN** vejo `15 dias` selecionado, preflight com `N combinações · ~T · 15 dias + datas da janela` e CTA `Iniciar varredura — N, ~T` dessa janela; as outras opções da lista partilhada seguem selecionáveis

#### Scenario: Restore keeps the saved period

- **WHEN** the operator reopens a saved sweep whose snapshot has a period other than 15 dias
- **THEN** the screen shows that saved period
- **AND** it does not force 15 dias
