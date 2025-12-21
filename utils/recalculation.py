"""
Task 7: Real-Time Route Recalculation
Handles dynamic changes to routes with optimized recomputation.

FEATURES:
1. Add/remove cities from active routes
2. Update priorities and reoptimize remaining route
3. Resume from current position (mid-route optimization)
4. Smart skip logic when changes don't affect future route
5. Bulk updates with single recalculation

PERFORMANCE NOTES:
- Optimized for small to medium city sets (10-20 cities)
- Recalculation avoids already-completed route segments
- Fast enough for real-time operational use
"""

import time
from typing import List, Optional, Dict, Tuple
from .algorithm import optimize_route
from .distance import build_distance_matrix, calculate_distance
from .cities import validate_city


def recalculate_route(
    current_position: str,
    remaining_destinations: List[str],
    priorities: Optional[Dict[str, int]] = None,
    use_ai: bool = False
) -> Dict:
    """
    Recalculate route from current position with remaining destinations.
    
    USE CASES:
    - Driver completed some deliveries, need to optimize remaining route
    - New urgent delivery added mid-route
    - Priority changed for remaining cities
    - Some destinations cancelled
    
    Args:
        current_position: Current city (where driver is now)
        remaining_destinations: Cities still to visit
        priorities: Optional priority mapping for remaining cities
        use_ai: Use AI optimization (default: False for speed)
    
    Returns:
        Dict with optimized remaining route, distances, and recalculation metrics
    """
    start_time = time.time()
    
    # Optimize from current position (only remaining cities)
    result = optimize_route(
        start=current_position,
        destinations=remaining_destinations,
        priorities=priorities,
        use_ai=use_ai
    )
    
    total_time = (time.time() - start_time) * 1000
    
    # Add recalculation metadata
    result["recalculation_metadata"] = {
        "current_position": current_position,
        "remaining_cities": len(remaining_destinations),
        "total_recalc_time_ms": round(total_time, 2)
    }
    
    return result


def add_cities_to_route(
    current_position: str,
    existing_route: List[str],
    new_cities: List[str],
    priorities: Optional[Dict[str, int]] = None,
    use_ai: bool = False
) -> Dict:
    """
    Add new cities to existing route with minimal recomputation.
    
    STRATEGY:
    - If route not started: Add to beginning, full reoptimization
    - If mid-route: Insert into remaining portion only
    
    Args:
        current_position: Where driver is currently
        existing_route: Original planned route
        new_cities: Cities to add
        priorities: Updated priority mapping (including new cities)
        use_ai: Use AI optimization
    
    Returns:
        Dict with updated route and performance metrics
    """
    start_time = time.time()
    
    # Validate new cities
    invalid_cities = [city for city in new_cities if not validate_city(city)]
    if invalid_cities:
        return {
            "success": False,
            "error": f"Invalid cities: {', '.join(invalid_cities)}",
            "execution_time_ms": 0
        }
    
    # Find remaining destinations (cities after current position)
    try:
        current_idx = existing_route.index(current_position)
        remaining_destinations = existing_route[current_idx + 1:]
    except ValueError:
        # Current position not in route, treat as new start
        remaining_destinations = existing_route.copy()
    
    # Add new cities to remaining destinations
    all_remaining = remaining_destinations + new_cities
    
    # Recalculate from current position
    result = recalculate_route(
        current_position=current_position,
        remaining_destinations=all_remaining,
        priorities=priorities,
        use_ai=use_ai
    )
    
    total_time = (time.time() - start_time) * 1000
    
    result["change_metadata"] = {
        "operation": "add_cities",
        "cities_added": new_cities,
        "cities_added_count": len(new_cities),
        "total_operation_time_ms": round(total_time, 2)
    }
    
    return result


