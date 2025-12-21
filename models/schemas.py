"""Pydantic schemas for API request/response validation."""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict, List
from datetime import datetime


# ========== Recalculation Request Models ==========

class RecalculateRequest(BaseModel):
    """Request model for route recalculation."""
    current_position: str = Field(..., description="Current position/city")
    remaining_destinations: List[str] = Field(..., description="Remaining cities to visit")
    priorities: Optional[Dict[str, int]] = Field(None, description="Priority mapping for cities")
    use_ai: bool = Field(False, description="Use AI optimization")


class AddCitiesRequest(BaseModel):
    """Request model for adding cities to route."""
    current_position: str = Field(..., description="Current position/city")
    existing_route: List[str] = Field(..., description="Current route")
    new_cities: List[str] = Field(..., description="Cities to add")
    priorities: Optional[Dict[str, int]] = Field(None, description="Priority mapping")
    use_ai: bool = Field(False, description="Use AI optimization")


class RemoveCitiesRequest(BaseModel):
    """Request model for removing cities from route."""
    current_position: str = Field(..., description="Current position/city")
    existing_route: List[str] = Field(..., description="Current route")
    cities_to_remove: List[str] = Field(..., description="Cities to remove")


# ========== Main Optimization Models ==========

# ===== INPUT MODELS (What users send TO the API) =====

class OptimizeRequest(BaseModel):
    """
    Delivery request model for route optimization.
    
    Sample JSON 1 (Simple - 3 cities):
    {
        "start": "Mumbai",
        "destinations": ["Pune", "Bangalore", "Chennai"]
    }
    
    Sample JSON 2 (With Priorities):
    {
        "start": "Mumbai",
        "destinations": ["Pune", "Bangalore", "Chennai", "Hyderabad"],
        "priorities": {
            "Bangalore": 1,
            "Chennai": 2,
            "Pune": 3,
            "Hyderabad": 3
        },
        "options": {
            "improve": true
        }
    }
    
    Sample JSON 3 (Maximum Cities - Edge Case):
    {
        "start": "Mumbai",
        "destinations": ["Delhi", "Bangalore", "Chennai", "Kolkata", 
                        "Hyderabad", "Pune", "Ahmedabad", "Jaipur", "Lucknow"],
        "priorities": {
            "Bangalore": 1,
            "Delhi": 1,
            "Chennai": 2
        }
    }
    """
    start: str = Field(
        ..., 
        description="Starting city name (must be valid Indian city)",
        examples=["Mumbai", "Delhi", "Bangalore"]
    )
    
    destinations: List[str] = Field(
        ..., 
        min_length=1,
        description="List of destination cities to visit (1-20 cities)",
        examples=[["Pune", "Bangalore", "Chennai"]]
    )
    
    priorities: Optional[Dict[str, int]] = Field(
        default=None,
        description="Priority levels for cities: 1=urgent/high, 2=medium, 3=low. Cities without priority default to 3.",
        examples=[{"Bangalore": 1, "Chennai": 2, "Pune": 3}]
    )
    
    options: Optional[Dict[str, bool]] = Field(
        default_factory=lambda: {"use_ai": False},
        description="Optimization options: use_ai=true runs AI optimization",
        examples=[{"use_ai": True}]
    )
    
    @field_validator('destinations')
    @classmethod
    def validate_destinations(cls, v):
        """Ensure scalability: limit to 20 cities for reasonable performance."""
        if len(v) < 1:
            raise ValueError("Must have at least 1 destination city")
        if len(v) > 20:
            raise ValueError("Maximum 20 destinations allowed for performance. Got: {}".format(len(v)))
        # Remove duplicates while preserving order
        seen = set()
        unique = []
        for city in v:
            if city not in seen:
                seen.add(city)
                unique.append(city)
        if len(unique) != len(v):
            raise ValueError("Duplicate cities found in destinations. Each city should appear only once.")
        return unique
    
    @field_validator('priorities')
    @classmethod
    def validate_priorities(cls, v):
        """Validate priority levels are 1, 2, or 3."""
        if v is None:
            return v
        for city, priority in v.items():
            if priority not in [1, 2, 3]:
                raise ValueError(f"Priority for '{city}' must be 1 (high), 2 (medium), or 3 (low). Got: {priority}")
        return v
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "start": "Mumbai",
                    "destinations": ["Pune", "Bangalore", "Chennai"],
                    "priorities": {"Bangalore": 1, "Chennai": 2, "Pune": 3},
                    "options": {"improve": True}
                }
            ]
        }
    }


# ===== OUTPUT MODELS (What API returns TO users) =====

class RouteStep(BaseModel):
    """Individual step in the optimized route."""
    order: int = Field(..., description="Stop number in sequence (1, 2, 3...)")
    city: str = Field(..., description="City name")
    distanceFromPrevKm: float = Field(..., description="Distance from previous city in km")
    cumulativeDistanceKm: float = Field(..., description="Total distance from start")
    priority: Optional[int] = Field(None, description="Priority level (1=high, 2=medium, 3=low)")
    priorityLabel: Optional[str] = Field(None, description="Human-readable priority (🔴 URGENT, 🟡 MEDIUM, 🟢 LOW)")


class OptimizationDetails(BaseModel):
    """Optimization algorithm performance metrics."""
    algorithm: str = Field(..., description="Algorithm used (e.g., 'Nearest Neighbor + 2-Opt')")
    calculationTimeMs: float = Field(..., description="Time taken to compute route in milliseconds")
    savedDistanceKm: Optional[float] = Field(None, description="Distance saved compared to random/baseline route")
    improvementPercentage: Optional[float] = Field(None, description="Percentage improvement over baseline")
    citiesProcessed: int = Field(..., description="Number of cities in optimization")
    baselineDistanceKm: Optional[float] = Field(None, description="Baseline (random route) distance for comparison")
    greedyDistanceKm: Optional[float] = Field(None, description="Greedy algorithm distance for comparison")
    aiImprovementOverGreedy: Optional[float] = Field(None, description="AI improvement percentage over Greedy")
    aiSavedOverGreedy: Optional[float] = Field(None, description="Distance saved by AI vs Greedy")


