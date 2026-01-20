"""
Reproduction Script: Missing Stop Loss in Legacy Mode

Verifies if stop_loss is skipped in generate_stages when no optimization_schema extends,
but custom_ranges includes it.
"""

import sys
sys.path.append('backend')

import logging
from app.services.combo_optimizer import ComboOptimizer
from unittest.mock import MagicMock

# Configure logging
logging.basicConfig(level=logging.INFO)

def test_legacy_stage_generation_with_stop_loss():
    print("\n" + "=" * 60)
    print("TEST: Legacy Stage Generation (Missing Stop Loss)")
    print("=" * 60)
    
    optimizer = ComboOptimizer()
    
    # Mock template metadata (Legacy style - no optimization_schema)
    template_name = "legacy_template"
    metadata = {
        "name": template_name,
        "indicators": [
            {
                "type": "ema",
                "alias": "ema_short",
                "params": {"length": 10}
            }
        ]
        # No optimization_schema
    }
    
    # Mock combo_service to return our metadata
    optimizer.combo_service.get_template_metadata = MagicMock(return_value=metadata)
    optimizer._validate_correlation_metadata = MagicMock()
    
    # Custom ranges including stop_loss
    custom_ranges = {
        "ema_short_length": {"min": 5, "max": 15, "step": 1},
        "stop_loss": {"min": 0.01, "max": 0.05, "step": 0.01}
    }
    
    print(f"Custom Ranges provided: {list(custom_ranges.keys())}")
    
    # Generate stages
    stages = optimizer.generate_stages(
        template_name=template_name,
        symbol="BTC/USDT",
        custom_ranges=custom_ranges
    )
    
    print(f"\nGenerated {len(stages)} stages:")
    found_stop_loss = False
    
    for stage in stages:
        print(f"  Stage {stage['stage_num']}: {stage['parameter']}")
        if stage['parameter'] == 'stop_loss':
            found_stop_loss = True
            
    if found_stop_loss:
        print("\n✅ PASSED: stop_loss stage generated!")
    else:
        print("\n❌ FAILED: stop_loss stage MISSING in legacy mode")

if __name__ == '__main__':
    test_legacy_stage_generation_with_stop_loss()
