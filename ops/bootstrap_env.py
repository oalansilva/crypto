#!/usr/bin/env python3
"""Bootstrap append-only para dotenv — fail-closed (card #752).

Contrato:
- --file obrigatório, sem default; destino ausente → exit ≠0, não cria.
- Patch via --from-file e/ou stdin (KEY=VALUE); sem --set; file→stdin (stdin ganha).
- Patch vazio → exit ≠0.
- Merge destino ∪ patch; nenhuma chave do destino some; piso DATABASE_URL+JWT_SECRET imutável.
- Preserva comentários/linhas vazias/ordem; update só valor com sufixo #/; preservado; novas no fim.
- Backup .env.bak-YYYYMMDD-HHMMSS (chmod 600) antes de escrever; tmp mkstemp + os.replace atómico; chmod 600 no destino.
- Idempotente: merge idêntico → exit 0 sem bak/mv.
- Saída só nomes/contagens/paths, nunca valores.
"""

from __future__ import annotations

import argparse
import datetime
import os
import re
import shutil
import sys
import tempfile
from collections import OrderedDict
from pathlib import Path

PISO_KEYS = ("DATABASE_URL", "JWT_SECRET")
KEY_RE = re.compile(r"^\s*(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)$")
BAK_FMT = "%Y%m%d-%H%M%S"


def eprint(*args, **kwargs) -> None:
    print(*args, file=sys.stderr, **kwargs)


def parse_kv_lines(text: str) -> OrderedDict[str, str]:
    """Parse KEY=VALUE lines; ignora comentários/vazias; último valor vence."""
    out: OrderedDict[str, str] = OrderedDict()
    for raw_line in text.splitlines():
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        # linhas com ';' como comentário completo? tratar como comentário se começar com ; ou #
        if stripped.startswith(";"):
            continue
        m = KEY_RE.match(raw_line)
        if not m:
            continue
        key = m.group(1)
        # raw value é everything after '=', mas precisamos separar sufixo comentário? para patch, valor é antes de #/; com espaço
        raw_val = m.group(2)
        # Detectar sufixo comentário no patch: se raw_val contém ' #' ou '\t#' ou ' ;', o valor é antes
        # Para patch, tratamos valor como antes do comentário (strip)
        # Ex.: "FOO=bar # comment" → value "bar"
        # Se valor for quoted, mantemos conteúdo até comentário separado por espaço
        val = raw_val
        # procurar comentário solto: espaço + # ou ;
        # não confundir com valor que contém # sem espaço (ex. token abc#def) → não é comentário
        comment_idx = -1
        for marker in (" #", "\t#", " ;", "\t;"):
            idx = raw_val.find(marker)
            if idx != -1:
                if comment_idx == -1 or idx < comment_idx:
                    comment_idx = idx
        if comment_idx != -1:
            val = raw_val[:comment_idx]
        # strip surrounding whitespace; preservar valor literal sem comentário
        val = val.strip()
        # Se valor for quoted com " ou ', remover? Não — comparar literal sem aspas externas?
        # Mantemos literal (incluindo aspas) para escrita; comparação de piso usa strip
        # Mas para escrita, usaremos val stripped (sem aspas extras)
        out[key] = val
        # mover para fim para preservar ordem efetiva (último vence mas ordem é da última ocorrência)
        out.move_to_end(key)
    return out


def effective_dest_map(lines: list[str]) -> OrderedDict[str, str]:
    """Último valor efetivo por chave no destino (ignora comentadas)."""
    out: OrderedDict[str, str] = OrderedDict()
    for line in lines:
        stripped = line.lstrip()
        if not stripped or stripped.startswith("#") or stripped.startswith(";"):
            continue
        m = KEY_RE.match(line)
        if not m:
            continue
        key = m.group(1)
        raw_val = m.group(2)
        # separar sufixo comentário para extrair valor efetivo
        comment_idx = -1
        for marker in (" #", "\t#", " ;", "\t;"):
            idx = raw_val.find(marker)
            if idx != -1:
                if comment_idx == -1 or idx < comment_idx:
                    comment_idx = idx
        if comment_idx != -1:
            raw_val = raw_val[:comment_idx]
        val = raw_val.strip()
        out[key] = val
        out.move_to_end(key)
    return out


def piso_present(map_: OrderedDict[str, str]) -> tuple[bool, str | None]:
    for k in PISO_KEYS:
        v = map_.get(k)
        if v is None or not v.strip():
            return False, k
    return True, None


