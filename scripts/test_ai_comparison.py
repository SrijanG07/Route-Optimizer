"""Test AI summary with GA comparison"""
from utils.ai_summary import generate_ai_summary

# Simulate result with GA comparison
test_result = {
    "route": ["Mumbai", "Pune", "Indore", "Bhopal", "Jaipur", "Delhi", "Bangalore", "Chennai"],
    "total_distance": 4195.0,
    "distance_saved": 1825.0,
    "improvement_percentage": 30.3,
    "algorithm": "Evolutionary Optimizer",
    "priorities": {"Bangalore": 1, "Delhi": 2},
    "greedy_distance": 4835.0,  # Greedy found this
    "ai_improvement_over_greedy": 13.2,  # AI is 13.2% better
    "ai_saved_over_greedy": 640.0  # AI saved 640 km vs greedy
}

print("=" * 80)
print("AI SUMMARY TEST - WITH GA vs GREEDY COMPARISON")
print("=" * 80)
print()
print("Testing with Genetic Algorithm route that beat greedy by 640 km...")
print()

summary = generate_ai_summary(test_result)

print("✅ AI-Generated Summary:")
print()
print(summary)
print()
print("=" * 80)
print()
print("The summary should mention:")
print("  ✓ How GA/AI approach explored route variations")
print("  ✓ That it found a better solution than greedy nearest-neighbor")
print("  ✓ The 640 km improvement over greedy approach")
print("  ✓ The evolutionary optimization advantages")
