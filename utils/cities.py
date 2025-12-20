"""
Hardcoded Indian cities with GPS coordinates.
No database required for MVP.
"""

CITIES = {
    "Mumbai": {"lat": 19.0760, "lon": 72.8777},
    "Delhi": {"lat": 28.7041, "lon": 77.1025},
    "Bangalore": {"lat": 12.9716, "lon": 77.5946},
    "Chennai": {"lat": 13.0827, "lon": 80.2707},
    "Kolkata": {"lat": 22.5726, "lon": 88.3639},
    "Hyderabad": {"lat": 17.3850, "lon": 78.4867},
    "Pune": {"lat": 18.5204, "lon": 73.8567},
    "Ahmedabad": {"lat": 23.0225, "lon": 72.5714},
    "Jaipur": {"lat": 26.9124, "lon": 75.7873},
    "Lucknow": {"lat": 26.8467, "lon": 80.9462},
    "Indore": {"lat": 22.7196, "lon": 75.8577},
    "Nagpur": {"lat": 21.1458, "lon": 79.0882},
    "Surat": {"lat": 21.1702, "lon": 72.8311},
    "Kanpur": {"lat": 26.4499, "lon": 80.3319},
    "Bhopal": {"lat": 23.2599, "lon": 77.4126},
    "Visakhapatnam": {"lat": 17.6868, "lon": 83.2185},
    "Patna": {"lat": 25.5941, "lon": 85.1376},
    "Vadodara": {"lat": 22.3072, "lon": 73.1812},
}

def get_city_coords(city_name: str) -> tuple[float, float]:
    """
    Get latitude and longitude for a city.
    
    Args:
        city_name: City name (case-sensitive)
    
    Returns:
        (latitude, longitude) tuple
    
    Raises:
        ValueError: If city not found
    """
    if city_name not in CITIES:
        raise ValueError(f"City '{city_name}' not found. Available: {list(CITIES.keys())}")
    
    city = CITIES[city_name]
    return city["lat"], city["lon"]

def validate_city(city_name: str) -> bool:
    """Check if city exists in database."""
    return city_name in CITIES

def get_all_cities() -> list[str]:
    """Get list of all available cities."""
    return list(CITIES.keys())
