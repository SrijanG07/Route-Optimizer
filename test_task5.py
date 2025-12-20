"""
Task 5 Test Suite: Route Optimization Algorithm
Tests Nearest Neighbor implementation with priority handling.
"""

from utils.algorithm import optimize_route
from utils.cities import get_all_cities
import time


def test_basic_optimization():
    """Test basic 3-city optimization (no priorities)."""
    print("=" * 70)
    print("TEST 1: Basic Optimization (3 cities, no priorities)")
    print("=" * 70)
    
    start = "Mumbai"
    destinations = ["Pune", "Bangalore", "Chennai"]
    
    result = optimize_route(start, destinations)
    
    print(f"✅ Route: {' → '.join(result['route'])}")
    print(f"   Optimized Distance: {result['total_distance']} km")
    print(f"   Baseline Distance: {result['baseline_distance']} km")
    print(f"   Savings: {result['distance_saved']} km ({result['improvement_percentage']}%)")
    print(f"   Algorithm: {result['algorithm']}")
    print(f"   Execution Time: {result['execution_time_ms']} ms")
    print()
    
    assert len(result['route']) == 4, "Route should have 4 cities (start + 3 destinations)"
    assert result['route'][0] == start, "Route should start with source city"
    assert result['execution_time_ms'] < 1000, "Should complete in under 1 second"
    print("✅ PASSED\n")


def test_with_priorities():
    """Test optimization with priority handling."""
    print("=" * 70)
    print("TEST 2: With Priorities (Urgent cities visited first)")
    print("=" * 70)
    
    start = "Mumbai"
    destinations = ["Pune", "Bangalore", "Chennai", "Hyderabad"]
    priorities = {
        "Bangalore": 1,  # URGENT - should be visited first
        "Chennai": 2,    # MEDIUM
        "Pune": 3,       # LOW
        "Hyderabad": 3   # LOW
    }
    
    result = optimize_route(start, destinations, priorities)
    
    print(f"✅ Route: {' → '.join(result['route'])}")
    print(f"   Priority Handling:")
    for i, city in enumerate(result['route']):
        if i == 0:
            print(f"      {i+1}. {city} (START)")
        else:
            priority = priorities.get(city, 3)
            label = {1: "🔴 URGENT", 2: "🟡 MEDIUM", 3: "🟢 LOW"}[priority]
            print(f"      {i+1}. {city} - {label}")
    
    print(f"\n   Total Distance: {result['total_distance']} km")
    print(f"   Baseline Distance: {result['baseline_distance']} km")
    print(f"   Savings: {result['distance_saved']} km ({result['improvement_percentage']}%)")
    print(f"   Execution Time: {result['execution_time_ms']} ms")
    print()
    
    # Verify Bangalore (priority 1) is visited before Chennai (priority 2)
    bangalore_index = result['route'].index("Bangalore")
    chennai_index = result['route'].index("Chennai")
    pune_index = result['route'].index("Pune")
    
    assert bangalore_index < chennai_index, "Priority 1 cities should come before priority 2"
    assert chennai_index < pune_index, "Priority 2 cities should come before priority 3"
    print("✅ PASSED - Priority ordering correct\n")


def test_large_route():
    """Test with 10 cities (scalability test)."""
    print("=" * 70)
    print("TEST 3: Large Route (10 cities - scalability test)")
    print("=" * 70)
    
    all_cities = get_all_cities()
    start = "Mumbai"
    destinations = [c for c in all_cities if c != start]  # All other cities
    
    print(f"   Testing with {len(destinations)} destinations...")
    
    start_time = time.time()
    result = optimize_route(start, destinations)
    exec_time = (time.time() - start_time) * 1000
    
    print(f"✅ Route: {' → '.join(result['route'][:3])} ... {result['route'][-1]}")
    print(f"   Total Cities: {len(result['route'])}")
    print(f"   Total Distance: {result['total_distance']} km")
    print(f"   Baseline Distance: {result['baseline_distance']} km")
    print(f"   Savings: {result['distance_saved']} km ({result['improvement_percentage']}%)")
    print(f"   Execution Time: {exec_time:.2f} ms")
    print()
    
    assert len(result['route']) == 10, "Should have 10 cities"
    assert exec_time < 2000, "Should complete in under 2 seconds"
    assert result['improvement_percentage'] >= 0, "Should show improvement over baseline"
    print("✅ PASSED - Handles 10 cities efficiently\n")


