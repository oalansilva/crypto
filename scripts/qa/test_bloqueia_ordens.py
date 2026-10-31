"""Liga `bloqueia-ordens.test.js` ao pytest: um só comando para os testes de `scripts/qa/`."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

PASTA = Path(__file__).resolve().parent


def test_trava_de_ordem_em_node() -> None:
    node = shutil.which("node")
    assert node, "os testes de scripts/qa precisam de node"
    resultado = subprocess.run([node, "--test", str(PASTA / "bloqueia-ordens.test.js")], capture_output=True, text=True, timeout=60, check=False)
    assert resultado.returncode == 0, resultado.stdout + resultado.stderr


def test_prova_cobre_as_rotas_reais_do_backend() -> None:
    raiz = PASTA.parents[1]
    trava = (PASTA / "bloqueia-ordens.js").read_text(encoding="utf-8")
    assert 'prefix="/api/monitor/spot-market-orders"' in (raiz / "backend" / "app" / "routes" / "monitor_spot_market.py").read_text(encoding="utf-8")
    assert '"/spot-stop-order"' in (raiz / "backend" / "app" / "routes" / "monitor_spot_stop.py").read_text(encoding="utf-8")
    assert "/api/monitor/spot-market-orders" in trava and "/api/monitor/spot-stop-order" in trava and "/api/admin/users" in trava
