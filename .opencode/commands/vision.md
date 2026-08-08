---
description: Analisa uma ou mais imagens (arquivos, URLs de anexo do GitHub, artifacts do CI) com o agente vision (gpt-5.6-luna) — julgamento visual rigoroso.
---

Analyze the image(s) with the vision subagent (gpt-5.6-luna). Input: `$ARGUMENTS` — one or more image paths, GitHub attachment URLs, or CI artifact paths (e.g. `diff.png`, `actual.png`, screenshot, baseline, before/after pair).

Steps:

1. **Resolve inputs**
   - For GitHub attachment URLs (`github.com/oalansilva/crypto/assets/...` or `user-images.githubusercontent.com/...`): download the image to `qa_artifacts/` or `.impeccable/attachments/` (curl/gh) and keep the local path.
   - For CI artifact references: download with `gh run download` when a run/artifact is given; otherwise use the local path provided.
   - Local paths: keep as-is.

2. **Delegate to the vision subagent**
   - Use the task tool with subagent `vision` passing every resolved image path and the analysis goal:
     - visual QA judgment (`diff.png`/`actual.png`): intentional UI change vs regression;
     - design fidelity vs `DESIGN.md` (tokens, typography, density, shell, states);
     - before/after comparison (fidelity of prototype, UI change, desktop vs mobile);
     - chart/signal exports, CI artifact screenshots, bug reproduction screenshots;
     - a11y checks visible in pixels (contrast, clipping, overflow, focus).
   - The vision subagent opens the real files with vision (`gpt-5.6-luna`) — never describe pixels yourself.

3. **Report**
   - Return the vision verdict and findings ordered by severity, with file references, and the recommended next step (e.g. fix, accept baseline change, update baseline, reopen bug).

Guardrails:
- If no valid image input was resolved, ask for a path/URL instead of guessing.
- Never attempt to analyze pixels with the main model (no vision support).
- Do not modify files unless the analysis outcome is an explicit follow-up request.
