"""`setup-dev.sh`: só o `--check` roda aqui, numa casa falsa. O registro é passo do Alan."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

PASTA = Path(__file__).resolve().parent
SCRIPT = PASTA / "setup-dev.sh"
NOME = "playwright-qa"


def _casa(tmp_path: Path) -> Path:
    casa = tmp_path / "casa"
    chrome = casa / ".cache" / "ms-playwright" / "chromium-1248" / "chrome-linux-arm64" / "chrome"
    chrome.parent.mkdir(parents=True)
    chrome.write_text("#!/bin/true\n", encoding="utf-8")
    chrome.chmod(0o755)
    estado = casa / ".local" / "state" / "covenant-flow" / "qa-dev"
    config = casa / ".config" / "covenant-flow" / "qa-dev"
    for pasta in (estado, estado / "saida", config):
        pasta.mkdir(parents=True)
        pasta.chmod(0o700)
    trava = config / "bloqueia-ordens.js"
    shutil.copyfile(PASTA / "bloqueia-ordens.js", trava)
    argumentos = ["-y", "@playwright/mcp@0.0.83", "--headless", "--isolated", "--executable-path", str(chrome), "--init-script", str(trava), "--caps=devtools"]
    (casa / ".claude.json").write_text(json.dumps({"mcpServers": {NOME: {"command": "npx", "args": argumentos}}}), encoding="utf-8")
    (casa / ".claude").mkdir()
    permissoes = {"allow": [f"mcp__{NOME}"], "deny": [f"mcp__{NOME}__browser_run_code_unsafe", f"mcp__{NOME}__browser_start_tracing"]}
    (casa / ".claude" / "settings.json").write_text(json.dumps({"permissions": permissoes}), encoding="utf-8")
    return casa


def _check(casa: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["bash", str(SCRIPT), "--check"], env={**os.environ, "HOME": str(casa)}, capture_output=True, text=True, timeout=30, check=False)


def test_check_ok_nao_escreve(tmp_path: Path) -> None:
    casa = _casa(tmp_path)
    antes = sorted((str(item), item.stat().st_mtime_ns) for item in casa.rglob("*"))
    saida = _check(casa)
    assert saida.returncode == 0, saida.stderr
    assert saida.stdout == "ok\n"
    assert sorted((str(item), item.stat().st_mtime_ns) for item in casa.rglob("*")) == antes


def test_check_acusa_chromium_ausente(tmp_path: Path) -> None:
    casa = _casa(tmp_path)
    (casa / ".cache" / "ms-playwright" / "chromium-1248" / "chrome-linux-arm64" / "chrome").unlink()
    saida = _check(casa)
    assert saida.returncode == 1 and "Chromium ausente" in saida.stderr


def test_check_acusa_registro_ausente(tmp_path: Path) -> None:
    casa = _casa(tmp_path)
    (casa / ".claude.json").write_text("{}", encoding="utf-8")
    saida = _check(casa)
    assert saida.returncode == 1 and "registro playwright-qa ausente" in saida.stderr


def test_check_acusa_versao_diferente(tmp_path: Path) -> None:
    casa = _casa(tmp_path)
    conta = casa / ".claude.json"
    conta.write_text(conta.read_text(encoding="utf-8").replace("0.0.83", "0.0.84"), encoding="utf-8")
    saida = _check(casa)
    assert saida.returncode == 1 and "@playwright/mcp@0.0.83" in saida.stderr


def test_check_acusa_copia_diferente_da_trava(tmp_path: Path) -> None:
    casa = _casa(tmp_path)
    (casa / ".config" / "covenant-flow" / "qa-dev" / "bloqueia-ordens.js").write_text("// antiga\n", encoding="utf-8")
    saida = _check(casa)
    assert saida.returncode == 1 and "trava diferente" in saida.stderr


@pytest.mark.parametrize("ferramenta", ["browser_run_code_unsafe", "browser_start_tracing"])
def test_check_acusa_negacao_ausente(tmp_path: Path, ferramenta: str) -> None:
    casa = _casa(tmp_path)
    settings = casa / ".claude" / "settings.json"
    dados = json.loads(settings.read_text(encoding="utf-8"))
    dados["permissions"]["deny"].remove(f"mcp__{NOME}__{ferramenta}")
    settings.write_text(json.dumps(dados), encoding="utf-8")
    saida = _check(casa)
    assert saida.returncode == 1 and ferramenta in saida.stderr


def test_check_acusa_pasta_aberta(tmp_path: Path) -> None:
    casa = _casa(tmp_path)
    (casa / ".local" / "state" / "covenant-flow" / "qa-dev").chmod(0o755)
    saida = _check(casa)
    assert saida.returncode == 1 and "0700" in saida.stderr


def test_argumento_desconhecido_nao_registra(tmp_path: Path) -> None:
    saida = subprocess.run(["bash", str(SCRIPT), "--registrar"], env={**os.environ, "HOME": str(tmp_path)}, capture_output=True, text=True, timeout=30, check=False)
    assert saida.returncode == 2 and not list(tmp_path.iterdir())


def test_registro_segue_o_design() -> None:
    texto = SCRIPT.read_text(encoding="utf-8")
    assert subprocess.run(["bash", "-n", str(SCRIPT)], capture_output=True, check=False).returncode == 0
    for trecho in (
        'claude mcp add --scope user "$NOME" -- ',
        '"@playwright/mcp@$VERSAO_MCP" --headless --isolated',
        '--executable-path "$CHROME"',
        '--storage-state "$ESTADO/storage-state.json"',
        '--output-dir "$ESTADO/saida"',
        '--init-script "$TRAVA"',
        '--blocked-origins "https://criptofarol.com.br;https://www.criptofarol.com.br"',
        "--caps=devtools --viewport-size 1440x900",
    ):
        assert trecho in texto
    assert "--save-session" not in texto and "--save-trace" not in texto
