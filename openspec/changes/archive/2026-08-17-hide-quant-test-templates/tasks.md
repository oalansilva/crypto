## 1. Exclusão física

- [x] 1.1 Script/rotina de exclusão: backup JSON dos 16 templates `quant_*` + 10 favoritos órfãos, deleção de favoritos, deleção de templates, resumo em log
- [x] 1.2 Executar no banco DEV e validar contagens (16 templates, 10 favoritos)

## 2. Validação

- [x] 2.1 `GET /api/combos/templates` sem templates `quant_*`
- [x] 2.2 `GET /api/opportunities` sem favoritos órfãos (nenhum erro de template not found)
- [x] 2.3 Backup JSON disponível em `scripts/backups/` ou equivalente
- [x] 2.4 `openspec validate` da change verde
