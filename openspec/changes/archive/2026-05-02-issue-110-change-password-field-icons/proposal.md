## Why

O formulario de alterar senha exibe icones sobrepostos ao texto dos campos, prejudicando leitura e preenchimento. O bug bloqueia uma acao de seguranca basica e deve ser corrigido antes da homologacao do fluxo de acesso.

## What Changes

- Ajustar o componente de input com icone para manter padding interno suficiente no lado esquerdo.
- Garantir que os campos de senha da tela `/change-password` mantenham texto e placeholder sem colisao com o icone.
- Adicionar cobertura E2E focada na tela de alterar senha para validar o espacamento visual por bounding boxes.

## Capabilities

### New Capabilities

- `change-password-form-layout`: Contrato visual dos campos do formulario de alterar senha.

### Modified Capabilities

- Nenhuma.

## Impact

- Frontend: `frontend/src/components/ui/Input.tsx` e teste E2E focado.
- Sem mudanca de API, banco, dependencias ou regra de negocio.
