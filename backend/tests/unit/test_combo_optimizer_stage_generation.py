from __future__ import annotations

from app.services.combo_optimizer import ComboOptimizer


def test_correlated_schema_without_step_uses_coarse_step_once(monkeypatch):
    optimizer = ComboOptimizer()
    metadata = {
        "optimization_schema": {
            "parameters": {
                "ema_short": {"min": 3, "max": 20, "default": 18},
                "sma_medium": {"min": 10, "max": 40, "default": 20},
                "sma_long": {"min": 20, "max": 100, "default": 35},
                "stop_loss": {"min": 0.005, "max": 0.13, "default": 0.042},
            },
            "correlated_groups": [["ema_short", "sma_medium", "sma_long", "stop_loss"]],
        }
    }
    monkeypatch.setattr(
        optimizer.combo_service,
        "get_template_metadata",
        lambda _template_name: metadata,
    )
    generated_steps = []
    original_generate = optimizer._generate_range_values

    def record_generate(start, end, step):
        generated_steps.append(step)
        return original_generate(start, end, step)

    monkeypatch.setattr(optimizer, "_generate_range_values", record_generate)

    stages = optimizer.generate_stages(
        template_name="multi_ma_crossoverV2",
        symbol="BTC/USDT",
        fixed_timeframe="1d",
    )

    assert len(stages) == 1
    assert stages[0]["parameter"] == [
        "ema_short",
        "sma_medium",
        "sma_long",
        "stop_loss",
    ]
    assert generated_steps == [4, 4, 4, 0.1]
    assert all(values for values in stages[0]["values"])
