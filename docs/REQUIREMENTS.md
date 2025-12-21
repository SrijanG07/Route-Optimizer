# System Requirements Specification

> **AI-Powered Multi-City Route Optimization System**  
> Version 1.0 | December 2025

---

## 1. Overview

### 1.1 Purpose
This system provides intelligent route optimization for logistics companies to minimize travel distance while respecting delivery priorities and operational constraints.

### 1.2 Scope
- **Target Users:** Logistics dispatch managers, fleet operators
- **Use Case:** Single-truck multi-city delivery optimization
- **Geographic Coverage:** 18 major Indian cities (MVP)
- **Deployment:** Web application (REST API + Browser UI)

---

## 2. Functional Requirements

### 2.1 Input Requirements

| Field | Type | Required | Constraints | Example |
|-------|------|----------|-------------|---------|
| `start` | String | Yes | Must be valid city name | "Mumbai" |
| `destinations` | Array[String] | Yes | 1-17 cities, unique | ["Pune", "Delhi"] |
| `priorities` | Object | No | Priority ∈ {1, 2, 3} | {"Pune": 1} |
| `options.use_ai` | Boolean | No | Default: false | true |

**Validation Rules:**
- Start city must not appear in destinations
- No duplicate destinations
- All cities must exist in database (18 Indian cities)
- Priority levels: 1=URGENT, 2=MEDIUM, 3=LOW
- Cities without explicit priority default to 3 (LOW)

### 2.2 Output Requirements

The system must provide:
1. **Optimized Route:** Ordered list of cities to visit
2. **Total Distance:** Sum of all city-to-city distances (km)
3. **Estimated Time:** Travel time assuming 60 km/h average speed
4. **Optimization Metrics:**
   - Algorithm used (Greedy / Evolutionary)
   - Calculation time (milliseconds)
   - Distance saved vs baseline
   - Improvement percentage
5. **AI Summary:** Natural language explanation of route choice
6. **Google Maps Link:** Clickable route for navigation

### 2.3 Optimization Algorithms

#### 2.3.1 Greedy (Nearest Neighbor)
- **Purpose:** Fast baseline optimization
- **Complexity:** O(n²)
- **Target Performance:** <200ms for 10 cities
- **Quality:** 75-85% optimal

#### 2.3.2 Genetic Algorithm (AI)
- **Purpose:** Advanced optimization for better routes
- **Complexity:** O(n² × generations)
- **Target Performance:** <1s for 10 cities
- **Quality:** 90-98% optimal
- **Parameters:**
  - Population: 40 routes
  - Generations: 80 iterations
  - Mutation rate: 15%
  - Crossover: Order Crossover (OX)
  - Priority penalty: 1000 km per violation

### 2.4 Priority Handling

**Business Rule:** Higher priority deliveries must be scheduled earlier in route.

**Implementation:**
- Fitness function adds penalty (1000 km) for each priority violation
- Priority violation = Lower priority city before higher priority city
- Example: If Pune (priority 3) appears before Bangalore (priority 1), penalty = 1000 km

**Expected Behavior:**
- Priority 1 cities appear first after start city
- Priority 2 cities appear after all priority 1 cities
- Priority 3 cities appear last

---

## 3. Real-Time Recalculation

### 3.1 Use Cases

| Scenario | API Endpoint | Expected Behavior |
|----------|--------------|-------------------|
| Driver completed deliveries | POST /api/recalculate | Optimize remaining cities from current position |
| Urgent delivery added mid-route | POST /api/add-cities | Insert city and reoptimize |
| Delivery cancelled | POST /api/remove-cities | Remove city and reoptimize |
| Priority changed | POST /api/recalculate | Reorder based on new priorities |

### 3.2 Performance Requirements
- Recalculation time: <500ms for 15 cities
- UI update latency: <100ms after API response
- No full route recomputation (optimize only remaining cities)

---

## 4. Performance Requirements

### 4.1 Response Time

| City Count | Greedy Algorithm | AI Algorithm | Target Met? |
|------------|------------------|--------------|-------------|
| 5 cities   | <100ms           | <200ms       | ✅ Required |
| 10 cities  | <200ms           | <1000ms      | ✅ Required |
| 15 cities  | <500ms           | <2500ms      | ✅ Required |
| 17 cities  | <800ms           | <5000ms      | ✅ Acceptable |

### 4.2 Scalability
- **Current:** 17 cities maximum (18 total in database, need 1 for start)
- **Production Target:** 100+ cities with spatial indexing

### 4.3 Caching
- Distance cache hit rate: >95%
- LRU cache size: 2000 entries
- Cache speedup: 500x for repeated calculations

---

## 5. Distance Calculation

### 5.1 Method (Demo Reliability)
**Geodesic (great circle distance)** - Default, no API limits
- Uses geopy library for accurate great circle calculations
- Approximates road distance at 85-90% accuracy
- No external API dependencies = reliable for demos

**Haversine formula** - Fallback if geopy fails
- Pure mathematical calculation
- Always available

### 5.2 Accuracy
- Geodesic accuracy: 85-90% of road distance
- Example: Mumbai→Delhi geodesic = 1154 km vs road ≈ 1420 km
- Sufficient for route optimization comparisons

