# Proposta: Estender Timeframes e Suporte a Período Completo

## Problema
Os usuários estão limitados a um subconjunto de timeframes ('15m', '30m', '1h', '4h', '1d', '3d', '1w') e precisam selecionar datas manualmente. Não há uma maneira fácil de executar um backtest em "todos os dados disponíveis" ou usar timeframes granulares como 5m ou 10m.

## Solução

### 1. Timeframes Estendidos
Adicionar suporte para:
- `5m` (Suportado pela Binance)
- `2h` (Suportado pela Binance)

### 2. Opção de Período Completo (Full Period)
Adicionar uma flag `full_period` à configuração do Backtest.
- **Frontend:** Checkbox "Todo o período". Desabilita os seletores de data.
- **Backend:** Se `full_period=True`, `since` assume como padrão a data de início (inception) padrão do sistema (ex: `2017-01-01`), garantindo cobertura máxima dos dados.

## Design

### Schema da API (`BacktestRunCreate`)
```python
class BacktestRunCreate(BaseModel):
    # ...
    full_period: bool = False  # NOVO
    since: Optional[str] = None  # Alterado de obrigatório para opcional
```

### Carregamento de Dados
O `CCXTLoader` continuará usando sua lógica de paginação. Se `since` for fornecido como "início dos tempos", ele buscará progressivamente até o momento atual.

## Experiência do Usuário
- **Wizard:** Usuário vê novos timeframes no dropdown.
- **Seleção de Data:** Usuário clica em "Todo o período" -> Datas ficam cinza -> Dados "Max" são usados.
