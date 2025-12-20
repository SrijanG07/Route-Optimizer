# 🏗️ System Architecture & Design
## Task 2: Architecture, Algorithms, and Tech Stack

**Tech Stack:** Python + FastAPI + Nearest Neighbor + 2-Opt  
**Timeline:** 48 Hours | **Date:** December 20-22, 2025

---

## 🏗️ System Architecture

### High-Level Architecture Diagram

```
┌─────────────┐
│   User/UI   │
└──────┬──────┘
       │ HTTP POST /api/optimize
       ▼
┌─────────────────────────────┐
│     FastAPI Server          │
│  ┌─────────────────────┐   │
│  │  Input Validator    │
│  ┌─────────────────────┐   │
│  │  Distance Engine    │   │ ← Geopy + hardcoded coords
│  └──────────┬──────────┘   │
│             ▼               │
│  ┌─────────────────────┐   │
│  │ Optimization Engine │   │ ← NN + 2-Opt algorithms
│  │  • Nearest Neighbor │   │
│  │  • 2-Opt Improver   │   │
│  │  • Priority Handler │   │
│  │  • Time Windows     │   │
│  └──────────┬──────────┘   │
│             ▼               │
│  ┌─────────────────────┐   │
│  │   AI Summary Gen    │   │ ← Template or LLM API
│  └──────────┬──────────┘   │
└─────────────┼───────────────┘
              ▼
       ┌──────────────┐
       │ JSON Response│
       └──────────────┘
```

### Component Breakdown

**Components:**
- **Input Validator:** FastAPI + Pydantic (validate cities, priorities)
- **Distance Engine:** Geopy with LRU caching (no external API)
- **Optimization Engine:** Nearest Neighbor → 2-Opt → Priority sorting
- **AI Summary:** Template or LLM API (explains route decisions)

## 🔄 API Flow

### Request-Response Flow Diagram

```
1. User Input
   ↓
2. FastAPI receives POST /api/optimize
   ↓
3. Pydantic validates request body
   ├─ Valid? → Continue
   └─ Invalid? → Return 400 error
   ↓
4. Distance Engine calculates all distances
   ├─ Check cache first
   └─ Calculate missing distances
   ↓
5. Optimization Engine processes
   ├─ Stage 1: Nearest Neighbor (initial route)
   ├─ Stage 2: 2-Opt optimization (improve)
   ├─ Stage 3: Priority handling (reorder)
   └─ Stage 4: Time window validation (Day 2)
   ↓
6. AI Summary Generator creates explanation
   ├─ Template: "Your route saves X km..."
   └─ OR LLM API: "I optimized your route by..."
   ↓
7. Build JSON response with:
   ├─ Optimized route array
   ├─ Distance metrics
   ├─ Performance stats
   └─ AI summary
   ↓
8. Return HTTP 200 with JSON
```

### Data Flow Example

**Input:**
```json
**POST /api/optimize**
1. Validate request (Pydantic)
2. Calculate distances (Geopy + cache)
3. Run Nearest Neighbor → 2-Opt → Priority sort
4. Generate AI summary
5. Return JSON response
### Data Validation
**Pydantic 2.5.0** (built into FastAPI)
- ✅ **Why:** Type hints → automatic validation
- ✅ **Why:** JSON schema generation
- ✅ **Why:** Clear error messages

### Server Runtime
**Uvicorn 0.24.0** (ASGI server)
- ✅ **Why:** Required for FastAPI async support
- ✅ **Why:** Hot reload during development

### Development Tools
- **python-dotenv 1.0.0:** Environment variables (.env file)
- **pytest:** Unit testing (optional)

### Frontend (Optional)
- **HTML/CSS/JavaScript:** Plain vanilla (no framework)
- **Leaflet.js:** Interactive map visualization
- **Tailwind CSS:** Quick styling via CDN

### No Database Required
- Hardcoded city coordinates in Python dict
- In-memory caching (LRU cache decorator)
- No persistence needed for MVP

---

## 🧠 Algorithm Selection & Reasoning

### Problem Classification

**Traveling Salesman Problem (TSP) Variant**
- **NP-Hard Complexity:** No polynomial-time exact algorithm exists
- **Computational Challenge:**
  - 10 cities = 10! = 3,628,800 possible routes
  - 15 cities = 15! = 1.3 trillion routes
  - 20 cities = 20! = 2.4 × 10¹⁸ routes (would take centuries)
- **Goal:** Find near-optimal solution in < 1 second

### Multi-Stage Algorithm Design

#### **Stage 1: Nearest Neighbor (Constructive Heuristic)**

**How it Works:**
1. Start at origin city
2. Repeatedly visit the closest unvisited city
3. Continue until all cities visited

**Pseudocode:**
```python
def nearest_neighbor(start, cities, distances):
    route = [start]
    unvisited = set(cities)
    current = start
    
    while unvisited:
        nearest = min(unvisited, key=lambda c: distances[current][c])
        route.append(nearest)
        unvisited.remove(nearest)
        current = nearest
    
    return route
