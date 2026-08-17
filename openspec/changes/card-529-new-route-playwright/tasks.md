## 1. Inventário

- [x] 1.1 Extrair rotas de `frontend/src/App.tsx` e mapear specs existentes em `frontend/tests/e2e/`
- [x] 1.2 Commitar allowlist/inventário das rotas atuais (cobertas ou grandfathered)

## 2. Check

- [x] 2.1 Script que falha se uma rota nova não tiver spec funcional+visual apontado no inventário
- [x] 2.2 Mensagem de erro com a rota e o spec esperado
- [x] 2.3 Honrar `qa-visual-skip` + comentário Alan no formato documentado

## 3. CI e docs

- [x] 3.1 Ligar o check ao `qa-gate` (job dedicado ou step)
- [x] 3.2 Atualizar `AGENTS.md`/`rules.md` para o mecanismo automatizado
- [x] 3.3 Fixture/teste: rota nova sem spec falha o script

## 4. QA

- [x] 4.1 QA visual obrigatória (baseline inalterada)