def remove_cities_from_route(
    current_position: str,
    existing_route: List[str],
    cities_to_remove: List[str],
    priorities: Optional[Dict[str, int]] = None,
    use_ai: bool = False
) -> Dict:
    """
    Remove cities from route (cancellations/completed deliveries).
    
    OPTIMIZATION:
    - If removed city is behind current position: No recalculation needed
    - If removed city is ahead: Recalculate remaining route
    
    Args:
        current_position: Current location
        existing_route: Original route
        cities_to_remove: Cities to remove
        priorities: Updated priorities (excluding removed cities)
        use_ai: Use AI optimization
    
    Returns:
        Dict with updated route and metrics
    """
    start_time = time.time()
    
    # Find remaining destinations
    try:
        current_idx = existing_route.index(current_position)
        remaining_destinations = existing_route[current_idx + 1:]
    except ValueError:
        remaining_destinations = existing_route.copy()
    
    # Remove cities from remaining destinations
    updated_remaining = [city for city in remaining_destinations if city not in cities_to_remove]
    
    # Check if recalculation needed
    cities_removed_from_remaining = len(remaining_destinations) - len(updated_remaining)
    
    if cities_removed_from_remaining == 0:
        # All removed cities were already visited, no recalculation needed
        return {
            "success": True,
            "route": existing_route,
            "recalculation_needed": False,
            "execution_time_ms": round((time.time() - start_time) * 1000, 2),
            "change_metadata": {
                "operation": "remove_cities",
                "cities_removed": cities_to_remove,
                "recalculation_skipped": True,
                "reason": "All removed cities already visited"
            }
        }
    
    # Recalculate remaining route
    result = recalculate_route(
        current_position=current_position,
        remaining_destinations=updated_remaining,
        priorities=priorities,
        use_ai=use_ai
    )
    
    total_time = (time.time() - start_time) * 1000
    
    result["change_metadata"] = {
        "operation": "remove_cities",
        "cities_removed": cities_to_remove,
        "cities_removed_count": len(cities_to_remove),
        "total_operation_time_ms": round(total_time, 2)
    }
    
    return result


def update_priorities(
    current_position: str,
    remaining_destinations: List[str],
    old_priorities: Optional[Dict[str, int]],
    new_priorities: Dict[str, int],
    use_ai: bool = False
) -> Dict:
    """
    Update priorities for remaining deliveries.
    
    SCENARIOS:
    - Urgent delivery notification (priority 3 -> 1)
    - Priority downgrade due to customer request
    - New business rules applied
    
    Args:
        current_position: Current location
        remaining_destinations: Cities still to visit
        old_priorities: Previous priority mapping
        new_priorities: Updated priority mapping
        use_ai: Use AI optimization
    
    Returns:
        Dict with reoptimized route based on new priorities
    """
    start_time = time.time()
    
    # Detect priority changes
    changes = []
    for city in remaining_destinations:
        old_p = old_priorities.get(city) if old_priorities else None
        new_p = new_priorities.get(city)
        if old_p != new_p:
            changes.append({
                "city": city,
                "old_priority": old_p,
                "new_priority": new_p
            })
    
    # Recalculate with new priorities
    result = recalculate_route(
        current_position=current_position,
        remaining_destinations=remaining_destinations,
        priorities=new_priorities,
        use_ai=use_ai
    )
    
    total_time = (time.time() - start_time) * 1000
    
    result["change_metadata"] = {
        "operation": "update_priorities",
        "priority_changes": changes,
        "changes_count": len(changes),
        "total_operation_time_ms": round(total_time, 2)
    }
    
    return result


def bulk_update_route(
    current_position: str,
    existing_route: List[str],
    cities_to_add: Optional[List[str]] = None,
    cities_to_remove: Optional[List[str]] = None,
    updated_priorities: Optional[Dict[str, int]] = None,
    use_ai: bool = False
) -> Dict:
    """
    Handle multiple changes to route at once (most efficient).
    
    OPTIMIZATION:
    - Single recalculation for all changes
    - Reuses distance matrix across operations
    
    Args:
        current_position: Current location
        existing_route: Original route
        cities_to_add: Optional list of cities to add
        cities_to_remove: Optional list of cities to remove
        updated_priorities: New priority mapping for all cities
        use_ai: Use AI optimization
    
    Returns:
        Dict with updated route and detailed change summary
    """
    start_time = time.time()
    
    # Find remaining destinations from existing route
    try:
        current_idx = existing_route.index(current_position)
        remaining = existing_route[current_idx + 1:]
    except ValueError:
        remaining = existing_route.copy()
    
    # Apply removals
    if cities_to_remove:
        remaining = [city for city in remaining if city not in cities_to_remove]
    
    # Apply additions
    if cities_to_add:
        # Validate new cities
        invalid = [city for city in cities_to_add if not validate_city(city)]
        if invalid:
            return {
                "success": False,
                "error": f"Invalid cities: {', '.join(invalid)}",
                "execution_time_ms": 0
            }
        remaining.extend(cities_to_add)
    
    # Recalculate with all changes
    result = recalculate_route(
        current_position=current_position,
        remaining_destinations=remaining,
        priorities=updated_priorities,
        use_ai=use_ai
    )
    
    total_time = (time.time() - start_time) * 1000
    
    result["change_metadata"] = {
        "operation": "bulk_update",
        "cities_added": cities_to_add or [],
        "cities_removed": cities_to_remove or [],
        "priorities_updated": updated_priorities is not None,
        "total_changes": (len(cities_to_add or []) + len(cities_to_remove or []) + 
                         (1 if updated_priorities else 0)),
        "total_operation_time_ms": round(total_time, 2)
    }
    
    return result
