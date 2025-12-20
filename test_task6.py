"""
Task 6 Test Suite: AI/ML Enhanced Optimization (Genetic Algorithm)
Tests AI-powered route optimization with configurable parameters.
"""

from utils.algorithm import optimize_route
import time


def test_genetic_vs_greedy():
    """Compare Genetic Algorithm (AI) vs Nearest Neighbor (Greedy)."""
    print("=" * 80)
    print("TEST 1: AI/ML Enhancement - Genetic Algorithm vs Greedy")
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
    greedy_result = optimize_route(start, destinations, priorities, use_genetic=False)
    
    print(f"   Route: {' → '.join(greedy_result['route'][:3])} ... {greedy_result['route'][-1]}")
    print(f"   Distance: {greedy_result['total_distance']} km")
    print(f"   Savings: {greedy_result['distance_saved']} km ({greedy_result['improvement_percentage']}%)")
    print(f"   Time: {greedy_result['execution_time_ms']} ms")
    
    print("\n🟢 Running AI/ML (Genetic Algorithm)...")
    ai_result = optimize_route(
        start, destinations, priorities, 
        use_genetic=True,
        population_size=50,
        generations=100,
        mutation_rate=0.2,
        priority_penalty=1000.0
    )
    
    print(f"   Route: {' → '.join(ai_result['route'][:3])} ... {ai_result['route'][-1]}")
    print(f"   Distance: {ai_result['total_distance']} km")
    print(f"   Savings: {ai_result['distance_saved']} km ({ai_result['improvement_percentage']}%)")
    print(f"   Time: {ai_result['execution_time_ms']} ms")
    
    if 'ai_metrics' in ai_result:
        print(f"\n   🤖 AI Metrics:")
        print(f"      Generations: {ai_result['ai_metrics']['generations_run']}")
        print(f"      Population Size: {ai_result['ai_metrics']['population_size']}")
        print(f"      Mutation Rate: {ai_result['ai_metrics']['mutation_rate']}")
        print(f"      Fitness Improvement: {ai_result['ai_metrics']['fitness_improvement']:.1f}%")
        print(f"      Priority Violations: {ai_result['ai_metrics']['priority_violations']}")
    
    print(f"\n   📊 COMPARISON:")
    improvement = greedy_result['total_distance'] - ai_result['total_distance']
    pct = (improvement / greedy_result['total_distance']) * 100 if greedy_result['total_distance'] > 0 else 0
    print(f"      Greedy: {greedy_result['total_distance']} km")
    print(f"      AI/ML:  {ai_result['total_distance']} km")
    print(f"      AI Better By: {improvement:.2f} km ({pct:.1f}%)")
    
    print()
    assert 'ai_metrics' in ai_result, "AI metrics should be present"
    assert ai_result['ai_metrics']['priority_violations'] == 0, "Should have no priority violations"
    print("✅ PASSED - AI/ML enhancement working\n")


def test_configurable_parameters():
    """Test different Genetic Algorithm configurations."""
    print("=" * 80)
    print("TEST 2: Configurable Parameters - Different GA Configurations")
    print("=" * 80)
    
    start = "Delhi"
    destinations = ["Mumbai", "Bangalore", "Chennai", "Kolkata", "Hyderabad"]
    
    configs = [
        {"population_size": 30, "generations": 50, "mutation_rate": 0.1, "name": "Small Population"},
        {"population_size": 100, "generations": 150, "mutation_rate": 0.3, "name": "Large Population"},
        {"population_size": 50, "generations": 100, "mutation_rate": 0.2, "name": "Balanced (Default)"},
    ]
    
    results = []
    
    for config in configs:
        print(f"\n🔧 Configuration: {config['name']}")
        print(f"   Population: {config['population_size']}, Generations: {config['generations']}, Mutation: {config['mutation_rate']}")
        
        result = optimize_route(
            start, destinations,
            use_genetic=True,
            population_size=config['population_size'],
            generations=config['generations'],
            mutation_rate=config['mutation_rate']
        )
        
        print(f"   Distance: {result['total_distance']} km")
        print(f"   Time: {result['execution_time_ms']} ms")
        print(f"   Improvement: {result['improvement_percentage']}% vs baseline")
        
        results.append(result)
    
    print(f"\n   📊 Results Summary:")
    for i, config in enumerate(configs):
        print(f"      {config['name']}: {results[i]['total_distance']} km in {results[i]['execution_time_ms']} ms")
    
    print()
    assert all('configurable_params' in r for r in results), "Should have configurable params"
    print("✅ PASSED - Different configurations work\n")


