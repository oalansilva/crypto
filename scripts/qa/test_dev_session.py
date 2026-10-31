"""Login, estado de sessão e varredura. Servidor falso e cofre falso; o segredo real nunca é lido."""

from __future__ import annotations

import json
import stat
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import dev_session as ds  # noqa: E402

SENHA = "fake\"pass\\wo/rd%+ çã"
EMAIL = "login.falso@exemplo.test"
FAKE_BWS = """#!/usr/bin/env bash
case "$2" in
  list) cat "$COFRE_DIR/lista.json" ;;
  get) cat "$COFRE_DIR/segredo-$3.json" ;;
esac
"""


@pytest.fixture
def cofre(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    casa = tmp_path / "casa"
    (casa / ".config" / "bws").mkdir(parents=True)
    (casa / ".config" / "bws" / "access.env").write_text("BWS_ACCESS_TOKEN=falso\n", encoding="utf-8")
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    programa = bin_dir / "bws"
    programa.write_text(FAKE_BWS, encoding="utf-8")
    programa.chmod(0o755)
    pasta = tmp_path / "cofre"
    pasta.mkdir()
    (pasta / "lista.json").write_text(json.dumps([{"id": "1", "key": ds.SEGREDO_LOGIN}, {"id": "2", "key": "OUTRO"}]), encoding="utf-8")
    (pasta / "segredo-1.json").write_text(json.dumps({"value": SENHA, "note": EMAIL}), encoding="utf-8")
    monkeypatch.setenv("HOME", str(casa))
    monkeypatch.setenv("COFRE_DIR", str(pasta))
    monkeypatch.setenv("PATH", f"{bin_dir}:{Path('/usr/bin')}:{Path('/bin')}")
    return pasta


class Servidor:
    def __init__(self, status: int = 200, corpo: dict[str, Any] | None = None, destino: str = "") -> None:
        self.pedidos: list[dict[str, Any]] = []
        servidor = self

        class Handler(BaseHTTPRequestHandler):
            def do_POST(self) -> None:  # noqa: N802
                tamanho = int(self.headers.get("Content-Length") or 0)
                servidor.pedidos.append({"path": self.path, "body": json.loads(self.rfile.read(tamanho) or "{}")})
                self.send_response(status)
                if destino:
                    self.send_header("Location", destino)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(corpo or {}).encode("utf-8"))

            def log_message(self, *_args: Any) -> None:
                return

        self.http = HTTPServer(("127.0.0.1", 0), Handler)
        self.url = f"http://127.0.0.1:{self.http.server_port}"
        threading.Thread(target=self.http.serve_forever, daemon=True).start()

    def fechar(self) -> None:
        self.http.shutdown()
        self.http.server_close()


@pytest.fixture
def servidor() -> Any:
    criados: list[Servidor] = []

    def criar(*args: Any, **kwargs: Any) -> Servidor:
        item = Servidor(*args, **kwargs)
        criados.append(item)
        return item

    yield criar
    for item in criados:
        item.fechar()


LOGIN_OK = {"accessToken": "tok-a", "refreshToken": "tok-r", "id": "u1", "email": EMAIL, "name": "Nome", "isAdmin": False, "mustChangePassword": False}


def test_login_grava_o_estado_que_o_navegador_le(cofre: Path, servidor: Any, tmp_path: Path) -> None:
    falso = servidor(200, LOGIN_OK)
    destino = tmp_path / "estado" / "storage-state.json"
    assert ds.abrir_sessao(falso.url, dev_url=falso.url, destino=destino) == "nao"
    assert falso.pedidos == [{"path": "/api/auth/login", "body": {"email": EMAIL, "password": SENHA}}]
    assert stat.S_IMODE(destino.stat().st_mode) == 0o600
    estado = json.loads(destino.read_text(encoding="utf-8"))
    assert estado["cookies"] == [] and estado["origins"][0]["origin"] == falso.url
    itens = {item["name"]: item["value"] for item in estado["origins"][0]["localStorage"]}
    assert itens["auth_access_token"] == "tok-a" and itens["auth_refresh_token"] == "tok-r"
    assert json.loads(itens["auth_user"]) == {"id": "u1", "email": EMAIL, "name": "Nome", "isAdmin": False, "mustChangePassword": False}
    assert SENHA not in destino.read_text(encoding="utf-8")


def test_admin_vem_do_login(cofre: Path, servidor: Any) -> None:
    falso = servidor(200, {**LOGIN_OK, "isAdmin": True})
    assert ds.abrir_sessao(falso.url, dev_url=falso.url, destino=None) == "sim"


