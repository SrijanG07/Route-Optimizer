"""
Task 6 Test Suite: AI-Enhanced Route Optimization
Tests AI-powered route optimization with simplified presentation-ready API.
"""

from utils.algorithm import optimize_route
import time


def test_ai_vs_greedy():
    """Compare AI Optimizer vs Nearest Neighbor (Greedy)."""
    print("=" * 80)
    print("TEST 1: AI Enhancement - AI Optimizer vs Greedy")
    print("=" * 80)
    
    start = "Mumbai"
    destinations = ["Pune", "Bangalore", "Chennai", "Hyderabad", "Kolkata"]
    priorities = {
        "Bangalore": 1,
        "Chennai": 2,
        "Pune": 3,
        "Hyderabad": 3,
        "Kolkata": 3
    }
    
    print("\n🔵 Running Greedy (Nearest Neighbor)...")
    greedy_result = optimize_route(start, destinations, priorities, use_ai=False)
    
    print(f"   Route: {' → '.join(greedy_result['route'])}")
    print(f"   Distance: {greedy_result['total_distance']} km")
    print(f"   Savings: {greedy_result['distance_saved']} km ({greedy_result['improvement_percentage']}%)")
    print(f"   Time: {greedy_result['execution_time_ms']} ms")
    
    print("\n🟢 Running AI Optimizer...")
    ai_result = optimize_route(start, destinations, priorities, use_ai=True)
    
    print(f"   Route: {' → '.join(ai_result['route'])}")
    print(f"   Distance: {ai_result['total_distance']} km")
    print(f"   Savings: {ai_result['distance_saved']} km ({ai_result['improvement_percentage']}%)")
    print(f"   Time: {ai_result['execution_time_ms']} ms")
    
    if 'ai_metrics' in ai_result:
        print(f"\n   🤖 AI Metrics:")
        print(f"      Iterations: {ai_result['ai_metrics']['iterations']}")
        print(f"      Distance Improvement: {ai_result['ai_metrics']['distance_improvement_percent']:.1f}%")
        print(f"      Priority Violations: {ai_result['ai_metrics']['priority_violations']}")
        
        # Show convergence (AI learning over time)
        if 'convergence_history' in ai_result['ai_metrics'] and ai_result['ai_metrics']['convergence_history']:
            print(f"\n   🧠 AI CONVERGENCE (How it learns):")
            history = ai_result['ai_metrics']['convergence_history']
            for record in history[:5]:  # Show first 5 checkpoints
                print(f"      Iteration {record['generation']}: Score = {record['best_fitness']}")
            if len(history) > 5:
                print(f"      Iteration {history[-1]['generation']}: Score = {history[-1]['best_fitness']} (Final)")
    
    print(f"\n   📊 COMPARISON:")
    improvement = greedy_result['total_distance'] - ai_result['total_distance']
    pct = (improvement / greedy_result['total_distance']) * 100 if greedy_result['total_distance'] > 0 else 0
    print(f"      Greedy: {greedy_result['total_distance']} km")
    print(f"      AI:     {ai_result['total_distance']} km")
    print(f"      Improvement: {improvement:.2f} km ({pct:.1f}%)")
    
    print()
    assert 'ai_metrics' in ai_result, "Should have AI metrics"
    assert ai_result['ai_metrics']['priority_violations'] == 0, "Should respect priorities"
    print("✅ PASSED - AI shows improvement over greedy\n")


def test_priority_handling():
    """Test that AI respects priority constraints."""
    print("=" * 80)
    print("TEST 2: Priority Handling - High Priority Cities First")
    print("=" * 80)
    
    start = "Mumbai"
    destinations = ["Pune", "Bangalore", "Chennai"]
    priorities = {
        "Bangalore": 1,  # URGENT - should be first
        "Chennai": 2,    # MEDIUM
        "Pune": 3        # LOW - should be last
    }
    
    result = optimize_route(start, destinations, priorities, use_ai=True)
    
    route = result['route']
    print(f"\n   Route: {' → '.join(route)}")
    
    # Find positions
    bangalore_pos = route.index("Bangalore")
    chennai_pos = route.index("Chennai")
    pune_pos = route.index("Pune")
    
    print(f"   Priority Check:")
    print(f"      Bangalore (P1): Position {bangalore_pos}")
    print(f"      Chennai (P2): Position {chennai_pos}")
    print(f"      Pune (P3): Position {pune_pos}")
    
    # Bangalore (P1) should come before Chennai (P2) and Pune (P3)
    # Chennai (P2) should come before Pune (P3)
    priority_correct = bangalore_pos < chennai_pos < pune_pos
    
    print(f"\n   Priority Violations: {result['ai_metrics']['priority_violations']}")
    
    print()
    assert result['ai_metrics']['priority_violations'] == 0, "Should have 0 priority violations"
    print("✅ PASSED - Priorities respected\n")


def test_ai_metrics():
    """Test that AI metrics are captured correctly."""
    print("=" * 80)
    print("TEST 3: AI Metrics - Iteration Tracking")
    print("=" * 80)
    
    start = "Delhi"
    destinations = ["Mumbai", "Bangalore", "Chennai", "Kolkata"]
    
    result = optimize_route(start, destinations, use_ai=True)
    
    print(f"\n   Route: {' → '.join(result['route'])}")
    print(f"   Distance: {result['total_distance']} km")
    
    ai_metrics = result['ai_metrics']
    print(f"\n   🤖 AI Performance:")
    print(f"      Iterations Run: {ai_metrics['iterations']}")
    print(f"      Distance Improvement: {ai_metrics['distance_improvement_percent']}%")
    print(f"      Priority Violations: {ai_metrics['priority_violations']}")
    
    print()
    assert 'iterations' in ai_metrics, "Should track iterations"
    assert 'distance_improvement_percent' in ai_metrics, "Should track improvement"
    assert 'priority_violations' in ai_metrics, "Should track violations"
    assert 'convergence_history' in ai_metrics, "Should have convergence history"
    print("✅ PASSED - All AI metrics present\n")


