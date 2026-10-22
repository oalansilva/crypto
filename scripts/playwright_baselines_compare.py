#!/usr/bin/env python3
"""Before/after comparison of Playwright visual baselines (card #1133, design D3/D4).

Called by ``.github/workflows/playwright-baselines.yml`` after
``playwright test --update-snapshots=all`` regenerated the PNGs in the checkout.

Inputs
  --before DIR     copy of the committed PNGs, keyed by repo-relative path
  --repo-root DIR  checkout whose ``frontend/tests/e2e/*-snapshots/`` now holds the new PNGs
  --out DIR        artifact root to create

Outputs under --out
  snapshots/<repo path>.png          the new PNGs, at their repository path
  comparacao/index.html              static page, one block per image, most different first
  comparacao/manifest.json           same fields as the page, plus the baseline set digest
  comparacao/img/{before,after,mask}/<repo path>.png

The differing-pixel ratio uses the pixelmatch YIQ colour delta with threshold 0.2
(what ``toHaveScreenshot`` uses) but without anti-alias detection, so it is an
upper-bound indicator. The real gate remains ``e2e-playwright`` with
``maxDiffPixelRatio: 0.001``.

Requires Pillow and numpy.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import shutil
import sys
from pathlib import Path

import numpy as np
from PIL import Image

SNAPSHOT_GLOB = "frontend/tests/e2e/*-snapshots"
YIQ_THRESHOLD = 0.2
YIQ_MAX_DELTA = 35215 * YIQ_THRESHOLD * YIQ_THRESHOLD


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def list_pngs(root: Path) -> dict[str, Path]:
    """Repo-relative POSIX path -> file, for every PNG under ``*-snapshots`` dirs."""
    found: dict[str, Path] = {}
    for snap_dir in sorted(root.glob(SNAPSHOT_GLOB)):
        if not snap_dir.is_dir():
            continue
        for png in sorted(snap_dir.rglob("*.png")):
            found[png.relative_to(root).as_posix()] = png
    return found


def baseline_set_digest(hashes: dict[str, str]) -> str:
    """Same value as ``git ls-files -z ... | LC_ALL=C sort -z | xargs -0 sha256sum | sha256sum``."""
    lines = "".join(
        f"{hashes[path]}  {path}\n" for path in sorted(hashes, key=lambda p: p.encode())
    )
    return hashlib.sha256(lines.encode()).hexdigest()


def _rgba_over_white(image: Image.Image) -> np.ndarray:
    rgba = np.asarray(image.convert("RGBA"), dtype=np.float64)
    alpha = rgba[..., 3:4] / 255.0
    return rgba[..., :3] * alpha + 255.0 * (1.0 - alpha)


def _yiq_delta(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    def yiq(rgb: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        r, g, bl = rgb[..., 0], rgb[..., 1], rgb[..., 2]
        return (
            r * 0.29889531 + g * 0.58662247 + bl * 0.11448223,
            r * 0.59597799 - g * 0.27417610 - bl * 0.32180189,
            r * 0.21147017 - g * 0.52261711 + bl * 0.31114694,
        )

    ya, ia, qa = yiq(a)
    yb, ib, qb = yiq(b)
    dy, di, dq = ya - yb, ia - ib, qa - qb
    return 0.5053 * dy * dy + 0.299 * di * di + 0.1957 * dq * dq


def compare_images(before: Image.Image, after: Image.Image) -> dict:
    """Pixel comparison; returns counts and (if sizes match) a mask image."""
    if before.size != after.size:
        return {
            "same_dimensions": False,
            "diff_pixels": None,
            "diff_ratio": 1.0,
            "changed_pixels": None,
            "mask": None,
        }
    a, b = _rgba_over_white(before), _rgba_over_white(after)
    delta = _yiq_delta(a, b)
    differing = delta > YIQ_MAX_DELTA
    changed = np.any(a != b, axis=-1)
    total = differing.size
    # Mask: dimmed "after" with differing pixels in red.
    base = (b * 0.35 + 255 * 0.65).astype(np.uint8)
    base[changed] = (b[changed] * 0.5 + 128).astype(np.uint8)
    base[differing] = (255, 0, 0)
    return {
        "same_dimensions": True,
        "diff_pixels": int(differing.sum()),
        "diff_ratio": float(differing.sum()) / total,
        "changed_pixels": int(changed.sum()),
        "mask": Image.fromarray(base, "RGB"),
    }


def _copy(src: Path, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dest)


def build_entries(before_root: Path, repo_root: Path, out: Path) -> list[dict]:
    before_files = list_pngs(before_root)
    after_files = list_pngs(repo_root)
    img_root = out / "comparacao" / "img"
    entries: list[dict] = []

    for path in sorted(set(before_files) | set(after_files)):
        before_file, after_file = before_files.get(path), after_files.get(path)
        entry: dict = {
            "path": path,
            "before_sha256": sha256_file(before_file) if before_file else None,
            "after_sha256": sha256_file(after_file) if after_file else None,
            "before_size": None,
            "after_size": None,
            "diff_pixels": None,
            "diff_ratio": 0.0,
            "changed_pixels": 0,
            "img_before": None,
            "img_after": None,
            "img_mask": None,
        }
        before_img = after_img = None
        if before_file:
            before_img = Image.open(before_file)
            entry["before_size"] = list(before_img.size)
            _copy(before_file, img_root / "before" / path)
            entry["img_before"] = f"img/before/{path}"
        if after_file:
            after_img = Image.open(after_file)
            entry["after_size"] = list(after_img.size)
            _copy(after_file, out / "snapshots" / path)
            _copy(after_file, img_root / "after" / path)
            entry["img_after"] = f"img/after/{path}"

        if before_img is None:
            entry["status"] = "new"
            entry["diff_ratio"] = 1.0
        elif after_img is None:
            entry["status"] = "removed"
            entry["diff_ratio"] = 1.0
        elif entry["before_sha256"] == entry["after_sha256"]:
            entry["status"] = "identical"
            entry["diff_pixels"] = 0
        else:
            result = compare_images(before_img, after_img)
            entry["diff_pixels"] = result["diff_pixels"]
            entry["diff_ratio"] = result["diff_ratio"]
            entry["changed_pixels"] = result["changed_pixels"]
            entry["status"] = "changed" if result["same_dimensions"] else "resized"
            if result["mask"] is not None:
                mask_path = img_root / "mask" / path
                mask_path.parent.mkdir(parents=True, exist_ok=True)
                result["mask"].save(mask_path)
                entry["img_mask"] = f"img/mask/{path}"
        entries.append(entry)

    entries.sort(key=lambda e: (-e["diff_ratio"], -(e["changed_pixels"] or 0), e["path"]))
    return entries


def render_html(entries: list[dict], digest: str, summary: dict) -> str:
    def cell(title: str, src: str | None) -> str:
        if not src:
            return f"<figure><figcaption>{title}</figcaption><p>n/a</p></figure>"
        return (
            f"<figure><figcaption>{title}</figcaption>"
            f'<a href="{html.escape(src)}"><img loading="lazy" src="{html.escape(src)}" alt="{title}"></a></figure>'
        )

    blocks = []
    for e in entries:
        ratio = (
            "n/a"
            if e["diff_pixels"] is None and e["status"] in ("new", "removed")
            else f"{e['diff_ratio'] * 100:.4f}%"
        )
        blocks.append(f"""<section class="{html.escape(e['status'])}">
