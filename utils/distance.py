"""
Distance calculation with geopy + caching + fallback logic.
"""

from functools import lru_cache
from geopy.distance import geodesic
import math

from .cities import get_city_coords

# LRU Cache: stores last 1000 distance calculations
@lru_cache(maxsize=1000)
def calculate_distance(city1: str, city2: str) -> float:
    """
    Calculate great-circle distance between two cities using Haversine formula.
    
    Args:
        city1: First city name
        city2: Second city name
    
    Returns:
        Distance in kilometers (float)
    
    Raises:
        ValueError: If either city not found
    
    Example:
        >>> calculate_distance("Mumbai", "Delhi")
        1153.45
    """
    # Same city = 0 distance
    if city1 == city2:
        return 0.0
    
    # Try primary method: geopy
    try:
        coords1 = get_city_coords(city1)
        coords2 = get_city_coords(city2)
        distance = geodesic(coords1, coords2).kilometers
        return round(distance, 2)
    
    except Exception as e:
        # Fallback to manual Haversine calculation
        print(f"Warning: Geopy failed ({e}), using fallback Haversine")
        return _haversine_distance(city1, city2)


def _haversine_distance(city1: str, city2: str) -> float:
    """
    Fallback: Manual Haversine formula if geopy fails.
    
    Formula:
        a = sin²(Δlat/2) + cos(lat1) × cos(lat2) × sin²(Δlon/2)
        c = 2 × atan2(√a, √(1−a))
        distance = R × c  (R = Earth radius = 6371 km)
    """
    lat1, lon1 = get_city_coords(city1)
    lat2, lon2 = get_city_coords(city2)
    
    # Convert to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    # Earth radius in kilometers
    R = 6371.0
    distance = R * c
    
    return round(distance, 2)


def calculate_duration(distance_km: float, speed_kmph: int = 60) -> float:
    """
    Calculate estimated travel time.
    
    Args:
        distance_km: Distance in kilometers
        speed_kmph: Average speed (default 60 km/h)
    
    Returns:
        Duration in hours (float)
    
    Example:
        >>> calculate_duration(300, 60)
        5.0
    """
    if distance_km <= 0:
        return 0.0
    
    duration = distance_km / speed_kmph
    return round(duration, 2)


def build_distance_matrix(cities: list[str]) -> dict[str, dict[str, float]]:
    """
    Build complete distance matrix for all city pairs.
    Uses cached distances for performance.
    
    Args:
        cities: List of city names
    
    Returns:
        Nested dict: {city1: {city2: distance, ...}, ...}
    
    Example:
        >>> build_distance_matrix(["Mumbai", "Delhi", "Pune"])
        {
            "Mumbai": {"Mumbai": 0.0, "Delhi": 1153.45, "Pune": 148.58},
            "Delhi": {"Mumbai": 1153.45, "Delhi": 0.0, "Pune": 1234.67},
            "Pune": {"Mumbai": 148.58, "Delhi": 1234.67, "Pune": 0.0}
        }
    """
    matrix = {}
    
    for city1 in cities:
        matrix[city1] = {}
        for city2 in cities:
            matrix[city1][city2] = calculate_distance(city1, city2)
    
    return matrix


def normalize_distance(distance_km: float, max_distance: float = 3000.0) -> float:
    """
    Normalize distance to [0, 1] range for AI processing.
    
    Args:
        distance_km: Raw distance in km
        max_distance: Maximum expected distance (default 3000 km for India)
    
    Returns:
        Normalized value between 0 and 1
    
    Example:
        >>> normalize_distance(1500, 3000)
        0.5
    """
    return min(distance_km / max_distance, 1.0)


def clear_cache():
    """Clear the distance calculation cache."""
    calculate_distance.cache_clear()


def get_cache_info():
    """Get cache statistics for monitoring."""
    return calculate_distance.cache_info()
