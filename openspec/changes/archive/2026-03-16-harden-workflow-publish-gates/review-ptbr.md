# Revisão PT-BR — harden-workflow-publish-gates

## Resumo

Esta change ajusta o **fluxo operacional** para evitar o problema recorrente em que:
- a QA valida funcionalmente
- mas o card continua travado por publish/upstream guard
- ou o runtime live está desatualizado em relação ao código local

## O que entra
- endurecer o handoff **DEV → QA** para mudanças de runtime/API/UI
- exigir reconciliação de publish/runtime antes de considerar o item realmente pronto para homologação
- separar explicitamente no fluxo:
  - validação funcional
  - publish/reconcile
  - avanço de stage no runtime
- impedir mensagem ambígua de “pronto para homologação” quando uma dessas partes ainda não fechou

## O que não entra
- reescrever toda a CI
- remover guard-rails de segurança
- mudar features do produto fora do fluxo

## Decisão de PO
- o problema é de **processo**, não só de implementação isolada
- a correção precisa priorizar clareza operacional e reduzir estados confusos
- mudanças que afetam runtime/API/UI devem ter um check live mínimo antes do handoff para QA
- uma change só pode ser tratada como pronta para homologação quando **QA funcional + publish/reconcile + stage runtime** estiverem consistentes

## Próximo gate
- Alan approval do pacote de planning para então implementar o ajuste do fluxo
