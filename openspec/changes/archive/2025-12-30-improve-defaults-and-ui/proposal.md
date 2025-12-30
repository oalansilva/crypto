# Proposta: Melhorar Padrões e Interface do Usuário

## Objetivo
Alterar os valores padrão do formulário de backtest (1 ano de histórico, timeframe diário) e corrigir problemas de legibilidade na interface, especificamente nos dropdowns.

## Por Quê
O usuário relatou que o período padrão de 1 mês é curto demais para testes significativos e que o timeframe de 4h não é o desejado como padrão. Além disso, a interface atual apresenta dropdowns (selects) com fundo branco e texto ilegível contrastando com o tema escuro da aplicação, dificultando a leitura e uso.

## O Que Muda

### Frontend ([CustomBacktestForm.tsx](file:///c:/Users/alans.triggo/OneDrive%20-%20Corpay/Documentos/projetos/crypto/frontend/src/components/CustomBacktestForm.tsx))

#### Padrões (Defaults)
- **Start Date (Since):** Alterar de `Date.now() - 1 month` para `Date.now() - 1 year`.
- **Timeframe:** Alterar padrão de `'4h'` para `'1d'`.

#### Interface (UI/CSS)
- **Dropdowns (Selects):** Aplicar estilos CSS explícitos para garantir fundo escuro (`bg-slate-900` ou similar) e texto claro em todos os elementos `<select>` e `<option>`.
- **Contraste:** Verificar labels e inputs para garantir contraste adequado.
- **Layout:** (Opcional) Ajustar espaçamentos se necessário para melhor leitura.

## Verificação
- Abrir o formulário e verificar se a data de início é 1 ano atrás.
- Verificar se o timeframe já vem selecionado como '1d'.
- Abrir o dropdown de Timeframe e verificar se o fundo é escuro e o texto é legível.
