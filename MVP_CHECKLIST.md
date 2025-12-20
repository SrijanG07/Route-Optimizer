# 🎯 Route Optimizer MVP: 24-48 Hour Checklist
## Python/FastAPI Edition

A structured, actionable checklist to build a demo-ready route optimization system.

---

## ⚡ Day 1: Core MVP (0-24 hours)

### Phase 1: Project Setup (0-2 hours)

- [ ] Create project folder: `mkdir route-optimizer && cd route-optimizer`
- [ ] Create virtual environment: `python -m venv venv`
- [ ] Activate virtual environment:
  - Windows: `venv\Scripts\activate`
  - Mac/Linux: `source venv/bin/activate`
- [ ] Create `requirements.txt` with core dependencies:
  ```
  fastapi==0.104.1
  uvicorn[standard]==0.24.0
  geopy==2.4.0
  pydantic==2.5.0
  python-dotenv==1.0.0
  ```
- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Create folder structure:
  ```bash
  mkdir utils optimizer static models ai
  ```
- [ ] Create empty Python files:
  ```bash
  touch main.py
  touch utils/__init__.py utils/cities.py utils/distance.py
  touch optimizer/__init__.py optimizer/nearest_neighbor.py
  touch models/__init__.py models/schemas.py
  touch static/index.html
  ```
- [ ] Test basic FastAPI server (Hello World in main.py)
- [ ] Run server: `uvicorn main:app --reload`
- [ ] Verify server runs on http://localhost:8000
- [ ] Check auto-generated docs at http://localhost:8000/docs

**✅ Checkpoint:** Server running, project structure ready

---

### Phase 2: Data Layer & Distance Calculation (2-5 hours)

- [ ] **Create `utils/cities.py`**
  - [ ] Add 8-12 Indian cities with coordinates (Mumbai, Delhi, Bangalore, Chennai, Kolkata, Hyderabad, Pune, Ahmedabad, Jaipur, Lucknow)
  - [ ] Create `CITIES` dictionary with `{"name": {"lat": float, "lon": float}}` structure
  - [ ] Add `get_city_coordinates(city_name: str)` helper function
  - [ ] Add `is_valid_city(city_name: str) -> bool` validation function

- [ ] **Create `utils/distance.py`**
  - [ ] Import `geopy.distance` and cities data
  - [ ] Write `get_distance(city1: str, city2: str) -> float` function using `geopy.distance.distance()`
  - [ ] Return distance in kilometers (rounded to nearest km)
  - [ ] Add in-memory cache dictionary for distances (avoid recalculation)
  - [ ] Write `get_cached_distance(city1: str, city2: str)` that checks cache first
  - [ ] Add exception handling for invalid cities

- [ ] **Test distance calculations**
  - [ ] Test Mumbai to Delhi (~1400 km)
  - [ ] Test Bangalore to Chennai (~350 km)
  - [ ] Test cache hits (second call should be instant)
  - [ ] Test invalid city names (should raise ValueError)

**✅ Checkpoint:** Distance calculator working with 8+ cities and caching

---

### Phase 3: Core Optimization Algorithm (5-10 hours)

- [ ] **Create `optimizer/nearest_neighbor.py`**
  - [ ] Write `find_nearest_neighbor_route(start: str, destinations: list[str]) -> dict` function
  - [ ] Initialize route list with start city
  - [ ] Create copy of destinations as `unvisited` list
  - [ ] Loop while unvisited cities remain:
    - [ ] Find closest unvisited city to current position
    - [ ] Add to route and update total distance
    - [ ] Remove from unvisited list
  - [ ] Return dict with `{"route": list, "total_distance": float, "message": str}`

- [ ] **Create `optimizer/route_calculator.py`**
  - [ ] Write `calculate_total_distance(route: list[str]) -> float` helper
  - [ ] Loop through consecutive cities and sum distances
  - [ ] Write `estimate_time_hours(distance_km: float) -> float` (assume 60 km/h average)
  - [ ] Write `generate_route_steps(route: list[str]) -> list[dict]` (returns list of dicts with city, order, distance)