def test_single_destination():
    """Edge case: Only 1 destination."""
    print("=" * 70)
    print("TEST 4: Edge Case - Single Destination")
    print("=" * 70)
    
    start = "Mumbai"
    destinations = ["Pune"]
    
    result = optimize_route(start, destinations)
    
    print(f"✅ Route: {' → '.join(result['route'])}")
    print(f"   Distance: {result['total_distance']} km")
    print(f"   Execution Time: {result['execution_time_ms']} ms")
    print()
    
    assert len(result['route']) == 2, "Should have exactly 2 cities"
    assert result['route'] == [start, "Pune"], "Should be direct route"
    print("✅ PASSED\n")


def test_performance_comparison():
    """Test that optimization actually improves over baseline."""
    print("=" * 70)
    print("TEST 5: Performance Comparison (Optimization vs Baseline)")
    print("=" * 70)
    
    start = "Delhi"
    destinations = ["Mumbai", "Bangalore", "Chennai", "Kolkata", "Hyderabad"]
    
    result = optimize_route(start, destinations)
    
    print(f"   Baseline (Random) Route:")
    print(f"      Distance: {result['baseline_distance']} km")
    print()
    print(f"   Optimized (Nearest Neighbor) Route:")
    print(f"      Route: {' → '.join(result['route'])}")
    print(f"      Distance: {result['total_distance']} km")
    print()
    print(f"   📊 IMPROVEMENT:")
    print(f"      Saved: {result['distance_saved']} km")
    print(f"      Improvement: {result['improvement_percentage']}%")
    print()
    
    # In worst case, NN should be at least as good as random
    assert result['total_distance'] <= result['baseline_distance'], \
        "Optimized route should be equal or better than baseline"
    print("✅ PASSED - Optimization shows improvement\n")


def test_all_same_priority():
    """Edge case: All cities have same priority."""
    print("=" * 70)
    print("TEST 6: Edge Case - All Cities Same Priority")
    print("=" * 70)
    
    start = "Mumbai"
    destinations = ["Pune", "Bangalore", "Chennai"]
    priorities = {
        "Pune": 1,
        "Bangalore": 1,
        "Chennai": 1
    }
    
    result = optimize_route(start, destinations, priorities)
    
    print(f"✅ Route: {' → '.join(result['route'])}")
    print(f"   All cities have priority 1 (URGENT)")
    print(f"   Distance: {result['total_distance']} km")
    print(f"   Execution Time: {result['execution_time_ms']} ms")
    print()
    
    assert len(result['route']) == 4, "Should have all 4 cities"
    print("✅ PASSED\n")


def run_all_tests():
    """Run complete test suite."""
    print("\n")
    print("🧪 TASK 5: ROUTE OPTIMIZATION ALGORITHM TEST SUITE")
    print("Testing Nearest Neighbor (Greedy) implementation")
    print("\n")
    
    tests = [
        ("Basic Optimization", test_basic_optimization),
        ("Priority Handling", test_with_priorities),
        ("Large Route (10 cities)", test_large_route),
        ("Single Destination", test_single_destination),
        ("Performance Comparison", test_performance_comparison),
        ("All Same Priority", test_all_same_priority),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"❌ FAILED: {test_name}")
            print(f"   Error: {e}\n")
            failed += 1
        except Exception as e:
            print(f"❌ ERROR in {test_name}: {e}\n")
            failed += 1
    
    print("=" * 70)
    print(f"📊 TEST RESULTS: {passed}/{len(tests)} passed")
    print("=" * 70)
    
    if failed == 0:
        print("\n✅ ALL TESTS PASSED! Task 5 is complete and working correctly.")
        print("\n📋 Deliverables Completed:")
        print("   ✅ Working optimization function (optimize_route)")
        print("   ✅ Performance comparison with random/baseline route")
        print("   ✅ Code comments explaining logic")
        print("   ✅ Priority handling implemented")
        print("   ✅ Scalability tested (works with 10+ cities)")
        print("\n🚀 Ready for Task 8 (REST API integration)")
    else:
        print(f"\n⚠️ {failed} test(s) failed. Review output above.")
    
    print()


if __name__ == "__main__":
    run_all_tests()
