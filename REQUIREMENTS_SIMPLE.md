# 🚚 Route Optimizer - Technical Requirements Document

## ⚠️ MVP SCOPE WARNING
**This document includes Day 1 + Day 2 features. For Tasks 1-4, SKIP time windows/weights.**

**Project Type:** AI/ML Route Optimization System  
**Target Users:** Logistics & Transport Companies  
**Core Technology:** FastAPI + Optimization Algorithms + AI Summaries   
**Business Impact:** 15-20% fuel savings, 99% faster route planning

---

## 🎯 The Problem
Logistics companies need to deliver to 10+ cities but can't figure out the best route manually. This wastes fuel and time.

**Our Solution:** API that takes cities as input, returns optimized route in seconds.

---

## 💡 Real-World Impact

**Current Problem:** 
- Logistics companies manually plan routes using Google Maps
- Planning 10-city route takes 2-3 hours per day
- Inefficient routes waste 15-20% fuel (~₹50,000/month per truck)
- Human planners can only handle 5 routes per day
- No optimization for priority deliveries

**Our Solution Impact:**
- Route planning: **3 hours → 2 seconds** (99.98% faster)
- Fuel savings: **15-20% reduction** (₹50,000/month per truck)
- Capacity: **Can handle 50+ routes per day** vs 5 manual routes
- Priority handling: **Automatic** high-priority delivery scheduling
- Annual savings: **₹6 lakhs per truck** in fuel + time costs

**Market Potential:**
- India has 7.5 million commercial vehicles
- Target market: 100,000+ logistics companies
- Each company operates 10-50 trucks on average

---

## 📥 API Input

```json
{
  "start": "Mumbai",
  "destinations": ["Pune", "Bangalore", "Chennai"],
  "priorities": {
    "Bangalore": 1,
    "Chennai": 2,
    "Pune": 3
  },
  "timeWindows": {
    "Bangalore": {
      "from": "2025-12-21T08:00:00Z",
      "to": "2025-12-21T14:00:00Z"
    }
  },
  "options": {
    "improve": true
  }
}
```

### Required Fields
- `start` - Starting city (string)
- `destinations` - List of cities to visit (array, 1-20 cities)

### Optional Fields
- `priorities` - City priorities (1=high, 2=medium, 3=low)
- `timeWindows` - Delivery time windows (ISO 8601 format, from/to)
- `options.improve` - Run 2-Opt optimization (true/false)

---

## 📤 API Output

```json
{
  "success": true,
  "route": ["Mumbai", "Bangalore", "Pune", "Chennai"],
  "totalDistanceKm": 1850,
  "estimatedHours": 31,
  "summary": "Optimized route visiting 3 cities. High-priority delivery to Bangalore scheduled first.",
  "optimization": {
    "algorithm": "Nearest Neighbor + 2-Opt",
    "calculationTimeMs": 245,
    "savedDistanceKm": 380,
    "improvementPercentage": 17
  }
}
```

### Key Response Fields
- `route` - Ordered list of cities to visit
- `totalDistanceKm` - Total trip distance
- `estimatedHours` - Estimated travel time
- `summary` - Human-readable explanation
- `optimization` - Performance metrics (for demo)

---

## ⚠️ Edge Cases

### 1. Single Destination
**Input:** Mumbai → [Pune]  
**Output:** Just return [Mumbai, Pune], no optimization needed

### 2. Invalid City Name
**Input:** "Mumbay" (typo)  
**Output:** HTTP 400 error with suggestions: "Did you mean Mumbai?"

### 3. Duplicate Cities
**Input:** [Pune, Bangalore, Pune]  
**Output:** Auto-remove duplicates → [Pune, Bangalore]

### 4. 10+ Cities (Performance Test)
**Input:** 15 cities  
**Output:** Complete in under 3 seconds, skip 2-Opt if needed

### 5. Multiple High Priorities (Conflict)
**Input:** Both Pune and Bangalore are priority 1  
**Output:** Visit both first, choose order by distance

### 6. Impossible Time Window
**Input:** Mumbai → [Kolkata], time window 2 hours from now  
**Output:** Warning that time window cannot be met (distance 2000 km = 33 hours travel)

---

## 💻 Quick Examples

### Simple Route (Demo This First!)

**Request:**
```json
POST /api/optimize
{
  "start": "Mumbai",
  "destinations": ["Pune", "Ahmedabad"]
}
```

**Response:**
```json
{
  "success": true,
  "route": ["Mumbai", "Pune", "Ahmedabad"],
  "totalDistanceKm": 645,
  "estimatedHours": 10.8,
  "summary": "Optimized route for 2 cities. Pune visited first (150 km), then Ahmedabad (495 km)."
}
```

