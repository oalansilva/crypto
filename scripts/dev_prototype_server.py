#!/usr/bin/env python3
"""Serve /prototypes/* without SPA fallback.

DEV preview (`npm run preview`) falls through missing prototype paths to the
React index.html, which then logs `No routes matched location "/prototypes/…"`.
This server looks up HTML in source public/dist and in card worktrees, then
returns 404 (not the SPA) when the file is absent.
"""

from __future__ import annotations

import argparse
import mimetypes
import os
import posixpath
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

DEFAULT_SOURCE = Path("/srv/apps/dev/criptofarol/source")
DEFAULT_WORKTREES = Path("/srv/apps/dev/criptofarol/crypto-worktrees")
NOT_FOUND_HTML = """<!DOCTYPE html>
<html lang="pt-BR">
<head><meta charset="utf-8"><title>Protótipo não encontrado</title></head>
<body style="font:16px/1.45 system-ui,sans-serif;max-width:42rem;margin:3rem auto;padding:0 1rem">
  <h1>Protótipo não encontrado</h1>
  <p>Não há <code>index.html</code> para <code>{path}</code> em
  <code>frontend/public/prototypes/</code> do source DEV nem nos worktrees
  <code>crypto-worktrees/*/frontend/public/prototypes/</code>.</p>
  <p>Isto <strong>não</strong> é o app React — o fallback SPA foi bloqueado de propósito.</p>
</body>
</html>
"""


def public_roots(source: Path, worktrees: Path) -> list[Path]:
    roots: list[Path] = []
    for candidate in (
        source / "frontend" / "dist",
        source / "frontend" / "public",
    ):
        if candidate.is_dir():
            roots.append(candidate.resolve())
    if worktrees.is_dir():
        for child in sorted(worktrees.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True):
            public = child / "frontend" / "public"
            if public.is_dir():
                roots.append(public.resolve())
    return roots


def normalize_prototype_path(raw_path: str) -> str | None:
    parsed = urlparse(raw_path)
    path = unquote(parsed.path or "/")
    had_slash = path.endswith("/")
    path = posixpath.normpath(path)
    if path == ".":
        path = "/"
    if not path.startswith("/prototypes"):
        return None
    if path == "/prototypes":
        return "/prototypes/"
    if had_slash and not path.endswith("/"):
        path += "/"
    return path


def resolve_file(url_path: str, roots: list[Path]) -> Path | None:
    relative = url_path.lstrip("/")
    if relative.endswith("/"):
        relative = relative + "index.html"
    elif not Path(relative).suffix:
        relative = relative.rstrip("/") + "/index.html"
    if ".." in Path(relative).parts:
        return None
    for root in roots:
        candidate = (root / relative).resolve()
        try:
            candidate.relative_to(root)
        except ValueError:
            continue
        if candidate.is_file():
            return candidate
    return None


class PrototypeHandler(BaseHTTPRequestHandler):
    roots: list[Path] = []

    def log_message(self, fmt: str, *args: object) -> None:
        sys_stderr = __import__("sys").stderr
        sys_stderr.write("%s - %s\n" % (self.address_string(), fmt % args))

    def do_GET(self) -> None:  # noqa: N802
        normalized = normalize_prototype_path(self.path)
        if normalized is None:
            self._send(404, b"not a prototype path\n", "text/plain; charset=utf-8")
            return
        if normalized == "/prototypes/" and self.path.split("?", 1)[0] in {"/prototypes", "/prototypes/"}:
            listing = "\n".join(str(root) for root in self.roots) + "\n"
            self._send(200, listing.encode("utf-8"), "text/plain; charset=utf-8")
            return
        raw_path = urlparse(self.path).path
        if not raw_path.endswith("/") and not Path(raw_path).suffix:
            loc = raw_path + "/"
            if urlparse(self.path).query:
                loc += "?" + urlparse(self.path).query
            self.send_response(308)
            self.send_header("Location", loc)
            self.end_headers()
            return
        found = resolve_file(normalized, self.roots)
        if found is None:
            body = NOT_FOUND_HTML.format(path=normalized).encode("utf-8")
            self._send(404, body, "text/html; charset=utf-8")
            return
        data = found.read_bytes()
        ctype = mimetypes.guess_type(found.name)[0] or "application/octet-stream"
        if found.suffix in {".html", ".htm"}:
            ctype = "text/html; charset=utf-8"
        self._send(200, data, ctype)

    def do_HEAD(self) -> None:  # noqa: N802
        self.do_GET()

    def _send(self, status: int, body: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="dev-prototype-server")
    parser.add_argument("--host", default=os.environ.get("HOST", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(os.environ.get("PORT", "5176")))
    parser.add_argument("--source", type=Path, default=Path(os.environ.get("CRYPTOFAROL_SOURCE", str(DEFAULT_SOURCE))))
    parser.add_argument(
        "--worktrees",
        type=Path,
        default=Path(os.environ.get("CRYPTOFAROL_WORKTREES", str(DEFAULT_WORKTREES))),
    )
    args = parser.parse_args(argv)
    PrototypeHandler.roots = public_roots(args.source, args.worktrees)
    server = ThreadingHTTPServer((args.host, args.port), PrototypeHandler)
    print(
        f"dev-prototype-server http://{args.host}:{args.port}/prototypes/ roots={len(PrototypeHandler.roots)}",
        flush=True,
    )
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        return 0
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
