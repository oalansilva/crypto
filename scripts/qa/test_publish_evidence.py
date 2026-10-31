"""Envio ao Drive com `gog` falso e cofre falso: nenhuma chamada ao Drive real."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import dev_session  # noqa: E402
import publish_evidence as pe  # noqa: E402

LEITOR = "leitor.falso@exemplo.test"
GOG_FALSO = """#!/usr/bin/env python3
import json, os, sys
from pathlib import Path

base = Path(os.environ["GOG_DIR"])
args = sys.argv[1:]
with (base / "chamadas.jsonl").open("a", encoding="utf-8") as saida:
    saida.write(json.dumps(args) + "\\n")
config = json.loads((base / "config.json").read_text(encoding="utf-8"))
comando = args[1]
if comando in config.get("falha", []):
    print("erro com " + os.environ.get("VALOR_PROIBIDO", ""), file=sys.stderr)
    sys.exit(1)
if comando == "ls":
    print(json.dumps({"files": config.get("existentes", {}).get(args[args.index("--parent") + 1], [])}))
elif comando == "mkdir":
    print(json.dumps({"folder": {"id": "pasta-" + args[2], "name": args[2]}}))
elif comando == "permissions":
    print(json.dumps({"permissions": config.get("permissoes", [{"type": "user", "role": "owner"}])}))
elif comando == "upload":
    print(json.dumps({"file": {"id": "arq-" + Path(args[2]).name}}))
else:
    print("{}")