def test_priority_penalties():
    """Test that priority penalties work correctly."""
    print("=" * 80)
    print("TEST 3: Priority Penalties - Ensures High Priority Cities Come First")
    print("=" * 80)
    
    start = "Mumbai"
    destinations = ["Pune", "Bangalore", "Chennai"]
    priorities = {
        "Bangalore": 1,  # URGENT - should be first
        "Chennai": 2,    # MEDIUM
        "Pune": 3        # LOW - should be last
    }
    
    result = optimize_route(
        start, destinations, priorities,
        use_genetic=True,
        population_size=50,
        generations=100,
        priority_penalty=5000.0  # High penalty for violations
    )
    
    print(f"\n   Route: {' → '.join(result['route'])}")
    print(f"   Priority Order Check:")
    
    for i, city in enumerate(result['route']):
        if i == 0:
            print(f"      {i+1}. {city} (START)")
        else:
            priority = priorities.get(city, 3)
            label = {1: "🔴 URGENT", 2: "🟡 MEDIUM", 3: "🟢 LOW"}[priority]
            print(f"      {i+1}. {city} - {label}")
    
    print(f"\n   Priority Violations: {result['ai_metrics']['priority_violations']}")
    print(f"   Distance: {result['total_distance']} km")
    
    # Verify order: Bangalore (1) before Chennai (2) before Pune (3)
    bangalore_idx = result['route'].index("Bangalore")
    chennai_idx = result['route'].index("Chennai")
    pune_idx = result['route'].index("Pune")
    
    print()
    assert bangalore_idx < chennai_idx, "Priority 1 should come before priority 2"
    assert chennai_idx < pune_idx, "Priority 2 should come before priority 3"
    assert result['ai_metrics']['priority_violations'] == 0, "Should have 0 violations with high penalty"
    print("✅ PASSED - Priority penalties working correctly\n")


def test_ai_metrics_improvement():
    """Test that AI shows fitness improvement over generations."""
    print("=" * 80)
    print("TEST 4: AI Metrics - Fitness Improvement Over Generations")
    print("=" * 80)
    
    start = "Mumbai"
    destinations = ["Pune", "Bangalore", "Chennai", "Hyderabad"]
    
    result = optimize_route(
        start, destinations,
        use_genetic=True,
        population_size=50,
        generations=100
    )
    
    print(f"\n   🤖 AI Learning Progress:")
    print(f"      Initial Fitness: {result['ai_metrics']['initial_fitness']:.2f}")
    print(f"      Best Fitness: {result['ai_metrics']['best_fitness']:.2f}")
    print(f"      Improvement: {result['ai_metrics']['fitness_improvement']:.1f}%")
    print(f"      Generations: {result['ai_metrics']['generations_run']}")
    
    print(f"\n   Route Quality:")
    print(f"      Optimized Distance: {result['total_distance']} km")
    print(f"      Baseline Distance: {result['baseline_distance']} km")
    print(f"      Savings: {result['distance_saved']} km ({result['improvement_percentage']}%)")
    
    print()
    assert result['ai_metrics']['fitness_improvement'] > 0, "Should show fitness improvement"
    print("✅ PASSED - AI shows learning/improvement\n")


