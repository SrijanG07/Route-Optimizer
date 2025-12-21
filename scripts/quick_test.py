"""Quick distance check"""
import sys
sys.path.insert(0, 'c:\\Users\\srija\\Downloads\\hackathon')

from utils.distance import calculate_distance

# Routes from user
route_a = ["Mumbai", "Pune", "Indore", "Jaipur", "Delhi", "Bhopal", "Bangalore", "Chennai"]
route_b = ["Mumbai", "Pune", "Indore", "Bhopal", "Jaipur", "Delhi", "Bangalore", "Chennai"]

print("ROUTE A:")
total_a = 0
for i in range(len(route_a) - 1):
    d = calculate_distance(route_a[i], route_a[i+1])
    total_a += d
    print(f"{route_a[i]} -> {route_a[i+1]}: {d:.2f} km")
print(f"TOTAL A: {total_a:.2f} km\n")

print("ROUTE B:")
total_b = 0
for i in range(len(route_b) - 1):
    d = calculate_distance(route_b[i], route_b[i+1])
    total_b += d
    print(f"{route_b[i]} -> {route_b[i+1]}: {d:.2f} km")
print(f"TOTAL B: {total_b:.2f} km\n")

print(f"Difference: {abs(total_a - total_b):.2f} km")
print(f"Route B is {'BETTER' if total_b < total_a else 'WORSE'} by {abs(total_a - total_b):.2f} km")