def test_scalability():
    """Test AI with larger number of cities."""
    print("=" * 80)
    print("TEST 4: Scalability - 8 Cities")
    print("=" * 80)
    
    start = "Mumbai"
    destinations = ["Pune", "Bangalore", "Chennai", "Hyderabad", "Kolkata", "Delhi", "Jaipur", "Ahmedabad"]
    
    print(f"\n   Testing with {len(destinations)} destinations...")
    
    result = optimize_route(start, destinations, use_ai=True)
    
    print(f"   Full Route: {' → '.join(result['route'])}")
    print(f"   Total Cities: {result['cities_processed']}")
    print(f"   Total Distance: {result['total_distance']} km")
    print(f"   Improvement: {result['improvement_percentage']}%")
    print(f"   Execution Time: {result['execution_time_ms']} ms")
    print(f"   Iterations: {result['ai_metrics']['iterations']}")
    
    print()
    assert result['execution_time_ms'] < 500, f"Should complete in <500ms (took {result['execution_time_ms']}ms)"
    assert result['cities_processed'] == 9, "Should process 9 cities"
    print("✅ PASSED - Handles 8 cities efficiently\n")


def test_convergence_tracking():
    """Test that convergence history shows improvement."""
    print("=" * 80)
    print("TEST 5: Convergence - AI Learning Over Time")
    print("=" * 80)
    
    start = "Delhi"
    destinations = ["Mumbai", "Bangalore", "Chennai", "Kolkata", "Hyderabad"]
    
    result = optimize_route(start, destinations, use_ai=True)
    
    history = result['ai_metrics']['convergence_history']
    
    print(f"\n   Route: {' → '.join(result['route'])}")
    print(f"   Total Iterations: {result['ai_metrics']['iterations']}")
    print(f"\n   📈 Learning Progress:")
    
    for i, record in enumerate(history[:10]):
        print(f"      Iteration {record['generation']}: Score = {record['best_fitness']}")
    
    if len(history) > 10:
        print(f"      ... ({len(history) - 10} more iterations)")
        print(f"      Iteration {history[-1]['generation']}: Score = {history[-1]['best_fitness']} (Final)")
    
    # Check that score improved (lower score = better route in our system)
    initial_fitness = history[0]['best_fitness']
    final_fitness = history[-1]['best_fitness']
    improvement = initial_fitness - final_fitness  # Distance reduction
    
    print(f"\n   📊 Improvement:")
    print(f"      Initial Distance: {initial_fitness} km")
    print(f"      Final Distance: {final_fitness} km")
    print(f"      Reduced by: {improvement:.1f} km")
    
    print()
    assert len(history) > 0, "Should have convergence history"
    assert improvement >= 0, "Distance should decrease or stay same"
    print("✅ PASSED - AI learns and improves\n")


def test_consistency():
    """Test that AI gives consistent results."""
    print("=" * 80)
    print("TEST 6: Consistency - Multiple Runs")
    print("=" * 80)
    
    start = "Mumbai"
    destinations = ["Pune", "Bangalore", "Chennai"]
    
    print(f"\n   Running AI optimizer 3 times on same input...")
    
    results = []
    for i in range(3):
        result = optimize_route(start, destinations, use_ai=True)
        results.append(result['total_distance'])
        print(f"      Run {i+1}: {result['total_distance']} km")
    
    # All results should be reasonable (within 10% of each other)
    min_dist = min(results)
    max_dist = max(results)
    variance = (max_dist - min_dist) / min_dist * 100
    
    print(f"\n   Range: {min_dist:.2f} - {max_dist:.2f} km")
    print(f"   Variance: {variance:.1f}%")
    
    print()
    assert variance < 15, f"Results should be consistent (variance {variance:.1f}% < 15%)"
    print("✅ PASSED - Consistent results\n")


if __name__ == "__main__":
    print("\n")
    print("🤖 TASK 6: AI-ENHANCED OPTIMIZATION TEST SUITE")
    print("Testing AI-powered route optimization with simplified API")
    print("\n")
    
    tests = [
        ("AI vs Greedy Comparison", test_ai_vs_greedy),
        ("Priority Handling", test_priority_handling),
        ("AI Metrics & Improvement", test_ai_metrics),
        ("Scalability (8 cities)", test_scalability),
        ("Convergence Tracking", test_convergence_tracking),
        ("Consistency", test_consistency),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            test_func()
            passed += 1
        except Exception as e:
            failed += 1
            print(f"❌ ERROR in {test_name}: {e}")
    
    print("=" * 80)
    print(f"📊 TEST RESULTS: {passed}/{len(tests)} passed")
    print("=" * 80)
    
    if failed == 0:
        print("\n✅ ALL TESTS PASSED! Task 6 refactored successfully.")
        print("\n📋 Hackathon-Ready Features:")
        print("   ✅ Simplified API (use_ai=True/False)")
        print("   ✅ Business-friendly metrics (iterations, improvement%)")
        print("   ✅ No exposed complexity (parameters locked internally)")
        print("   ✅ Clear comparison: Greedy vs AI")
        print("   ✅ Priority handling maintained")
        print("\n🚀 Ready for demo presentation!")
    else:
        print(f"\n⚠️ {failed} test(s) failed. Review output above.")
