# Tasks: Auto-retry do Dev após feedback do Trader

## Backend
- [x] Implementar loop de retry pós-Trader
- [x] Aplicar limite max_retries (default 2)
- [x] Registrar eventos de trace dos retries
- [x] Ajustar estado do run para needs_adjustment quando limite atingir
- [x] Testes unitários para retry/limite

## QA
- [x] Rodar ./backend/.venv/bin/python -m pytest -q
