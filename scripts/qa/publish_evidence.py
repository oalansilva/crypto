#!/usr/bin/env python3
"""Envia prints e vídeo do teste no DEV à pasta do projeto no Drive (#1144, D7).

Saída: uma linha JSON, `{"ok": true, "pasta": <url>, "arquivos": {<nome>: <url>}}` ou
`{"ok": false, "motivo": <texto>}`. Falha aqui nunca bloqueia o card: o relatório sai dizendo que a
evidência ficou no servidor. O repositório é público, então a pasta do run abre só para a conta de
`CRIPTOFAROL_QA_DRIVE_READER`, e nada sobe se ela tiver acesso `anyone` ou `domain`, inclusive herdado.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Iterator

sys.path.insert(0, str(Path(__file__).resolve().parent))

from dev_session import Falha, ler_segredo  # noqa: E402

SEGREDO_LEITOR = "CRIPTOFAROL_QA_DRIVE_READER"
CONTA = "claravalente840@gmail.com"
PASTA_PROJETO = "1OE0D_nsb7BAMQ_ntZXUonnsfX9MtXhT9"
TIPO_PASTA = "application/vnd.google-apps.folder"
# `page-*.yml` ficam no servidor: só o que é evidência sai dele.
EXTENSOES = frozenset({".png", ".jpg", ".jpeg", ".webm", ".mp4", ".md"})


class Recusa(Exception):
    """Motivo visível no relatório público: nunca leva e-mail nem saída crua do `gog`."""


def _gog(*args: str, timeout: int = 120) -> Any:
    programa = str(Path.home() / ".local" / "bin" / "gog-bws")
    try:
        proc = subprocess.run([programa, "drive", *args, "--account", CONTA, "--json", "--no-input"], capture_output=True, text=True, timeout=timeout, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise Recusa(f"gog indisponível ({type(exc).__name__})") from exc
    if proc.returncode != 0:
        raise Recusa(f"gog drive {args[0]} falhou")
    try:
        return json.loads(proc.stdout or "null")
    except ValueError as exc:
        raise Recusa(f"gog drive {args[0]} com saída inválida") from exc


def _objetos(dados: Any) -> Iterator[dict[str, Any]]:
    if isinstance(dados, dict):
        yield dados
        for valor in dados.values():
            yield from _objetos(valor)
    elif isinstance(dados, list):
        for valor in dados:
            yield from _objetos(valor)


def _id(dados: Any, contexto: str) -> str:
    for objeto in _objetos(dados):
        if isinstance(objeto.get("id"), str) and objeto["id"]:
            return objeto["id"]
    raise Recusa(f"gog drive {contexto} sem id")


def _pasta(nome: str, pai: str) -> str:
    consulta = f"name = '{nome}' and mimeType = '{TIPO_PASTA}' and trashed = false"
    for objeto in _objetos(_gog("ls", "--parent", pai, "--query", consulta)):
        if objeto.get("name") == nome and objeto.get("id"):
            return str(objeto["id"])
    return _id(_gog("mkdir", nome, "--parent", pai), "mkdir")


def conferir_acesso(pasta: str) -> None:
    """Fail-closed: sem lista legível, não há prova de que a pasta está fechada."""
    tipos = [str(item["type"]).lower() for item in _objetos(_gog("permissions", pasta)) if "type" in item]
    if not tipos:
        raise Recusa("permissões da pasta do run ilegíveis")
    abertos = sorted({tipo for tipo in tipos if tipo in {"anyone", "domain"}})
    if abertos:
        raise Recusa(f"pasta do run com acesso {' e '.join(abertos)}")


def publicar(card: str, run: str, origem: Path) -> dict[str, Any]:
    arquivos = sorted(item for item in origem.iterdir() if item.is_file() and item.suffix.lower() in EXTENSOES)
    if not arquivos:
        raise Recusa("sem prints nem vídeo para enviar")
    leitor = ler_segredo(SEGREDO_LEITOR)["value"]
    pasta = PASTA_PROJETO
    for nome in ("QA", str(card), run):
        pasta = _pasta(nome, pasta)
    _gog("share", pasta, "--to", "user", "--email", leitor, "--role", "reader")
    conferir_acesso(pasta)
    links: dict[str, str] = {}
    for arquivo in arquivos:
        ident = _id(_gog("upload", str(arquivo), "--parent", pasta, timeout=900), "upload")
        links[arquivo.name] = f"https://drive.google.com/file/d/{ident}/view"
    return {"ok": True, "pasta": f"https://drive.google.com/drive/folders/{pasta}", "arquivos": links}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--card", required=True)
    parser.add_argument("--run", required=True)
    parser.add_argument("--dir", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        saida = publicar(args.card, args.run, args.dir)
    except Recusa as recusa:
        saida = {"ok": False, "motivo": str(recusa)}
    except Falha as falha:
        saida = {"ok": False, "motivo": f"cofre: {falha.codigo}"}
    except OSError as exc:
        saida = {"ok": False, "motivo": f"pasta local ilegível ({type(exc).__name__})"}
    print(json.dumps(saida, ensure_ascii=False))
    return 0 if saida.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
