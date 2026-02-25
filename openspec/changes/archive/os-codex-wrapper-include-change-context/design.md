## Overview

O wrapper já obtém `APPLY_JSON` via `openspec instructions apply --change <id> --json`.
Vamos usar `contextFiles` para descobrir paths e anexar o conteúdo no prompt.

## Source of truth

- `contextFiles.proposal` → proposal.md
- `contextFiles.design` → design.md
- `contextFiles.specs` → glob (specs/**/*.md)
- `contextFiles.tasks` → tasks.md

## Implementation notes

- Implementar uma função helper no bash (via python) para:
  - resolver glob de specs
  - ler arquivos com limite de chars (ex.: 12000)
  - imprimir blocos delimitados com header

Formato sugerido no prompt:

```
[CHANGE FILE] <path>
<content>
```

Se truncar:
```
[TRUNCATED to 12000 chars]
```
