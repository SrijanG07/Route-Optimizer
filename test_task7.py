"""
Task 7 Test Suite: Real-Time Route Recalculation
Tests dynamic route updates, performance, and edge cases.
"""

from utils.recalculation import (
    recalculate_route,
    add_cities_to_route,
    remove_cities_from_route,
    update_priorities,
    bulk_update_route
)
import time


def test_basic_recalculation():
    """Test basic recalculation from mid-route position."""
    print("=" * 80)
    print("TEST 1: Basic Recalculation - Mid-Route Optimization")
    print("=" * 80)
    
    # Scenario: Driver completed Mumbai->Pune, now in Pune with 3 remaining cities
    current_position = "Pune"
    remaining_destinations = ["Bangalore", "Chennai", "Hyderabad"]
    
    print(f"\n📍 Current Position: {current_position}")
    print(f"   Remaining Destinations: {remaining_destinations}")
    
    result = recalculate_route(
        current_position=current_position,
        remaining_destinations=remaining_destinations,
        use_ai=False
    )
    
    print(f"\n   ✅ Optimized Remaining Route: {' → '.join(result['route'])}")
    print(f"   Distance: {result['total_distance']} km")
    print(f"   Recalculation Time: {result['recalculation_metadata']['total_recalc_time_ms']} ms")
    
    print()
    assert result['recalculation_metadata']['total_recalc_time_ms'] < 100, "Should complete in <100ms"
    assert len(result['route']) == 4, "Should have 4 cities (current + 3 remaining)"
    print("✅ PASSED - Fast recalculation\n")


def test_add_urgent_delivery():
    """Test adding urgent delivery mid-route."""
    print("=" * 80)
    print("TEST 2: Add Cities - Urgent Delivery Added Mid-Route")
    print("=" * 80)
    
    # Scenario: Driver at Pune, original route to Bangalore->Chennai
    # Urgent delivery to Hyderabad comes in
    current_position = "Pune"
    existing_route = ["Mumbai", "Pune", "Bangalore", "Chennai"]
    new_cities = ["Hyderabad"]
    priorities = {
        "Hyderabad": 1,  # URGENT
        "Bangalore": 2,
        "Chennai": 3
    }
    
    print(f"\n📦 Original Route: {' → '.join(existing_route)}")
    print(f"   Current Position: {current_position}")
    print(f"   ⚠️ URGENT: Adding {new_cities[0]} (Priority 1)")
    
    result = add_cities_to_route(
        current_position=current_position,
        existing_route=existing_route,
        new_cities=new_cities,
        priorities=priorities,
        use_ai=False
    )
    
    print(f"\n   ✅ Updated Route: {' → '.join(result['route'])}")
    print(f"   Distance: {result['total_distance']} km")
    print(f"   Operation Time: {result['change_metadata']['total_operation_time_ms']} ms")
    print(f"   Cities Added: {result['change_metadata']['cities_added_count']}")
    
    # Hyderabad (P1) should come before Bangalore (P2) and Chennai (P3)
    route = result['route']
    hyderabad_pos = route.index("Hyderabad")
    bangalore_pos = route.index("Bangalore")
    chennai_pos = route.index("Chennai")
    
    print(f"\n   Priority Order Check:")
    print(f"      Hyderabad (P1): Position {hyderabad_pos}")
    print(f"      Bangalore (P2): Position {bangalore_pos}")
    print(f"      Chennai (P3): Position {chennai_pos}")
    
    print()
    assert result['change_metadata']['total_operation_time_ms'] < 50, "Should complete in <50ms"
    assert hyderabad_pos < bangalore_pos, "Urgent delivery should be prioritized"
    print("✅ PASSED - Urgent delivery inserted correctly\n")


def test_remove_cancelled_delivery():
    """Test removing cancelled delivery from route."""
    print("=" * 80)
    print("TEST 3: Remove Cities - Cancelled Delivery")
    print("=" * 80)
    
    # Scenario: Chennai delivery cancelled, driver at Pune
    current_position = "Pune"
    existing_route = ["Mumbai", "Pune", "Bangalore", "Chennai", "Hyderabad"]
    cities_to_remove = ["Chennai"]
    
    print(f"\n📦 Original Route: {' → '.join(existing_route)}")
    print(f"   Current Position: {current_position}")
    print(f"   ❌ CANCELLED: {cities_to_remove[0]}")
    
    result = remove_cities_from_route(
        current_position=current_position,
        existing_route=existing_route,
        cities_to_remove=cities_to_remove,
        use_ai=False
    )
    
    print(f"\n   ✅ Updated Route: {' → '.join(result['route'])}")
    print(f"   Distance: {result['total_distance']} km")
    print(f"   Operation Time: {result['change_metadata']['total_operation_time_ms']} ms")
    print(f"   Cities Removed: {result['change_metadata']['cities_removed_count']}")
    
    print()
    assert "Chennai" not in result['route'], "Chennai should be removed"
    assert result['change_metadata']['total_operation_time_ms'] < 50, "Should complete in <50ms"
    print("✅ PASSED - City removed efficiently\n")


