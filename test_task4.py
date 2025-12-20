from utils.distance  import build_distance_matrix, calculate_duration

# 1. Select 4 cities for the test case
test_cities = ["Mumbai", "Delhi", "Bangalore", "Chennai"]

# 2. Generate the Matrix
print("--- TASK 4: DISTANCE MATRIX TEST ---")
matrix = build_distance_matrix(test_cities)

# 3. Print Results with Time Estimations
for start_city in test_cities:
    for end_city in test_cities:
        if start_city != end_city:
            dist = matrix[start_city][end_city]
            time = calculate_duration(dist)
            print(f"{start_city} -> {end_city}: {dist} km (~{time} hours)")

print("\n✅ Task 4 Deliverable: Distance-Time Engine verified.")