"""


@pytest.fixture
def ambiente(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    casa = tmp_path / "casa"
    (casa / ".local" / "bin").mkdir(parents=True)
    programa = casa / ".local" / "bin" / "gog-bws"
    programa.write_text(GOG_FALSO, encoding="utf-8")
    programa.chmod(0o755)
    base = tmp_path / "gog"
    base.mkdir()
    (base / "config.json").write_text("{}", encoding="utf-8")
    monkeypatch.setenv("HOME", str(casa))
    monkeypatch.setenv("GOG_DIR", str(base))
    monkeypatch.setenv("VALOR_PROIBIDO", LEITOR)
    monkeypatch.setattr(pe, "ler_segredo", lambda nome: {"value": LEITOR, "note": ""} if nome == pe.SEGREDO_LEITOR else pytest.fail(nome))
    return base


@pytest.fixture
def evidencia(tmp_path: Path) -> Path:
    pasta = tmp_path / "evidencia"
    pasta.mkdir()
    for nome in ("c1.png", "bloco-1.webm", "page-1.yml"):
        (pasta / nome).write_bytes(b"x")
    return pasta


def _config(base: Path, **dados: Any) -> None:
    (base / "config.json").write_text(json.dumps(dados), encoding="utf-8")


def _chamadas(base: Path) -> list[list[str]]:
    caminho = base / "chamadas.jsonl"
    if not caminho.exists():
        return []
    return [json.loads(linha) for linha in caminho.read_text(encoding="utf-8").splitlines()]


def _rodar(evidencia: Path, capsys: pytest.CaptureFixture[str]) -> tuple[int, dict[str, Any], str]:
    codigo = pe.main(["--card", "1144", "--run", "r1", "--dir", str(evidencia)])
    texto = capsys.readouterr().out
    return codigo, json.loads(texto), texto


def test_publica_na_pasta_do_run_e_devolve_links(ambiente: Path, evidencia: Path, capsys: pytest.CaptureFixture[str]) -> None:
    codigo, saida, _ = _rodar(evidencia, capsys)
    assert codigo == 0 and saida["ok"] is True
    assert saida["pasta"] == "https://drive.google.com/drive/folders/pasta-r1"
    assert saida["arquivos"] == {"bloco-1.webm": "https://drive.google.com/file/d/arq-bloco-1.webm/view", "c1.png": "https://drive.google.com/file/d/arq-c1.png/view"}
    pastas = [(item[2], item[item.index("--parent") + 1]) for item in _chamadas(ambiente) if item[1] == "mkdir"]
    assert pastas == [("QA", pe.PASTA_PROJETO), ("1144", "pasta-QA"), ("r1", "pasta-1144")]


def test_reaproveita_pasta_existente(ambiente: Path, evidencia: Path, capsys: pytest.CaptureFixture[str]) -> None:
    _config(ambiente, existentes={pe.PASTA_PROJETO: [{"id": "qa-antiga", "name": "QA"}]})
    _rodar(evidencia, capsys)
    pastas = [(item[2], item[item.index("--parent") + 1]) for item in _chamadas(ambiente) if item[1] == "mkdir"]
    assert pastas[0] == ("1144", "qa-antiga")


def test_compartilha_so_com_o_leitor_do_cofre(ambiente: Path, evidencia: Path, capsys: pytest.CaptureFixture[str]) -> None:
    _, _, texto = _rodar(evidencia, capsys)
    compartilhamentos = [item for item in _chamadas(ambiente) if item[1] == "share"]
    assert len(compartilhamentos) == 1
    item = compartilhamentos[0]
    assert item[2] == "pasta-r1"
    assert item[item.index("--to") + 1] == "user" and item[item.index("--email") + 1] == LEITOR and item[item.index("--role") + 1] == "reader"
    assert LEITOR not in texto


def test_nunca_usa_link_aberto(ambiente: Path, evidencia: Path, capsys: pytest.CaptureFixture[str]) -> None:
    _rodar(evidencia, capsys)
    planas = [campo for item in _chamadas(ambiente) for campo in item]
    assert "anyone" not in planas and "domain" not in planas and "--domain" not in planas


def test_nao_publica_arquivo_de_pagina(ambiente: Path, evidencia: Path, capsys: pytest.CaptureFixture[str]) -> None:
    _rodar(evidencia, capsys)
    assert sorted(Path(item[2]).name for item in _chamadas(ambiente) if item[1] == "upload") == ["bloco-1.webm", "c1.png"]


@pytest.mark.parametrize(("tipo", "esperado"), [("anyone", "acesso anyone"), ("domain", "acesso domain")])
def test_recusa_enviar_com_acesso_aberto_inclusive_herdado(ambiente: Path, evidencia: Path, capsys: pytest.CaptureFixture[str], tipo: str, esperado: str) -> None:
    _config(ambiente, permissoes=[{"type": "user", "role": "owner"}, {"type": tipo, "role": "reader", "permissionDetails": [{"inherited": True}]}])
    codigo, saida, _ = _rodar(evidencia, capsys)
    assert codigo == 1 and saida["ok"] is False and esperado in saida["motivo"]
    assert not [item for item in _chamadas(ambiente) if item[1] == "upload"]


def test_confere_acesso_depois_de_compartilhar_e_antes_de_enviar(ambiente: Path, evidencia: Path, capsys: pytest.CaptureFixture[str]) -> None:
    _rodar(evidencia, capsys)
    ordem = [item[1] for item in _chamadas(ambiente) if item[1] in {"share", "permissions", "upload"}]
    assert ordem[:3] == ["share", "permissions", "upload"]


def test_permissoes_ilegiveis_recusam(ambiente: Path, evidencia: Path, capsys: pytest.CaptureFixture[str]) -> None:
    _config(ambiente, permissoes=[])
    codigo, saida, _ = _rodar(evidencia, capsys)
    assert codigo == 1 and "ilegíveis" in saida["motivo"]
    assert not [item for item in _chamadas(ambiente) if item[1] == "upload"]


@pytest.mark.parametrize("comando", ["ls", "mkdir", "share", "permissions", "upload"])
def test_falha_do_gog_vira_motivo_sem_saida_crua(ambiente: Path, evidencia: Path, capsys: pytest.CaptureFixture[str], comando: str) -> None:
    _config(ambiente, falha=[comando])
    codigo, saida, texto = _rodar(evidencia, capsys)
    assert codigo == 1 and saida["ok"] is False and comando in saida["motivo"]
    assert LEITOR not in texto


def test_cofre_sem_o_leitor_nao_envia(ambiente: Path, evidencia: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch) -> None:
    def sem_segredo(_nome: str) -> dict[str, str]:
        raise dev_session.Falha("segredo_ausente")

    monkeypatch.setattr(pe, "ler_segredo", sem_segredo)
    codigo, saida, _ = _rodar(evidencia, capsys)
    assert codigo == 1 and saida["motivo"] == "cofre: segredo_ausente"
    assert _chamadas(ambiente) == []


def test_pasta_sem_evidencia_nao_chama_o_gog(ambiente: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    vazia = tmp_path / "vazia"
    vazia.mkdir()
    codigo, saida, _ = _rodar(vazia, capsys)
    assert codigo == 1 and saida["ok"] is False
    assert _chamadas(ambiente) == []


def test_sem_gog_bws_vira_motivo(ambiente: Path, evidencia: Path, capsys: pytest.CaptureFixture[str]) -> None:
    (Path.home() / ".local" / "bin" / "gog-bws").unlink()
    codigo, saida, _ = _rodar(evidencia, capsys)
    assert codigo == 1 and "indisponível" in saida["motivo"]
