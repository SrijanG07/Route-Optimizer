# 📊 Data Models & Schemas
## Task 3: Data Models, Validation, and Sample Payloads

**Tech Stack:** Python + FastAPI + Pydantic  
**Date:** December 20, 2025

---

## 🔷 Pydantic Models

### 1. City Model (Optional - for future DB)

```python
class City(BaseModel):
    name: str
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
```

### 2. Priority Enum

```python
from enum import IntEnum

class Priority(IntEnum):
    """
    Delivery priority levels.
    Lower number = higher priority (visited first).
    """
    HIGH = 1      # Urgent delivery (SLA < 24 hours)
    MEDIUM = 2    # Standard delivery (SLA 24-48 hours)
    LOW = 3       # Flexible delivery (SLA > 48 hours)
    
    @classmethod
    def get_weight(cls, priority: int) -> float:
        """
        Convert priority to optimization weight.
        Higher weight = visit earlier.
        """
        weights = {
            cls.HIGH: 10.0,    # 10x preference
            cls.MEDIUM: 2.0,   # 2x preference
            cls.LOW: 1.0       # baseline
        }
        return weights.get(priority, 1.0)
```

**Priority Logic:**
- **HIGH (1):** Visited first, even if longer route
- **MEDIUM (2):** Visited after HIGH, balanced with distance
- **LOW (3):** Visited last, purely distance-optimized

---

### HIGH = 1
    MEDIUM = 2
    LOW = 3
``` 
    class Config:
        json_schema_extra = {
            "example": {
                "from": "2025-12-21T08:00:00Z",
                "to": "2025-12-21T14:00:00Z"
            }
        }
```

**Time Window Rules:**
- Must be ISO 8601 format with timezone
- `to` must be after `from`
- Must be in the future (not past)
- Window must be realistic (≥ 1 hour recommended)

---

### 4. Delivery Request Model (Input)

```python
from pydantic import BaseModel, Field, validator
from typing import List, Dict, Optional

class OptimizationOptions(BaseModel):
    """Configuration options for route optimization."""
    improve: bool = Field(True, description="Run 2-Opt optimization after Nearest Neighbor")
    max_iterations: int = Field(50, ge=1, le=1000, description="Max 2-Opt iterations")
    assume_speed_kmph: int = Field(60, ge=10, le=150, description="Average travel speed for ETA")
    

class TimeWindow(BaseModel):
    from_time: datetime = Field(..., alias="from")
    to_time: datetime = Field(..., alias="to")
    
    @validator('to_time')
    def validate_time_range(cls, v, values):
        if 'from_time' in values and v <= values['from_time']:
            raise ValueError("'to' must be after 'from'")
        return v
```