class OptimizeResponse(BaseModel):
    """
    Route optimization response model.
    
    Sample JSON Response:
    {
        "success": true,
        "route": ["Mumbai", "Pune", "Bangalore", "Chennai", "Hyderabad"],
        "totalDistanceKm": 1847.32,
        "estimatedHours": 30.79,
        "summary": "Optimized route visiting 4 cities covering 1847 km. High-priority delivery to Bangalore scheduled first. Estimated savings: 312 km (14%) compared to unoptimized route.",
        "routeSteps": [
            {"order": 1, "city": "Mumbai", "distanceFromPrevKm": 0, "cumulativeDistanceKm": 0, "priority": null, "priorityLabel": "START"},
            {"order": 2, "city": "Pune", "distanceFromPrevKm": 148.5, "cumulativeDistanceKm": 148.5, "priority": 3, "priorityLabel": "🟢 LOW"},
            {"order": 3, "city": "Bangalore", "distanceFromPrevKm": 850.2, "cumulativeDistanceKm": 998.7, "priority": 1, "priorityLabel": "🔴 URGENT"}
        ],
        "optimization": {
            "algorithm": "Nearest Neighbor + 2-Opt",
            "calculationTimeMs": 187,
            "savedDistanceKm": 312,
            "improvementPercentage": 14.4,
            "citiesProcessed": 5
        },
        "mapsLink": "https://www.google.com/maps/dir/Mumbai/Pune/Bangalore/Chennai/Hyderabad",
        "timestamp": "2025-12-20T10:30:45.123456Z"
    }
    """
    success: bool = Field(..., description="Whether optimization succeeded")
    route: List[str] = Field(..., description="Optimized route as ordered list of cities")
    totalDistanceKm: float = Field(..., description="Total distance of optimized route in kilometers")
    estimatedHours: float = Field(..., description="Estimated travel time in hours (assumes 60 km/h average)")
    summary: str = Field(..., description="AI-generated human-readable explanation of the route")
    
    routeSteps: Optional[List[RouteStep]] = Field(
        default=None,
        description="Detailed breakdown of each stop with distances and priorities"
    )
    
    optimization: OptimizationDetails = Field(..., description="Optimization performance metrics")
    
    mapsLink: Optional[str] = Field(
        default=None,
        description="Google Maps link for visual route display"
    )
    
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="UTC timestamp when route was calculated"
    )
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "success": True,
                    "route": ["Mumbai", "Pune", "Bangalore", "Chennai"],
                    "totalDistanceKm": 1847.32,
                    "estimatedHours": 30.79,
                    "summary": "Optimized route visiting 3 cities covering 1847 km.",
                    "optimization": {
                        "algorithm": "Nearest Neighbor",
                        "calculationTimeMs": 187,
                        "savedDistanceKm": 312,
                        "improvementPercentage": 14.4,
                        "citiesProcessed": 4
                    },
                    "mapsLink": "https://www.google.com/maps/dir/Mumbai/Pune/Bangalore/Chennai",
                    "timestamp": "2025-12-20T10:30:45.123456Z"
                }
            ]
        }
    }


class ErrorResponse(BaseModel):
    """Error response model for API failures."""
    success: bool = Field(default=False, description="Always false for errors")
    error: str = Field(..., description="Error type/code")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[Dict] = Field(default=None, description="Additional error details")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "success": False,
                    "error": "INVALID_CITY",
                    "message": "City 'Bangalor' not found. Did you mean 'Bangalore'?",
                    "details": {
                        "invalidCity": "Bangalor",
                        "availableCities": ["Mumbai", "Delhi", "Bangalore", "Chennai"]
                    },
                    "timestamp": "2025-12-20T10:30:45.123456Z"
                }
            ]
        }
    }


# ===== EDGE CASE TEST PAYLOADS =====

# Edge Case 1: Single Destination (Minimum)
SAMPLE_REQUEST_SINGLE = {
    "start": "Mumbai",
    "destinations": ["Pune"]
}

# Edge Case 2: Maximum Cities (20 destinations)
SAMPLE_REQUEST_MAX = {
    "start": "Mumbai",
    "destinations": ["Delhi", "Bangalore", "Chennai", "Kolkata", "Hyderabad", 
                    "Pune", "Ahmedabad", "Jaipur", "Lucknow", "Mumbai",
                    "Delhi", "Bangalore", "Chennai", "Kolkata", "Hyderabad",
                    "Pune", "Ahmedabad", "Jaipur", "Lucknow", "Mumbai"]
}

# Edge Case 3: Priority Conflict (Multiple cities with same priority)
SAMPLE_REQUEST_PRIORITY_CONFLICT = {
    "start": "Mumbai",
    "destinations": ["Pune", "Bangalore", "Chennai", "Hyderabad"],
    "priorities": {
        "Bangalore": 1,
        "Chennai": 1,  # Same priority as Bangalore
        "Pune": 1,     # All cities have priority 1
        "Hyderabad": 1
    }
}

# Edge Case 4: No Priorities (All default to 3)
SAMPLE_REQUEST_NO_PRIORITY = {
    "start": "Delhi",
    "destinations": ["Mumbai", "Bangalore", "Chennai", "Kolkata"],
    "options": {"improve": True}
}
