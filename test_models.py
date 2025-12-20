"""
Test script to validate data models (Task 3).
Run this to verify models work correctly before building API.
"""

from models import OptimizeRequest, OptimizeResponse, OptimizationDetails, RouteStep, ErrorResponse
from pydantic import ValidationError
import json


def test_valid_request():
    """Test valid request with all fields."""
    print("=" * 60)
    print("TEST 1: Valid Request (3 cities with priorities)")
    print("=" * 60)
    
    data = {
        "start": "Mumbai",
        "destinations": ["Pune", "Bangalore", "Chennai"],
        "priorities": {
            "Bangalore": 1,
            "Chennai": 2,
            "Pune": 3
        },
        "options": {"improve": True}
    }
    
    try:
        request = OptimizeRequest(**data)
        print("✅ PASS - Request validated successfully")
        print(f"   Start: {request.start}")
        print(f"   Destinations: {request.destinations}")
        print(f"   Priorities: {request.priorities}")
        print(f"   Options: {request.options}")
    except ValidationError as e:
        print(f"❌ FAIL - {e}")
    print()


def test_simple_request():
    """Test minimal request (no priorities)."""
    print("=" * 60)
    print("TEST 2: Simple Request (no priorities)")
    print("=" * 60)
    
    data = {
        "start": "Mumbai",
        "destinations": ["Pune", "Bangalore"]
    }
    
    try:
        request = OptimizeRequest(**data)
        print("✅ PASS - Simple request validated")
        print(f"   Start: {request.start}")
        print(f"   Destinations: {request.destinations}")
        print(f"   Priorities: {request.priorities} (defaults to None)")
    except ValidationError as e:
        print(f"❌ FAIL - {e}")
    print()


def test_max_cities():
    """Test maximum city limit (20 destinations)."""
    print("=" * 60)
    print("TEST 3: Maximum Cities (20 destinations)")
    print("=" * 60)
    
    # Create 20 unique cities (repeat with numbers to avoid duplicates)
    cities = [f"City{i}" for i in range(1, 21)]
    
    data = {
        "start": "Mumbai",
        "destinations": cities  # Exactly 20
    }
    
    try:
        request = OptimizeRequest(**data)
        print(f"✅ PASS - 20 cities accepted")
        print(f"   Destinations count: {len(request.destinations)}")
    except ValidationError as e:
        print(f"❌ FAIL - {e}")
    print()


def test_too_many_cities():
    """Test exceeding city limit (should fail)."""
    print("=" * 60)
    print("TEST 4: Too Many Cities (21 destinations - should FAIL)")
    print("=" * 60)
    
    cities = ["Delhi"] * 21  # 21 cities
    
    data = {
        "start": "Mumbai",
        "destinations": cities
    }
    
    try:
        request = OptimizeRequest(**data)
        print("❌ FAIL - Should have rejected 21 cities")
    except ValidationError as e:
        print(f"✅ PASS - Correctly rejected: {e.errors()[0]['msg']}")
    print()


def test_duplicate_cities():
    """Test duplicate city handling (should fail)."""
    print("=" * 60)
    print("TEST 5: Duplicate Cities (should FAIL)")
    print("=" * 60)
    
    data = {
        "start": "Mumbai",
        "destinations": ["Pune", "Bangalore", "Pune"]  # Duplicate Pune
    }
    
    try:
        request = OptimizeRequest(**data)
        print("❌ FAIL - Should have rejected duplicate cities")
    except ValidationError as e:
        print(f"✅ PASS - Correctly rejected: {e.errors()[0]['msg']}")
    print()


def test_invalid_priority():
    """Test invalid priority value (should fail)."""
    print("=" * 60)
    print("TEST 6: Invalid Priority (should FAIL)")
    print("=" * 60)
    
    data = {
        "start": "Mumbai",
        "destinations": ["Pune", "Bangalore"],
        "priorities": {
            "Bangalore": 5  # Invalid - must be 1, 2, or 3
        }
    }
    
    try:
        request = OptimizeRequest(**data)
        print("❌ FAIL - Should have rejected priority 5")
    except ValidationError as e:
        print(f"✅ PASS - Correctly rejected: {e.errors()[0]['msg']}")
    print()


def test_empty_destinations():
    """Test empty destination list (should fail)."""
    print("=" * 60)
    print("TEST 7: Empty Destinations (should FAIL)")
    print("=" * 60)
    
    data = {
        "start": "Mumbai",
        "destinations": []
    }
    
    try:
        request = OptimizeRequest(**data)
        print("❌ FAIL - Should have rejected empty destinations")
    except ValidationError as e:
        print(f"✅ PASS - Correctly rejected: {e.errors()[0]['msg']}")
    print()


