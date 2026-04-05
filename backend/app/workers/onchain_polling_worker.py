# file: backend/app/workers/onchain_polling_worker.py
"""
Onchain polling worker — collects DeFiLlama + GitHub data every 15 min
and persists snapshots + history records to the DB.

Can be invoked manually or scheduled via cron.
"""

from __future__ import annotations

import time
from datetime import datetime

from app.services.onchain_service import (
    TOP_CHAINS,
    compose_onchain_signal,
    save_onchain_signal,
)


# Representative tokens per chain (MVP sample)
CHAIN_TOKENS: dict[str, list[str]] = {
    "ethereum":  ["ETH", "WBTC", "USDC", "USDT", "stETH"],
    "solana":    ["SOL", "mSOL", "USDC", "RAY", "SRM"],
    "arbitrum":  ["ARB", "ETH", "USDC", "USDt", "MIM"],
    "base":      ["ETH", "USDC", "CBETH", "DAI", "AERO"],
    "matic":     ["MATIC", "ETH", "USDC", "WETH", "DAI"],
}


def poll_all_chains() -> dict[str, int]:
    """Run one polling cycle for all chains and tokens.

    Returns dict with counts: tokens_processed, signals_saved.
    """
    tokens_processed = 0
    signals_saved = 0

    for chain in TOP_CHAINS:
        tokens = CHAIN_TOKENS.get(chain, [chain.upper()])
        for token in tokens:
            try:
                result = compose_onchain_signal(token, chain)
                save_onchain_signal(token, chain, result)
                signals_saved += 1
            except Exception as e:
                print(f"[onchain-polling] Error for {token}/{chain}: {e}")
            tokens_processed += 1
            # Brief pause to avoid hammering public APIs
            time.sleep(0.5)

    return {"tokens_processed": tokens_processed, "signals_saved": signals_saved}


def run_as_scheduled(interval_seconds: int = 900) -> None:
    """Run polling loop forever (15-min interval). Call from a process entrypoint."""
    print(f"[onchain-polling] Started — polling every {interval_seconds}s")
    while True:
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[onchain-polling] Cycle at {ts}")
        try:
            result = poll_all_chains()
            print(f"[onchain-polling] Done: {result}")
        except Exception as e:
            print(f"[onchain-polling] Cycle error: {e}")
        time.sleep(interval_seconds)


if __name__ == "__main__":
    # Manual one-shot run
    print("[onchain-polling] One-shot polling run")
    result = poll_all_chains()
    print(f"[onchain-polling] Result: {result}")