```

**Complexity Analysis:**
- **Time:** O(n²) - for each of n cities, check all remaining cities
- **Space:** O(n) - store route and unvisited set
- **Performance:** Finds solution in < 1ms for 10 cities

**Quality:**
- ✅ Fast and simple
| Layer | Technology | Why? |
|-------|-----------|------|
| **Backend** | FastAPI 0.104.1 | Auto docs, Pydantic validation, fastest Python framework |
| **Distance** | Geopy 2.4.0 | Haversine formula, offline, no API costs |
| **Algorithms** | Custom Python | Nearest Neighbor + 2-Opt (simple, hackathon-friendly) |
| **AI Summary** | OpenAI/Claude API | Natural language explanations (optional) |
| **Server** | Uvicorn 0.24.0 | ASGI runtime for FastAPI |
| **Frontend** | HTML/JS + Leaflet | Map visualization (optional) |
| **Database** | None | 10 hardcoded cities, in-memory caching |inimal effort
- Standard in TSP literature

---

#### **Stage 3: Priority Handling (Constraint Satisfaction)**

**How it Works:**
1. Sort cities by priority (1 > 2 > 3)
2. Optimize within each priority group
3. High-priority cities visited first

**Weighted Scoring:**
```python
score = distance × (1 / priority_weight)
# Example:
# Priority 1: weight = 10 → score = distance × 0.1
# Priority 2: weight = 2  → score = distance × 0.5
# Priority 3: weight = 1  → score = distance × 1.0
```

**Why Chosen:**
- Balances business needs with optimization
- Simple pre-sorting step
- Maintains route quality

---

#### **Stage 4: Time Window Validation (Day 2 Feature)**

**How it Works:**
1. Calculate arrival time at each city (distance ÷ speed)
2. Check if arrival falls within [from, to] window
3. If violation, reorder route to prioritize constrained cities

**Pseudocode:**
```python
def validate_time_windows(route, distances, time_windows, speed=60):
    current_time = datetime.now()
    for city in route:
        travel_time = distances[prev_city][city] / speed
        arrival_time = current_time + timedelta(hours=travel_time)
        
        if city in time_windows:
            if not (time_windows[city]['from'] <= arrival_time <= time_windows[city]['to']):
                # Reorder route to visit this city earlier
                route = prioritize_city(route, city)
        
        current_time = arrival_time
    return route
```

**Problem:** Traveling Salesman Problem (NP-Hard)
- 10 cities = 3.6M routes | 20 cities = 2.4 × 10¹⁸ routes
- **Goal:** Find near-optimal solution in < 1 second

### Chosen Algorithms
```

**Why Cache?**
- Avoid recalculating Mumbai↔Delhi 100+ times
- O(1) lookups after first calculation
- Significant speedup for 2-Opt (checks same pairs repeatedly)

---

## ✅ Task 2 Deliverables Checklist

- [x] **Architecture Diagram** - Complete system flow with all components
- [x] **API Flow Diagram** - Request-response pipeline with data flow
- [x] **Algorithm Selection Reasoning** - Detailed comparison of TSP algorithms
- [x] **ML vs Heuristic Justification** - Why this qualifies as AI/ML project
- [x] **Tech Stack** - Complete technology choices with rationale
- [x] **Data Layer Design** - Hardcoded cities with caching strategy

---

## 🎯 Ready for Implementation

All architectural decisions are made. Next steps:
1. Set up Python project structure
2. Implement distance engine (utils/distance.py)
3. Implement Nearest Neighbor algorithm
4. Implement 2-Opt optimization
5. Build FastAPI endpoints
6. Create simple UI
7. Test and demo

Estimated time: **24-36 hours** for full MVP with time windows.

---

**Document Version:** 1.0  
**Last Updated:** December 20, 2025  
**Status:** ✅ Complete - Ready for judges
**1. Nearest Neighbor (O(n²))**
- Greedy: always visit closest unvisited city
- 30 min to implement, 75-90% optimal
- Fast baseline

**2. 2-Opt (O(n²) per iteration)**
- Swap edge pairs to eliminate crossings
- 1 hour to implement, 10-25% improvement
- Standard TSP optimization

**3. Priority Sorting**
- Visit high-priority cities first
- Simple constraint handling

### Why Not Others?

| Algorithm | Why Not? |
|-----------|----------|
| Genetic Algorithm | 8-12 hours, unpredictable |
| Simulated Annealing | Requires parameter tuning |
| A* Search | Wrong problem (pathfinding ≠ TSP) |
| Ant Colony | Too complex for hackathon |Why This is AI/ML

**1. NP-Hard Problem**
- Brute force impossible for n > 15 cities
- AI uses intelligent exploration, not exhaustive search

**2. ML Techniques**
- **Heuristic search** - like beam search in ML
- **Local search** - like gradient descent (iterative improvement)
- **Constraint satisfaction** - multi-objective optimization

**3. Self-Optimization**
- Learns better routes through 2-Opt iterations
- Adapts to any city configuration automatically
- No manual tuning required

**4. Traditional vs AI**

| Traditional | Our AI Approach |
|-------------|-----------------|
| Fixed rules | Adaptive heuristics |
| Manual tuning | Self-optimizing |
| O(n!) brute force | O(n²) intelligent search |

**5. Future ML Path**
- Phase 2: Neural networks for traffic prediction
- Phase 3: Reinforcement learning for dynamic routing
- Phase 4: Graph neural networks for large-scale problems**10 Hardcoded Indian Cities** (no database needed):

```python
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
    "Lucknow": {"lat": 26.8467, "lon": 80.9462}
}
```

**Distance Caching:**
```python
@lru_cache(maxsize=1000)
def calculate_distance(city1, city2):
    return geopy.distance.distance(...).kilometers
```

---

## ✅ Task 2 Complete

- [x] Architecture diagram with all layers
- [x] API flow (request → validation → optimization → response)
- [x] Algorithm selection (Nearest Neighbor + 2-Opt vs alternatives)
- [x] ML justification (NP-Hard problem, heuristic search, self-optimization)
- [x] Tech stack (FastAPI, Geopy, custom algorithms)

**Status:** Ready for implementation | **Estimated time:** 24-36 hour