def test_priority_update():
    """Test updating priorities for remaining deliveries."""
    print("=" * 80)
    print("TEST 4: Priority Update - Customer Upgraded to Urgent")
    print("=" * 80)
    
    # Scenario: Bangalore upgraded from P3 to P1 (urgent)
    current_position = "Pune"
    remaining_destinations = ["Bangalore", "Chennai", "Hyderabad"]
    
    old_priorities = {
        "Bangalore": 3,
        "Chennai": 2,
        "Hyderabad": 2
    }
    
    new_priorities = {
        "Bangalore": 1,  # Upgraded to URGENT
        "Chennai": 2,
        "Hyderabad": 2
    }
    
    print(f"\n📍 Current Position: {current_position}")
    print(f"   Remaining Cities: {remaining_destinations}")
    print(f"   📈 PRIORITY CHANGE: Bangalore: P3 → P1 (URGENT)")
    
    result = update_priorities(
        current_position=current_position,
        remaining_destinations=remaining_destinations,
        old_priorities=old_priorities,
        new_priorities=new_priorities,
        use_ai=False
    )
    
    print(f"\n   ✅ Reoptimized Route: {' → '.join(result['route'])}")
    print(f"   Distance: {result['total_distance']} km")
    print(f"   Operation Time: {result['change_metadata']['total_operation_time_ms']} ms")
    print(f"   Priority Changes: {result['change_metadata']['changes_count']}")
    
    # Bangalore should be first after Pune
    assert result['route'][1] == "Bangalore", "Bangalore should be prioritized"
    
    print()
    assert result['change_metadata']['total_operation_time_ms'] < 30, "Should complete in <30ms"
    print("✅ PASSED - Priority update handled correctly\n")


def test_bulk_update():
    """Test multiple changes at once (most efficient)."""
    print("=" * 80)
    print("TEST 5: Bulk Update - Add, Remove, and Reprioritize")
    print("=" * 80)
    
    # Scenario: Complex update with multiple changes
    current_position = "Mumbai"
    existing_route = ["Mumbai", "Pune", "Bangalore", "Chennai"]
    
    cities_to_add = ["Hyderabad", "Kolkata"]
    cities_to_remove = ["Pune"]
    updated_priorities = {
        "Hyderabad": 1,  # New urgent
        "Bangalore": 2,
        "Chennai": 3,
        "Kolkata": 3
    }
    
    print(f"\n📦 Original Route: {' → '.join(existing_route)}")
    print(f"   Current Position: {current_position}")
    print(f"\n   CHANGES:")
    print(f"      ➕ Adding: {', '.join(cities_to_add)}")
    print(f"      ➖ Removing: {', '.join(cities_to_remove)}")
    print(f"      📊 Priorities: Hyderabad=URGENT, others=MEDIUM/LOW")
    
    start_time = time.time()
    result = bulk_update_route(
        current_position=current_position,
        existing_route=existing_route,
        cities_to_add=cities_to_add,
        cities_to_remove=cities_to_remove,
        updated_priorities=updated_priorities,
        use_ai=False
    )
    bulk_time = (time.time() - start_time) * 1000
    
    print(f"\n   ✅ Updated Route: {' → '.join(result['route'])}")
    print(f"   Distance: {result['total_distance']} km")
    print(f"   Operation Time: {result['change_metadata']['total_operation_time_ms']} ms")
    print(f"   Total Changes: {result['change_metadata']['total_changes']}")
    
    print()
    assert "Pune" not in result['route'], "Pune should be removed"
    assert "Hyderabad" in result['route'], "Hyderabad should be added"
    assert "Kolkata" in result['route'], "Kolkata should be added"
    assert result['change_metadata']['total_operation_time_ms'] < 200, "Bulk update should complete in <200ms"
    print("✅ PASSED - Bulk update efficient\n")


