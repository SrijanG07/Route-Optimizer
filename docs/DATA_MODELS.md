# Data Models Documentation

> **Pydantic Schema Reference**  
> File: `models/schemas.py`

---

## Overview

All API requests and responses use **Pydantic models** for validation and serialization. This ensures type safety, automatic validation, and auto-generated Swagger documentation.

---

## Input Models (User → API)

### 1. OptimizeRequest

**Purpose:** Main route optimization request

**Fields:**

| Field | Type | Required | Default | Validation |
|-------|------|----------|---------|------------|
| `start` | str | Yes | - | Must be valid city |
| `destinations` | List[str] | Yes | - | 1-17 unique cities |
| `priorities` | Dict[str, int] | No | `None` | Priority ∈ {1,2,3} |
| `options` | Dict[str, bool] | No | `{"use_ai": false}` | Keys: use_ai |

**Example:**
```json
{
  "start": "Mumbai",
  "destinations": ["Pune", "Bangalore", "Chennai"],
  "priorities": {
    "Bangalore": 1,
    "Chennai": 2,
    "Pune": 3
  },
  "options": {
    "use_ai": true
  }
}
```

**Validators:**
- `destinations` must have 1-17 cities (line 115-118)
- No duplicates allowed (line 119-128)
- Priorities must be 1, 2, or 3 (line 130-139)

---

### 2. RecalculateRequest

**Purpose:** Mid-route recalculation from current position

**Fields:**

| Field | Type | Required | Default |
|-------|------|----------|---------|
| `current_position` | str | Yes | - |
| `remaining_destinations` | List[str] | Yes | - |
| `priorities` | Dict[str, int] | No | `None` |
| `use_ai` | bool | No | `false` |

**Example:**
```json
{
  "current_position": "Pune",
  "remaining_destinations": ["Bangalore", "Chennai"],
  "priorities": {"Bangalore": 1},
  "use_ai": false
}
```

**Use Case:** Driver completed Mumbai→Pune, now optimizing rest of route

---

### 3. AddCitiesRequest

**Purpose:** Add new cities to existing route

**Fields:**

| Field | Type | Required | Default |
|-------|------|----------|---------|
| `current_position` | str | Yes | - |
| `existing_route` | List[str] | Yes | - |
| `new_cities` | List[str] | Yes | - |
| `priorities` | Dict[str, int] | No | `None` |
| `use_ai` | bool | No | `false` |

**Example:**
```json
{
  "current_position": "Pune",
  "existing_route": ["Mumbai", "Pune", "Bangalore"],
  "new_cities": ["Indore"],
  "priorities": {"Indore": 1},
  "use_ai": false
}
```

**Use Case:** Urgent delivery to Indore added mid-route

---

### 4. RemoveCitiesRequest

**Purpose:** Remove cities from route (cancellations)

**Fields:**

| Field | Type | Required | Default |
|-------|------|----------|---------|
| `current_position` | str | Yes | - |
| `existing_route` | List[str] | Yes | - |
| `cities_to_remove` | List[str] | Yes | - |

**Example:**
```json
{
  "current_position": "Pune",
  "existing_route": ["Mumbai", "Pune", "Bangalore", "Chennai"],
  "cities_to_remove": ["Chennai"]
}
```

**Use Case:** Chennai delivery cancelled

---

## Output Models (API → User)

### 5. OptimizeResponse

**Purpose:** Route optimization result with full metrics

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `success` | bool | Always `true` for 200 responses |
| `route` | List[str] | Optimized route (ordered cities) |
| `totalDistanceKm` | float | Sum of all city-to-city distances |
| `estimatedHours` | float | Travel time @ 60 km/h |
| `summary` | str | AI-generated explanation |
| `routeSteps` | List[RouteStep] | Detailed per-stop breakdown |
| `optimization` | OptimizationDetails | Algorithm metrics |
| `mapsLink` | str | Google Maps URL |
| `timestamp` | datetime | UTC timestamp |

**Example:**
```json
{
  "success": true,
  "route": ["Mumbai", "Bangalore", "Pune", "Chennai"],
  "totalDistanceKm": 1847.32,
  "estimatedHours": 30.79,
  "summary": "AI optimizer explored 3200 variations...",
  "optimization": {
    "algorithm": "Evolutionary Optimizer",
    "calculationTimeMs": 892,
    "savedDistanceKm": 312,
    "improvementPercentage": 14.4,
    "greedyDistanceKm": 2015,
    "aiImprovementOverGreedy": 8.3
  },
  "mapsLink": "https://www.google.com/maps/dir/Mumbai/Bangalore/Pune/Chennai",
  "timestamp": "2025-12-22T10:30:45Z"
}
```

---

### 6. RouteStep

**Purpose:** Individual stop details in route

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `order` | int | Stop number (1, 2, 3...) |
| `city` | str | City name |
| `distanceFromPrevKm` | float | Distance from previous stop |
| `cumulativeDistanceKm` | float | Total distance from start |
| `priority` | int | Priority level (1/2/3) |
| `priorityLabel` | str | Human-readable (🔴/🟡/🟢) |

