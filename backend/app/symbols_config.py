"""
Carrega a lista de símbolos excluídos a partir do arquivo de configuração.
Usado por: opportunity_service, api (binance symbols), batch_backtest_service.
"""
import json
import logging
from pathlib import Path
from typing import FrozenSet

logger = logging.getLogger(__name__)

# backend/config/excluded_symbols.json
_CONFIG_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = _CONFIG_DIR / "config" / "excluded_symbols.json"

# Fallback se o arquivo não existir (lista mínima conhecida)
_DEFAULT_SYMBOLS = frozenset({
    "1INCHDOWN/USDT", "1INCHUP/USDT",
    "AAVEDOWN/USDT", "AAVEUP/USDT",
    "ADADOWN/USDT", "ADAUP/USDT",
    "AION/USDT",
})


def _load_excluded_symbols() -> FrozenSet[str]:
    """Lê excluded_symbols.json e retorna frozenset em uppercase."""
    if not CONFIG_PATH.exists():
        logger.warning("Config não encontrado: %s — usando lista padrão", CONFIG_PATH)
        return _DEFAULT_SYMBOLS
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        raw = data.get("excluded_symbols", [])
        return frozenset((s or "").strip().upper() for s in raw if (s or "").strip())
    except Exception as e:
        logger.warning("Erro ao ler %s: %s — usando lista padrão", CONFIG_PATH, e)
        return _DEFAULT_SYMBOLS


# Cache da lista (carregada uma vez ao importar o módulo)
_EXCLUDED: FrozenSet[str] = _load_excluded_symbols()


def get_excluded_symbols() -> FrozenSet[str]:
    """Retorna o conjunto de símbolos excluídos (somente leitura)."""
    return _EXCLUDED


def _base_ends_with_up_or_down(symbol: str) -> bool:
    """True se o ativo base termina com UP ou DOWN (ex.: ADAUP/USDT, BNBDOWN/USDT)."""
    s = (symbol or "").strip().upper()
    if not s or "/" not in s:
        return False
    base = s.split("/", 1)[0]
    return base.endswith("DOWN") or base.endswith("UP")


def is_excluded_symbol(symbol: str) -> bool:
    """Retorna True se o símbolo estiver na lista de excluídos ou for *UP/*DOWN."""
    s = (symbol or "").strip().upper()
    if not s:
        return True
    if _base_ends_with_up_or_down(s):
        return True
    return s in _EXCLUDED


def reload_excluded_symbols() -> FrozenSet[str]:
    """Recarrega o arquivo de config (útil em testes ou após editar o JSON)."""
    global _EXCLUDED
    _EXCLUDED = _load_excluded_symbols()
    return _EXCLUDED
