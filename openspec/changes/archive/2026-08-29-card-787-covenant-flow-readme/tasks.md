## 1. README no produto oalansilva/covenant-flow

- [x] 1.1 Reescrever `/srv/apps/dev/covenant-flow/README.md` em PT-BR com a ordem D4: estranho (o que é, quem usa, núcleo vs consumidor vs overlay, canal v1, primeiro consumidor Cripto) **antes** de qualquer clone/`install.sh`
- [x] 1.2 No bloco do estranho, nomear Cursor, Grok, OpenCode e dsh; distinguir Auto (Cursor `clients.cursor.auto: true`; sem prompt de ferramenta; **não** autoriza cruzar colunas) vs cooperativo (os outros três, `auto: false`, até ensaio deny PASS); MUST NOT reivindicar Auto em Grok/OpenCode/dsh
- [x] 1.3 Walkthrough das 12 colunas yaml (incluindo Cancelado terminal), uma linha cada, nomes PT-BR, significados de D5; exactamente uma frase dos 3 gates sem IDs T0–T17; MUST NOT tabela T0–T17/I1–I9, parágrafo por coluna, hooks/OpenSpec/release
- [x] 1.4 Secções Install / Pin / Layout em PT-BR **depois** do estranho e do walkthrough; exemplo `--pin v1.1.2`; MUST NOT `latest` nem placeholder; MUST NOT paths de backup host; uma linha a apontar skill `covenant-flow` como runbook
- [x] 1.5 Não criar `CONTRIBUTING.md` nem segundo ficheiro de install; não editar skills/hooks/yaml/`install.sh`/`AGENTS.md` gerado/adapters

## 2. Description GitHub

- [x] 2.1 `gh repo edit oalansilva/covenant-flow --description 'Covenant Flow — processo portátil de 12 colunas (núcleo + adapters)'` (string exacta; substitui o texto EN)
- [x] 2.2 Não alterar LICENSE nem homepage

## 3. Tag de produto

- [x] 3.1 Commit do README no repo `oalansilva/covenant-flow` e tag patch **`v1.1.2`** (não major `v2.0.0`; schema overlay inalterado)

## 4. Pin Cripto após o bump

- [x] 4.1 `implantar --pin v1.1.2` no worktree Cripto deste card; overlay `pin: v1.1.2`
- [x] 4.2 Confirmar que o pin **não** copiou `README.md` do produto para o consumidor; MUST NOT editar `backend/**` nem `frontend/src/**`; MUST NOT reabrir #773 nem #784

## 5. Verificação

- [x] 5.1 `openspec validate --change card-787-covenant-flow-readme` verde
- [x] 5.2 `UI impact: none` — zero diff `frontend/src/` / `backend/` de produto; clone não é o primeiro parágrafo do README; description GitHub exacta
