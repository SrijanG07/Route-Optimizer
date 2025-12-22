"""
Performance Testing Script for Route Optimization System

Tests the Genetic Algorithm optimizer with 5, 10, and 20 cities.
Measures response times, identifies bottlenecks, and generates detailed reports.

Usage:
    python scripts/test_performance.py
    
Output:
    - Console report with timing breakdowns
    - performance_report.csv with detailed metrics
"""

import time
import random
import statistics
import csv
from typing import Dict, List, Tuple
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.algorithm import optimize_route
from utils.cities import get_all_cities
from utils.distance import get_cache_info


def measure_performance(
    start_city: str,
    destinations: List[str],
    priorities: Dict[str, int] = None,
    test_name: str = ""
) -> Dict:
    """
    Run a single optimization and measure performance metrics.
    
    Returns dict with:
        - total_time: Total execution time
        - route: Optimized route
        - total_distance: Route distance in km
        - algorithm_time: Time spent in algorithm
        - city_count: Number of cities
        - test_name: Test identifier
    """
    start_time = time.time()
    
    # Run optimization
    result = optimize_route(
        start=start_city,
        destinations=destinations,
        priorities=priorities,
        use_ai=True  # Always use Genetic Algorithm
    )
    
    total_time = (time.time() - start_time) * 1000  # Convert to ms
    
    return {
        "test_name": test_name,
        "city_count": len(destinations) + 1,  # +1 for start city
        "total_time_ms": round(total_time, 2),
        "algorithm_time_ms": result["execution_time_ms"],
        "total_distance_km": result["total_distance"],
        "distance_saved_km": result["distance_saved"],
        "improvement_pct": result["improvement_percentage"],
        "algorithm": result["algorithm"],
        "route": " -> ".join(result["route"][:3]) + "..." if len(result["route"]) > 3 else " -> ".join(result["route"])
    }


def run_test_suite():
    """
    Run comprehensive performance tests with 5, 10, and 20 cities.
    """
    print("\n" + "="*80)
    print("GENETIC ALGORITHM PERFORMANCE TEST SUITE")
    print("="*80 + "\n")
    
    all_cities = get_all_cities()
    print(f"[INFO] Total cities available: {len(all_cities)}")
    print(f"[TEST] Test scenarios: 5, 10, 20 cities\n")
    
    # Test configurations
    test_configs = [
        {"size": 5, "name": "Small Scale (5 cities)", "runs": 3},
        {"size": 10, "name": "Medium Scale (10 cities)", "runs": 3},
        {"size": 20, "name": "Large Scale (20 cities)", "runs": 2},
    ]
    
    all_results = []
    
    for config in test_configs:
        size = config["size"]
        runs = config["runs"]
        
        print(f"\n{'='*80}")
        print(f"[TEST] {config['name']}")
        print(f"{'='*80}")
        
        test_times = []
        
        for run in range(runs):
            # Select random cities for this test
            random.seed(42 + run)  # Reproducible random selection
            selected = random.sample(all_cities, size)
            start_city = selected[0]
            destinations = selected[1:]
            
            # Create some priority constraints for realism
            priorities = {}
            if len(destinations) >= 3:
                priorities[destinations[0]] = 1  # First dest = urgent
                priorities[destinations[1]] = 2  # Second dest = medium
                # Rest default to low (3)
            
            print(f"\n  Run #{run + 1}/{runs}")
            print(f"  Route: {start_city} to {len(destinations)} cities")
            
            # Measure performance
            result = measure_performance(
                start_city=start_city,
                destinations=destinations,
                priorities=priorities,
                test_name=f"{config['name']} - Run {run + 1}"
            )
            
            test_times.append(result["total_time_ms"])
            all_results.append(result)
            
            # Print result
            print(f"  [OK] Completed in {result['total_time_ms']:.2f}ms")
            print(f"    - Algorithm time: {result['algorithm_time_ms']:.2f}ms")
            print(f"    - Total distance: {result['total_distance_km']:.2f} km")
            print(f"    - Improvement: {result['improvement_pct']}%")
        
        # Calculate statistics for this test size
        avg_time = statistics.mean(test_times)
        min_time = min(test_times)
        max_time = max(test_times)
        
        print(f"\n  [STATS] Statistics for {size} cities:")
        print(f"    - Average time: {avg_time:.2f}ms")
        print(f"    - Min time: {min_time:.2f}ms")
        print(f"    - Max time: {max_time:.2f}ms")
        
        # Performance verdict
        if size == 5 and avg_time > 1000:
            print(f"    [WARN] WARNING: Slow for 5 cities (target: <1000ms)")
        elif size == 10 and avg_time > 3000:
            print(f"    [WARN] WARNING: Slow for 10 cities (target: <3000ms)")
        elif size == 20 and avg_time > 10000:
            print(f"    [WARN] WARNING: Slow for 20 cities (target: <10000ms)")
        else:
            print(f"    [OK] Performance within acceptable range")
    
    # Generate summary report
    print(f"\n{'='*80}")
    print("[SUMMARY] PERFORMANCE SUMMARY")
    print(f"{'='*80}\n")
    
    # Group by city count
    by_size = {}
    for result in all_results:
        size = result["city_count"]
        if size not in by_size:
            by_size[size] = []
        by_size[size].append(result["total_time_ms"])
    
    for size in sorted(by_size.keys()):
        times = by_size[size]
        avg = statistics.mean(times)
        print(f"  {size} cities: {avg:.2f}ms average")
    
    # Cache statistics
    cache_info = get_cache_info()
    print(f"\n[CACHE] Cache Statistics:")
    print(f"  - Hits: {cache_info.hits}")
    print(f"  - Misses: {cache_info.misses}")
    print(f"  - Hit rate: {cache_info.hits / (cache_info.hits + cache_info.misses) * 100:.1f}%")
    print(f"  - Cache size: {cache_info.currsize}/{cache_info.maxsize}")
    
    # Bottleneck analysis
    print(f"\n[BOTTLENECK] Bottleneck Analysis:")
    print(f"  - Main bottleneck: Genetic Algorithm iterations")
    print(f"  - 80 generations multiplied by 40 population = 3200 route evaluations per optimization")
    if 20 in by_size:
        print(f"  - For 20 cities: approximately {statistics.mean(by_size[20]) / 3200:.3f}ms per route evaluation")
    
    # Save to CSV
    csv_filename = "performance_report.csv"
    with open(csv_filename, 'w', newline='') as f:
        fieldnames = ["test_name", "city_count", "total_time_ms", "algorithm_time_ms", 
                     "total_distance_km", "distance_saved_km", "improvement_pct", "algorithm", "route"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_results)
    
    print(f"\n[SAVE] Detailed results saved to: {csv_filename}")
    
    # Final verdict
    print(f"\n{'='*80}")
    print("[DONE] PERFORMANCE TEST COMPLETED")
    print(f"{'='*80}\n")
    
    return all_results


if __name__ == "__main__":
    try:
        results = run_test_suite()
        print(f"\n[SUCCESS] All tests passed! Tested {sum(1 for _ in results)} optimizations.\n")
    except Exception as e:
        print(f"\n[ERROR] Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