- [ ] **Add priority handling**
  - [ ] Modify Nearest Neighbor to accept `priorities: dict[str, int]` parameter
  - [ ] Pre-sort destinations by priority (1=high, 2=medium, 3=low)
  - [ ] Visit high-priority cities first, then apply NN within each group
  - [ ] Document logic with docstrings and comments

- [ ] **Test optimization algorithm**
  - [ ] Test 3 cities: Mumbai → [Pune, Ahmedabad] 
    - Expected: Mumbai → Pune → Ahmedabad (closer first)
  - [ ] Test 5 cities with priorities
  - [ ] Test 10 cities (should complete under 1 second)
  - [ ] Compare to random route (calculate savings)

**✅ Checkpoint:** Nearest Neighbor algorithm working with priority support

---

### Phase 4: REST API (10-15 hours)

- [ ] **Create Pydantic models (`models/schemas.py`)**
  - [ ] Create `OptimizeRequest` model with fields: start, destinations, priorities (optional), options (optional)
  - [ ] Create `OptimizeResponse` model with fields: success, route, totalDistanceKm, estimatedHours, summary, timestamp
  - [ ] Add field validators for city names and priorities

- [ ] **Build main FastAPI app (`main.py`)**
  - [ ] Import FastAPI, optimizer modules, models
  - [ ] Create FastAPI app instance: `app = FastAPI(title="Route Optimizer API")`
  - [ ] Add CORS middleware
  - [ ] Mount static files: `app.mount("/static", StaticFiles(directory="static"), name="static")`
  - [ ] Add health check: `@app.get("/")` returns `{"status": "ok"}`

- [ ] **Create POST `/api/optimize` endpoint**
  - [ ] Use `@app.post("/api/optimize", response_model=OptimizeResponse)`
  - [ ] Accept `OptimizeRequest` body with automatic validation
  - [ ] Validate inputs:
    - [ ] Check `start` is valid city (use `is_valid_city()`)
    - [ ] Check all `destinations` are valid cities
    - [ ] Raise HTTPException(400) if validation fails
  - [ ] Remove duplicates from destinations (use `list(set())`)
  - [ ] Remove start city if in destinations
  - [ ] Call `find_nearest_neighbor_route()`
  - [ ] Calculate estimated time
  - [ ] Generate simple summary text
  - [ ] Return OptimizeResponse with all fields
  - [ ] Handle errors with try-except, raise HTTPException(500) on failure

- [ ] **Create GET `/api/cities` endpoint**
  - [ ] Use `@app.get("/api/cities")`
  - [ ] Return list of all available cities from CITIES dict
  - [ ] Return city count
  - [ ] Format: `{"cities": [{"name": str, "lat": float, "lon": float}], "count": int}`

- [ ] **Test API with Postman or Swagger UI (`/docs`)**
  - [ ] Test valid request (3 cities) via Swagger UI
  - [ ] Test with priorities
  - [ ] Test missing start city (should fail with 422)
  - [ ] Test invalid city name (should fail with 400)
  - [ ] Test empty destinations (should fail with 422)
  - [ ] Test duplicate cities (should auto-remove)

**✅ Checkpoint:** Working REST API with validation and error handling

---

### Phase 5: Frontend UI (15-20 hours)

- [ ] **Create `public/index.html`**
  - [ ] Add HTML boilerplate with title "Route Optimizer"
  - [ ] Link CSS (inline styles for MVP)
  - [ ] Create form container with:
    - [ ] Dropdown for start city (populated from cities list)
    - [ ] Multi-select for destinations (use `<select multiple>`)
    - [ ] Optional: Priority selection for each city (checkboxes or buttons)
    - [ ] "Optimize Route" button
  - [ ] Create results container `<div id="results">`
  - [ ] Add loading indicator (hidden by default)

- [ ] **Style the UI**
  - [ ] Center container, max-width 800px
  - [ ] Style form inputs (padding, borders, margins)
  - [ ] Style button (primary color, hover effect)
  - [ ] Style results card (background, padding, shadow)
  - [ ] Add route list styling (numbered items)
  - [ ] Add responsive design (works on mobile)

