"""Enhanced distance verification with detailed output"""
import sys
sys.path.insert(0, 'c:\\Users\\srija\\Downloads\\hackathon')

from utils.distance import calculate_distance, get_distance_method

# Routes from user
route_a = ["Mumbai", "Pune", "Indore", "Jaipur", "Delhi", "Bhopal", "Bangalore", "Chennai"]
route_b = ["Mumbai", "Pune", "Indore", "Bhopal", "Jaipur", "Delhi", "Bangalore", "Chennai"]

print("=" * 80)
print("ROAD DISTANCE CALCULATION TEST (OpenRouteService API)")
print("=" * 80)
print()

print("ROUTE A (AI Optimizer chose this):")
print("  " + " → ".join(route_a))
print()
total_a = 0
for i in range(len(route_a) - 1):
    d = calculate_distance(route_a[i], route_a[i+1])
    total_a += d
    method = get_distance_method()
    print(f"  {route_a[i]:15} → {route_a[i+1]:15} : {d:8.2f} km  [{method}]")

print(f"\n  {'TOTAL ROUTE A:':40} {total_a:8.2f} km")
print(f"  System previously showed: 3,364.64 km (haversine)")
print(f"  User expected: ~5,744 km (road distance)")
print()
print()

print("ROUTE B (Better geographic progression):")
print("  " + " → ".join(route_b))
print()
total_b = 0
for i in range(len(route_b) - 1):
    d = calculate_distance(route_b[i], route_b[i+1])
    total_b += d
    method = get_distance_method()
    print(f"  {route_b[i]:15} → {route_b[i+1]:15} : {d:8.2f} km  [{method}]")

print(f"\n  {'TOTAL ROUTE B:':40} {total_b:8.2f} km")
print(f"  User expected: ~5,104 km (road distance)")
print()
print()

print("=" * 80)
print("COMPARISON")
print("=" * 80)
print(f"Route A (AI chose): {total_a:,.2f} km")
print(f"Route B (Better):   {total_b:,.2f} km")
print()

if total_b < total_a:
    savings = total_a - total_b
    pct = (savings / total_a) * 100
    print(f"✅ Route B is BETTER by {savings:.2f} km ({pct:.1f}% shorter)")
    print(f"   This confirms user's analysis that Route B is the better route!")
else:
    diff = total_b - total_a
    pct = (diff / total_b) * 100
    print(f"❌ Route A is better by {diff:.2f} km ({pct:.1f}% shorter)")
    print(f"   This contradicts user's analysis - needs investigation")

print()
print("Expected difference: Route B should be ~640 km shorter than Route A")
print(f"Actual difference:   Route B is {abs(total_a - total_b):.2f} km {'shorter' if total_b < total_a else 'longer'}")
print()

# Statistics from user's analysis
print("=" * 80)
print("USER'S MANUAL CALCULATIONS (for comparison)")
print("=" * 80)
print("Route A (User calculated): ~5,744 km")
print("Route B (User calculated): ~5,104 km")
print(f"Route A (System):          {total_a:,.2f} km  (Diff: {abs(total_a - 5744):.0f} km)")
print(f"Route B (System):          {total_b:,.2f} km  (Diff: {abs(total_b - 5104):.0f} km)")
print()