def build_result_lines(
    dest_lines: list[str], patch: OrderedDict[str, str], dest_map: OrderedDict[str, str]
) -> list[str]:
    """Retorna novas linhas do destino após merge."""
    # índice da última ocorrência por chave
    last_idx: dict[str, int] = {}
    for idx, line in enumerate(dest_lines):
        stripped = line.lstrip()
        if not stripped or stripped.startswith("#") or stripped.startswith(";"):
            continue
        m = KEY_RE.match(line)
        if not m:
            continue
        key = m.group(1)
        last_idx[key] = idx

    # Para chaves do patch que já existem, atualizar linha correspondente
    # Para chaves novas, append no fim
    new_lines = list(dest_lines)
    # manter controle de offset se houver? mas atualizamos no lugar, sem inserir no meio, então índice estável
    appended: list[str] = []
    for key, new_val in patch.items():
        if key in last_idx:
            idx = last_idx[key]
            orig = new_lines[idx]
            # extrair prefix e sufixo da linha original
            # prefix = até '=', sufixo = comentário após valor
            m = KEY_RE.match(orig)
            if not m:
                # fallback: substituir linha toda
                new_lines[idx] = f"{key}={new_val}"
                continue
            # reconstruir: usar regex que captura prefix, valor, sufixo
            # orig: "  export KEY = oldval # comment"
            # queremos prefix = "  export KEY = " (inclui espaços e =)
            # método: encontrar posição do '='
            eq_pos = orig.find("=")
            if eq_pos == -1:
                new_lines[idx] = f"{key}={new_val}"
                continue
            prefix = orig[: eq_pos + 1]  # inclui =
            # prefix pode ter espaços após =? actually orig[:eq+1] é até '=', sem espaços pós-
            # precisamos capturar espaços pós-=
            # Se orig tem "KEY=  oldval", queremos preservar? Melhor normalizar para "KEY=val"
            # Mas spec diz "chaves já presentes mudam só o valor na linha (sufixo permanece)"
            # Vamos reconstruir como: key_part = orig[:eq_pos+1] + (space se orig tem espaço após =?")
            # Simpler: prefix = orig[: eq_pos + 1]  ; se pós-= tem espaços, eles são parte do valor separador, vamos tratar
            # Detectar suffix
            after_eq = orig[eq_pos + 1 :]
            # after_eq = "  oldval # comment"
            # encontrar suffix marcadores " #", "\t#", " ;", "\t;"
            suffix = ""
            suffix_idx = -1
            for marker in (" #", "\t#", " ;", "\t;"):
                idx2 = after_eq.find(marker)
                if idx2 != -1:
                    if suffix_idx == -1 or idx2 < suffix_idx:
                        suffix_idx = idx2
            if suffix_idx != -1:
                suffix = after_eq[suffix_idx:]  # inclui espaço + #...
                # normalizar um espaço antes de suffix? já tem
            # reconstruir com um espaço entre = e valor se prefix não termina com espaço?
            # Se orig tem "KEY=oldval", prefix="KEY=", after_eq="oldval..."
            # Queremos "KEY=newval" + suffix
            # Se orig tem "KEY = oldval", prefix="KEY =", after_eq=" oldval..."
            # Então prefix já tem '=' e talvez espaço antes? Vamos usar: prefix_stripped = orig[:eq_pos+1].rstrip()?
            # Mais simples: prefix_key = orig[:eq_pos].strip() ? Mas queremos preservar espaços antes de = e export
            # Estratégia: extrair key_part com regex
            km = re.match(r"^(\s*(?:export\s+)?[A-Za-z_][A-Za-z0-9_]*\s*=\s*)", orig)
            if km:
                prefix_full = km.group(1)
                # prefix_full inclui espaços pós-=
                # vamos manter prefix_full como prefix (ex. "FOO= " ou "export FOO = ")
                # e sufixo já tem espaço
                new_lines[idx] = f"{prefix_full}{new_val}{suffix}"
            else:
                new_lines[idx] = f"{key}={new_val}{suffix}"
        else:
            # chave nova → append no fim, ordem do patch
            # se for piso, já validado, mas ainda append
            appended.append(f"{key}={new_val}")
            # registrar idx para caso patch tenha duplicatas (não há, OrderedDict já deduplicou)
            last_idx[key] = len(new_lines) + len(appended) - 1
    # append novas chaves
    new_lines.extend(appended)
    return new_lines