### 4. Delivery Request Model (INPUTe 1, 2, or 3."""
        if v:
            for city, priority in v.items():
                if priority not in [1, 2, 3]:
                    raise ValueError(f"Priority for {city} must be 1 (HIGH), 2 (MEDIUM), or 3 (LOW)")
        return v
    
    @validator('weights')
    def validate_positive_weights(cls, v):
        """Ensure weights are positive."""
        if v:
            for city, weight in v.items():
                if weight <= 0:
                    raise ValueError(f"Weight for {city} must be positive")
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "start": "Mumbai",
                "destinations": ["Pune", "Bangalore", "Chennai", "Hyderabad"],
                "priorities": {
                    "Bangalore": 1,
                    "Chennai": 2,
                    "Hyderabad": 3,
                    "Pune": 3
                },
                "timeWindows": {
                    "Bangalore": {
                        "from": "2025-12-21T08:00:00Z",
                        "to": "2025-12-21T14:00:00Z"
                    }
class OptimizationOptions(BaseModel):
    improve: bool = True
    max_iterations: int = Field(50, ge=1, le=1000)
    assume_speed_kmph: int = Field(60, ge=10, le=150)
    
class DeliveryRequest(BaseModel):
    start: str = Field(..., min_length=2, max_length=50)
    destinations: List[str] = Field(..., min_items=1, max_items=20)
    priorities: Optional[Dict[str, int]] = None
    timeWindows: Optional[Dict[str, TimeWindow]] = None
    weights: Optional[Dict[str, float]] = None
    options: Optional[OptimizationOptions] = Field(default_factory=OptimizationOptions)
    
    @validator('destinations')
    def validate_unique_cities(cls, v, values):
        if len(v) != len(set(v)):
            raise ValueError("Destinations must be unique")
        if 'start' in values and values['start'] in v:
            raise ValueError("Start city cannot be in destinations")
        return v
    
    @validator('priorities')
    def validate_priority_values(cls, v):
        if v:
            for city, priority in v.items():
                if priority not in [1, 2, 3]:
                    raise ValueError(f"Priority for {city} must be 1, 2, or 3")
        return v
```                 "total_duration_hours": 47.4,
                    "cities_visited": 4,
                    "algorithm_time_seconds": 0.42,
                    "improvement_percent": 15.3,
                    "distance_saved_km": 513.8
                },
                "algorithm": "Nearest Neighbor + 2-Opt + Priority Sorting",
                "summary": "Your route has been optimized to prioritize Bangalore (high priority) for delivery by 9:24 AM, within the requested time window. The route saves 513.8 km (15.3%) compared to a random order, reducing fuel costs by approximately ₹15,414.",
                "warnings": []
            }
        }
```

---

## 📝 Sample JSON Payloads

### Example 1: Basic Route (No Constraints)

**Request:**
```json
{
  "start": "Delhi",
  "destinations": ["Jaipur", "Ahmedabad", "Mumbai"]
}
```

**Response:**
```json
{
  "success": true,
  "route": ["Delhi", "Jaipur", "Ahmedabad", "Mumbai"],
  "segments": [
    {
      "from_city": "Delhi",
      "to_city": "Jaipur",
      "distance_km": 280.5,
      "estimated_duration_hours": 4.68,
      "arrival_time": null,
      "priority": null,
      "within_time_window": null
    },
    {
      "from_city": "Jaipur",
      "to_city": "Ahmedabad",
      "distance_km": 635.2,
      "estimated_duration_hours": 10.59,
      "arrival_time": null,
      "priority": null,
      "within_time_window": null
    },
    {
      "from_city": "Ahmedabad",
      "to_city": "Mumbai",
      "distance_km": 534.8,
      "estimated_duration_hours": 8.91,
      "arrival_time": null,
      "priority": null,
      "within_time_window": null
    }
  ],
  "metrics": {
    "total_distance_km": 1450.5,
    "total_duration_hours": 24.18,
    "cities_visited": 3,
    "algorithm_time_seconds": 0.12,
    "improvement_percent": null,
    "distance_saved_km": null
  },
  "algorithm": "Nearest Neighbor",
  "summary": "Your route from Delhi covering 3 cities has been optimized to minimize travel distance. Total distance: 1,450.5 km, estimated time: 24.2 hours at 60 km/h average speed.",
  "warnings": []
}
```

class RouteSegment(BaseModel):
    from_city: str
    to_city: str
    distance_km: float = Field(..., gt=0)
    estimated_duration_hours: float = Field(..., gt=0)
    arrival_time: Optional[datetime] = None
    priority: Optional[int] = None
    within_time_window: Optional[bool] = None
```

### 6. Route Response Model (OUTPUT6.4,
      "arrival_time": null,
      "priority": 1,
      "within_time_window": null
    },
    {
      "from_city": "Bangalore",
      "to_city": "Chennai",
      "distance_km": 346.4,
      "estimated_duration_hours": 5.77,
      "arrival_time": null,
      "priority": 2,
      "within_time_window": null
    },
    {
      "from_city": "Chennai",
      "to_city": "Hyderabad",
      "distance_km": 626.8,
      "estimated_duration_hours": 10.45,
      "arrival_time": null,
      "priority": 3,
      "within_time_window": null
    },
    {
      "from_city": "Hyderabad",
class RouteMetrics(BaseModel):
    total_distance_km: float
    total_duration_hours: float
    cities_visited: int
    algorithm_time_seconds: float
    improvement_percent: Optional[float] = None
    distance_saved_km: Optional[float] = None

class RouteResponse(BaseModel):
    success: bool
    route: List[str]
    segments: List[RouteSegment]
    metrics: RouteMetrics
    algorithm: str
    summary: str
    warnings: Optional[List[str]] = Field(default_factory=list)ove": true,
    "max_iterations": 100,
    "assume_speed_kmph": 60
  }
}
```

**Response:**
```json
{
  "success": true,
  "route": ["Mumbai", "Bangalore", "Chennai", "Pune"],
  "segments": [
    {
      "from_city": "Mumbai",
      "to_city": "Bangalore",
      "distance_km": 984.2,
      "estimated_duration_hours": 16.4,
      "arrival_time": "2025-12-21T09:24:00Z",
      "priority": 1,
      "within_time_window": true
    },
    {
      "from_city": "Bangalore",
      "to_city": "Chennai",
      "distance_km": 346.4,
      "estimated_duration_hours": 5.77,
      "arrival_time": "2025-12-21T15:11:00Z",
      "priority": 2,
      "within_time_window": null
    },
    {
      "from_city": "Chennai",
      "to_city": "Pune",
      "distance_km": 1168.5,
      "estimated_duration_hours": 19.47,
      "arrival_time": "2025-12-22T10:39:00Z",
      "priority": 3,
      "within_time_window": true
    }
  ],
  "metrics": {
    "total_distance_km": 2499.1,
    "total_duration_hours": 41.64,
    "cities_visited": 3,ment_percent": 8.7,
    "distance_saved_km": 238.4
  },
  "algorithm": "Nearest Neighbor + 2-Opt + Priority + Time Windows",
  "summary": "Your route has been optimized to prioritize Bangalore (high priority) for delivery by 9:24 AM, within the requested 8 AM-2 PM time window. Chennai is visited next, followed by Pune within its 10 AM-6 PM window on Dec 22. Total weight: 275.5 kg across all deliveries. The route saves 238.4 km (8.7%) compared to baseline, reducing fuel costs by approximately ₹7,152.",
  "warnings": []
}
```

---
 (simplified):**
```json
{
  "success": true,
  "route": ["Delhi", "Jaipur", "Ahmedabad", "Mumbai"],
  "metrics": {
    "total_distance_km": 1450.5,
    "algorithm_time_seconds": 0.12
  },
  "algorithm": "Nearest Neighbor"
}
```

### Example 2: With Priorities + Time Windows
### Current Capacity (MVP)
- **Max cities per request:** 20
- **Complexity:** O(n²) for Nearest Neighbor + 2-Opt
- **Computation time:** < 1 second for n=20

### Scaling to 50 Cities
```python
# Update DeliveryRequest model:
destinations: List[str] = Field(..., min_items=1, max_items=50)

# Update optimization settings:
max_iterations: int = Field(100, ge=1, le=500)  # More iterations for larger problems
```
- **Expected time:** 2-5 seconds
- **Algorithm:** Still feasible with Nearest Neighbor + 2-Opt
- **Memory:** O(n²) distance matrix = 2,500 entries (acceptable)

### Scaling to 100 Cities
```python
# Switch to more efficient algorithm:
# - Use Christofides algorithm (O(n³))
# - Or Genetic Algorithm with parallel evaluation
# - Or Lin-Kernighan heuristic (O(n²log n))
```
- **Expected time:** 10-30 seconds
- **Needs:** Better algorithm (2-Opt becomes too slow)
- **Memory:** 10,000 distance entries (still acceptable)

### Scaling to 1000+ Cities
```python
# Use production-grade algorithms:
# - Google OR-Tools (constraint programming)
# - Concorde TSP Solver (exact solution)
# - Gurobi optimizer (commercial)
```
- **Expected time:** Minutes to hours
- **Needs:** Database for distance caching
- **Needs:** Asynchronous processing (Celery + Redis)
- **Needs:** Distributed computing (split problem into regions)

### Database Schema (Future)

```python
# When scaling beyond in-memory:
class CityDB(BaseModel):
    id: int
    name: str
    latitude: float
    longitude: float
    country: str
    state: str
    population: int
    created_at: datetime

class DistanceCacheDB(BaseModel):
    id: int
    city1_id: int
    city2_id: int
    distance_km: float
    calculated_at: datetime
```

**Database Choice:**
- **PostgreSQL** - Relational data, PostGIS for geography
- **Redis** - Distance caching (key: "Mumbai-Delhi", value: 1453.2)
- **MongoDB** - Flexible schema for route history

---

## 🔧 Implementation File Structure

```
models/
├── __init__.py
├── city.py          # City model
├── priority.py      # Priority enum
├── time_window.py   # TimeWindow model
├── request.py       # DeliveryRequest model
├── response.py      # RouteResponse, RouteSegment, RouteMetrics
└── validation.py    # Custom validators
```

**Example: models/request.py**
```python
from pydantic import BaseModel, Field, validator
from typing import List, Dict, Optional
from .time_window import TimeWindow
from .priority import Priority

class OptimizationOptions(BaseModel):
    improve: bool = Field(True, description="Run 2-Opt optimization")
    max_iterations: int = Field(50, ge=1, le=1000)
    assume_speed_kmph: int = Field(60, ge=10, le=150)

class DeliveryRequest(BaseModel):
    start: str = Field(..., min_length=2, max_length=50)
    destinations: List[str] = Field(..., min_items=1, max_items=20)
    priorities: Optional[Dict[str, int]] = None
    timeWindows: Optional[Dict[str, TimeWindow]] = None
    weights: Optional[Dict[str, float]] = None
    options: Optional[OptimizationOptions] = Field(default_factory=OptimizationOptions)
    
    @validator('destinations')
    def validate_unique_cities(cls, v, values):
        if len(v) != len(set(v)):
            raise ValueError("Destinations must be unique")
        if 'start' in values and values['start'] in v:
            raise ValueError("Start city cannot be in destinations")
        return v
    
    @validator('priorities')
    def validate_priority_values(cls, v):
        if v:
            for city, priority in v.items():
                if priority not in [Priority.HIGH, Priority.MEDIUM, Priority.LOW]:
                    raise ValueError(f"Invalid priority for {city}")
        return v
```

---

## ✅ Task 3 Deliverables Checklist
"Bangalore": 1, "Chennai": 2, "Pune": 3},
  "timeWindows": {
    "Bangalore": {
      "from": "2025-12-21T08:00:00Z",
      "to": "2025-12-21T14:00:00Z"
    }
  },
  "weights": {"Bangalore": 150.5, "Chennai": 75.0, "Pune": 50.0}
}
```

**Response (simplified):**
```json
{
  "success": true,
  "route": ["Mumbai", "Bangalore", "Chennai", "Pune"],
  "metrics": {
    "total_distance_km": 2499.1,
    "improvement_percent": 8.7
  },
  "algorithm": "NN + 2-Opt + Priority + Time Windows",
  "summary": "Bangalore delivered within 8am-2pm window. Total weight: 275.5kg."
}
```

### Example 3: Validation Error"Pune": 5{
    "loc": ["body", "priorities"],
    "msg": "Priority for Pune must be 1, 2, or 3"
  }| Field | Rule | Error |
|-------|------|-------|
| `start` | Valid city | "City not found" |
| `destinations` | 1-20 unique cities | "Must be unique" |
| `priorities` | 1, 2, or 3 | "Invalid priority" |
| `timeWindows.to` | After `from` | "'to' must be after 'from'" |
| `weights` | Positive | "Must be positive" |

---

## ✅ Task 3 Complete

- [x] City, Priority, TimeWindow models
- [x] DeliveryRequest (input) with validation
- [x] RouteResponse (output) with metrics
- [x] 3 sample JSON payloads (basic, priority, time windows)
- [x] Error examples (validation, impossible time window)
- [x] Validation rules table

**Status:** Ready for implementation | **Estimated time:** 3-4 hours