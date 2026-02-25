# Tasks: resilient-async-backtest

- [ ] Ajustar Dev para disparar backtest via job assíncrono e retornar controle.
- [ ] Persistir status/erro do job no run (`backtest_job` + `diagnostic`).
- [ ] Permitir re-tentativas no loop Dev quando job falhar.
- [ ] Testes: job falho não bloqueia fluxo, run fica consistente.
