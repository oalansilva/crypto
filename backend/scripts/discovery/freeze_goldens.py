"""Manifest exact historical14/14 and corrected independent121period-pair oracle."""

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from app.services import combo_optimizer as opt
from app.services.combo_service import ComboService
from tests.fixtures.discovery_memory import semantic_oracle as oracle
from tests.oracles.card_945_legacy import LegacyComboStrategy, extract_trades_with_mode

ROOT = Path(
    "/srv/apps/dev/criptofarol/crypto-worktrees/card-1093-discovery-memory/backend/tests/fixtures/discovery_memory"
)


def digest(value):
    return hashlib.sha256(json.dumps(value, default=str, sort_keys=True).encode()).hexdigest()


def main():
    fixture = json.loads((ROOT / "original_template.json").read_text())
    frame = pd.read_parquet(ROOT / "original_candles.parquet").set_index("timestamp_utc")
    train, holdout = opt.split_train_holdout(frame, 0.7)
    holdout_with_burnin = pd.concat([train.iloc[-250:], holdout])
    metadata = {"name": fixture["name"], **fixture["template_data"]}
    service = object.__new__(ComboService)
    service.get_template_metadata = lambda _: metadata
    golden = {
        "policy": "effective-indicators-v1",
        "cases": {},
        "fixture_sha256": hashlib.sha256(
            (ROOT / "original_template.json").read_bytes()
        ).hexdigest(),
        "candles_sha256": hashlib.sha256(
            (ROOT / "original_candles.parquet").read_bytes()
        ).hexdigest(),
        "oracle_sha256": hashlib.sha256((ROOT / "semantic_oracle.py").read_bytes()).hexdigest(),
        "position_reference_sha256": hashlib.sha256(
            (ROOT / "position_reference.py").read_bytes()
        ).hexdigest(),
        "independent_semantics": "Direct TA-Lib calls and explicit intended series; frozen baseline position loop; unchanged shared execution-cost/Deep/metrics functions also checked against the frozen historical14/14 oracle.",
    }
    for rsi in range(10, 21):
        for adx in range(10, 21):
            parameters = {"rsi_length": rsi, "adx_length": adx, "timeframe": "15m"}
            records = {}
            for role, data in (("train", train), ("holdout_burnin", holdout_with_burnin)):
                metrics, trades, signals = oracle.evaluate(data, parameters, True, frame)
                strategy = service.create_strategy(metadata["name"], parameters)
                actual = strategy.generate_signals(data.copy())
                np.testing.assert_array_equal(actual.signal, signals.signal)
                production_trades = opt.extract_trades_with_mode(
                    actual,
                    strategy.stop_loss,
                    True,
                    "BTC/USDT",
                    "2025-10-06",
                    "2026-10-06",
                    frame,
                    slippage=opt.slippage_for_timeframe("15m"),
                )
                assert production_trades == trades
                intended = oracle.masks(data, parameters)
                records[role] = {
                    "metrics": metrics,
                    "trades_sha256": digest(trades),
                    "entry_sha256": hashlib.sha256(
                        intended["entry"].to_numpy().tobytes()
                    ).hexdigest(),
                    "exit_sha256": hashlib.sha256(
                        intended["exit"].to_numpy().tobytes()
                    ).hexdigest(),
                    "signal_sha256": hashlib.sha256(
                        signals.signal.to_numpy().tobytes()
                    ).hexdigest(),
                }
                if rsi == adx == 14:
                    historical = LegacyComboStrategy(**fixture["template_data"])
                    expected = historical.generate_signals(data.copy())
                    pd.testing.assert_frame_equal(actual, expected, check_exact=True)
                    historical_trades = extract_trades_with_mode(
                        expected,
                        historical.stop_loss,
                        True,
                        "BTC/USDT",
                        "2025-10-06",
                        "2026-10-06",
                        frame,
                        slippage=opt.slippage_for_timeframe("15m"),
                    )
                    assert historical_trades == trades
            golden["cases"][f"{rsi}/{adx}"] = records
    path = ROOT / "semantic_goldens.json"
    path.write_text(json.dumps(golden, default=str, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "period_pairs": len(golden["cases"]),
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "historical_14_14": "exact",
                "train_rows": len(train),
                "holdout_with_burnin_rows": len(holdout_with_burnin),
            },
            indent=2,
        ),
        flush=True,
    )


if __name__ == "__main__":
    main()