**Why this route:** Pune is closer to Mumbai (150 km) than Ahmedabad (495 km), so visit it first.

---

### Priority Override (Impress Judges!)

**Request:**
```json
{
  "start": "Mumbai",
  "destinations": ["Pune", "Ahmedabad", "Bangalore"],
  "priorities": {
    "Ahmedabad": 1,
    "Pune": 3,
    "Bangalore": 3
  }
}
```

**Response:**
```json
{
  "route": ["Mumbai", "Ahmedabad", "Pune", "Bangalore"],
  "totalDistanceKm": 2145,
  "summary": "High-priority delivery to Ahmedabad scheduled first despite being farther."
}
```

**Why this route:** Priority 1 (Ahmedabad) goes first even though Pune is closer.

---

## 🏗️ System Architecture

```
┌─────────────┐
│   User/UI   │
└──────┬──────┘
       │ HTTP POST /api/optimize
       ▼
┌─────────────────────────────┐
│     FastAPI Server          │
│  ┌─────────────────────┐   │
│  │  Input Validator    │   │ ← Pydantic models
│  └──────────┬──────────┘   │
│             ▼               │
│  ┌─────────────────────┐   │
│  │  Distance Engine    │   │ ← Geopy + hardcoded coords
│  └──────────┬──────────┘   │
│             ▼               │
│  ┌─────────────────────┐   │
│  │ Optimization Engine │   │ ← NN + 2-Opt algorithms
│  │  • Nearest Neighbor │   │
│  │  • 2-Opt Improver   │   │
│  │  • Priority Handler │   │
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

**Data Flow:**
1. User sends cities → Validator checks format
2. Distance Engine calculates all city-to-city distances (cached)
3. Optimization Engine finds best route using AI algorithms
4. Summary Generator creates human-readable explanation
5. Return optimized route + performance metrics

**Key Components:**
- **Input Validator:** FastAPI + Pydantic for automatic validation
- **Distance Engine:** Geopy library with LRU caching
- **Optimization Engine:** Nearest Neighbor + 2-Opt algorithms
- **AI Summary:** Template-based or OpenAI/Claude API integration

---

## 📍 Hardcoded Cities

Use these 10 Indian cities (no database needed):

| City | Latitude | Longitude |
|------|----------|-----------|
| Mumbai | 19.0760 | 72.8777 |
| Delhi | 28.7041 | 77.1025 |
| Bangalore | 12.9716 | 77.5946 |
| Chennai | 13.0827 | 80.2707 |
| Kolkata | 22.5726 | 88.3639 |
| Hyderabad | 17.3850 | 78.4867 |
| Pune | 18.5204 | 73.8567 |
| Ahmedabad | 23.0225 | 72.5714 |
| Jaipur | 26.9124 | 75.7873 |
| Lucknow | 26.8467 | 80.9462 |

---

## 🧠 Optimization Strategy

### Multi-Stage Algorithm

**Stage 1: Heuristic Initialization (Nearest Neighbor)**
- AI analyzes spatial distribution of cities
- Constructs initial feasible solution using greedy approach
- **Complexity:** O(n²) - handles up to 20 cities efficiently
- **Time:** < 1 second for 10 cities
- **Algorithm:** Iteratively select geographically closest unvisited city

**Stage 2: Local Search Optimization (2-Opt)**
- Iteratively improves route using edge-swap technique
- Escapes local optima through systematic segment reversal
- **Complexity:** O(n²) per iteration, typically converges in 10-50 iterations
- **Improvement:** Reduces total distance by 10-25% on average
- **Algorithm:** Swap pairs of edges to eliminate route crossings

**Stage 3: Priority-Aware Constraint Handling**
- Weighted scoring function: `score = distance × (1 / priority_weight)`
- High-priority cities receive exponential preference
- Balances optimization with business constraints
- **Algorithm:** Pre-sort by priority, then optimize within groups

**AI/ML Techniques Used:**
- ✅ Greedy heuristic search (constructive approach)
- ✅ Local search metaheuristics (improvement phase)
- ✅ Constraint satisfaction optimization (priority handling)
- ✅ Graph traversal algorithms (route finding)
- ✅ Computational geometry (distance calculations)

**Why This is "AI":**
- **Learns from problem structure** - adapts to any city configuration
- **Optimization without exhaustive search** - intelligent exploration
- **Handles NP-Hard problem** - finds near-optimal solution efficiently
- **Self-improving** - 2-Opt iteratively learns better configurations

**Future ML Enhancement (Post-Hackathon):**
- Train neural network on historical delivery data
- Predict traffic patterns using time-series forecasting
- Reinforcement learning for dynamic re-routing
- Deep learning for demand prediction

---

## 🤖 What Makes This AI/ML

### Why This is an AI/ML Project

**Problem Classification:** NP-Hard Optimization (Traveling Salesman Problem variant)
- **Brute force complexity:** 10! = 3,628,800 possible routes for just 10 cities
- **20 cities:** 20! = 2.4 × 10¹⁸ permutations (would take years to compute)
- **AI approach:** Finds near-optimal solution in < 1 second using heuristics

**Machine Learning & AI Techniques:**

1. **Heuristic Search Algorithms**
   - AI learns from spatial patterns in city distribution
   - Makes intelligent decisions without trying all possibilities
   - Similar to how humans intuitively plan routes

2. **Optimization Algorithms** 
   - Iterative improvement (like gradient descent in ML)
   - Escapes local optima through strategic exploration
   - Learns better configurations through trial and refinement

3. **Constraint Satisfaction**
   - Balances multiple competing objectives (distance + priorities + time)
   - Weighted scoring function adjusts behavior dynamically
   - Similar to multi-objective optimization in ML

4. **NLP Integration** (Optional)
   - AI-generated route summaries using language models (OpenAI/Claude)
   - Explains reasoning behind route choices
   - Natural language output from computational decisions

**Why Not Traditional Programming?**

| Traditional Code | AI Approach (This Project) |
|------------------|----------------------------|
| Hard-coded rules for every scenario | Learns optimal patterns from problem structure |
| Breaks with new city configurations | Adapts to any city set automatically |
| Requires manual tuning | Self-optimizing through algorithms |
| Fixed decision paths | Explores solution space intelligently |

**ML Evolution Path:**
- **Phase 1 (Hackathon):** Heuristic ML algorithms (Nearest Neighbor + 2-Opt)
- **Phase 2 (Next Week):** Train on real delivery data to learn traffic patterns
- **Phase 3 (Production):** Deep reinforcement learning for real-time adaptation
- **Phase 4 (Scale):** Neural networks predict optimal routes from city features

**Academic Foundation:**
- Based on Traveling Salesman Problem (TSP) research
- Uses metaheuristic optimization techniques
- Applies computational intelligence principles
- Implements constraint programming methods

---

## 🧪 Test Cases

### Test Case 1: Basic Optimization
**Input:** Mumbai → [Pune, Bangalore, Chennai]  
**Expected Route:** Mumbai → Pune → Bangalore → Chennai  
**Distance:** ~1,850 km  
**Time:** < 500ms  
**Why:** Geographically logical southwest to south progression

### Test Case 2: Priority Override
**Input:** Mumbai → [Pune, Delhi, Bangalore], Delhi priority=1  
**Expected Route:** Mumbai → Delhi → Pune → Bangalore  
**Distance:** ~2,800 km (longer than optimal!)  
**Time:** < 500ms  
**Why:** High-priority Delhi visited first despite being farthest north

### Test Case 3: Scalability Test
**Input:** Mumbai → [All 9 other cities]  
**Expected Route:** Optimized 10-city route  
**Distance:** ~5,000-6,000 km  
**Time:** < 2 seconds  
**Why:** Proves algorithm handles real-world scale

### Test Case 4: Edge Case - Single Destination
**Input:** Mumbai → [Pune]  
**Expected Route:** Mumbai → Pune  
**Distance:** 150 km  
**Time:** < 10ms  
**Why:** No optimization needed, direct route

### Test Case 5: 2-Opt Improvement Demo
**Input:** Delhi → [Jaipur, Ahmedabad, Mumbai, Pune, Bangalore, Chennai, Hyderabad, Kolkata], improve=true  
**Expected:** 8-15% distance reduction vs Nearest Neighbor alone  
**Time:** < 1 second  
**Why:** Shows AI improvement over baseline algorithm

### Test Case 6: Time Window Constraint (Day 2 Feature)
**Input:** Mumbai → [Pune, Bangalore, Chennai], Bangalore window: 8am-2pm  
**Expected Route:** Mumbai → Bangalore (within window) → Pune → Chennai  
**Distance:** May be longer than optimal  
**Time:** < 500ms  
**Why:** Demonstrates constraint handling - Bangalore scheduled to meet time window

---

## 🎯 Project Scope

### ✅ In Scope

**Data & Infrastructure:**
- ✅ **Static distances** - Use great-circle distance (Haversine formula)
- ✅ **Hardcoded cities** - 10 Indian cities with lat/lon coordinates
- ✅ **In-memory caching** - Distance calculations cached for performance
- ✅ **RESTful API** - FastAPI with auto-generated documentation

**Core Algorithm:**
- ✅ **Nearest Neighbor** - Fast heuristic for initial route
- ✅ **2-Opt optimization** - Iterative improvement algorithm
- ✅ **Priority handling** - High/medium/low priority deliveries
- ✅ **Time windows** - Deliver within specified time ranges (Day 2 feature)
- ✅ **Performance metrics** - Distance saved, time taken, improvement percentage

**User Experience:**
- ✅ **Simple web UI** - HTML form for input, visual route display
- ✅ **AI-generated summaries** - Natural language route explanations
- ✅ **Error handling** - Graceful validation and helpful error messages
- ✅ **Demo scenarios** - Pre-configured test cases for presentation

**Assumptions:**
- Constant speed: 60 km/h average
- Single vehicle: One truck handles all deliveries
- No capacity limits: Infinite truck capacity
- No return trip: Truck stops at final destination
- No delivery time: Only considers travel time, not unloading

---

## ❌ Explicitly Out of Scope (For MVP)

To keep the hackathon project achievable in 24 hours, we are **intentionally excluding**:

**Not Implementing:**
- ❌ **Real-time traffic data** - Would require Google Maps API ($$$) and slow down responses
- ❌ **Multiple vehicles** - Fleet routing is 10x more complex (vehicle routing problem)
- ❌ **Vehicle capacity/weight limits** - Adds constraint satisfaction complexity
- ❌ **Return to origin** - Round-trip routing adds complexity
- ❌ **Database persistence** - All data in memory for speed
- ❌ **User authentication** - Public API for demo purposes
- ❌ **Real Maps API integration** - Use hardcoded coordinates instead
- ❌ **Mobile app** - Web API + simple frontend only
- ❌ **Historical data analysis** - No analytics or reporting
- ❌ **Driver shift scheduling** - No labor optimization
- ❌ **Fuel cost calculations** - Only distance optimization
- ❌ **Real-time vehicle tracking** - No GPS integration

**Rationale:** These features would add 20+ hours of development time but don't demonstrate the core AI optimization capability. Our goal is to prove the algorithm works, not build a production system.

**Post-Hackathon Roadmap:**
- **Week 1:** Google Maps API integration for real road distances
- **Week 2:** Implement time window constraints
- **Week 3:** Multi-vehicle support (VRP solver)
- **Week 4:** Train ML model on real delivery data
- **Month 2:** Production deployment with authentication
- **Month 3:** Mobile app + real-time tracking

---

## ✅ Success Criteria

### Day 1 Goals (0-24 hours)
- [ ] User inputs start city + 3-5 destinations
- [ ] API returns optimized route in under 2 seconds
- [ ] Route shows distance and time
- [ ] Works for 10 cities without crashing
- [ ] Handles priority deliveries
- [ ] Basic web UI working

### Day 2 Goals (24-48 hours)
- [ ] **Time window constraints** - Deliver within specified time ranges
- [ ] Visual map showing route
- [ ] "Saved X km vs random route" metric
- [ ] 2-Opt improvement toggle
- [ ] AI-generated route explanation
- [ ] Time window validation and warnings

---

## ⚠️ Error Handling

| Error | HTTP Code | Response Example |
|-------|-----------|------------------|
| Missing start city | 422 | `{"detail": "Field 'start' is required"}` |
| Empty destinations | 422 | `{"detail": "Field 'destinations' must contain at least 1 city"}` |
| Invalid city name | 404 | `{"detail": "City 'Mumbay' not found", "suggestions": ["Mumbai"]}` |
| Too many cities (20+) | 400 | `{"detail": "Maximum 20 cities allowed. Received: 25"}` |
| Duplicate cities | 400 | `{"detail": "Duplicate cities removed", "cleaned": ["Pune", "Bangalore"]}` |
| Invalid priority | 400 | `{"detail": "Priority must be 1, 2, or 3. Got: 5"}` |
| Server error | 500 | `{"detail": "Route optimization failed", "retry": true}` |

**Error Handling Strategy:**
- FastAPI + Pydantic automatically validates input types
- Custom validators check city names against hardcoded list
- Helpful error messages with suggestions (fuzzy matching)
- All errors return JSON (no HTML error pages)
- 4xx errors for client mistakes, 5xx for server issues

---

## ⚡ Performance Targets

| Cities | Target Time | Algorithm |
|--------|-------------|-----------|
| 1-5 | < 500ms | Nearest Neighbor |
| 6-10 | < 1s | NN + 2-Opt |
| 11-15 | < 2s | NN + 2-Opt |
| 16-20 | < 5s | NN only (skip 2-Opt) |

---