# login-bypass-senha-alan

## Status
- PO: done
- DESIGN: skipped
- DEV: done
- QA: pending
- Homologation: pending

## Decisions (locked)
- Bypass: email `alan.silva@gmail.com` entra sem senha em ambiente dev
- Não aplicar em produção
- Implementação mínima: endpoint `/api/auth/login` aceita só email e retorna JWT

## Links
- OpenSpec: http://72.60.150.140:5173/openspec/changes/login-bypass-senha-alan/proposal

## Handoff
- Alan pedido direto: login sem senha pro email dele em dev
- Scott: implementar bypass mínimo em `/api/auth/login`