<h2>{html.escape(e['path'])} <span class="tag">{html.escape(e['status'])}</span></h2>
<p>Pixels diferentes: <b>{ratio}</b>
 ({e['diff_pixels'] if e['diff_pixels'] is not None else 'n/a'} px) &middot;
 dimensoes antes {e['before_size']} depois {e['after_size']}</p>
<p class="sha">antes <code>{e['before_sha256']}</code><br>depois <code>{e['after_sha256']}</code></p>
<div class="row">{cell('antes', e['img_before'])}{cell('depois', e['img_after'])}{cell('mascara', e['img_mask'])}</div>
</section>""")
    return f"""<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Comparacao de baselines Playwright</title>
<style>
body{{font:14px/1.4 system-ui,sans-serif;margin:16px;background:#111;color:#eee}}
section{{border:1px solid #333;border-radius:8px;padding:12px;margin:0 0 16px}}
section.identical{{opacity:.6}}
h2{{font-size:15px;margin:0 0 6px;word-break:break-all}}
.tag{{font-size:12px;background:#333;border-radius:4px;padding:1px 6px;margin-left:6px}}
.row{{display:flex;gap:12px;flex-wrap:wrap}}
figure{{margin:0;flex:1 1 280px;min-width:0}}
figcaption{{color:#aaa;margin-bottom:4px}}
img{{max-width:100%;height:auto;background:#fff;border:1px solid #444}}
.sha code{{font-size:12px;word-break:break-all}}
</style></head><body>
<h1>Comparacao de baselines Playwright</h1>
<p>Total: {summary['total']} &middot; alteradas: {summary['changed']} &middot; identicas: {summary['identical']}
 &middot; novas: {summary['new']} &middot; removidas: {summary['removed']}</p>
<p>Conjunto (SHA-256 da lista SHA-256 + caminho): <code>{digest}</code></p>
<p>Ordenado da maior diferenca para a menor. A fracao usa delta YIQ 0.2 sem deteccao de antialias: e indicador, o gate e o e2e-playwright (maxDiffPixelRatio 0.001). Esta pagina nao aprova nada.</p>
{''.join(blocks)}
</body></html>
"""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--before", required=True, type=Path)
    parser.add_argument("--repo-root", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args(argv)

    if args.out.exists():
        shutil.rmtree(args.out)
    (args.out / "comparacao").mkdir(parents=True)
    (args.out / "snapshots").mkdir(parents=True)

    entries = build_entries(args.before, args.repo_root, args.out)
    after_hashes = {e["path"]: e["after_sha256"] for e in entries if e["after_sha256"]}
    digest = baseline_set_digest(after_hashes)
    summary = {
        "total": len(entries),
        "changed": sum(e["status"] in ("changed", "resized") for e in entries),
        "identical": sum(e["status"] == "identical" for e in entries),
        "new": sum(e["status"] == "new" for e in entries),
        "removed": sum(e["status"] == "removed" for e in entries),
    }
    manifest = {"schema_version": 1, "set_digest": digest, "summary": summary, "images": entries}
    (args.out / "comparacao" / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    (args.out / "comparacao" / "index.html").write_text(
        render_html(entries, digest, summary), encoding="utf-8"
    )

    print(f"baselines: {summary}")
    print(f"set digest: {digest}")
    for e in entries:
        print(f"{e['diff_ratio'] * 100:9.4f}%  {e['status']:9}  {e['path']}")
    if summary["new"] or summary["removed"]:
        print("::warning::baselines added or removed; review manifest.json", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