- [ ] **Write frontend JavaScript (inline or `static/app.js`)**
  - [ ] Function `optimizeRoute()` triggered by button click
  - [ ] Get selected start city from dropdown
  - [ ] Get selected destinations from multi-select (use `selectedOptions`)
  - [ ] Validate at least 1 destination selected (show alert if not)
  - [ ] Show loading indicator
  - [ ] Make POST request to `http://localhost:8000/api/optimize` using `fetch()`
  - [ ] Handle response:
    - [ ] Parse JSON
    - [ ] Display route sequence with numbers
    - [ ] Show total distance prominently
    - [ ] Show estimated time
    - [ ] Show summary text
  - [ ] Handle errors (network failure, API error)
  - [ ] Hide loading indicator

- [ ] **Test frontend**
  - [ ] Test selecting 3 cities and optimizing
  - [ ] Test error case (no destinations selected)
  - [ ] Test UI on mobile (responsive)
  - [ ] Verify results display correctly

**✅ Checkpoint:** Functional frontend with route display

---

### Phase 6: Polish & Demo Preparation (20-24 hours)

- [ ] **Add savings metric**
  - [ ] Calculate random route distance in API
  - [ ] Compare to optimized route
  - [ ] Return savings: `{savedKm, percentImprovement}`
  - [ ] Display in UI: "💰 Saved 412 km (18% improvement)"

- [ ] **Add route summary card**
  - [ ] Show total stops count
  - [ ] Show total distance (large, bold)
  - [ ] Show estimated time
  - [ ] Add icons: 📍 for stops, 🛣️ for distance, ⏱️ for time

- [ ] **Generate route explanation**
  - [ ] Create `ai/summaryGenerator.js`
  - [ ] Write template-based summary function:
    - Mention number of cities
    - Mention priority deliveries if any
    - Explain routing strategy
  - [ ] Optional: Integrate OpenAI/Claude API for AI-generated summary
  - [ ] Add summary to API response
  - [ ] Display summary in UI below route

- [ ] **Create demo dataset**
  - [ ] Create 3 pre-filled scenarios:
    1. **Urban:** 3-4 nearby cities (e.g., Mumbai, Pune, Nashik)
    2. **Long-haul:** 5-6 cities across India (Delhi, Mumbai, Bangalore, Chennai)
    3. **Priority:** 4 cities with 1-2 high priority (simulate urgent delivery)
  - [ ] Add "Load Demo" buttons in UI for each scenario
  - [ ] Write JavaScript to auto-fill form when demo clicked

- [ ] **Performance logging**
  - [ ] Add timestamp before optimization
  - [ ] Add timestamp after optimization
  - [ ] Calculate time taken in milliseconds
  - [ ] Return in API response: `{optimizationTimeMs: 145}`
  - [ ] Display in UI (optional): "Calculated in 145ms"

- [ ] **Test thoroughly**
  - [ ] Test with 3 cities (fast, simple case)
  - [ ] Test with 5 cities (medium complexity)
  - [ ] Test with 10 cities (stress test, should complete under 2s)
  - [ ] Test priority handling (high priority city should come early)
  - [ ] Test edge case: 1 destination (should just return start→dest)
  - [ ] Test edge case: duplicate cities (should auto-remove)

- [ ] **Capture screenshots**
  - [ ] Screenshot of form filled out
  - [ ] Screenshot of optimized route results
  - [ ] Screenshot of 10-city route (scalability proof)

- [ ] **Write demo script**
  - [ ] 30-second problem explanation
  - [ ] 60-second live demo
  - [ ] 30-second technical explanation
  - [ ] Practice presenting 3 times

**✅ Checkpoint:** MVP complete, demo-ready with screenshots

---

## 🚀 Day 2: Enhancement & Polish (24-48 hours)

### Phase 7: Algorithm Enhancement (24-32 hours)

- [ ] **Implement 2-Opt optimization**
  - [ ] Create `optimizer/two_opt.py`
  - [ ] Write `improve_two_opt(route: list[str]) -> list[str]` function
  - [ ] Loop through all pairs of route segments
  - [ ] Try reversing each segment
  - [ ] If reversal reduces distance, keep it
  - [ ] Repeat until no improvements found
  - [ ] Return improved route

