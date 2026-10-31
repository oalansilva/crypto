#!/usr/bin/env bash
# Registra o navegador do teste no DEV na conta do Claude Code (#1144, D4). Idempotente.
#
# Quem roda é o Alan, no terminal: isto altera a lista de permissões da conta, e um agente não concede
# permissão a si mesmo. Agente só roda `--check`, que não escreve nada, antes de cada teste.
set -euo pipefail

VERSAO_MCP="0.0.83"
NOME="playwright-qa"
CHROME="$HOME/.cache/ms-playwright/chromium-1248/chrome-linux-arm64/chrome"
ESTADO="$HOME/.local/state/covenant-flow/qa-dev"
CONFIG="$HOME/.config/covenant-flow/qa-dev"
TRAVA_ORIGEM="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/bloqueia-ordens.js"
TRAVA="$CONFIG/bloqueia-ordens.js"
SETTINGS="$HOME/.claude/settings.json"
CONTA="$HOME/.claude.json"

falha() {
  echo "setup-dev: $*" >&2
  exit 1
}

conferir() {
  [[ -x "$CHROME" ]] || falha "Chromium ausente em $CHROME"
  for pasta in "$ESTADO" "$ESTADO/saida" "$CONFIG"; do
    [[ -d "$pasta" ]] || falha "pasta ausente: $pasta"
    [[ "$(stat -c %a "$pasta")" == "700" ]] || falha "pasta sem modo 0700: $pasta"
  done
  [[ -f "$TRAVA" ]] || falha "trava ausente: $TRAVA"
  cmp -s "$TRAVA_ORIGEM" "$TRAVA" || falha "trava diferente da do repositório: rode setup-dev.sh"
  [[ -f "$CONTA" ]] || falha "conta do Claude Code sem $CONTA"
  [[ -f "$SETTINGS" ]] || falha "conta do Claude Code sem $SETTINGS"
  python3 - "$CONTA" "$SETTINGS" "$NOME" "$VERSAO_MCP" "$CHROME" "$TRAVA" <<'PY'
import json
import sys

conta, settings, nome, versao, chrome, trava = sys.argv[1:7]


def falha(texto):
    raise SystemExit(f"setup-dev: {texto}")


try:
    servidor = json.load(open(conta, encoding="utf-8")).get("mcpServers", {}).get(nome)
    permissoes = json.load(open(settings, encoding="utf-8")).get("permissions", {})
except (OSError, ValueError) as exc:
    falha(f"configuração ilegível: {type(exc).__name__}")
if not servidor:
    falha(f"registro {nome} ausente: rode setup-dev.sh")
argumentos = [str(item) for item in servidor.get("args", [])]
for esperado in (f"@playwright/mcp@{versao}", "--headless", "--isolated", chrome, trava, "--caps=devtools"):
    if esperado not in argumentos:
        falha(f"registro {nome} sem {esperado}: rode setup-dev.sh")
if f"mcp__{nome}" not in permissoes.get("allow", []):
    falha(f"permissions.allow sem mcp__{nome}")
for ferramenta in ("browser_run_code_unsafe", "browser_start_tracing"):
    if f"mcp__{nome}__{ferramenta}" not in permissoes.get("deny", []):
        falha(f"permissions.deny sem mcp__{nome}__{ferramenta}")
PY
  echo ok
}

registrar() {
  [[ -x "$CHROME" ]] || falha "Chromium ausente em $CHROME"
  command -v claude >/dev/null || falha "claude fora do PATH"
  mkdir -p "$ESTADO/saida" "$CONFIG"
  chmod 700 "$ESTADO" "$ESTADO/saida" "$CONFIG"
  install -m 600 "$TRAVA_ORIGEM" "$TRAVA"
  claude mcp remove --scope user "$NOME" >/dev/null 2>&1 || true
  claude mcp add --scope user "$NOME" -- \
    npx -y "@playwright/mcp@$VERSAO_MCP" --headless --isolated \
    --executable-path "$CHROME" \
    --storage-state "$ESTADO/storage-state.json" \
    --output-dir "$ESTADO/saida" \
    --init-script "$TRAVA" \
    --blocked-origins "https://criptofarol.com.br;https://www.criptofarol.com.br" \
    --caps=devtools --viewport-size 1440x900
  python3 - "$SETTINGS" "$NOME" <<'PY'
import json
import os
import sys
from pathlib import Path

caminho, nome = Path(sys.argv[1]), sys.argv[2]
dados = json.loads(caminho.read_text(encoding="utf-8")) if caminho.exists() else {}
permissoes = dados.setdefault("permissions", {})
for chave, valores in (
    ("allow", [f"mcp__{nome}"]),
    ("deny", [f"mcp__{nome}__browser_run_code_unsafe", f"mcp__{nome}__browser_start_tracing"]),
):
    lista = permissoes.setdefault(chave, [])
    lista.extend(item for item in valores if item not in lista)
caminho.parent.mkdir(parents=True, exist_ok=True)
temporario = caminho.with_name(f".{caminho.name}.{os.getpid()}.tmp")
temporario.write_text(json.dumps(dados, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
if caminho.exists():
    os.chmod(temporario, caminho.stat().st_mode & 0o777)
os.replace(temporario, caminho)
PY
  conferir
  echo "Abra uma sessão nova do Claude Code: servidor MCP novo só aparece em sessão nova."
}

case "${1:-}" in
  --check) conferir ;;
  "") registrar ;;
  *) echo "uso: setup-dev.sh [--check]" >&2; exit 2 ;;
esac
