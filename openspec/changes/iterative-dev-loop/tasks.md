# Tasks: Iterative Dev Loop

## Implementation
- [ ] Adicionar função de ajuste (ex.: `_apply_dev_adjustments`) em `backend/app/routes/lab.py`.
- [ ] Integrar loop Dev: após backtest, rodar preflight; se falhar, ajustar + re‑rodar até limite.
- [ ] Registrar eventos de trace para ajustes.
- [ ] Garantir ATR nos indicadores quando stop/trailing usar ATR.

## Tests
- [ ] Atualizar/Adicionar testes em `tests/test_lab_refactor.py` para validar:
  - loop de ajuste chamado quando `holdout_total_trades=0`.
  - limite de tentativas respeitado.
  - trace de ajuste gerado.

## Validation
- [ ] `./backend/.venv/bin/python -m pytest -q`