- [ ] **Integrate 2-Opt with API**
  - [ ] Add `improve` field to OptimizeRequest options
  - [ ] If `options.improve=True`, run 2-Opt after Nearest Neighbor
  - [ ] Track before/after distances
  - [ ] Return improvement metrics in response: `{"beforeKm": float, "afterKm": float, "improvement": float}`

- [ ] **Show before/after comparison**
  - [ ] Display "Before 2-Opt" distance
  - [ ] Display "After 2-Opt" distance
  - [ ] Display percentage improvement
  - [ ] Add visual indicator (green checkmark + percentage)

- [ ] **Test 2-Opt**
  - [ ] Test with 5 cities (should see 5-15% improvement)
  - [ ] Test with 10 cities (should complete under 3 seconds)
  - [ ] Compare to baseline Nearest Neighbor
  - [ ] Document improvement percentages in README

**✅ Checkpoint:** 2-Opt optimization working with visible improvements

---

### Phase 8: Dynamic Features (32-36 hours)

- [ ] **Create POST `/api/recalculate` endpoint**
  - [ ] Accept JSON body:
    ```json
    {
      "currentRoute": [...],
      "currentPosition": "Pune",
      "changes": {
        "add": ["Hyderabad"],
        "remove": ["Chennai"],
        "updatePriorities": {"Hyderabad": 1}
      }
    }
    ```
  - [ ] Extract remaining cities (from current position onward)
  - [ ] Apply additions and removals
  - [ ] Re-run optimization on updated city list
  - [ ] Return new route starting from current position

- [ ] **Add performance logging**
  - [ ] Log optimization start time
  - [ ] Log optimization end time
  - [ ] Calculate and return `recalculationTimeMs`
  - [ ] Log to console for debugging

- [ ] **Test recalculation**
  - [ ] Test adding a city mid-route
  - [ ] Test removing a city mid-route
  - [ ] Test changing priorities mid-route
  - [ ] Verify performance (should complete under 1 second)

**✅ Checkpoint:** Real-time route recalculation working

---

### Phase 9: Visualization (36-42 hours)

- [ ] **Integrate Leaflet.js**
  - [ ] Add Leaflet CSS and JS to `index.html` via CDN
  - [ ] Create `<div id="map">` container
  - [ ] Style map container (height: 400px, width: 100%)

- [ ] **Display route on map**
  - [ ] Initialize map centered on India
  - [ ] Fetch city coordinates from API response
  - [ ] Add numbered markers for each stop
  - [ ] Draw polyline connecting all stops in route order
  - [ ] Style polyline (color, width)
  - [ ] Add popup to each marker showing city name + order

- [ ] **Add priority badges to UI**
  - [ ] For each city in route list, show priority badge
  - [ ] Color-code badges:
    - High priority: Red background
    - Medium priority: Yellow background
    - Low priority: Green background
  - [ ] Add legend explaining colors

- [ ] **Polish map interactions**
  - [ ] Auto-zoom map to fit all markers
  - [ ] Add hover effects on markers
  - [ ] Optional: Click marker to highlight in route list

**✅ Checkpoint:** Visual route map with priority indicators

---

### Phase 10: Final Polish (42-48 hours)

- [ ] **AI-generated summaries (if API key available)**
  - [ ] Sign up for OpenAI or Claude API
  - [ ] Add API key to `.env` file
  - [ ] Install API SDK: `npm install @anthropic-ai/sdk` or `openai`
  - [ ] Update `summaryGenerator.js` to call API
  - [ ] Prompt: "Explain this delivery route in 2 sentences: [route]. Total distance: [X] km."
  - [ ] Handle API failures gracefully (fallback to template)

- [ ] **Write README.md**
  - [ ] Project title and description
  - [ ] Problem statement (2-3 sentences)
  - [ ] Features list
  - [ ] Installation steps:
    ```bash
    npm install
    npm start
    ```
  - [ ] API documentation (endpoints, request/response examples)
  - [ ] Algorithm explanation (Nearest Neighbor + 2-Opt)
  - [ ] Tech stack list
  - [ ] Screenshots
  - [ ] Future improvements section

- [ ] **Create API documentation**
  - [ ] Option 1: Write markdown file `API.md`
  - [ ] Option 2: Export Postman collection
  - [ ] Document all endpoints with examples
  - [ ] Document error responses

