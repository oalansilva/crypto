from __future__ import annotations

from pathlib import Path

from dev_prototype_server import normalize_prototype_path, public_roots, resolve_file


def test_normalize_rejects_app_routes():
    assert normalize_prototype_path("/monitor") is None
    assert normalize_prototype_path("/prototypes/card-637-monitor-buy-with-usdc/") == (
        "/prototypes/card-637-monitor-buy-with-usdc/"
    )


def test_resolve_prefers_worktree_over_missing_source(tmp_path: Path):
    source = tmp_path / "source"
    worktrees = tmp_path / "worktrees"
    slug = "card-999-example"
    html = worktrees / "card-999-example" / "frontend" / "public" / "prototypes" / slug / "index.html"
    html.parent.mkdir(parents=True)
    html.write_text("<html>worktree</html>", encoding="utf-8")
    roots = public_roots(source, worktrees)
    found = resolve_file(f"/prototypes/{slug}/", roots)
    assert found == html.resolve()
    assert resolve_file("/prototypes/does-not-exist/", roots) is None


def test_resolve_blocks_path_escape(tmp_path: Path):
    public = tmp_path / "frontend" / "public"
    (public / "prototypes" / "ok").mkdir(parents=True)
    (public / "prototypes" / "ok" / "index.html").write_text("ok", encoding="utf-8")
    secret = tmp_path / "secret.txt"
    secret.write_text("nope", encoding="utf-8")
    roots = [public.resolve()]
    assert resolve_file("/prototypes/ok/../../secret.txt", roots) is None
