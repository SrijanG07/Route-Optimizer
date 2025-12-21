"""
Quick test to verify priority system is working correctly.
Run after restarting the server.
"""

import requests
import json

API_URL = "http://localhost:8000"

def test_priority_system():
    print("=" * 80)
    print("PRIORITY SYSTEM TEST")
    print("=" * 80)
    print()
    
    # Test case: Bangalore should appear first (Priority 1), then Chennai (Priority 2), 
    # then Pune and Hyderabad (Priority 3)
    test_data = {
        "start": "Mumbai",
        "destinations": ["Pune", "Bangalore", "Chennai", "Hyderabad"],
        "priorities": {
            "Bangalore": 1,    # URGENT - Should be first
            "Chennai": 2,       # MEDIUM - Should be second
            "Pune": 3,          # LOW
            "Hyderabad": 3      # LOW
        },
        "options": {
            "use_ai": True
        }
    }
    
    print("📋 Test Configuration:")
    print(f"   Start: {test_data['start']}")
    print(f"   Destinations: {test_data['destinations']}")
    print(f"   Priorities:")
    for city, priority in test_data['priorities'].items():
        priority_label = {1: "URGENT", 2: "MEDIUM", 3: "LOW"}[priority]
        print(f"      {city}: {priority} ({priority_label})")
    print()
    
    print("🚀 Sending request to /api/optimize...")
    response = requests.post(f"{API_URL}/api/optimize", json=test_data)
    
    if response.status_code != 200:
        print(f"❌ ERROR: Request failed with status {response.status_code}")
        print(response.text)
        return False
    
    result = response.json()
    route = result.get("route", [])
    
    print(f"✅ Response received")
    print()
    print("=" * 80)
    print("RESULTS:")
    print("=" * 80)
    print(f"📍 Optimized Route: {' → '.join(route)}")
    print(f"🛣️  Total Distance: {result.get('totalDistanceKm', 0):.2f} km")
    print(f"⏱️  Algorithm: {result.get('optimization', {}).get('algorithm', 'Unknown')}")
    print()
    
    # Verify priority order
    print("=" * 80)
    print("PRIORITY VERIFICATION:")
    print("=" * 80)
    
    # Find positions in route (skip start city)
    route_without_start = route[1:]
    bangalore_pos = route_without_start.index("Bangalore") + 1 if "Bangalore" in route_without_start else -1
    chennai_pos = route_without_start.index("Chennai") + 1 if "Chennai" in route_without_start else -1
    pune_pos = route_without_start.index("Pune") + 1 if "Pune" in route_without_start else -1
    hyderabad_pos = route_without_start.index("Hyderabad") + 1 if "Hyderabad" in route_without_start else -1
    
    print(f"   Bangalore (Priority 1): Position {bangalore_pos}")
    print(f"   Chennai (Priority 2):   Position {chennai_pos}")
    print(f"   Pune (Priority 3):      Position {pune_pos}")
    print(f"   Hyderabad (Priority 3): Position {hyderabad_pos}")
    print()
    
    # Check if priorities are respected
    issues = []
    
    if bangalore_pos > chennai_pos:
        issues.append(f"❌ FAIL: Bangalore (P1, pos {bangalore_pos}) should come before Chennai (P2, pos {chennai_pos})")
    else:
        print(f"✅ PASS: Bangalore (P1) comes before Chennai (P2)")
    
    if bangalore_pos > pune_pos or bangalore_pos > hyderabad_pos:
        issues.append(f"❌ FAIL: Bangalore (P1, pos {bangalore_pos}) should come before low-priority cities")
    else:
        print(f"✅ PASS: Bangalore (P1) comes before all low-priority cities")
    
    if chennai_pos > pune_pos or chennai_pos > hyderabad_pos:
        issues.append(f"❌ FAIL: Chennai (P2, pos {chennai_pos}) should come before low-priority cities")
    else:
        print(f"✅ PASS: Chennai (P2) comes before all low-priority cities")
    
    print()
    
    if issues:
        print("=" * 80)
        print("❌ TEST FAILED - PRIORITY VIOLATIONS FOUND:")
        print("=" * 80)
        for issue in issues:
            print(f"   {issue}")
        print()
        print("🔧 The priority system needs further debugging.")
        return False
    else:
        print("=" * 80)
        print("✅ TEST PASSED - ALL PRIORITIES RESPECTED!")
        print("=" * 80)
        print()
        print("🎉 Priority system is working correctly!")
        return True


if __name__ == "__main__":
    try:
        success = test_priority_system()
        exit(0 if success else 1)
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Cannot connect to server. Make sure it's running at http://localhost:8000")
        print("   Run: python main.py")
        exit(1)
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