def test_scalability_with_ai():
    """Test AI/ML algorithm with larger routes."""
    print("=" * 80)
    print("TEST 5: Scalability - AI with 8 Cities")
    print("=" * 80)
    
    start = "Mumbai"
    destinations = ["Delhi", "Bangalore", "Chennai", "Kolkata", "Hyderabad", "Pune", "Ahmedabad", "Jaipur"]
    
    print(f"\n   Testing with {len(destinations)} destinations...")
    
    start_time = time.time()
    result = optimize_route(
        start, destinations,
        use_genetic=True,
        population_size=80,
        generations=150,
        mutation_rate=0.25
    )
    exec_time = (time.time() - start_time) * 1000
    
    print(f"\n   ✅ Route: {' → '.join(result['route'][:3])} ... {result['route'][-2]} → {result['route'][-1]}")
    print(f"   Total Cities: {len(result['route'])}")
    print(f"   Distance: {result['total_distance']} km")
    print(f"   Baseline: {result['baseline_distance']} km")
    print(f"   Improvement: {result['improvement_percentage']}%")
    print(f"   Execution Time: {exec_time:.2f} ms")
    
    print()
    assert len(result['route']) == 9, "Should have 9 cities"
    assert exec_time < 5000, "Should complete in under 5 seconds"
    assert result['improvement_percentage'] > 0, "Should show improvement"
    print("✅ PASSED - AI scales well with 8+ cities\n")


def test_extreme_mutation():
    """Test with very high mutation rate (exploration vs exploitation)."""
    print("=" * 80)
    print("TEST 6: Extreme Parameters - High Mutation Rate (Exploration)")
    print("=" * 80)
    
    start = "Delhi"
    destinations = ["Mumbai", "Bangalore", "Chennai"]
    
    print("\n   Testing with mutation_rate = 0.8 (high exploration)")
    
    result = optimize_route(
        start, destinations,
        use_genetic=True,
        population_size=50,
        generations=80,
        mutation_rate=0.8  # Very high mutation
    )
    
    print(f"   Route: {' → '.join(result['route'])}")
    print(f"   Distance: {result['total_distance']} km")
    print(f"   Improvement: {result['improvement_percentage']}%")
    print(f"   Fitness Improvement: {result['ai_metrics']['fitness_improvement']:.1f}%")
    
    print()
    assert result['total_distance'] > 0, "Should produce valid route"
    print("✅ PASSED - Extreme parameters handled\n")


def run_all_tests():
    """Run complete AI/ML test suite."""
    print("\n")
    print("🤖 TASK 6: AI/ML ENHANCED OPTIMIZATION TEST SUITE")
    print("Testing Genetic Algorithm with configurable parameters")
    print("\n")
    
    tests = [
        ("AI vs Greedy Comparison", test_genetic_vs_greedy),
        ("Configurable Parameters", test_configurable_parameters),
        ("Priority Penalties", test_priority_penalties),
        ("AI Metrics & Improvement", test_ai_metrics_improvement),
        ("Scalability (8 cities)", test_scalability_with_ai),
        ("Extreme Parameters", test_extreme_mutation),
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
    
    print("=" * 80)
    print(f"📊 TEST RESULTS: {passed}/{len(tests)} passed")
    print("=" * 80)
    
    if failed == 0:
        print("\n✅ ALL TESTS PASSED! Task 6 (AI/ML Enhancement) is complete!")
        print("\n📋 Task 6 Deliverables Completed:")
        print("   ✅ AI-enhanced optimizer (Genetic Algorithm)")
        print("   ✅ Metrics showing improvement (fitness, generations, violations)")
        print("   ✅ Configurable parameters (population_size, generations, mutation_rate, penalty)")
        print("   ✅ Priority handling with penalties")
        print("   ✅ Performance comparison (AI vs Greedy)")
        print("   ✅ Scalability tested (8+ cities)")
        print("\n🎯 AI/ML FEATURES:")
        print("   • Population-based evolution")
        print("   • Fitness function with priority penalties")
        print("   • Crossover (combining best routes)")
        print("   • Mutation (random exploration)")
        print("   • Elitism (keeping best solutions)")
        print("   • Configurable hyperparameters")
        print("\n🚀 Ready for demo! Now implement Task 8 (REST API)")
    else:
        print(f"\n⚠️ {failed} test(s) failed. Review output above.")
    
    print()


if __name__ == "__main__":
    run_all_tests()
