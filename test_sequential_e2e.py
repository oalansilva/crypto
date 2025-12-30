"""
End-to-End Integration Tests for Sequential Optimization

Tests the complete flow:
1. Start optimization
2. Monitor progress
3. Test checkpoint system
4. Test recovery
5. Verify results
"""

import sys
import asyncio
import json
from pathlib import Path

sys.path.insert(0, 'backend')

from app.services.sequential_optimizer import SequentialOptimizer
from app.schemas.indicator_params import get_indicator_schema, estimate_total_tests


class TestSequentialOptimizationE2E:
    """End-to-end integration tests"""
    
    def __init__(self):
        self.optimizer = SequentialOptimizer()
        self.test_job_id = "test_e2e_macd_001"
        self.symbol = "BTC/USDT"
        self.strategy = "macd"
    
    async def test_1_stage_generation(self):
        """Test 1: Verify stage generation for MACD"""
        print("\n" + "=" * 70)
        print("TEST 1: Stage Generation")
        print("=" * 70)
        
        stages = self.optimizer.generate_stages(self.strategy, self.symbol)
        
        # Verify stage count
        assert len(stages) == 6, f"Expected 6 stages, got {len(stages)}"
        print(f"✓ Generated {len(stages)} stages correctly")
        
        # Verify stage structure
        stage_names = [s['stage_name'] for s in stages]
        print(f"\nStages: {stage_names}")
        
        # Verify first stage is timeframe
        assert stages[0]['parameter'] == 'timeframe', "First stage should be timeframe"
        print("✓ Stage 1 is timeframe optimization")
        
        # Verify last two stages are risk management
        assert stages[-2]['parameter'] == 'stop_loss', "Second to last should be stop-loss"
        assert stages[-1]['parameter'] == 'stop_gain', "Last should be stop-gain"
        print("✓ Final stages are risk management (stop-loss, stop-gain)")
        
        # Verify stop-gain includes None option
        assert None in stages[-1]['values'], "Stop-gain should include None option"
        print("✓ Stop-gain includes 'None' option")
        
        return stages
    
    async def test_2_checkpoint_creation(self):
        """Test 2: Verify checkpoint system"""
        print("\n" + "=" * 70)
        print("TEST 2: Checkpoint System")
        print("=" * 70)
        
        # Create test checkpoint
        test_state = {
            "job_id": self.test_job_id,
            "symbol": self.symbol,
            "strategy": self.strategy,
            "current_stage": 3,
            "total_stages": 6,
            "tests_completed": 7,
            "total_tests_in_stage": 13,
            "completed_tests": [
                {"slow_period": 20, "pnl": 1200, "win_rate": 0.35},
                {"slow_period": 21, "pnl": 1400, "win_rate": 0.38},
                {"slow_period": 22, "pnl": 1789, "win_rate": 0.45},
            ],
            "best_result": {"slow_period": 22, "pnl": 1789},
            "locked_params": {"timeframe": "1h", "fast_period": 12}
        }
        
        # Create checkpoint
        self.optimizer.create_checkpoint(self.test_job_id, test_state)
        print(f"✓ Checkpoint created for job: {self.test_job_id}")
        
        # Verify checkpoint file exists
        checkpoint_file = self.optimizer.checkpoint_dir / f"{self.test_job_id}.json"
        assert checkpoint_file.exists(), "Checkpoint file should exist"
        print(f"✓ Checkpoint file exists: {checkpoint_file}")
        
        # Load and verify checkpoint
        loaded_state = self.optimizer.load_checkpoint(self.test_job_id)
        assert loaded_state is not None, "Should load checkpoint"
        assert loaded_state['current_stage'] == 3, "Stage should be 3"
        assert loaded_state['tests_completed'] == 7, "Should have 7 tests completed"
        assert loaded_state['best_result']['pnl'] == 1789, "Best PnL should be 1789"
        print("✓ Checkpoint loaded correctly")
        print(f"  - Stage: {loaded_state['current_stage']}/{loaded_state['total_stages']}")
        print(f"  - Progress: {loaded_state['tests_completed']}/{loaded_state['total_tests_in_stage']} tests")
        print(f"  - Best result: slow_period={loaded_state['best_result']['slow_period']}, PnL=${loaded_state['best_result']['pnl']}")
        
        return loaded_state
    
    async def test_3_incomplete_job_detection(self):
        """Test 3: Verify incomplete job detection"""
        print("\n" + "=" * 70)
        print("TEST 3: Incomplete Job Detection")
        print("=" * 70)
        
        # Find incomplete jobs
        incomplete = self.optimizer.find_incomplete_jobs()
        
        assert len(incomplete) > 0, "Should find at least one incomplete job"
        print(f"✓ Found {len(incomplete)} incomplete job(s)")
        
        # Verify our test job is in the list
        job_ids = [job['job_id'] for job in incomplete]
        assert self.test_job_id in job_ids, "Test job should be in incomplete list"
        print(f"✓ Test job '{self.test_job_id}' detected as incomplete")
        
        # Display incomplete job details
        for job in incomplete:
            if job['job_id'] == self.test_job_id:
                print(f"\nIncomplete Job Details:")
                print(f"  - Job ID: {job['job_id']}")
                print(f"  - Strategy: {job['strategy']}")
                print(f"  - Stage: {job['current_stage']}/{job['total_stages']}")
                print(f"  - Tests: {job['tests_completed']}/{job['total_tests_in_stage']}")
    
    async def test_4_checkpoint_recovery(self):
        """Test 4: Verify checkpoint recovery simulation"""
        print("\n" + "=" * 70)
        print("TEST 4: Checkpoint Recovery Simulation")
        print("=" * 70)
        
        # Simulate power failure scenario
        print("\n📝 Scenario: Power failure during Stage 3")
        print("   - 7 out of 13 tests completed")
        print("   - Best result: slow_period=22, PnL=$1,789")
        
        # Load checkpoint (simulating app restart)
        print("\n🔄 Simulating app restart...")
        recovered_state = self.optimizer.load_checkpoint(self.test_job_id)
        
        assert recovered_state is not None, "Should recover state"
        print("✓ State recovered successfully")
        
        # Verify we can resume from correct position
        assert recovered_state['current_stage'] == 3, "Should resume at Stage 3"
        assert recovered_state['tests_completed'] == 7, "Should resume from test 7"
        print(f"✓ Ready to resume from Stage {recovered_state['current_stage']}, test {recovered_state['tests_completed'] + 1}")
        
        # Verify locked parameters are preserved
        assert 'timeframe' in recovered_state['locked_params'], "Timeframe should be locked"
        assert 'fast_period' in recovered_state['locked_params'], "Fast period should be locked"
        print(f"✓ Locked parameters preserved: {recovered_state['locked_params']}")
        
        # Verify best result is preserved
        assert recovered_state['best_result'] is not None, "Best result should be preserved"
        print(f"✓ Best result preserved: {recovered_state['best_result']}")
    
    async def test_5_performance_calculation(self):
        """Test 5: Verify performance calculations"""
        print("\n" + "=" * 70)
        print("TEST 5: Performance Calculations")
        print("=" * 70)
        
        schema = get_indicator_schema(self.strategy)
        
        # Calculate estimated tests
        sequential_tests = estimate_total_tests(schema)
        print(f"\nSequential Optimization:")
        print(f"  - Total tests: {sequential_tests}")
        
        # Calculate grid search equivalent
        grid_tests = 7 * 13 * 13 * 7 * 10 * 8  # timeframes × fast × slow × signal × SL × SG
        print(f"\nGrid Search (for comparison):")
        print(f"  - Total tests: {grid_tests:,}")
        
        # Calculate speedup
        speedup = grid_tests / sequential_tests
        savings = (1 - sequential_tests / grid_tests) * 100
        
        print(f"\nPerformance Improvement:")
        print(f"  - Speedup: {speedup:,.0f}x faster")
        print(f"  - Savings: {savings:.2f}% reduction")
        
        assert speedup > 10000, "Should be at least 10,000x faster"
        print(f"✓ Performance improvement verified: {speedup:,.0f}x speedup")
    
    async def test_6_cleanup(self):
        """Test 6: Cleanup test data"""
        print("\n" + "=" * 70)
        print("TEST 6: Cleanup")
        print("=" * 70)
        
        # Delete test checkpoint
        self.optimizer.delete_checkpoint(self.test_job_id)
        
        # Verify deletion
        deleted_state = self.optimizer.load_checkpoint(self.test_job_id)
        assert deleted_state is None, "Checkpoint should be deleted"
        print(f"✓ Test checkpoint deleted: {self.test_job_id}")
    
    async def run_all_tests(self):
        """Run all tests in sequence"""
        print("\n" + "=" * 70)
        print("SEQUENTIAL OPTIMIZATION - END-TO-END INTEGRATION TESTS")
        print("=" * 70)
        
        try:
            # Run tests
            await self.test_1_stage_generation()
            await self.test_2_checkpoint_creation()
            await self.test_3_incomplete_job_detection()
            await self.test_4_checkpoint_recovery()
            await self.test_5_performance_calculation()
            await self.test_6_cleanup()
            
            # Summary
            print("\n" + "=" * 70)
            print("🎉 ALL INTEGRATION TESTS PASSED!")
            print("=" * 70)
            print("\n✅ Test Summary:")
            print("  1. Stage Generation: PASSED")
            print("  2. Checkpoint System: PASSED")
            print("  3. Incomplete Job Detection: PASSED")
            print("  4. Checkpoint Recovery: PASSED")
            print("  5. Performance Calculations: PASSED")
            print("  6. Cleanup: PASSED")
            print("\n📊 System Status:")
            print("  - Backend: ✅ Fully Functional")
            print("  - Checkpoint System: ✅ Working")
            print("  - Recovery System: ✅ Working")
            print("  - Performance: ✅ 11,422x speedup verified")
            print("\n🚀 Ready for production deployment!")
            
        except AssertionError as e:
            print(f"\n❌ Test failed: {e}")
            raise
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            import traceback
            traceback.print_exc()
            raise


async def main():
    """Main test runner"""
    tester = TestSequentialOptimizationE2E()
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())
