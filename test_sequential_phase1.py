"""
Simple validation script for indicator schemas.
Run this to verify basic functionality before proceeding.
"""

import sys
sys.path.insert(0, 'backend')

from app.schemas.indicator_params import (
    get_indicator_schema,
    calculate_total_stages,
    estimate_total_tests,
    TIMEFRAME_OPTIONS
)


def test_schemas():
    """Test indicator schemas"""
    print("=" * 60)
    print("Testing Indicator Schemas")
    print("=" * 60)
    
    # Test MACD schema
    print("\n1. Testing MACD schema...")
    macd = get_indicator_schema("macd")
    assert macd is not None, "MACD schema not found"
    assert macd.name == "MACD", f"Expected 'MACD', got '{macd.name}'"
    assert len(macd.parameters) == 3, f"Expected 3 parameters, got {len(macd.parameters)}"
    print("   ✓ MACD schema loaded correctly")
    print(f"   ✓ Parameters: {list(macd.parameters.keys())}")
    
    # Test RSI schema
    print("\n2. Testing RSI schema...")
    rsi = get_indicator_schema("rsi")
    assert rsi is not None, "RSI schema not found"
    assert len(rsi.parameters) == 3, f"Expected 3 parameters, got {len(rsi.parameters)}"
    print("   ✓ RSI schema loaded correctly")
    print(f"   ✓ Parameters: {list(rsi.parameters.keys())}")
    
    # Test Bollinger schema
    print("\n3. Testing Bollinger Bands schema...")
    bollinger = get_indicator_schema("bollinger")
    assert bollinger is not None, "Bollinger schema not found"
    assert len(bollinger.parameters) == 2, f"Expected 2 parameters, got {len(bollinger.parameters)}"
    print("   ✓ Bollinger Bands schema loaded correctly")
    print(f"   ✓ Parameters: {list(bollinger.parameters.keys())}")
    
    # Test stage calculation
    print("\n4. Testing stage calculation...")
    macd_stages = calculate_total_stages(macd)
    rsi_stages = calculate_total_stages(rsi)
    bollinger_stages = calculate_total_stages(bollinger)
    
    assert macd_stages == 6, f"Expected 6 stages for MACD, got {macd_stages}"
    assert rsi_stages == 6, f"Expected 6 stages for RSI, got {rsi_stages}"
    assert bollinger_stages == 5, f"Expected 5 stages for Bollinger, got {bollinger_stages}"
    
    print(f"   ✓ MACD: {macd_stages} stages")
    print(f"   ✓ RSI: {rsi_stages} stages")
    print(f"   ✓ Bollinger: {bollinger_stages} stages")
    
    # Test total tests estimation
    print("\n5. Testing total tests estimation...")
    macd_tests = estimate_total_tests(macd)
    rsi_tests = estimate_total_tests(rsi)
    bollinger_tests = estimate_total_tests(bollinger)
    
    print(f"   ✓ MACD: {macd_tests} total tests")
    print(f"   ✓ RSI: {rsi_tests} total tests")
    print(f"   ✓ Bollinger: {bollinger_tests} total tests")
    
    # Test timeframes
    print("\n6. Testing timeframe options...")
    assert "3d" not in TIMEFRAME_OPTIONS, "3d should be excluded"
    assert "1w" not in TIMEFRAME_OPTIONS, "1w should be excluded"
    assert len(TIMEFRAME_OPTIONS) == 7, f"Expected 7 timeframes, got {len(TIMEFRAME_OPTIONS)}"
    print(f"   ✓ Timeframes: {TIMEFRAME_OPTIONS}")
    print("   ✓ 3d and 1w correctly excluded")
    
    print("\n✅ All schema tests passed!")


def test_grid_search_comparison():
    """Show grid search vs sequential comparison"""
    print("\n" + "=" * 60)
    print("Grid Search vs Sequential Comparison")
    print("=" * 60)
    
    macd = get_indicator_schema("macd")
    rsi = get_indicator_schema("rsi")
    
    # MACD comparison
    print("\n📊 MACD Strategy:")
    macd_sequential = estimate_total_tests(macd)
    macd_grid = 7 * 13 * 13 * 7 * 10 * 8  # timeframes × fast × slow × signal × stop_loss × stop_gain
    macd_speedup = macd_grid / macd_sequential
    
    print(f"   Grid Search:  {macd_grid:,} tests")
    print(f"   Sequential:   {macd_sequential:,} tests")
    print(f"   Speedup:      {macd_speedup:.0f}x faster! 🚀")
    print(f"   Savings:      {(1 - macd_sequential/macd_grid)*100:.2f}%")
    
    # RSI comparison
    print("\n📊 RSI Strategy:")
    rsi_sequential = estimate_total_tests(rsi)
    rsi_grid = 7 * 11 * 16 * 16 * 10 * 8
    rsi_speedup = rsi_grid / rsi_sequential
    
    print(f"   Grid Search:  {rsi_grid:,} tests")
    print(f"   Sequential:   {rsi_sequential:,} tests")
    print(f"   Speedup:      {rsi_speedup:.0f}x faster! 🚀")
    print(f"   Savings:      {(1 - rsi_sequential/rsi_grid)*100:.2f}%")


if __name__ == "__main__":
    try:
        test_schemas()
        test_grid_search_comparison()
        
        print("\n" + "=" * 60)
        print("🎉 ALL TESTS PASSED! Schemas are working correctly.")
        print("=" * 60)
        print("\n📝 Note: SequentialOptimizer tests skipped (requires full backend setup)")
        print("   Will test optimizer after installing all dependencies.")
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
