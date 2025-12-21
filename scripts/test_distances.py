"""
Test script to verify actual distances for both routes.
This will help identify where the distance calculation is going wrong.
"""

from utils.distance import calculate_distance, build_distance_matrix
from utils.algorithm import optimize_route, _calculate_total_distance

# Routes from user's analysis
ROUTE_A = ["Mumbai", "Pune", "Indore", "Jaipur", "Delhi", "Bhopal", "Bangalore", "Chennai"]
ROUTE_B = ["Mumbai", "Pune", "Indore", "Bhopal", "Jaipur", "Delhi", "Bangalore", "Chennai"]

def calculate_route_distance(route):
    """Calculate total distance for a given route."""
    total = 0.0
    segments = []
    
    for i in range(len(route) - 1):
        city1 = route[i]
        city2 = route[i + 1]
        distance = calculate_distance(city1, city2)
        total += distance
        segments.append({
            "from": city1,
            "to": city2,
            "distance_km": distance
        })
    
    return total, segments

def main():
    print("=" * 80)
    print("DISTANCE CALCULATION VERIFICATION")
    print("=" * 80)
    print()
    
    # Test Route A (AI Optimized)
    print("📍 ROUTE A (AI Optimized):")
    print("   " + " → ".join(ROUTE_A))
    print()
    
    total_a, segments_a = calculate_route_distance(ROUTE_A)
    
    for seg in segments_a:
        print(f"   {seg['from']:15} → {seg['to']:15} = {seg['distance_km']:8.2f} km")
    
    print(f"\n   {'TOTAL DISTANCE':32} = {total_a:8.2f} km")
    print(f"   System reported: 3364.64 km")
    print(f"   Discrepancy: {abs(total_a - 3364.64):.2f} km ({abs(total_a - 3364.64) / total_a * 100:.1f}%)")
    print()
    print()
    
    # Test Route B (Greedy)
    print("📍 ROUTE B (Greedy - Better Route):")
    print("   " + " → ".join(ROUTE_B))
    print()
    
    total_b, segments_b = calculate_route_distance(ROUTE_B)
    
    for seg in segments_b:
        print(f"   {seg['from']:15} → {seg['to']:15} = {seg['distance_km']:8.2f} km")
    
    print(f"\n   {'TOTAL DISTANCE':32} = {total_b:8.2f} km")
    print(f"   System reported: ~3507 km (Standard)")
    print()
    print()
    
    # Comparison
    print("=" * 80)
    print("COMPARISON")
    print("=" * 80)
    print(f"Route A Distance: {total_a:.2f} km")
    print(f"Route B Distance: {total_b:.2f} km")
    print(f"Difference: {abs(total_a - total_b):.2f} km")
    
    if total_b < total_a:
        savings = total_a - total_b
        print(f"\n✅ Route B is BETTER by {savings:.2f} km ({savings / total_a * 100:.1f}% shorter)")
    else:
        print(f"\n❌ Route A is better by {total_a - total_b:.2f} km")
    
    print()
    print("Expected from user's analysis:")
    print("  Route A: ~5,744 km")
    print("  Route B: ~5,104 km")
    print("  Route B should be ~640 km shorter")
    print()
    
    # Now test with the optimization algorithm
    print("=" * 80)
    print("TESTING OPTIMIZATION ALGORITHMS")
    print("=" * 80)
    print()
    
    cities = ["Pune", "Indore", "Jaipur", "Delhi", "Bhopal", "Bangalore", "Chennai"]
    
    print("Testing Greedy Algorithm...")
    greedy_result = optimize_route(
        start="Mumbai",
        destinations=cities,
        priorities=None,
        use_ai=False
    )
    
    print(f"Greedy Route: {' → '.join(greedy_result['route'])}")
    print(f"Greedy Distance: {greedy_result['total_distance']:.2f} km")
    print()
    
    print("Testing AI Algorithm...")
    ai_result = optimize_route(
        start="Mumbai",
        destinations=cities,
        priorities=None,
        use_ai=True
    )
    
    print(f"AI Route: {' → '.join(ai_result['route'])}")
    print(f"AI Distance: {ai_result['total_distance']:.2f} km")
    print()
    
    if ai_result['total_distance'] < greedy_result['total_distance']:
        print(f"✅ AI is better by {greedy_result['total_distance'] - ai_result['total_distance']:.2f} km")
    else:
        print(f"❌ AI is WORSE by {ai_result['total_distance'] - greedy_result['total_distance']:.2f} km")
    
    print()

if __name__ == "__main__":
    main()