def test_valid_response():
    """Test valid response model."""
    print("=" * 60)
    print("TEST 8: Valid Response Model")
    print("=" * 60)
    
    data = {
        "success": True,
        "route": ["Mumbai", "Pune", "Bangalore", "Chennai"],
        "totalDistanceKm": 1847.32,
        "estimatedHours": 30.79,
        "summary": "Optimized route visiting 3 cities covering 1847 km.",
        "optimization": {
            "algorithm": "Nearest Neighbor",
            "calculationTimeMs": 187.5,
            "savedDistanceKm": 312.0,
            "improvementPercentage": 14.4,
            "citiesProcessed": 4
        },
        "mapsLink": "https://www.google.com/maps/dir/Mumbai/Pune/Bangalore/Chennai"
    }
    
    try:
        response = OptimizeResponse(**data)
        print("✅ PASS - Response validated successfully")
        print(f"   Route: {response.route}")
        print(f"   Distance: {response.totalDistanceKm} km")
        print(f"   Time: {response.estimatedHours} hours")
        print(f"   Algorithm: {response.optimization.algorithm}")
        print(f"   Savings: {response.optimization.savedDistanceKm} km ({response.optimization.improvementPercentage}%)")
    except ValidationError as e:
        print(f"❌ FAIL - {e}")
    print()


def test_error_response():
    """Test error response model."""
    print("=" * 60)
    print("TEST 9: Error Response Model")
    print("=" * 60)
    
    data = {
        "error": "INVALID_CITY",
        "message": "City 'Bangalor' not found. Did you mean 'Bangalore'?",
        "details": {
            "invalidCity": "Bangalor",
            "suggestions": ["Bangalore"]
        }
    }
    
    try:
        error = ErrorResponse(**data)
        print("✅ PASS - Error response validated")
        print(f"   Error: {error.error}")
        print(f"   Message: {error.message}")
        print(f"   Details: {error.details}")
        print(f"   Success: {error.success} (always False)")
    except ValidationError as e:
        print(f"❌ FAIL - {e}")
    print()


def test_route_steps():
    """Test route steps with priority labels."""
    print("=" * 60)
    print("TEST 10: Route Steps with Priority Badges")
    print("=" * 60)
    
    steps = [
        {
            "order": 1,
            "city": "Mumbai",
            "distanceFromPrevKm": 0,
            "cumulativeDistanceKm": 0,
            "priority": None,
            "priorityLabel": "🟢 START"
        },
        {
            "order": 2,
            "city": "Bangalore",
            "distanceFromPrevKm": 980.5,
            "cumulativeDistanceKm": 980.5,
            "priority": 1,
            "priorityLabel": "🔴 URGENT"
        },
        {
            "order": 3,
            "city": "Chennai",
            "distanceFromPrevKm": 346.2,
            "cumulativeDistanceKm": 1326.7,
            "priority": 2,
            "priorityLabel": "🟡 MEDIUM"
        }
    ]
    
    try:
        route_steps = [RouteStep(**step) for step in steps]
        print("✅ PASS - Route steps validated")
        for step in route_steps:
            print(f"   {step.order}. {step.city} - {step.priorityLabel} (+{step.distanceFromPrevKm} km)")
    except ValidationError as e:
        print(f"❌ FAIL - {e}")
    print()


def test_json_serialization():
    """Test JSON export (for API responses)."""
    print("=" * 60)
    print("TEST 11: JSON Serialization")
    print("=" * 60)
    
    request_data = {
        "start": "Mumbai",
        "destinations": ["Pune", "Bangalore"],
        "priorities": {"Bangalore": 1, "Pune": 2}
    }
    
    try:
        request = OptimizeRequest(**request_data)
        json_output = request.model_dump_json(indent=2)
        print("✅ PASS - JSON serialization successful")
        print("   JSON Output:")
        print(json_output)
    except Exception as e:
        print(f"❌ FAIL - {e}")
    print()


if __name__ == "__main__":
    print("\n")
    print("🧪 DATA MODELS VALIDATION TEST SUITE")
    print("Task 3: Testing Pydantic models for Route Optimization API")
    print("\n")
    
    # Run all tests
    test_valid_request()
    test_simple_request()
    test_max_cities()
    test_too_many_cities()
    test_duplicate_cities()
    test_invalid_priority()
    test_empty_destinations()
    test_valid_response()
    test_error_response()
    test_route_steps()
    test_json_serialization()
    
    print("=" * 60)
    print("✅ ALL TESTS COMPLETED")
    print("=" * 60)
    print("\nModels are ready for use in FastAPI endpoints (Task 8)")
    print("\nNext step: Implement optimization algorithm (Task 5)")
    print()
