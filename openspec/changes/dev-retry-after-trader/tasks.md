# Tasks: Auto-retry do Dev após feedback do Trader

## Backend
- [ ] Implementar loop de retry pós-Trader
- [ ] Aplicar limite max_retries (default 2)
- [ ] Registrar eventos de trace dos retries
- [ ] Ajustar estado do run para needs_adjustment quando limite atingir
- [ ] Testes unitários para retry/limite

## QA
- [ ] Rodar ./backend/.venv/bin/python -m pytest -q