def make_backup(dest: Path) -> Path:
    ts = datetime.datetime.now().strftime(BAK_FMT)
    base = f"{dest.name}.bak-{ts}"
    bak = dest.parent / base
    n = 0
    while bak.exists():
        n += 1
        bak = dest.parent / f"{base}.{n}"
    shutil.copy2(dest, bak)
    try:
        bak.chmod(0o600)
    except OSError:
        pass
    return bak


def main() -> int:
    parser = argparse.ArgumentParser(description="bootstrap_env append-only (fail-closed)")
    parser.add_argument("--file", required=True, help="dotenv destino concreto (obrigatório)")
    parser.add_argument("--from-file", dest="from_file", help="ficheiro com patch KEY=VALUE")
    args = parser.parse_args()

    # Sem flag --set permitida — argparse já não a define, invocação com --set falha com exit 2

    dest = Path(args.file)
    # Destino deve existir e ser ficheiro regular; não cria do zero; rejeita symlink (fail-closed)
    if dest.is_symlink():
        eprint(f"error: --file não pode ser symlink: {dest}")
        return 1
    if not dest.is_file():
        eprint(f"error: --file destino ausente ou não-regular: {dest}")
        return 1

    # Ler destino (fail se EACCES sem truncar)
    try:
        orig_text = dest.read_text(encoding="utf-8")
    except PermissionError as exc:
        eprint(f"error: sem permissão para ler destino: {dest} ({exc})")
        return 1
    except UnicodeDecodeError as exc:
        eprint(f"error: destino não é utf-8: {dest} ({exc})")
        return 1
    except OSError as exc:
        eprint(f"error: falha ao ler destino: {dest} ({exc})")
        return 1

    dest_lines = orig_text.splitlines()
    has_trailing_nl = orig_text.endswith("\n")

    dest_map = effective_dest_map(dest_lines)
    ok, missing = piso_present(dest_map)
    if not ok:
        eprint(f"error: piso ausente no destino: {missing} (destino inválido, sem escrita)")
        return 1

    # Ler patch de --from-file
    patch_file_map: OrderedDict[str, str] = OrderedDict()
    if args.from_file:
        pf = Path(args.from_file)
        if pf.is_symlink():
            eprint(f"error: --from-file não pode ser symlink: {pf}")
            return 1
        if not pf.is_file():
            eprint(f"error: --from-file não encontrado: {pf}")
            return 1
        try:
            pf_text = pf.read_text(encoding="utf-8")
        except UnicodeDecodeError as exc:
            eprint(f"error: --from-file não é utf-8: {pf} ({exc})")
            return 1
        except OSError as exc:
            eprint(f"error: falha ao ler --from-file: {pf} ({exc})")
            return 1
        patch_file_map = parse_kv_lines(pf_text)

    # Ler stdin se não-TTY
    stdin_map: OrderedDict[str, str] = OrderedDict()
    stdin_has_data = False
    # Se stdin não for tty, lê; se for tty mas pipe pode ter dados, isatty false
    # Em CI, stdin é pipe vazio → read retorna ""
    try:
        if not sys.stdin.isatty():
            stdin_text = sys.stdin.read()
            if stdin_text is not None and stdin_text != "":
                stdin_has_data = True
                stdin_map = parse_kv_lines(stdin_text)
            else:
                # stdin vazio → patch vazio dessa fonte
                stdin_map = OrderedDict()
        else:
            # tty sem pipe → sem dados
            stdin_map = OrderedDict()
    except OSError:
        stdin_map = OrderedDict()

    # Merge patch interno: file → stdin (stdin ganha)
    patch: OrderedDict[str, str] = OrderedDict()
    for k, v in patch_file_map.items():
        patch[k] = v
    for k, v in stdin_map.items():
        patch[k] = v
        patch.move_to_end(k)

    if not patch:
        eprint(
            "error: patch sem nenhuma chave KEY=VALUE (ficheiro vazio/só comentários ou stdin vazio)"
        )
        return 1

    # Validar piso no patch se trouxer valor diferente
    for k in PISO_KEYS:
        if k in patch:
            # comparação após strip
            if patch[k].strip() != dest_map.get(k, "").strip():
                eprint(f"error: piso {k} no patch difere do destino (imutable, sem escrita)")
                return 1

    # Resultado também deve ter piso (defesa)
    # Simular merge para verificar se resultado manteria piso
    # Se patch não tem piso, destino já tem, ok
    # Se patch tem piso igual, ok
    # Já validado acima, então piso permanece

    result_lines = build_result_lines(dest_lines, patch, dest_map)
    # Reconstruir texto resultado
    result_text = "\n".join(result_lines)
    # preservar trailing newline se original tinha, ou se resultado tem linhas
    if has_trailing_nl or result_lines:
        if not result_text.endswith("\n"):
            result_text += "\n"

    # Verificar se resultado ainda tem piso
    result_map = effective_dest_map(result_lines)
    ok2, missing2 = piso_present(result_map)
    if not ok2:
        eprint(f"error: resultado sem piso {missing2} (recusa mv)")
        return 1

    # Idempotência: se igual ao destino, sem bak/mv
    if result_text == orig_text:
        # saída com contagem, sem mutação
        eprint(f"ok: idempotente, nenhuma mudança em {dest} ({len(patch)} chaves no patch)")
        return 0

    # Probe writability antes do backup para cumprir spec EACCES sem bak
    bak: Path | None = None
    probe_path: Path | None = None
    probe_fd = None
    try:
        pfd, pname = tempfile.mkstemp(dir=str(dest.parent), prefix=".probe-bootstrap-")
        probe_fd = pfd
        probe_path = Path(pname)
        os.close(pfd)
        probe_fd = None
        probe_path.unlink()
        probe_path = None
    except (PermissionError, OSError) as exc:
        if probe_fd is not None:
            try:
                os.close(probe_fd)
            except OSError:
                pass
        if probe_path and probe_path.exists():
            try:
                probe_path.unlink()
            except OSError:
                pass
        eprint(f"error: sem permissão para escrever no diretório de {dest} ({exc})")
        return 1

    # Backup timestamped antes de escrever
    try:
        bak = make_backup(dest)
    except PermissionError as exc:
        eprint(f"error: sem permissão para backup {dest} ({exc})")
        return 1
    except OSError as exc:
        eprint(f"error: falha ao criar backup {dest} ({exc})")
        return 1

    # Replace atómico via tmp no mesmo filesystem
    tmp_fd = None
    tmp_path: Path | None = None
    try:
        fd, tmp_name = tempfile.mkstemp(dir=str(dest.parent), prefix=".tmp-bootstrap-")
        tmp_fd = fd
        tmp_path = Path(tmp_name)
        # escrever resultado
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
            f.write(result_text)
            f.flush()
            try:
                os.fsync(f.fileno())
            except OSError:
                pass
        tmp_fd = None  # fd já fechado
        try:
            tmp_path.chmod(0o600)
        except OSError:
            pass
        # recusar se destino antes ou resultado não tiverem piso já validado
        os.replace(str(tmp_path), str(dest))
        tmp_path = None
        try:
            dest.chmod(0o600)
        except OSError:
            pass
    except PermissionError as exc:
        eprint(f"error: sem permissão para escrever destino {dest} ({exc})")
        # limpar tmp se existir
        if tmp_path and tmp_path.exists():
            try:
                tmp_path.unlink()
            except OSError:
                pass
        # EACCES deve ser sem bak (spec); remover bak criado neste run
        if bak and bak.exists():
            try:
                bak.unlink()
            except OSError:
                pass
        return 1
    except OSError as exc:
        eprint(f"error: falha ao escrever destino {dest} ({exc})")
        if tmp_path and tmp_path.exists():
            try:
                tmp_path.unlink()
            except OSError:
                pass
        return 1
    finally:
        if tmp_fd is not None:
            try:
                os.close(tmp_fd)
            except OSError:
                pass

    # Saída só nomes/contagens/paths, nunca valores
    new_keys = [k for k in patch if k not in dest_map]
    updated_keys = [k for k in patch if k in dest_map and patch[k] != dest_map.get(k)]
    eprint(
        f"ok: {len(patch)} chaves no patch, {len(new_keys)} novas, {len(updated_keys)} atualizadas em {dest}"
    )
    if new_keys:
        eprint(f"new: {', '.join(new_keys)}")
    if updated_keys:
        eprint(f"updated: {', '.join(updated_keys)}")
    eprint(f"backup: {bak}")
    eprint(f"dest: {dest}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
