#!/usr/bin/env python3
"""Passo do `qa-gate`: com o teste no DEV ligado na base, branch sem a chave ligada não integra (#1144).

Branch antiga roda o motor antigo, que não enxerga `qa_dev`: faria a T14 sem teste e sem trava. Só o
workflow que vem da base alcança essa branch, então a checagem fica aqui, e não na T14. Compara o
overlay de duas revisões do git; no PR, os dois pais do merge.
"""

from __future__ import annotations

import argparse
import subprocess
import sys

import yaml

OVERLAY = ".covenant-flow/overlay.yaml"
MENSAGEM = (
    "qa_dev.enabled está ligado na base e esta branch não tem a chave ligada: "
    "atualize a branch a partir de develop antes de integrar."
)


class Ilegivel(Exception):
    pass


def ligado(texto: str | None, rotulo: str) -> bool:
    """Overlay ausente ou sem a chave é desligado; YAML quebrado não vira "desligado" em silêncio."""
    if texto is None:
        return False
    try:
        dados = yaml.safe_load(texto)
    except yaml.YAMLError as exc:
        raise Ilegivel(f"overlay ilegível em {rotulo}") from exc
    secao = dados.get("qa_dev") if isinstance(dados, dict) else None
    return isinstance(secao, dict) and secao.get("enabled") is True


def recusa(base: str | None, head: str | None) -> str | None:
    if ligado(base, "base") and not ligado(head, "head"):
        return MENSAGEM
    return None


def ler(revisao: str) -> str | None:
    proc = subprocess.run(["git", "show", f"{revisao}:{OVERLAY}"], capture_output=True, text=True, check=False)
    return proc.stdout if proc.returncode == 0 else None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", required=True, help="revisão da base")
    parser.add_argument("--head", required=True, help="revisão do head do PR")
    args = parser.parse_args(argv)
    try:
        motivo = recusa(ler(args.base), ler(args.head))
    except Ilegivel as exc:
        motivo = str(exc)
    if motivo:
        print(motivo, file=sys.stderr)
        return 1
    print("qa_dev: nada a recusar")
    return 0


if __name__ == "__main__":
    sys.exit(main())