def test_check_nao_grava_e_a_saida_nao_tem_valor(cofre: Path, servidor: Any, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    falso = servidor(200, LOGIN_OK)
    monkeypatch.setattr(ds, "url_dev", lambda: falso.url)
    assert ds.main(["--check"]) == 0
    assert capsys.readouterr().out == "sessao_ok admin=nao\n"
    assert not ds.caminho_estado().exists()


def test_sem_check_grava_na_pasta_do_teste(cofre: Path, servidor: Any, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    falso = servidor(200, LOGIN_OK)
    monkeypatch.setattr(ds, "url_dev", lambda: falso.url)
    assert ds.main([]) == 0
    assert ds.caminho_estado().parts[-3:] == ("covenant-flow", "qa-dev", "storage-state.json")
    assert stat.S_IMODE(ds.caminho_estado().stat().st_mode) == 0o600
    assert SENHA not in capsys.readouterr().out


@pytest.mark.parametrize(("status", "codigo"), [(401, "senha_recusada"), (403, "conta_bloqueada"), (500, "login_falhou"), (200, "login_falhou")])
def test_codigos_distintos(cofre: Path, servidor: Any, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], status: int, codigo: str) -> None:
    falso = servidor(status, {"detail": "x"})
    monkeypatch.setattr(ds, "url_dev", lambda: falso.url)
    assert ds.main(["--check"]) == 1
    assert capsys.readouterr().out == f"{codigo}\n"


def test_redirecionamento_nao_leva_a_senha_para_outra_origem(cofre: Path, servidor: Any) -> None:
    outro = servidor(200, LOGIN_OK)
    falso = servidor(307, {}, destino=f"{outro.url}/api/auth/login")
    with pytest.raises(ds.Falha) as erro:
        ds.abrir_sessao(falso.url, dev_url=falso.url, destino=None)
    assert erro.value.codigo == "login_falhou"
    assert outro.pedidos == []


@pytest.mark.parametrize("url", ["https://criptofarol.com.br", "http://dev.exemplo.test", "https://dev.exemplo.test:8443", "https://dev.exemplo.test.mal.test"])
def test_recusa_origem_que_nao_e_a_do_dev(cofre: Path, url: str) -> None:
    with pytest.raises(ds.Falha) as erro:
        ds.abrir_sessao(url, dev_url="https://dev.exemplo.test", destino=None)
    assert erro.value.codigo == "origem_recusada"


def test_recusa_origem_sem_dev_configurado() -> None:
    with pytest.raises(ds.Falha):
        ds.exigir_origem("https://dev.exemplo.test", "")


def test_recusa_url_por_argumento_antes_do_cofre(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    monkeypatch.setattr(ds, "url_dev", lambda: "https://dev.exemplo.test")
    monkeypatch.setattr(ds, "ler_segredo", lambda _nome: pytest.fail("não pode ler o cofre"))
    assert ds.main(["--url", "https://criptofarol.com.br"]) == 1
    assert capsys.readouterr().out == "origem_recusada\n"


def test_url_dev_vem_do_overlay(tmp_path: Path) -> None:
    (tmp_path / ".covenant-flow").mkdir()
    (tmp_path / ".covenant-flow" / "overlay.yaml").write_text("environments:\n  dev:\n    url: https://dev.exemplo.test/\n", encoding="utf-8")
    assert ds.url_dev(tmp_path) == "https://dev.exemplo.test"


def test_url_dev_do_repositorio_e_a_do_overlay() -> None:
    assert ds.url_dev().startswith("https://dev.")


@pytest.mark.parametrize(
    ("lista", "segredo", "codigo"),
    [
        ([], None, "segredo_ausente"),
        ([{"id": "1", "key": ds.SEGREDO_LOGIN}], {"value": "", "note": EMAIL}, "segredo_ausente"),
        ([{"id": "1", "key": ds.SEGREDO_LOGIN}], {"value": SENHA, "note": ""}, "segredo_ausente"),
    ],
)
def test_cofre_incompleto(cofre: Path, lista: list[dict[str, str]], segredo: dict[str, str] | None, codigo: str) -> None:
    (cofre / "lista.json").write_text(json.dumps(lista), encoding="utf-8")
    if segredo is not None:
        (cofre / "segredo-1.json").write_text(json.dumps(segredo), encoding="utf-8")
    with pytest.raises(ds.Falha) as erro:
        ds.abrir_sessao("https://dev.exemplo.test", dev_url="https://dev.exemplo.test", destino=None)
    assert erro.value.codigo == codigo


def test_cofre_com_saida_invalida(cofre: Path) -> None:
    (cofre / "lista.json").write_text("não é json", encoding="utf-8")
    with pytest.raises(ds.Falha) as erro:
        ds.ler_segredo(ds.SEGREDO_LOGIN)
    assert erro.value.codigo == "cofre_indisponivel"


@pytest.mark.parametrize("forma", ["literal", "json", "json-em-json", "url", "url-mais"])
@pytest.mark.parametrize("senha", [SENHA, ds.SENHA_SINTETICA, "simples123"])
def test_varredura_acha_cada_forma(tmp_path: Path, forma: str, senha: str) -> None:
    arquivo = tmp_path / "transcript.jsonl"
    arquivo.write_text(ds.sementes(senha)[forma] + "\n", encoding="utf-8")
    assert ds.varrer([arquivo], senha)[0] == [str(arquivo)]


def test_varredura_acha_json_sem_escape_de_acento(tmp_path: Path) -> None:
    arquivo = tmp_path / "t.jsonl"
    arquivo.write_text(json.dumps({"r": json.dumps({"c": SENHA}, ensure_ascii=False)}, ensure_ascii=False), encoding="utf-8")
    assert ds.varrer([arquivo], SENHA)[0]


def test_varredura_arquivo_limpo(tmp_path: Path) -> None:
    arquivo = tmp_path / "limpo.txt"
    arquivo.write_text("nada aqui, nem o e-mail\n", encoding="utf-8")
    assert ds.varrer([arquivo], SENHA, email=EMAIL, publico=True) == ([], [])


def test_publico_acrescenta_jwt_e_email_e_transcript_nao(tmp_path: Path) -> None:
    jwt = tmp_path / "jwt.md"
    jwt.write_text("token eyJhbGciOiJIUzI1.eyJzdWIiOiIxMjM0.c2lnbmF0dXJhLWZhbHNh fim", encoding="utf-8")
    email = tmp_path / "email.md"
    email.write_text(f"logado como {EMAIL.upper()}", encoding="utf-8")
    assert ds.varrer([jwt, email], SENHA, email=EMAIL) == ([], [])
    assert ds.varrer([jwt, email], SENHA, email=EMAIL, publico=True)[0] == [str(jwt), str(email)]


def test_scan_saida_so_com_o_nome_do_arquivo(cofre: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    sujo = tmp_path / "relatorio.md"
    sujo.write_text(f"vazou {SENHA}", encoding="utf-8")
    limpo = tmp_path / "ok.md"
    limpo.write_text("ok", encoding="utf-8")
    assert ds.main(["--scan", str(sujo), str(limpo)]) == 1
    saida = capsys.readouterr().out
    assert saida == f"PRESENTE: {sujo}\n" and SENHA not in saida
    assert ds.main(["--scan", str(limpo)]) == 0
    assert capsys.readouterr().out == "ausente\n"


def test_scan_publico_recusa_email_de_login(cofre: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    relatorio = tmp_path / "relatorio.md"
    relatorio.write_text(f"conta {EMAIL}", encoding="utf-8")
    assert ds.main(["--scan", str(relatorio)]) == 0
    capsys.readouterr()
    assert ds.main(["--scan", "--publico", str(relatorio)]) == 1
    saida = capsys.readouterr().out
    assert saida == f"PRESENTE: {relatorio}\n" and EMAIL not in saida


def test_scan_de_arquivo_ilegivel_nao_diz_ausente(cofre: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    faltando = tmp_path / "nao-existe.md"
    assert ds.main(["--scan", str(faltando)]) == 1
    assert capsys.readouterr().out == f"ILEGIVEL: {faltando}\n"


def test_scan_sem_cofre_nao_diz_ausente(cofre: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    (cofre / "lista.json").write_text("[]", encoding="utf-8")
    arquivo = tmp_path / "a.md"
    arquivo.write_text("x", encoding="utf-8")
    assert ds.main(["--scan", str(arquivo)]) == 1
    assert capsys.readouterr().out == "segredo_ausente\n"


def test_self_test_acha_todas_as_formas_sem_gravar_a_senha_real(cofre: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert ds.main(["--scan", "--self-test"]) == 0
    saida = capsys.readouterr().out
    assert saida.splitlines() == ["PRESENTE: literal", "PRESENTE: json", "PRESENTE: json-em-json", "PRESENTE: url", "PRESENTE: url-mais", "ausente: controle", "cofre_ok"]
    assert SENHA not in saida


def test_self_test_usa_senha_sintetica_com_todos_os_caracteres() -> None:
    for caractere in ('"', "\\", "/", "%", "+", " ", "ç"):
        assert caractere in ds.SENHA_SINTETICA


def test_self_test_sem_cofre_falha(cofre: Path, capsys: pytest.CaptureFixture[str]) -> None:
    (cofre / "lista.json").write_text("[]", encoding="utf-8")
    assert ds.main(["--scan", "--self-test"]) == 1
    assert "segredo_ausente" in capsys.readouterr().out
