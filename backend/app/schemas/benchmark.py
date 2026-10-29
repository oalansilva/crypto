"""Contrato ``BenchmarkComparison`` (card #1123, design, decisão 4).

A gravação valida o payload contra este contrato antes de escrever; a leitura devolve o que foi gravado.
``reason.code`` cobre os motivos do resultado (``no_history | no_overlap | short_overlap``) e os da
coluna extra do Decidir (``sample_expired``, ``sample_unavailable`` e ``regeneration_failed``), sempre
sem número.
"""

from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict


class _Open(BaseModel):
    model_config = ConfigDict(extra="allow")


class ReferenceIdentity(_Open):
    kind: Literal["own", "catalog"]
    symbol: str
    asset_id: Optional[str] = None
    asset_class: Optional[str] = None
    currency: Optional[str] = None
    name: Optional[str] = None
    return_kind: Literal["price", "price_no_dividends"]
    long_only: bool = True


class StrategyWindow(_Open):
    start: Optional[str] = None
    end: Optional[str] = None
    state: Optional[str] = None


class StrategyResult(_Open):
    symbol: str
    asset_class: Optional[str] = None
    currency: Optional[str] = None
    window: Optional[StrategyWindow] = None
    direction: Optional[str] = None
    # Sem número quando não há comparação (nunca zero no lugar de "sem comparação").
    return_: Optional[float] = None
    cagr: Optional[float] = None
    trades_in: Optional[int] = None
    trades_out: Optional[int] = None


class Close(_Open):
    date: str
    price: float


class ReferenceResult(_Open):
    return_: Optional[float] = None
    cagr: Optional[float] = None
    first_close: Close
    last_close: Close


class CommonWindow(_Open):
    start: str
    end: str
    days: int


class LeftOut(_Open):
    start: Optional[str] = None
    end: Optional[str] = None
    trades: int = 0
    note: Optional[str] = None


class Delta(_Open):
    cagr_pp: Optional[float] = None


class Reason(_Open):
    code: Literal[
        "no_history",
        "no_overlap",
        "short_overlap",
        "sample_expired",
        "sample_unavailable",
        "regeneration_failed",
    ]
    text: str
    short: Optional[str] = None
    # ``sample_unavailable``: ``metrics_mismatch | missing | unrecorded`` (cripto do caminho antigo).
    detail: Optional[str] = None


class ReferenceSample(_Open):
    snapshot_id: Optional[str] = None
    version_label: Optional[str] = None
    data_version: Optional[int] = None
    content_sha256: Optional[str] = None
    source: Optional[str] = None
    session: Optional[str] = None
    adjustment: Optional[str] = None


class Samples(_Open):
    strategy: Optional[dict] = None
    reference: Optional[ReferenceSample] = None


class Owner(_Open):
    kind: Literal["result", "favorite", "discovery_result"]
    favorite_id: Optional[int] = None
    result_id: Optional[str] = None
    column_id: Optional[str] = None


class BenchmarkComparisonContract(_Open):
    id: str
    created_at: str
    trigger: Literal["run", "choice", "favorite_refresh"]
    owner: Owner
    user_id: Optional[str] = None
    reference: ReferenceIdentity
    strategy: dict
    reference_result: Optional[dict] = None
    common_window: Optional[CommonWindow] = None
    left_out: list[LeftOut] = []
    delta: Optional[Delta] = None
    currency_note: Optional[Literal["usdt_as_usd"]] = None
    status: Literal["valid", "insufficient"]
    reason: Optional[Reason] = None
    samples: Optional[Samples] = None

    @classmethod
    def check(cls, payload: dict) -> "BenchmarkComparisonContract":
        """Valida o contrato e a regra "sem número quando insuficiente"."""

        model = cls.model_validate(payload)
        if model.status == "valid":
            if (
                model.reason is not None
                or model.common_window is None
                or model.reference_result is None
            ):
                raise ValueError(
                    "Comparação válida precisa de período comum e resultado da referência."
                )
            ReferenceResult.model_validate(
                {**model.reference_result, "return_": model.reference_result.get("return")}
            )
        else:
            if model.reason is None:
                raise ValueError("Comparação sem número precisa de motivo.")
            if model.reference_result is not None or (
                model.delta and model.delta.cagr_pp is not None
            ):
                raise ValueError("Comparação insuficiente não leva número.")
            if model.strategy.get("return") is not None or model.strategy.get("cagr") is not None:
                raise ValueError("Comparação insuficiente não leva número da estratégia.")
        return model