**Example:**
```json
{
  "order": 2,
  "city": "Bangalore",
  "distanceFromPrevKm": 850.2,
  "cumulativeDistanceKm": 998.7,
  "priority": 1,
  "priorityLabel": "🔴 URGENT"
}
```

---

### 7. OptimizationDetails

**Purpose:** Algorithm performance metrics

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `algorithm` | str | "Nearest Neighbor" or "Evolutionary Optimizer" |
| `calculationTimeMs` | float | Time taken to compute |
| `savedDistanceKm` | float | Distance saved vs baseline (random) |
| `improvementPercentage` | float | % improvement vs baseline |
| `citiesProcessed` | int | Number of cities in route |
| `baselineDistanceKm` | float | Random route distance |
| `greedyDistanceKm` | float | Greedy algorithm result |
| `aiImprovementOverGreedy` | float | AI improvement % vs greedy |
| `aiSavedOverGreedy` | float | Distance saved vs greedy |

**Example:**
```json
{
  "algorithm": "Evolutionary Optimizer",
  "calculationTimeMs": 892,
  "savedDistanceKm": 312,
  "improvementPercentage": 14.4,
  "citiesProcessed": 5,
  "baselineDistanceKm": 2327,
  "greedyDistanceKm": 2015,
  "aiImprovementOverGreedy": 8.3,
  "aiSavedOverGreedy": 168
}
```

**Key Metrics:**
- **savedDistanceKm** = baseline - optimized
- **improvementPercentage** = (saved / baseline) × 100
- **aiImprovementOverGreedy** = (greedy - AI) / greedy × 100

---

### 8. ErrorResponse

**Purpose:** Error handling for failed requests

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `success` | bool | Always `false` for errors |
| `error` | str | Error type/code |
| `message` | str | Human-readable message |
| `details` | Dict | Additional context |
| `timestamp` | datetime | When error occurred |

**Example:**
```json
{
  "success": false,
  "error": "INVALID_CITY",
  "message": "City 'Bangalor' not found. Did you mean 'Bangalore'?",
  "details": {
    "invalidCity": "Bangalor",
    "availableCities": ["Mumbai", "Delhi", "Bangalore", ...]
  },
  "timestamp": "2025-12-22T10:30:45Z"
}
```

---

## Validation Rules

### Destination Validation
```python
@field_validator('destinations')
def validate_destinations(cls, v):
    if len(v) < 1:
        raise ValueError("Must have at least 1 destination")
    if len(v) > 20:
        raise ValueError("Maximum 20 destinations allowed")
    # Remove duplicates
    if len(set(v)) != len(v):
        raise ValueError("Duplicate cities found")
    return v
```

### Priority Validation
```python
@field_validator('priorities')
def validate_priorities(cls, v):
    if v is None:
        return v
    for city, priority in v.items():
        if priority not in [1, 2, 3]:
            raise ValueError(f"Priority must be 1, 2, or 3. Got: {priority}")
    return v
```

---

## Default Values

| Model | Field | Default | Reason |
|-------|-------|---------|--------|
| OptimizeRequest | priorities | `None` | All cities default to priority 3 |
| OptimizeRequest | options | `{"use_ai": false}` | Greedy is faster for demo |
| RecalculateRequest | priorities | `None` | Preserve existing priorities |
| RecalculateRequest | use_ai | `false` | Speed over quality for real-time |

---

## Priority Labels

| Priority | Label | Icon | Meaning |
|----------|-------|------|---------|
| 1 | URGENT | 🔴 | Must deliver ASAP |
| 2 | MEDIUM | 🟡 | Standard delivery |
| 3 | LOW | 🟢 | Flexible timing |
| null | START | 🏁 | Starting city |

---

## Schema Examples

### Edge Case 1: Single Destination
```json
{
  "start": "Mumbai",
  "destinations": ["Pune"]
}
```
**Result:** Route is trivial: ["Mumbai", "Pune"]

### Edge Case 2: All Same Priority
```json
{
  "start": "Delhi",
  "destinations": ["Mumbai", "Bangalore", "Chennai"],
  "priorities": {
    "Mumbai": 1,
    "Bangalore": 1,
    "Chennai": 1
  }
}
```
**Result:** Optimize purely by distance (no priority ordering needed)

### Edge Case 3: Mixed Priorities
```json
{
  "start": "Mumbai",
  "destinations": ["Pune", "Bangalore", "Chennai", "Hyderabad"],
  "priorities": {
    "Bangalore": 1,
    "Chennai": 2
  }
}
```
**Result:** 
- Bangalore scheduled first (priority 1)
- Chennai scheduled second (priority 2)
- Pune, Hyderabad optimized within priority 3 group

---

## Swagger UI

All models are auto-documented at **http://localhost:8000/docs**

**Features:**
- Interactive API testing
- Request/response examples
- Field validation rules
- Error codes explained

---

**Last Updated:** December 22, 2025  
**Schema File:** [models/schemas.py](file:///c:/Users/srija/Downloads/hackathon/models/schemas.py)
