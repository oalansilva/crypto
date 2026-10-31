#!/usr/bin/env python3
"""Sessão do teste no DEV sem a senha passar pelo agente (#1144, D3).

Sem argumentos: faz o login e grava o estado de sessão que o navegador lê. `--check`: faz o login
e não grava nada. `--scan`: procura a senha nos arquivos dados, sem nunca imprimir o valor.

A senha fica só na memória deste processo: nunca em argumento de processo, variável exportada,
arquivo ou log. Nível cooperativo: o agente roda no mesmo usuário que lê o cofre e poderia chamar
`bws` por conta própria. Isto garante que ele não precisa da senha, não que ele não consiga buscá-la.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Iterable

SEGREDO_LOGIN = "CRIPTOFAROL_DEV_ALAN_PASSWORD"
LOGIN_PATH = "/api/auth/login"
# Senha sintética do auto-teste: aspas, barra invertida, barra, %, +, espaço e acento.
SENHA_SINTETICA = "Qa\"te'ste\\com/barra%25+ mais ação"
JWT = re.compile(rb"eyJ[A-Za-z0-9_-]{5,}\.[A-Za-z0-9_-]{5,}\.[A-Za-z0-9_-]{5,}")
ROOT = Path(__file__).resolve().parents[2]


class Falha(Exception):
    """Código de erro visível ao agente. Nunca carrega valor."""

    def __init__(self, codigo: str) -> None:
        super().__init__(codigo)
        self.codigo = codigo


def _bws(*args: str) -> subprocess.CompletedProcess[str]:
    """Roda o `bws` com o token carregado só no processo filho, como o `gog-bws`."""
    access = Path.home() / ".config" / "bws" / "access.env"
    script = 'set -a; . "$1"; set +a; shift; exec "$@"'
    return subprocess.run(["bash", "-c", script, "bws-cofre", str(access), "bws", *args], capture_output=True, text=True, timeout=30, check=False)


def ler_segredo(nome: str) -> dict[str, str]:
    """Valor e nota de um segredo. Falha com código; o texto do `bws` não sai daqui."""
    try:
        lista = _bws("secret", "list")
        if lista.returncode != 0:
            raise Falha("cofre_indisponivel")
        itens = json.loads(lista.stdout or "[]")
        ident = next((item.get("id") for item in itens if item.get("key") == nome), None)
        if not ident:
            raise Falha("segredo_ausente")
        lido = _bws("secret", "get", str(ident))
        if lido.returncode != 0:
            raise Falha("cofre_indisponivel")
        dados = json.loads(lido.stdout or "{}")
    except (OSError, subprocess.TimeoutExpired, ValueError, AttributeError, TypeError) as exc:
        raise Falha("cofre_indisponivel") from exc
    valor = str(dados.get("value") or "")
    if not valor:
        raise Falha("segredo_ausente")
    return {"value": valor, "note": str(dados.get("note") or "").strip()}


def _origem(url: str) -> tuple[str, str, int | None]:
    partes = urllib.parse.urlsplit(url)
    porta = partes.port or {"https": 443, "http": 80}.get(partes.scheme)
    return partes.scheme, (partes.hostname or "").lower(), porta


def exigir_origem(url: str, dev_url: str) -> None:
    if not dev_url or _origem(url) != _origem(dev_url):
        raise Falha("origem_recusada")


class _SemRedirecionar(urllib.request.HTTPRedirectHandler):
    """Um redirecionamento levaria a senha para fora da origem conferida: vira falha."""

    def redirect_request(self, *_args: Any, **_kwargs: Any) -> None:
        return None


def entrar(url: str, email: str, senha: str, *, dev_url: str) -> dict[str, Any]:
    exigir_origem(url, dev_url)
    pedido = urllib.request.Request(
        url.rstrip("/") + LOGIN_PATH,
        data=json.dumps({"email": email, "password": senha}).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.build_opener(_SemRedirecionar).open(pedido, timeout=20) as resposta:
            dados = json.loads(resposta.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        codigos = {401: "senha_recusada", 403: "conta_bloqueada"}
        raise Falha(codigos.get(exc.code, "login_falhou")) from None
    except (OSError, ValueError):
        raise Falha("login_falhou") from None
    if not isinstance(dados, dict) or not dados.get("accessToken") or not dados.get("refreshToken"):
        raise Falha("login_falhou")
    return dados


def estado_de_sessao(url: str, dados: dict[str, Any]) -> dict[str, Any]:
    """O formato `storage-state` do Playwright, com os três itens que `authStore.tsx` guarda."""
    usuario = {
        "id": dados.get("id"),
        "email": dados.get("email"),
        "name": dados.get("name"),
        "isAdmin": bool(dados.get("isAdmin")),
        "mustChangePassword": bool(dados.get("mustChangePassword")),
    }
    origem = url.rstrip("/")
    return {
        "cookies": [],
        "origins": [
            {
                "origin": origem,
                "localStorage": [
                    {"name": "auth_access_token", "value": str(dados["accessToken"])},
                    {"name": "auth_refresh_token", "value": str(dados["refreshToken"])},
                    {"name": "auth_user", "value": json.dumps(usuario)},
                ],
            }
        ],
    }


def caminho_estado() -> Path:
    return Path.home() / ".local" / "state" / "covenant-flow" / "qa-dev" / "storage-state.json"


def gravar_estado(destino: Path, estado: dict[str, Any]) -> None:
    destino.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    temporario = destino.with_name(f".{destino.name}.{os.getpid()}.tmp")
    fd = os.open(temporario, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as saida:
        json.dump(estado, saida)
    os.replace(temporario, destino)


def url_dev(raiz: Path = ROOT) -> str:
    import yaml

    try:
        overlay = yaml.safe_load((raiz / ".covenant-flow" / "overlay.yaml").read_text(encoding="utf-8"))
        return str(overlay["environments"]["dev"]["url"]).rstrip("/")
    except (OSError, KeyError, TypeError, ValueError, yaml.YAMLError) as exc:
        raise Falha("overlay_ilegivel") from exc


def abrir_sessao(url: str, *, dev_url: str, destino: Path | None) -> str:
    """Devolve `sim` ou `nao` para admin. Sem `destino` (`--check`), não grava nada."""
    exigir_origem(url, dev_url)
    segredo = ler_segredo(SEGREDO_LOGIN)
    if not segredo["note"]:
        raise Falha("segredo_ausente")
    dados = entrar(url, segredo["note"], segredo["value"], dev_url=dev_url)
    if destino is not None:
        gravar_estado(destino, estado_de_sessao(url, dados))
    return "sim" if dados.get("isAdmin") else "nao"


def _minusculo_percent(texto: str) -> str:
    return re.sub(r"%[0-9A-F]{2}", lambda achado: achado.group(0).lower(), texto)


def formas(valor: str) -> dict[str, set[bytes]]:
    """Como o valor aparece nos arquivos varridos: transcript é JSONL, e URL vem codificada."""
    em_json = {json.dumps(valor)[1:-1], json.dumps(valor, ensure_ascii=False)[1:-1]}
    em_json |= {item.replace("/", "\\/") for item in em_json}
    dentro_de_json = {json.dumps(item)[1:-1] for item in em_json}
    dentro_de_json |= {json.dumps(item, ensure_ascii=False)[1:-1] for item in em_json}
    em_url = {urllib.parse.quote(valor, safe=seguro) for seguro in ("", "/", "!'()*~")}
    em_url |= {_minusculo_percent(item) for item in em_url}
    com_mais = {urllib.parse.quote_plus(valor)}
    com_mais |= {_minusculo_percent(item) for item in com_mais}
    grupos = {"literal": {valor}, "json": em_json, "json-em-json": dentro_de_json, "url": em_url, "url-mais": com_mais}
    return {nome: {item.encode("utf-8") for item in itens} for nome, itens in grupos.items()}


def _contem(conteudo: bytes, valor: str, *, sem_caixa: bool = False) -> bool:
    agulhas = {item for itens in formas(valor).values() for item in itens}
    if sem_caixa:
        minusculo = conteudo.lower()
        return any(item.lower() in minusculo for item in agulhas)
    return any(item in conteudo for item in agulhas)


def varrer(arquivos: Iterable[str | Path], senha: str, *, email: str = "", publico: bool = False) -> tuple[list[str], list[str]]:
    """(presentes, ilegíveis). `--publico` acrescenta JWT e o e-mail de login, que em transcript é legítimo."""
    presentes: list[str] = []
    ilegiveis: list[str] = []
    for arquivo in arquivos:
        try:
            conteudo = Path(arquivo).read_bytes()
        except OSError:
            ilegiveis.append(str(arquivo))
            continue
        achou = _contem(conteudo, senha)
        if publico:
            achou = achou or bool(JWT.search(conteudo)) or (bool(email) and _contem(conteudo, email, sem_caixa=True))
        if achou:
            presentes.append(str(arquivo))
    return presentes, ilegiveis


def sementes(valor: str) -> dict[str, str]:
    """O valor como ele chega aos arquivos, montado sem passar por `formas`, que é o que se testa."""
    return {
        "literal": f"antes {valor} depois",
        "json": json.dumps({"campo": f"senha={valor}"}),
        "json-em-json": json.dumps({"resultado": json.dumps({"campo": f"senha={valor}"})}),
        "url": "https://exemplo.test/?senha=" + urllib.parse.quote(valor, safe=""),
        "url-mais": "https://exemplo.test/?senha=" + urllib.parse.quote_plus(valor),
    }


def auto_teste() -> tuple[dict[str, bool], bool]:
    """(forma -> achou, arquivo limpo passou). A senha real nunca vai para arquivo."""
    achou: dict[str, bool] = {}
    with tempfile.TemporaryDirectory(prefix="qa-dev-scan-") as pasta:
        for nome, texto in sementes(SENHA_SINTETICA).items():
            arquivo = Path(pasta) / f"{nome}.txt"
            arquivo.write_text(texto + "\n", encoding="utf-8")
            achou[nome] = bool(varrer([arquivo], SENHA_SINTETICA)[0])
        limpo = Path(pasta) / "limpo.txt"
        limpo.write_text("nada aqui\n", encoding="utf-8")
        controle = not varrer([limpo], SENHA_SINTETICA)[0]
    return achou, controle


def _comando_scan(args: argparse.Namespace) -> int:
    if args.self_test:
        resultado, controle = auto_teste()
        for nome, ok in resultado.items():
            print(f"{'PRESENTE' if ok else 'FALHOU'}: {nome}")
        print(f"{'ausente' if controle else 'FALHOU'}: controle")
        ler_segredo(SEGREDO_LOGIN)  # só confere que o cofre devolve a senha real, sem vazio
        print("cofre_ok")
        return 0 if controle and all(resultado.values()) else 1
    if not args.arquivos:
        raise Falha("sem_arquivos")
    segredo = ler_segredo(SEGREDO_LOGIN)
    presentes, ilegiveis = varrer(args.arquivos, segredo["value"], email=segredo["note"], publico=args.publico)
    for arquivo in presentes:
        print(f"PRESENTE: {arquivo}")
    for arquivo in ilegiveis:
        print(f"ILEGIVEL: {arquivo}")
    if presentes or ilegiveis:
        return 1
    print("ausente")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="faz o login e não grava o estado de sessão")
    parser.add_argument("--url", help="origem do login; só a de environments.dev.url é aceita")
    parser.add_argument("--scan", action="store_true", help="procura a senha nos arquivos")
    parser.add_argument("--publico", action="store_true", help="com --scan: acrescenta JWT e e-mail de login")
    parser.add_argument("--self-test", action="store_true", help="com --scan: auto-teste com senha sintética")
    parser.add_argument("arquivos", nargs="*")
    args = parser.parse_args(argv)
    try:
        if args.scan:
            return _comando_scan(args)
        dev_url = url_dev()
        admin = abrir_sessao((args.url or dev_url).rstrip("/"), dev_url=dev_url, destino=None if args.check else caminho_estado())
    except Falha as falha:
        print(falha.codigo)
        return 1
    print(f"sessao_ok admin={admin}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