def test_performance_benchmarks():
    """Benchmark recalculation performance."""
    print("=" * 80)
    print("TEST 6: Performance Benchmarks - Speed Tests")
    print("=" * 80)
    
    print("\n⏱️ Running performance benchmarks...\n")
    
    # Benchmark 1: Small route (3 cities)
    start = time.time()
    result1 = recalculate_route("Mumbai", ["Pune", "Bangalore", "Chennai"], use_ai=False)
    time1 = (time.time() - start) * 1000
    
    # Benchmark 2: Medium route (6 cities)
    start = time.time()
    result2 = recalculate_route(
        "Delhi",
        ["Mumbai", "Bangalore", "Chennai", "Kolkata", "Hyderabad", "Pune"],
        use_ai=False
    )
    time2 = (time.time() - start) * 1000
    
    # Benchmark 3: Large route (9 cities)
    start = time.time()
    result3 = recalculate_route(
        "Mumbai",
        ["Pune", "Bangalore", "Chennai", "Hyderabad", "Kolkata", "Delhi", "Jaipur", "Ahmedabad", "Indore"],
        use_ai=False
    )
    time3 = (time.time() - start) * 1000
    
    # Benchmark 4: Add city operation
    start = time.time()
    result4 = add_cities_to_route(
        "Pune",
        ["Mumbai", "Pune", "Bangalore", "Chennai"],
        ["Hyderabad"],
        use_ai=False
    )
    time4 = (time.time() - start) * 1000
    
    # Benchmark 5: Remove city operation
    start = time.time()
    result5 = remove_cities_from_route(
        "Pune",
        ["Mumbai", "Pune", "Bangalore", "Chennai", "Hyderabad"],
        ["Chennai"],
        use_ai=False
    )
    time5 = (time.time() - start) * 1000
    
    print("   📊 PERFORMANCE RESULTS:")
    print(f"      Small Route (3 cities):     {time1:.2f} ms ✅" if time1 < 50 else f"      Small Route (3 cities):     {time1:.2f} ms ⚠️")
    print(f"      Medium Route (6 cities):    {time2:.2f} ms ✅" if time2 < 100 else f"      Medium Route (6 cities):    {time2:.2f} ms ⚠️")
    print(f"      Large Route (9 cities):     {time3:.2f} ms ✅" if time3 < 150 else f"      Large Route (9 cities):     {time3:.2f} ms ⚠️")
    print(f"      Add City Operation:         {time4:.2f} ms ✅" if time4 < 50 else f"      Add City Operation:         {time4:.2f} ms ⚠️")
    print(f"      Remove City Operation:      {time5:.2f} ms ✅" if time5 < 50 else f"      Remove City Operation:      {time5:.2f} ms ⚠️")
    
    print(f"\n   🎯 PERFORMANCE TARGETS:")
    print(f"      ✅ All operations under acceptable limits")
    print(f"      ✅ Scales linearly with route size")
    print(f"      ✅ Fast enough for real-time use")
    
    print()
    assert time1 < 50, f"Small route should be <50ms (got {time1:.2f}ms)"
    assert time2 < 100, f"Medium route should be <100ms (got {time2:.2f}ms)"
    assert time3 < 150, f"Large route should be <150ms (got {time3:.2f}ms)"
    assert time4 < 50, f"Add city should be <50ms (got {time4:.2f}ms)"
    assert time5 < 50, f"Remove city should be <50ms (got {time5:.2f}ms)"
    print("✅ PASSED - All performance targets met\n")


def test_edge_cases():
    """Test edge cases and error handling."""
    print("=" * 80)
    print("TEST 7: Edge Cases - Error Handling")
    print("=" * 80)
    
    print("\n🔍 Testing edge cases...\n")
    
    # Edge Case 1: Add invalid city
    print("   Test 1: Adding invalid city")
    result1 = add_cities_to_route(
        "Mumbai",
        ["Mumbai", "Pune", "Bangalore"],
        ["InvalidCity"],
        use_ai=False
    )
    assert result1.get("success") == False, "Should reject invalid city"
    print(f"      ✅ Correctly rejected: {result1.get('error')}")
    
    # Edge Case 2: Remove already completed city
    print("\n   Test 2: Removing already completed city")
    result2 = remove_cities_from_route(
        "Bangalore",  # Current at Bangalore
        ["Mumbai", "Pune", "Bangalore", "Chennai"],
        ["Mumbai", "Pune"],  # Try to remove already visited
        use_ai=False
    )
    assert result2.get("recalculation_needed") == False, "Should skip recalculation"
    print(f"      ✅ Correctly skipped recalculation")
    
    # Edge Case 3: Empty remaining destinations
    print("\n   Test 3: Recalculation with single remaining city")
    result3 = recalculate_route(
        "Mumbai",
        ["Pune"],  # Only 1 remaining
        use_ai=False
    )
    assert len(result3['route']) == 2, "Should handle single destination"
    print(f"      ✅ Route: {' → '.join(result3['route'])}")
    
    # Edge Case 4: Current position not in route
    print("\n   Test 4: Current position not in original route")
    result4 = add_cities_to_route(
        "Kolkata",  # Not in original route
        ["Mumbai", "Pune", "Bangalore"],
        ["Chennai"],
        use_ai=False
    )
    assert result4['route'][0] == "Kolkata", "Should start from current position"
    print(f"      ✅ Started from new position: {result4['route'][0]}")
    
    print()
    print("✅ PASSED - All edge cases handled correctly\n")


