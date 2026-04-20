from typing import Literal

AssetType = Literal["crypto", "stock"]

_CRYPTO_ASSET_TYPES = {"crypto", "cryptomoeda", "criptomoeda"}
_STOCK_ASSET_TYPES = {"stock", "stocks", "acao", "acoes", "equity"}


def normalize_asset_type(asset_type: object | None) -> AssetType | None:
    normalized = str(asset_type or "").strip().lower()
    if normalized in _CRYPTO_ASSET_TYPES:
        return "crypto"
    if normalized in _STOCK_ASSET_TYPES:
        return "stock"
    return None


def classify_asset_type(symbol: str, asset_type: object | None = None) -> AssetType:
    explicit_type = normalize_asset_type(asset_type)
    if explicit_type is not None:
        return explicit_type

    normalized_symbol = str(symbol or "").strip().upper()
    return "crypto" if "/" in normalized_symbol else "stock"