### 5.3 Error Handling
- Geopy failure: Automatic fallback to Haversine
- Invalid city: Return 400 error with available cities list
- Cache misses: Transparent recalculation

---

## 6. Constraints

### 6.1 Hard Constraints
- ✅ **City limit:** 1-17 destinations
- ✅ **Priority levels:** Only 1, 2, 3 allowed
- ✅ **Unique cities:** No duplicates in route
- ✅ **Valid cities:** Must exist in predefined database

### 6.2 Soft Constraints (Not Implemented in MVP)
- ⚠️ **Time windows:** Delivery deadlines (defined in schema but not validated)
- ⚠️ **Capacity:** Truck weight/volume limits (not implemented)
- ⚠️ **Service time:** Time spent at each delivery location (not modeled)
- ⚠️ **Traffic:** Real-time traffic conditions (not considered)

**Note:** Time windows and capacity fields exist in data models for future implementation but are currently ignored by optimization logic.

---

## 7. AI Integration

### 7.1 Google Gemini (Route Summaries)
- **Purpose:** Generate natural language explanations
- **Model:** gemini-pro
- **Input:** Route details, distance, priorities, algorithm metrics
- **Output:** 2-3 sentence professional summary
- **Fallback:** Template-based summary if API fails

### 7.2 Requirements
- API response time: <2 seconds
- Graceful degradation: System works without Gemini
- Context-aware: Mentions priorities, algorithm choice, distance savings

---

## 8. Success Criteria

### 8.1 Functional Success
- ✅ Routes are valid (no repeated cities, starts at start city)
- ✅ Priority constraints respected (urgent deliveries first)
- ✅ Distance calculations accurate (±10% of real road distance)
- ✅ Real-time recalculation works without errors

### 8.2 Performance Success
- ✅ 10 cities optimized in <1 second
- ✅ AI improves over greedy by 5-18%
- ✅ System handles 17 cities without crashes

### 8.3 Usability Success
- ✅ UI wizard completes in <60 seconds
- ✅ API errors are human-readable
- ✅ Google Maps link opens correct route
- ✅ AI summaries are coherent and professional

---

## 9. Edge Cases

### 9.1 Handled Edge Cases
✅ **Single destination:** Route is trivial (start → destination)  
✅ **All same priority:** Optimize purely by distance  
✅ **Conflicting priorities:** Multiple cities with priority 1 handled correctly  
✅ **API failure:** Graceful fallback to geodesic  
✅ **Invalid city name:** Return 400 with suggestion list  

### 9.2 Known Limitations
⚠️ **No multi-vehicle support:** Single truck only  
⚠️ **No route return:** Assumes truck doesn't return to start  
⚠️ **No traffic awareness:** Static distance calculations  
⚠️ **Fixed city database:** Can't add new cities without code change  

---

## 10. Sample Input/Output

### 10.1 Sample Request (Priority Route)
```json
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
    "use_ai": true
  }
}
```

### 10.2 Expected Response
```json
{
  "success": true,
  "route": ["Mumbai", "Bangalore", "Chennai", "Hyderabad", "Pune"],
  "totalDistanceKm": 1847.32,
  "estimatedHours": 30.79,
  "summary": "The AI-powered evolutionary optimizer prioritized Bangalore for urgent delivery...",
  "optimization": {
    "algorithm": "Evolutionary Optimizer",
    "calculationTimeMs": 892,
    "savedDistanceKm": 312,
    "improvementPercentage": 14.4,
    "greedyDistanceKm": 2015,
    "aiImprovementOverGreedy": 8.3
  },
  "mapsLink": "https://www.google.com/maps/dir/Mumbai/Bangalore/Chennai/Hyderabad/Pune"
}
```

**Verification:**
- ✅ Bangalore appears first (priority 1)
- ✅ Chennai appears second (priority 2)
- ✅ Hyderabad and Pune last (priority 3)
- ✅ Distance is optimized within priority groups

---

## 11. Non-Functional Requirements

### 11.1 Reliability
- API uptime: 99% (local demo)
- Error rate: <1% (validation catches most errors)
- Crash recovery: Stateless API, instant recovery

### 11.2 Maintainability
- Code documentation: All functions have docstrings
- Type hints: Complete type annotations
- Modularity: Clear separation of concerns (API, algorithm, distance, AI layers)

### 11.3 Security
- Input validation: Pydantic models prevent injection
- API keys: Stored in .env (gitignored)
- No authentication: MVP only (future: JWT tokens)

---

## 12. Future Requirements (Out of Scope for MVP)

### Phase 2 Features
- [ ] Time window constraints (delivery deadlines)
- [ ] Vehicle capacity limits (weight, volume)
- [ ] Multi-vehicle optimization (fleet routing)
- [ ] Real-time traffic integration
- [ ] Driver mobile app

### Phase 3 Features
- [ ] Machine learning from historical routes
- [ ] Demand prediction
- [ ] Customer notification system
- [ ] Integration with ERP systems

---

**Document Version:** 1.0  
**Last Updated:** December 22, 2025  
**Status:** Approved for MVP Development