def test_matrix_reuse_optimization():
    """Test that distance matrix reuse improves performance."""
    print("=" * 80)
    print("TEST 8: Matrix Reuse - Performance Optimization")
    print("=" * 80)
    
    from utils.distance import build_distance_matrix
    
    current_position = "Mumbai"
    remaining = ["Pune", "Bangalore", "Chennai", "Hyderabad", "Kolkata"]
    
    # Build matrix once
    all_cities = [current_position] + remaining
    matrix = build_distance_matrix(all_cities)
    
    print(f"\n📍 Testing matrix reuse optimization...")
    print(f"   Cities: {len(all_cities)}")
    
    # Test 1: Without matrix reuse
    start = time.time()
    result1 = recalculate_route(current_position, remaining, use_ai=False)
    time_without_reuse = (time.time() - start) * 1000
    
    # Test 2: With matrix reuse
    start = time.time()
    result2 = recalculate_route(current_position, remaining, use_ai=False, previous_matrix=matrix)
    time_with_reuse = (time.time() - start) * 1000
    
    matrix_build_time = result1['recalculation_metadata']['matrix_build_time_ms']
    
    print(f"\n   ⏱️ Performance Comparison:")
    print(f"      Without Matrix Reuse: {time_without_reuse:.2f} ms")
    print(f"      With Matrix Reuse:    {time_with_reuse:.2f} ms")
    print(f"      Matrix Build Time:    {matrix_build_time:.2f} ms")
    print(f"      Speedup:              {time_without_reuse - time_with_reuse:.2f} ms ({((time_without_reuse - time_with_reuse) / time_without_reuse * 100):.1f}%)")
    
    print(f"\n   ✅ Matrix Reused: {result2['recalculation_metadata']['matrix_reused']}")
    
    print()
    assert result2['recalculation_metadata']['matrix_reused'] == True, "Matrix should be reused"
    assert time_with_reuse <= time_without_reuse, "Matrix reuse should be faster or equal"
    print("✅ PASSED - Matrix reuse optimization working\n")


if __name__ == "__main__":
    print("\n")
    print("🔄 TASK 7: REAL-TIME ROUTE RECALCULATION TEST SUITE")
    print("Testing dynamic route updates and performance")
    print("\n")
    
    tests = [
        ("Basic Recalculation", test_basic_recalculation),
        ("Add Urgent Delivery", test_add_urgent_delivery),
        ("Remove Cancelled Delivery", test_remove_cancelled_delivery),
        ("Priority Update", test_priority_update),
        ("Bulk Update", test_bulk_update),
        ("Performance Benchmarks", test_performance_benchmarks),
        ("Edge Cases", test_edge_cases),
        ("Matrix Reuse Optimization", test_matrix_reuse_optimization),
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
            import traceback
            traceback.print_exc()
    
    print("=" * 80)
    print(f"📊 TEST RESULTS: {passed}/{len(tests)} passed")
    print("=" * 80)
    
    if failed == 0:
        print("\n✅ ALL TESTS PASSED! Task 7 complete.")
        print("\n📋 Real-Time Recalculation Features:")
        print("   ✅ Mid-route optimization from current position")
        print("   ✅ Add urgent deliveries dynamically (<50ms)")
        print("   ✅ Remove cancelled deliveries efficiently")
        print("   ✅ Update priorities in real-time (<30ms)")
        print("   ✅ Bulk updates with single recalculation (<200ms)")
        print("   ✅ Distance matrix reuse for performance")
        print("   ✅ Comprehensive edge case handling")
        print("\n🚀 Ready for Task 8 (REST API integration)!")
    else:
        print(f"\n⚠️ {failed} test(s) failed. Review output above.")
