"""Passo do `qa-gate`: base com o teste ligado recusa head sem a chave ligada."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import check_qa_dev_key as chave  # noqa: E402

LIGADA = "repo: x\nqa_dev:\n  enabled: true\n"
DESLIGADA = "repo: x\nqa_dev:\n  enabled: false\n"
SEM_CHAVE = "repo: x\n"


@pytest.mark.parametrize(
    ("base", "head", "recusa"),
    [
        (LIGADA, SEM_CHAVE, True),
        (LIGADA, DESLIGADA, True),
        (LIGADA, None, True),
        (LIGADA, LIGADA, False),
        (DESLIGADA, SEM_CHAVE, False),
        (DESLIGADA, LIGADA, False),
        (SEM_CHAVE, SEM_CHAVE, False),
        (None, SEM_CHAVE, False),
    ],
)
def test_recusa_so_com_a_base_ligada(base: str | None, head: str | None, recusa: bool) -> None:
    assert (chave.recusa(base, head) is not None) is recusa


def test_mensagem_manda_atualizar_a_partir_de_develop() -> None:
    assert "atualize a branch a partir de develop" in str(chave.recusa(LIGADA, SEM_CHAVE))


def test_enabled_precisa_ser_booleano() -> None:
    assert chave.ligado('qa_dev:\n  enabled: "true"\n', "base") is False


def test_overlay_quebrado_nao_passa_por_desligado() -> None:
    with pytest.raises(chave.Ilegivel):
        chave.ligado("qa_dev: [", "base")


def _repo(tmp_path: Path, *versoes: str) -> Path:
    def git(*args: str) -> None:
        subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@exemplo.test", *args], cwd=tmp_path, check=True, capture_output=True)

    git("init", "-q")
    overlay = tmp_path / ".covenant-flow" / "overlay.yaml"
    overlay.parent.mkdir()
    for indice, texto in enumerate(versoes):
        overlay.write_text(texto, encoding="utf-8")
        git("add", ".")
        git("commit", "-qm", f"v{indice}")
    return tmp_path


def _rodar(raiz: Path, base: str, head: str) -> subprocess.CompletedProcess[str]:
    script = Path(chave.__file__).resolve()
    return subprocess.run([sys.executable, str(script), "--base", base, "--head", head], cwd=raiz, capture_output=True, text=True, check=False)


def test_cli_recusa_com_a_mensagem(tmp_path: Path) -> None:
    raiz = _repo(tmp_path, SEM_CHAVE, LIGADA)
    saida = _rodar(raiz, "HEAD", "HEAD~1")
    assert saida.returncode == 1 and "atualize a branch a partir de develop" in saida.stderr


def test_cli_nao_bloqueia_com_a_base_desligada(tmp_path: Path) -> None:
    raiz = _repo(tmp_path, DESLIGADA, SEM_CHAVE)
    assert _rodar(raiz, "HEAD", "HEAD~1").returncode == 0


def test_cli_passa_com_as_duas_ligadas(tmp_path: Path) -> None:
    raiz = _repo(tmp_path, LIGADA, LIGADA + "# outro commit\n")
    assert _rodar(raiz, "HEAD", "HEAD~1").returncode == 0


def test_cli_com_head_sem_overlay_conta_como_sem_a_chave(tmp_path: Path) -> None:
    raiz = _repo(tmp_path, LIGADA)
    assert _rodar(raiz, "HEAD", "HEAD:nao-existe").returncode == 1


def test_ci_tem_o_passo_no_qa_gate_e_os_testes_ligados() -> None:
    texto = (Path(__file__).resolve().parents[2] / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    trecho = texto.split("  qa-gate:\n", 1)[1].split("  deploy-staging:\n", 1)[0]
    assert "scripts/qa/check_qa_dev_key.py --base HEAD^1 --head HEAD^2" in trecho
    assert "fetch-depth: 2" in trecho
    assert trecho.index("check_qa_dev_key.py") < trecho.index("Require all QA checks")
    assert "scripts/qa" in texto.split("  process-fsm:\n", 1)[1].split("  backend-unit-tests:\n", 1)[0]