- [ ] **Add error boundaries**
  - [ ] Handle network failures in frontend
  - [ ] Show user-friendly error messages
  - [ ] Add retry button for failed requests

- [ ] **Performance optimization**
  - [ ] Cache city list in frontend (avoid repeated `/api/cities` calls)
  - [ ] Add loading states for all async operations
  - [ ] Optimize distance cache (limit size, use LRU if needed)

- [ ] **Final testing**
  - [ ] Test all 3 demo scenarios
  - [ ] Test all API endpoints
  - [ ] Test UI on different browsers (Chrome, Firefox)
  - [ ] Test on mobile device
  - [ ] Fix any bugs found

**✅ Checkpoint:** Fully polished MVP with documentation

---

## 🎁 Quick Wins (High-Impact, Low-Effort)

### Quick Win 1: Savings Metric (30 mins)
- [ ] Calculate random route distance
- [ ] Compare to optimized route
- [ ] Display: "💰 Saved 412 km (18% improvement)"
- [ ] Add to route summary card

### Quick Win 2: Priority Color Badges (20 mins)
- [ ] Add CSS classes for priority levels
- [ ] Apply colored left border to route items
- [ ] Add priority labels (High/Med/Low)

### Quick Win 3: 2-Opt Improvement Toggle (1 hour)
- [ ] Add "Improve Route" button to UI
- [ ] Call `/api/optimize?improve=true`
- [ ] Show before/after distances
- [ ] Display improvement percentage

### Quick Win 4: Demo Scenario Buttons (15 mins)
- [ ] Create 3 preset scenarios (urban, long-haul, priority)
- [ ] Add "Load Demo" buttons
- [ ] Auto-fill form when clicked
- [ ] Label each scenario clearly

---

## 📋 Pre-Demo Checklist (Final Hour)

- [ ] Server starts without errors
- [ ] All 3 demo scenarios work perfectly
- [ ] Screenshots saved and ready to show
- [ ] Demo script printed or memorized
- [ ] Laptop fully charged
- [ ] Internet connection tested (if using APIs)
- [ ] Backup plan if WiFi fails (use hardcoded data)
- [ ] GitHub repo updated with latest code
- [ ] README has clear setup instructions
- [ ] Practiced demo at least 3 times

---

## 🐛 Common Issues & Fixes

**Issue:** "Cannot find module 'express'"
- **Fix:** Run `npm install` in project folder

**Issue:** Distance returns NaN
- **Fix:** Check city coordinates are numbers, not strings

**Issue:** API returns 404 for all routes
- **Fix:** Verify Express middleware is before route definitions

**Issue:** Frontend can't reach API (CORS error)
- **Fix:** Add `app.use(cors())` in server.js

**Issue:** Map doesn't load
- **Fix:** Check Leaflet CDN links in HTML, verify map container has height

**Issue:** Optimization takes too long (10+ cities)
- **Fix:** Use Nearest Neighbor only (skip 2-Opt for 10+ cities)

---

## ✅ Definition of Done

**MVP is complete when:**
- [ ] User can select start + destinations in UI
- [ ] Click "Optimize" returns route in under 2 seconds
- [ ] Route displays in numbered list with total distance
- [ ] Map shows route visually (if time permits)
- [ ] API handles errors gracefully (no crashes)
- [ ] Demo works reliably 3 times in a row
- [ ] README has setup instructions
- [ ] At least 3 test cases work correctly

---

## 🎯 Success Metrics

**To impress judges, you need:**
- ✅ Working demo (no crashes during presentation)
- ✅ Clear problem explanation (who benefits, why)
- ✅ Visible results (numbers, savings, route list)
- ✅ At least 1 "wow" feature (map, AI summary, or 2-Opt)
- ✅ Professional UI (clean, not ugly)
- ✅ Technical depth (explain algorithm briefly)
- ✅ Scalability proof (show 10-city route works)

---

## 🚀 You Got This!

Remember:
- **Working > Perfect** - Get it running first, polish later
- **Demo > Code** - Judges care about what they see, not backend complexity
- **Simple > Complex** - Nearest Neighbor is enough to win
- **Explain > Assume** - Tell judges what problem you solved

**Now go build! 💪**
