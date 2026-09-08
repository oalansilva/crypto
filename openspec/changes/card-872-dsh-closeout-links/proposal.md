## Why

Alan operando pelo acesso remoto recebe no chat endereços que apontam para a máquina local e não consegue abrir nada: caminhos, `file://` e portas locais não abrem no dispositivo dele.

## What Changes

- **Regra geral:** QUALQUER endereço de máquina local que chegue ao chat passa a ser entregue como **endereço clicável** equivalente, abrível no dispositivo do Alan.
- **Caso primário fechamento:** os docs do dia (doc do lote + diário de melhorias) chegam clicáveis.
- **Caso primário fechamento:** os pedidos de integração do pacote (código e docs) chegam clicáveis.
- Quando abertura direta não existe/disponível, o **substituto é endereço clicável, sem erro visível** (nenhuma tentativa de abertura direta aparece na mensagem).
- **Caminho do servidor sozinho nunca conta como entrega**; a entrega traz endereço clicável, sem caminho de apoio.

## Vocabulário

- `Ligação local`: qualquer endereço de máquina local (caminho, `file://`, porta do painel).
- `Fechamento`: caso primário da regra geral (docs do dia + PRs do pacote).

## Capabilities

### New Capabilities

- `closeout-links`: contrato observável da regra geral no chat via túnel — QUALQUER ligação local vira endereço clicável equivalente (fechamento como caso primário: docs + PRs), proibidos `xdg-open`/abertura direta, caminho de servidor como entrega e erro visível; fallback silencioso para link.

### Modified Capabilities

(nenhuma — este repo consumidor não possui spec existente de closeout; o comportamento `xdg-open`/`canOpenNativePath` vive no harness dsh, outro checkout.)

## Impact

- **Código neste repo:** nenhum em tempo de execução — change de contrato observável; a verificação é textual sobre a mensagem do chat (contém links, não contém tentativa de abertura direta nem erro visível nem caminho sozinho).
- **Harness dsh (outro checkout):** comportamento vive no harness (fora deste repo; referenciado apenas como *como* em Riscos do design).
- **Operação:** docs do dia precisam estar publicados (URL blob em main) antes do fechamento ser reportado; sem publicação, sem fechamento válido.
- **Fora de escopo (não entra):** servir documento na porta do painel; instalar navegador no servidor; mudar o acesso remoto; reabrir lote já fechado.

## Decidido

- Q1: só clicável (sem abertura direta).
- Q2 REVERTIDA por Alan pós-T5: a regra agora é geral — vale para QUALQUER ligação local no chat, com o fechamento como caso primário (antes: só documentos de fechamento).
