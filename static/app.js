// ========== City Data ==========
// This will be populated from backend API
let CITIES = {
    "Delhi": { lat: 28.7041, lng: 77.1025 },
    "Mumbai": { lat: 19.0760, lng: 72.8777 },
    "Bangalore": { lat: 12.9716, lng: 77.5946 },
    "Chennai": { lat: 13.0827, lng: 80.2707 },
    "Kolkata": { lat: 22.5726, lng: 88.3639 },
    "Hyderabad": { lat: 17.3850, lng: 78.4867 },
    "Pune": { lat: 18.5204, lng: 73.8567 },
    "Ahmedabad": { lat: 23.0225, lng: 72.5714 },
    "Jaipur": { lat: 26.9124, lng: 75.7873 },
    "Lucknow": { lat: 26.8467, lng: 80.9462 },
    "Indore": { lat: 22.7196, lng: 75.8577 },
    "Nagpur": { lat: 21.1458, lng: 79.0882 },
    "Surat": { lat: 21.1702, lng: 72.8311 },
    "Kanpur": { lat: 26.4499, lng: 80.3319 },
    "Bhopal": { lat: 23.2599, lng: 77.4126 },
    "Visakhapatnam": { lat: 17.6868, lng: 83.2185 },
    "Patna": { lat: 25.5941, lng: 85.1376 },
    "Vadodara": { lat: 22.3072, lng: 73.1812 },
    "Chandigarh": { lat: 30.7333, lng: 76.7794 },
    "Kochi": { lat: 9.9312, lng: 76.2673 },
    "Thiruvananthapuram": { lat: 8.5241, lng: 76.9366 },
    "Coimbatore": { lat: 11.0168, lng: 76.9558 },
    "Guwahati": { lat: 26.1445, lng: 91.7362 },
    "Raipur": { lat: 21.2514, lng: 81.6296 },
    "Ranchi": { lat: 23.3441, lng: 85.3096 },
};

// ========== State ==========
let currentStep = 1;
let startCity = null;
let destCities = [];
let cityPriorities = {}; // Track priorities for each destination city
let useAI = true;

// ========== Initialize ==========
document.addEventListener('DOMContentLoaded', async () => {
    await loadCitiesFromBackend();
    renderCityGrids();
    updateUI();
});

// Load cities from backend API
async function loadCitiesFromBackend() {
    try {
        const response = await fetch('/api/cities');
        if (response.ok) {
            const data = await response.json();
            if (data.success && data.details) {
                // Update CITIES with backend data
                CITIES = {};
                for (const [city, coords] of Object.entries(data.details)) {
                    CITIES[city] = { lat: coords.lat, lng: coords.lon };
                }
                console.log('Loaded', Object.keys(CITIES).length, 'cities from backend');
            }
        }
    } catch (error) {
        console.warn('Failed to load cities from backend, using defaults:', error);
    }
}

function renderCityGrids() {
    const cities = Object.keys(CITIES).sort();

    // Start city grid
    const startGrid = document.getElementById('startCityGrid');
    startGrid.innerHTML = cities.map(city =>
        `<button class="city-btn" onclick="selectStartCity('${city}')" data-city="${city}">${city}</button>`
    ).join('');

    // Destination city grid
    const destGrid = document.getElementById('destCityGrid');
    destGrid.innerHTML = cities.map(city =>
        `<button class="city-btn" onclick="toggleDestCity('${city}')" id="dest-${city}" data-city="${city}">${city}</button>`
    ).join('');
}

// ========== City Search/Filter Functions ==========
function filterStartCities() {
    const searchTerm = document.getElementById('startCitySearch').value.toLowerCase();
    const cityButtons = document.querySelectorAll('#startCityGrid .city-btn');

    cityButtons.forEach(btn => {
        const cityName = btn.getAttribute('data-city').toLowerCase();
        if (cityName.includes(searchTerm)) {
            btn.style.display = 'inline-block';
        } else {
            btn.style.display = 'none';
        }
    });
}

function filterDestCities() {
    const searchTerm = document.getElementById('destCitySearch').value.toLowerCase();
    const cityButtons = document.querySelectorAll('#destCityGrid .city-btn');

    cityButtons.forEach(btn => {
        const cityName = btn.getAttribute('data-city').toLowerCase();
        if (cityName.includes(searchTerm)) {
            btn.style.display = 'inline-block';
        } else {
            btn.style.display = 'none';
        }
    });
}

// ========== City Selection ==========
function selectStartCity(city) {
    startCity = city;

    // Update UI
    document.querySelectorAll('#startCityGrid .city-btn').forEach(btn => {
        btn.classList.toggle('selected', btn.textContent === city);
    });

    // Disable this city in destinations
    updateDestGrid();
}

function toggleDestCity(city) {
    if (city === startCity) return;

    const idx = destCities.indexOf(city);
    if (idx > -1) {
        destCities.splice(idx, 1);
        delete cityPriorities[city]; // Remove priority when city is deselected
    } else if (destCities.length < 10) {
        destCities.push(city);
        cityPriorities[city] = 3; // Default to low priority
    }

    updateDestGrid();
    updateSelectedCitiesDisplay();
}

function updateDestGrid() {
    document.querySelectorAll('#destCityGrid .city-btn').forEach(btn => {
        const city = btn.getAttribute('data-city');
        btn.classList.toggle('selected', destCities.includes(city));
        btn.disabled = city === startCity;
        btn.style.opacity = city === startCity ? '0.3' : '1';
    });

    document.getElementById('destCount').textContent = destCities.length;
}

// ========== Priority Management ==========
function updateSelectedCitiesDisplay() {
    const container = document.getElementById('selectedCitiesContainer');

    if (destCities.length === 0) {
        container.innerHTML = '';
        return;
    }

    container.innerHTML = '<h3>Selected Cities & Priorities:</h3>';

    destCities.forEach(city => {
        const priority = cityPriorities[city] || 3;
        const priorityLabel = priority === 1 ? 'Urgent' : priority === 2 ? 'Medium' : 'Low';

        container.innerHTML += `
            <div class="selected-city-item">
                <span>${city}</span>
                <div>
                    <select onchange="updateCityPriority('${city}', this.value)">
                        <option value="1" ${priority === 1 ? 'selected' : ''}>🔴 Urgent</option>
                        <option value="2" ${priority === 2 ? 'selected' : ''}>🟡 Medium</option>
                        <option value="3" ${priority === 3 ? 'selected' : ''}>🟢 Low</option>
                    </select>
                    <button onclick="toggleDestCity('${city}')">✕</button>
                </div>
            </div>
        `;
    });
}

function updateCityPriority(city, priority) {
    cityPriorities[city] = parseInt(priority);
    console.log(`Updated ${city} priority to ${priority}`);
}

function collectPriorities() {
    // Return priorities only for selected destination cities
    const priorities = {};
    destCities.forEach(city => {
        priorities[city] = cityPriorities[city] || 3; // Default to low if not set
    });
    console.log('🎯 Priorities being sent to API:', priorities);
    return priorities;
}

// ========== Step Navigation ==========
function nextStep() {
    if (currentStep === 1 && !startCity) {
        alert('Please select a start city');
        return;
    }
    if (currentStep === 2 && destCities.length < 2) {
        alert('Please select at least 2 destination cities');
        return;
    }

    if (currentStep < 3) {
        currentStep++;
        updateUI();
    }
}

function prevStep() {
    if (currentStep > 1) {
        currentStep--;
        updateUI();
    }
}

function updateUI() {
    // Update steps indicator
    document.querySelectorAll('.step').forEach(step => {
        const stepNum = parseInt(step.dataset.step);
        step.classList.toggle('active', stepNum === currentStep);
        step.classList.toggle('completed', stepNum < currentStep);
    });

    // Show/hide form steps
    document.querySelectorAll('.form-step').forEach((el, idx) => {
        el.classList.toggle('hidden', idx + 1 !== currentStep);
    });

    // Update nav buttons
    document.getElementById('prevBtn').disabled = currentStep === 1;
    document.getElementById('nextBtn').classList.toggle('hidden', currentStep === 3);
}

// ========== Loading Animation Functions ==========
function showMetroLoader() {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        overlay.classList.remove('hidden');
        updateLoadingStage(1);
    }
}

function hideMetroLoader() {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        overlay.classList.add('hidden');
    }
}

function updateLoadingStage(stageNumber) {
    // Update stage indicators
    for (let i = 1; i <= 3; i++) {
        const stage = document.getElementById(`stage${i}`);
        if (!stage) continue;

        stage.classList.remove('active', 'complete');
        if (i < stageNumber) {
            stage.classList.add('complete');
        } else if (i === stageNumber) {
            stage.classList.add('active');
        }
    }

    // Update progress bar
    const progressFill = document.getElementById('progressFill');
    if (progressFill) {
        const percentage = ((stageNumber - 1) / 3) * 100 + 33; // 33%, 66%, 100%
        progressFill.style.width = `${Math.min(percentage, 100)}%`;
    }
}

// ========== Export Functions ==========
let lastOptimizedResult = null;

function exportToJSON() {
    if (!lastOptimizedResult) {
        alert('No route data to export. Please optimize a route first.');
        return;
    }

    const exportData = {
        route: lastOptimizedResult.route,
        totalDistance: lastOptimizedResult.totalDistance,
        estimatedHours: lastOptimizedResult.estimatedTime,
        startCity: lastOptimizedResult.route[0],
        destinations: lastOptimizedResult.route.slice(1),
        priorities: collectPriorities(),
        optimization: {
            algorithm: lastOptimizedResult.algorithm,
            iterations: lastOptimizedResult.iterations,
            calculationTime: lastOptimizedResult.calculationTime,
            distanceSaved: lastOptimizedResult.baselineDistance - lastOptimizedResult.totalDistance,
            improvementPercent: lastOptimizedResult.improvement,
            baselineDistance: lastOptimizedResult.baselineDistance
        },
        summary: lastOptimizedResult.summary || '',
        exportedAt: new Date().toISOString(),
        exportedBy: 'RouteOptimizer v1.0'
    };

    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `route-${exportData.startCity}-${new Date().toISOString().slice(0, 10)}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);

    console.log('✅ Route exported to JSON');
}

function exportToCSV() {
    if (!lastOptimizedResult) {
        alert('No route data to export. Please optimize a route first.');
        return;
    }

    // CSV Headers
    let csv = 'Stop Number,City,Priority,Distance from Previous (km),Cumulative Distance (km)\n';

    // Add route data
    let cumulativeDistance = 0;
    lastOptimizedResult.route.forEach((city, index) => {
        const priority = cityPriorities[city] || '-';
        const priorityLabel = priority === 1 ? 'Urgent' : priority === 2 ? 'Medium' : priority === 3 ? 'Low' : 'N/A';

        // Calculate distance from previous city
        let distanceFromPrevious = 0;
        if (index > 0) {
            const prevCity = lastOptimizedResult.route[index - 1];
            distanceFromPrevious = getDistance(prevCity, city);
            cumulativeDistance += distanceFromPrevious;
        }

        csv += `${index + 1},${city},${priorityLabel},${index === 0 ? '-' : distanceFromPrevious.toFixed(2)},${cumulativeDistance.toFixed(2)}\n`;
    });

    // Add summary
    csv += `\nSummary\n`;
    csv += `Total Distance,${lastOptimizedResult.totalDistance} km\n`;
    csv += `Estimated Time,${lastOptimizedResult.estimatedTime} hours\n`;
    csv += `Algorithm,${lastOptimizedResult.algorithm}\n`;
    csv += `Improvement,${lastOptimizedResult.improvement}%\n`;

    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `route-${lastOptimizedResult.route[0]}-${new Date().toISOString().slice(0, 10)}.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);

    console.log('✅ Route exported to CSV');
}

// ========== Optimization ==========
async function optimizeRoute() {
    const btn = document.getElementById('optimizeBtn');
    const btnText = btn.querySelector('.btn-text');
    const btnLoading = btn.querySelector('.btn-loading');

    // Show loading with metro animation
    btn.disabled = true;
    btnText.classList.add('hidden');
    btnLoading.classList.remove('hidden');
    showMetroLoader();

    try {
        // Stage 1: Analyzing
        updateLoadingStage(1);
        await new Promise(resolve => setTimeout(resolve, 300));

        // Stage 2: Optimizing
        updateLoadingStage(2);

        // Call backend API - Always use Genetic Algorithm
        const response = await fetch('/api/optimize', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                start: startCity,
                destinations: destCities,
                priorities: collectPriorities()
            })
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Optimization failed');
        }

        const result = await response.json();

        // Stage 3: Finalizing
        updateLoadingStage(3);
        await new Promise(resolve => setTimeout(resolve, 300));

        // Transform backend response to match frontend expectations
        const transformedResult = {
            route: result.route,
            totalDistance: result.totalDistanceKm,
            estimatedTime: result.estimatedHours.toFixed(1),
            // For comparison display:
            // - If Greedy: show Baseline (random) vs Optimized (greedy)
            // - If AI: show Standard (greedy) vs AI-Enhanced (evolutionary)
            greedyDistance: useAI
                ? result.optimization?.greedyDistanceKm  // AI mode: show greedy as comparison
                : result.optimization?.baselineDistanceKm,  // Greedy mode: show baseline as comparison
            aiDistance: result.totalDistanceKm,
            // Improvement percentage:
            // - If Greedy: improvement over baseline
            // - If AI: improvement over greedy
            improvement: result.optimization?.aiImprovementOverGreedy || result.optimization?.improvementPercentage || 0,
            // CRITICAL: Always pass baseline distance for distance saved calculation
            baselineDistance: result.optimization?.baselineDistanceKm || (result.totalDistanceKm + (result.optimization?.savedDistanceKm || 0)),
            iterations: result.optimization?.aiMetrics?.iterations || 0,
            calculationTime: result.optimization?.calculationTimeMs || 0,
            useAI: useAI,
            algorithm: result.optimization?.algorithm || 'Nearest Neighbor',
            summary: result.summary
        };

        // Debug logging
        console.log('🔍 Backend response:', result);
        console.log('🔍 result.optimization:', result.optimization);
        console.log('🔍 result.optimization.aiMetrics:', result.optimization?.aiMetrics);
        console.log('🔍 Iterations from backend:', result.optimization?.aiMetrics?.iterations);
        console.log('🔍 Transformed iterations:', transformedResult.iterations);

        // Store for export
        lastOptimizedResult = transformedResult;

        displayResults(transformedResult);

    } catch (error) {
        console.error(error);
        // Fallback: Use client-side calculation
        const result = calculateRoute();
        lastOptimizedResult = result;
        displayResults(result);
    } finally {
        hideMetroLoader();
        btn.disabled = false;
        btnText.classList.remove('hidden');
        btnLoading.classList.add('hidden');
    }
}

// ========== Client-side Calculation (Fallback) ==========
function calculateRoute() {
    const startTime = performance.now();
    const allCities = [startCity, ...destCities];

    // Greedy (Nearest Neighbor)
    const greedyRoute = greedyOptimize(allCities);
    const greedyDist = calculateTotalDistance(greedyRoute);

    // AI (2-Opt)
    let aiRoute = [...greedyRoute];
    let iterations = 0;
    if (useAI) {
        const result = twoOptOptimize(greedyRoute);
        aiRoute = result.route;
        iterations = result.iterations;
    }
    const aiDist = calculateTotalDistance(aiRoute);

    const calcTime = performance.now() - startTime;

    return {
        route: useAI ? aiRoute : greedyRoute,
        totalDistance: useAI ? aiDist : greedyDist,
        estimatedTime: ((useAI ? aiDist : greedyDist) / 60).toFixed(1),
        greedyDistance: greedyDist,
        aiDistance: aiDist,
        iterations: iterations,
        calculationTime: calcTime,
        useAI: useAI
    };
}

function greedyOptimize(cities) {
    const route = [cities[0]];
    const remaining = cities.slice(1);

    while (remaining.length > 0) {
        const current = route[route.length - 1];
        let nearest = remaining[0];
        let minDist = getDistance(current, remaining[0]);

        for (const city of remaining) {
            const dist = getDistance(current, city);
            if (dist < minDist) {
                minDist = dist;
                nearest = city;
            }
        }

        route.push(nearest);
        remaining.splice(remaining.indexOf(nearest), 1);
    }

    return route;
}

function twoOptOptimize(route) {
    let improved = true;
    let iterations = 0;
    let bestRoute = [...route];

    while (improved && iterations < 1000) {
        improved = false;
        iterations++;

        for (let i = 1; i < bestRoute.length - 1; i++) {
            for (let j = i + 1; j < bestRoute.length; j++) {
                const newRoute = twoOptSwap(bestRoute, i, j);
                if (calculateTotalDistance(newRoute) < calculateTotalDistance(bestRoute)) {
                    bestRoute = newRoute;
                    improved = true;
                }
            }
        }
    }

    return { route: bestRoute, iterations };
}

function twoOptSwap(route, i, j) {
    const newRoute = route.slice(0, i);
    const reversed = route.slice(i, j + 1).reverse();
    return [...newRoute, ...reversed, ...route.slice(j + 1)];
}

function getDistance(city1, city2) {
    const R = 6371;
    const c1 = CITIES[city1];
    const c2 = CITIES[city2];
    const dLat = (c2.lat - c1.lat) * Math.PI / 180;
    const dLng = (c2.lng - c1.lng) * Math.PI / 180;
    const a = Math.sin(dLat / 2) ** 2 + Math.cos(c1.lat * Math.PI / 180) * Math.cos(c2.lat * Math.PI / 180) * Math.sin(dLng / 2) ** 2;
    return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
}

function calculateTotalDistance(route) {
    let total = 0;
    for (let i = 0; i < route.length - 1; i++) {
        total += getDistance(route[i], route[i + 1]);
    }
    return Math.round(total);
}

// ========== Display Results ==========
function displayResults(result) {
    const section = document.getElementById('resultsSection');
    section.classList.remove('hidden');
    section.classList.add('fade-in');

    // Scroll to results
    section.scrollIntoView({ behavior: 'smooth' });

    // Add staggered animation to metric cards
    const metricCards = document.querySelectorAll('.metric-card');
    metricCards.forEach((card, index) => {
        // Remove previous animation
        card.classList.remove('animate-in');
        // Trigger reflow
        void card.offsetWidth;
        // Add animation
        card.classList.add('animate-in');
    });

    // Update metrics with animation
    animateValue('totalDistance', 0, result.totalDistance, 800);
    animateValue('estimatedTime', 0, parseFloat(result.estimatedTime), 800);

    // Distance saved is ALWAYS vs baseline (random route)
    // Calculate from baseline distance (worst case) to show total savings
    const baselineDistance = result.baselineDistance || result.greedyDistance;
    const distanceSaved = baselineDistance - result.aiDistance;
    animateValue('distanceSaved', 0, Math.max(0, distanceSaved), 800);

    const improvement = result.improvement || 0;
    document.getElementById('improvement').textContent = improvement + '%';

    // Update Before/After Comparison
    const baselineDist = result.baselineDistance || result.greedyDistance || 0;
    document.getElementById('baselineDistance').textContent = Math.round(baselineDist) + ' km';
    document.getElementById('optimizedDistance').textContent = Math.round(result.totalDistance) + ' km';
    document.getElementById('savingsValue').textContent = `${Math.round(distanceSaved)} km saved`;
    document.getElementById('savingsPercentage').textContent = `${improvement}% improvement`;

    // 🎊 CELEBRATION: If savings > 10%, trigger confetti
    if (improvement > 10) {
        setTimeout(() => {
            createConfetti();
            // Add celebration animation to savings card
            const savingsCard = document.querySelector('.metric-card--success');
            if (savingsCard) {
                savingsCard.classList.add('celebrate');
                setTimeout(() => savingsCard.classList.remove('celebrate'), 4500);
            }
        }, 1200);
    }



    // Route visualization with priority badges
    const routePath = document.getElementById('routePath');
    routePath.innerHTML = result.route.map((city, idx) => {
        let nodeClass = 'route-node';
        if (idx === 0) nodeClass += ' start';
        if (idx === result.route.length - 1) nodeClass += ' end';

        // Get priority for this city
        const priority = cityPriorities[city] || (idx === 0 ? null : 3);
        let priorityBadge = '';

        if (priority && idx > 0) {
            const priorityClass = priority === 1 ? 'urgent' : priority === 2 ? 'medium' : 'low';
            const priorityIcon = priority === 1 ? '🔴' : priority === 2 ? '🟡' : '🟢';
            const priorityLabel = priority === 1 ? 'Urgent' : priority === 2 ? 'Medium' : 'Low';
            priorityBadge = `<span class="priority-badge ${priorityClass}">${priorityIcon} ${priorityLabel}</span>`;
        }

        return `
            <div class="${nodeClass}">
                <span class="node-number">${idx + 1}</span>
                <span>${city}</span>
                ${priorityBadge}
            </div>
            ${idx < result.route.length - 1 ? '<span class="route-arrow">→</span>' : ''}
        `;
    }).join('');

    // Technical details
    document.getElementById('algoUsed').textContent = result.algorithm || (result.useAI ? 'Evolutionary Optimizer' : 'Nearest Neighbor');
    document.getElementById('calcTime').textContent = result.calculationTime.toFixed(2) + ' ms';
    document.getElementById('iterations').textContent = result.iterations !== undefined && result.iterations !== null ? result.iterations : '-';
    document.getElementById('greedyDist').textContent = Math.round(baselineDist) + ' km';
    document.getElementById('aiDist').textContent = Math.round(result.totalDistance) + ' km';

    // Summary text (if available from backend)
    if (result.summary) {
        const summaryEl = document.getElementById('summaryText');
        if (summaryEl) {
            summaryEl.textContent = result.summary;
            summaryEl.classList.add('fade-in');
        }
    }

    // Google Maps link
    const mapsUrl = 'https://www.google.com/maps/dir/' + result.route.map(c => encodeURIComponent(c + ', India')).join('/');
    const mapsLinkEl = document.getElementById('mapsLink');
    if (mapsLinkEl) {
        mapsLinkEl.href = mapsUrl;
        console.log('✅ Google Maps URL set:', mapsUrl);
    } else {
        console.error('❌ mapsLink element not found!');
    }

    // Populate real-time controls
    populateRealtimeControls(result.route, result.route[0]);
}

// 🎊 Confetti celebration function
function createConfetti() {
    const colors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4'];
    const particleCount = 50;

    for (let i = 0; i < particleCount; i++) {
        const confetti = document.createElement('div');
        confetti.className = 'confetti-particle';
        confetti.style.left = Math.random() * 100 + '%';
        confetti.style.background = colors[Math.floor(Math.random() * colors.length)];
        confetti.style.animationDelay = (Math.random() * 0.5) + 's';
        confetti.style.animationDuration = (2 + Math.random()) + 's';

        document.body.appendChild(confetti);

        // Remove after animation
        setTimeout(() => confetti.remove(), 3500);
    }
}

function animateValue(id, start, end, duration) {
    const el = document.getElementById(id);
    const startTime = performance.now();
    const isFloat = !Number.isInteger(end);

    function update(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const eased = 1 - Math.pow(1 - progress, 3);
        const current = start + (end - start) * eased;

        el.textContent = isFloat ? current.toFixed(1) : Math.round(current);

        if (progress < 1) {
            requestAnimationFrame(update);
        }
    }

    requestAnimationFrame(update);
}

// ========== Real-Time Recalculation Functions ==========

let currentRoute = [];
let currentStartCity = '';

function populateRealtimeControls(route, start) {
    // Store current route state
    currentRoute = route;
    currentStartCity = start;

    // Show realtime section
    document.getElementById('realtimeSection').style.display = 'block';

    // Populate current position dropdown (all cities in route)
    const posSelect = document.getElementById('currentPosSelect');
    posSelect.innerHTML = '<option value="">Select your current position...</option>';
    route.forEach(city => {
        posSelect.innerHTML += `<option value="${city}">${city}</option>`;
    });

    // Remove old event listener and add new one (to avoid duplicates)
    posSelect.removeEventListener('change', updatePriorityTableForPosition);
    posSelect.addEventListener('change', updatePriorityTableForPosition);

    // Populate add cities multi-select
    updateAddCitiesSelect(route);

    // Populate remove cities multi-select
    updateRemoveCitiesSelect(route);

    // Remove old event listener and add new one for addCitiesMultiSelect (to avoid duplicates)
    const addSelect = document.getElementById('addCitiesMultiSelect');
    if (addSelect) {
        addSelect.removeEventListener('change', updatePriorityTableForPosition);
        addSelect.addEventListener('change', updatePriorityTableForPosition);
    }
}

function updateAddCitiesSelect(route) {
    const addSelect = document.getElementById('addCitiesMultiSelect');
    addSelect.innerHTML = '';

    const availableCities = Object.keys(CITIES).filter(city => !route.includes(city));

    if (availableCities.length === 0) {
        addSelect.innerHTML = '<option disabled>No cities available to add</option>';
    } else {
        availableCities.forEach(city => {
            addSelect.innerHTML += `<option value="${city}">${city}</option>`;
        });
    }
}

function updateRemoveCitiesSelect(route) {
    const removeSelect = document.getElementById('removeCitiesMultiSelect');
    removeSelect.innerHTML = '';

    const removableCities = route.slice(1); // Exclude start city

    if (removableCities.length === 0) {
        removeSelect.innerHTML = '<option disabled>No cities to remove</option>';
    } else {
        removableCities.forEach(city => {
            removeSelect.innerHTML += `<option value="${city}">${city}</option>`;
        });
    }
}

function updatePriorityTableForPosition() {
    const currentPos = document.getElementById('currentPosSelect').value;
    const tbody = document.getElementById('priorityTableBody');

    if (!currentPos || !currentRoute) {
        tbody.innerHTML = '<tr><td colspan="3" class="empty-state">Select current position to see remaining cities</td></tr>';
        return;
    }

    const currentIndex = currentRoute.indexOf(currentPos);
    const remainingCities = currentRoute.slice(currentIndex + 1);

    // Get cities selected to be added (with null check)
    const addSelect = document.getElementById('addCitiesMultiSelect');
    const citiesToAdd = addSelect ? Array.from(addSelect.selectedOptions).map(opt => opt.value) : [];

    // Combine remaining cities + newly selected cities
    const allCities = [...remainingCities, ...citiesToAdd];

    if (allCities.length === 0) {
        tbody.innerHTML = '<tr><td colspan="3" class="empty-state">No remaining cities in route</td></tr>';
        return;
    }

    tbody.innerHTML = '';
    allCities.forEach(city => {
        const currentPriority = cityPriorities[city] || 3;
        const priorityLabel = currentPriority === 1 ? '🔴 Urgent' : currentPriority === 2 ? '🟡 Medium' : '🟢 Low';
        const isNewCity = citiesToAdd.includes(city);

        tbody.innerHTML += `
            <tr ${isNewCity ? 'style="background: rgba(16, 185, 129, 0.1);"' : ''}>
                <td><strong>${city}</strong> ${isNewCity ? '<span style="font-size: 11px; color: #10b981; font-weight: 600;">• NEW</span>' : ''}</td>
                <td>${priorityLabel}</td>
                <td>
                    <select data-city="${city}" class="priority-update-select">
                        <option value="1" ${currentPriority === 1 ? 'selected' : ''}>🔴 Urgent</option>
                        <option value="2" ${currentPriority === 2 ? 'selected' : ''}>🟡 Medium</option>
                        <option value="3" ${currentPriority === 3 ? 'selected' : ''}>🟢 Low</option>
                    </select>
                </td>
            </tr>
        `;
    });
}

async function bulkUpdateRoute() {
    const currentPos = document.getElementById('currentPosSelect').value;

    if (!currentPos) {
        showRealtimeStatus('❌ Please select your current position first', 'error');
        return;
    }

    // Get cities to add (selected options in multi-select)
    const addSelect = document.getElementById('addCitiesMultiSelect');
    const citiesToAdd = Array.from(addSelect.selectedOptions).map(opt => opt.value);

    // Get cities to remove (selected options in multi-select)
    const removeSelect = document.getElementById('removeCitiesMultiSelect');
    const citiesToRemove = Array.from(removeSelect.selectedOptions).map(opt => opt.value);

    // Get priority updates from table
    const priorityUpdates = {};
    const prioritySelects = document.querySelectorAll('.priority-update-select');
    let hasPriorityChanges = false;

    prioritySelects.forEach(select => {
        const city = select.getAttribute('data-city');
        const newPriority = parseInt(select.value);
        const oldPriority = cityPriorities[city] || 3;

        priorityUpdates[city] = newPriority;

        if (newPriority !== oldPriority) {
            hasPriorityChanges = true;
        }
    });

    // Check if any changes were made
    if (citiesToAdd.length === 0 && citiesToRemove.length === 0 && !hasPriorityChanges) {
        showRealtimeStatus('⚠️ No changes to apply', 'error');
        return;
    }

    // Show loading with details
    const changes = [];
    if (citiesToAdd.length > 0) changes.push(`+${citiesToAdd.length} cities`);
    if (citiesToRemove.length > 0) changes.push(`-${citiesToRemove.length} cities`);
    if (hasPriorityChanges) changes.push('priority updates');

    showRealtimeStatus(`🔄 Applying ${changes.join(', ')}...`, 'loading');

    try {
        // Step 1: Remove cities first
        let updatedRoute = currentRoute.slice();
        if (citiesToRemove.length > 0) {
            updatedRoute = updatedRoute.filter(city => !citiesToRemove.includes(city));
        }

        // Step 2: Add new cities to route (after current position)
        if (citiesToAdd.length > 0) {
            const currentIndex = updatedRoute.indexOf(currentPos);
            const beforeCurrent = updatedRoute.slice(0, currentIndex + 1);
            const afterCurrent = updatedRoute.slice(currentIndex + 1);
            updatedRoute = [...beforeCurrent, ...citiesToAdd, ...afterCurrent];
        }

        // Step 3: Update priorities globally
        Object.assign(cityPriorities, priorityUpdates);

        // Set default priorities for newly added cities
        citiesToAdd.forEach(city => {
            if (!(city in cityPriorities)) {
                cityPriorities[city] = 3; // Default to low
            }
        });

        // Step 4: Recalculate route from current position
        const currentIndex = updatedRoute.indexOf(currentPos);
        const remainingDests = updatedRoute.slice(currentIndex + 1);

        const remainingPriorities = {};
        remainingDests.forEach(city => {
            remainingPriorities[city] = cityPriorities[city] || 3;
        });

        const response = await fetch('/api/recalculate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                current_position: currentPos,
                remaining_destinations: remainingDests,
                priorities: remainingPriorities,
                use_ai: true
            })
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Failed to update route');
        }

        const result = await response.json();
        updateRouteDisplay(result);

        // Success message with stats
        const stats = [];
        if (citiesToAdd.length > 0) stats.push(`Added ${citiesToAdd.join(', ')}`);
        if (citiesToRemove.length > 0) stats.push(`Removed ${citiesToRemove.join(', ')}`);
        if (hasPriorityChanges) stats.push('Updated priorities');

        showRealtimeStatus(`✅ Route updated! ${stats.join('. ')}`, 'success');

        // Reset selections
        addSelect.selectedIndex = -1;
        removeSelect.selectedIndex = -1;

    } catch (error) {
        console.error('Bulk update error:', error);
        showRealtimeStatus('❌ Failed to update route: ' + error.message, 'error');
    }
}

async function updateCityPriorityMidRoute() {
    const currentPos = document.getElementById('currentPosSelect').value;
    const cityToUpdate = document.getElementById('updatePriorityCity').value;
    const newPriority = parseInt(document.getElementById('updatePriorityLevel').value);

    if (!currentPos) {
        showRealtimeStatus('Please select your current position first', 'error');
        return;
    }
    if (!cityToUpdate) {
        showRealtimeStatus('Please select a city to update', 'error');
        return;
    }

    showRealtimeStatus(`Updating ${cityToUpdate} priority...`, 'loading');

    try {
        const currentIndex = currentRoute.indexOf(currentPos);
        const remainingDests = currentRoute.slice(currentIndex + 1);
        const newPriorities = {};

        remainingDests.forEach(city => {
            if (city === cityToUpdate) {
                newPriorities[city] = newPriority;
            } else {
                newPriorities[city] = cityPriorities[city] || 3;
            }
        });

        cityPriorities[cityToUpdate] = newPriority;

        const response = await fetch('/api/recalculate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                current_position: currentPos,
                remaining_destinations: remainingDests,
                priorities: newPriorities,
                use_ai: useAI
            })
        });

        if (!response.ok) throw new Error('Failed to update priority');

        const result = await response.json();
        updateRouteDisplay(result);

        // Impact Analysis / COOL FEATURE: Show recalculation time
        const timeMs = result.recalculation_metadata ? result.recalculation_metadata.total_recalc_time_ms : 0;
        const priorityLabel = newPriority === 1 ? '🔴 Urgent' : newPriority === 2 ? '🟡 Medium' : '🟢 Low';

        showRealtimeStatus(`✅ Updated ${cityToUpdate} to ${priorityLabel}! (⚡ Recalculated in ${timeMs}ms)`, 'success');

    } catch (error) {
        showRealtimeStatus('❌ Failed to update priority: ' + error.message, 'error');
    }
}

async function addCityToRoute() {
    const currentPos = document.getElementById('currentPosSelect').value;
    const cityToAdd = document.getElementById('addCitySelect').value;

    if (!currentPos) {
        showRealtimeStatus('Please select your current position first', 'error');
        return;
    }
    if (!cityToAdd) {
        showRealtimeStatus('Please select a city to add', 'error');
        return;
    }

    showRealtimeStatus('Adding city and recalculating...', 'loading');

    try {
        const response = await fetch('/api/add-cities', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                current_position: currentPos,
                existing_route: currentRoute,
                new_cities: [cityToAdd],
                use_ai: useAI
            })
        });

        if (!response.ok) throw new Error('Failed to add city');

        const result = await response.json();
        updateRouteDisplay(result);

        // Impact Analysis
        const timeMs = result.change_metadata ? result.change_metadata.total_operation_time_ms : 0;
        showRealtimeStatus(`✅ Added ${cityToAdd} successfully! (⚡ Recalculated in ${timeMs}ms)`, 'success');
    } catch (error) {
        showRealtimeStatus('❌ Failed to add city: ' + error.message, 'error');
    }
}

async function removeCityFromRoute() {
    const currentPos = document.getElementById('currentPosSelect').value;
    const cityToRemove = document.getElementById('removeCitySelect').value;

    if (!currentPos) {
        showRealtimeStatus('Please select your current position first', 'error');
        return;
    }
    if (!cityToRemove) {
        showRealtimeStatus('Please select a city to remove', 'error');
        return;
    }

    showRealtimeStatus('Removing city and recalculating...', 'loading');

    try {
        const response = await fetch('/api/remove-cities', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                current_position: currentPos,
                existing_route: currentRoute,
                cities_to_remove: [cityToRemove]
            })
        });

        if (!response.ok) throw new Error('Failed to remove city');

        const result = await response.json();
        updateRouteDisplay(result);
        showRealtimeStatus(`✅ Removed ${cityToRemove} successfully!`, 'success');
    } catch (error) {
        showRealtimeStatus('❌ Failed to remove city: ' + error.message, 'error');
    }
}

async function recalculateFromPosition() {
    const currentPos = document.getElementById('currentPosSelect').value;
    if (!currentPos) {
        showRealtimeStatus('Please select current position', 'error');
        return;
    }

    // Get remaining destinations after current position
    const currentIndex = currentRoute.indexOf(currentPos);
    const remaining = currentRoute.slice(currentIndex + 1);

    if (remaining.length === 0) {
        showRealtimeStatus('No remaining destinations to recalculate', 'error');
        return;
    }

    showRealtimeStatus(`Recalculating from ${currentPos}...`, 'loading');

    try {
        const response = await fetch('/api/recalculate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                current_position: currentPos,
                remaining_destinations: remaining,
                use_ai: useAI
            })
        });

        if (!response.ok) throw new Error('Failed to recalculate');

        const result = await response.json();

        // Prepend completed portion of route
        const completed = currentRoute.slice(0, currentIndex + 1);
        result.route = completed.concat(result.route.slice(1)); // Skip duplicate current position

        updateRouteDisplay(result);
        showRealtimeStatus(`✅ Recalculated from ${currentPos}!`, 'success');
    } catch (error) {
        showRealtimeStatus('❌ Failed to recalculate: ' + error.message, 'error');
    }
}

function updateRouteDisplay(apiResult) {
    // Extract route data from API response
    const result = {
        route: apiResult.route || apiResult,
        totalDistance: apiResult.totalDistanceKm || apiResult.total_distance || 0,
        estimatedTime: (apiResult.estimatedHours || (apiResult.total_distance ? apiResult.total_distance / 60 : 0)).toFixed(1),
        greedyDistance: apiResult.optimization?.greedyDistanceKm || 0,
        aiDistance: apiResult.totalDistanceKm || apiResult.total_distance || 0,
        baselineDistance: apiResult.optimization?.baselineDistanceKm || 0,
        improvement: apiResult.optimization?.aiImprovementOverGreedy || apiResult.optimization?.improvementPercentage || 0,
        useAI: apiResult.optimization?.algorithm?.includes('Evolutionary') || false,
        algorithm: apiResult.optimization?.algorithm || 'Nearest Neighbor',
        iterations: apiResult.optimization?.aiMetrics?.iterations || 0,
        calculationTime: apiResult.optimization?.calculationTimeMs || 0,
        summary: apiResult.summary || ''
    };

    // Update route visualization
    const routePath = document.getElementById('routePath');
    if (routePath) {
        routePath.innerHTML = result.route.map((city, idx) => {
            let nodeClass = 'route-node';
            if (idx === 0) nodeClass += ' start';
            if (idx === result.route.length - 1) nodeClass += ' end';

            return `
                <div class="${nodeClass}">
                    <span class="node-number">${idx + 1}</span>
                    ${city}
                </div>
                ${idx < result.route.length - 1 ? '<span class="route-arrow">→</span>' : ''}
            `;
        }).join('');
    }

    // Update ALL metrics with animation
    animateValue('totalDistance', 0, result.totalDistance, 800);
    animateValue('estimatedTime', 0, parseFloat(result.estimatedTime), 800);

    const distanceSaved = result.baselineDistance - result.aiDistance;
    animateValue('distanceSaved', 0, Math.max(0, distanceSaved), 800);

    const improvementEl = document.getElementById('improvement');
    if (improvementEl) improvementEl.textContent = result.improvement + '%';

    // Update 3-way comparison
    const greedyLabel = document.querySelector('.compare-badge.greedy');
    const aiLabel = document.querySelectorAll('.compare-badge.ai')[0];
    const aiEnhancedLabel = document.querySelectorAll('.compare-badge.ai')[1];
    const thirdVs = document.getElementById('thirdVs');
    const thirdItem = document.getElementById('thirdItem');

    if (result.useAI && result.greedyDistance > 0) {
        // AI mode: Show 3-way comparison
        if (greedyLabel) greedyLabel.innerHTML = '📊 Baseline';
        if (aiLabel) aiLabel.innerHTML = '⚡ Standard';
        if (aiEnhancedLabel) aiEnhancedLabel.innerHTML = '🚀 AI-Enhanced';

        if (thirdVs) thirdVs.style.display = 'flex';
        if (thirdItem) thirdItem.style.display = 'flex';

        const greedyDistEl = document.getElementById('greedyDist');
        const aiDistEl = document.getElementById('aiDist');
        const aiEnhancedDistEl = document.getElementById('aiEnhancedDist');

        if (greedyDistEl) greedyDistEl.textContent = result.baselineDistance.toFixed(2) + ' km';
        if (aiDistEl) aiDistEl.textContent = result.greedyDistance.toFixed(2) + ' km';
        if (aiEnhancedDistEl) aiEnhancedDistEl.textContent = result.aiDistance.toFixed(2) + ' km';
    } else {
        // Greedy mode: Show 2-way comparison
        if (greedyLabel) greedyLabel.innerHTML = '📊 Baseline';
        if (aiLabel) aiLabel.innerHTML = '✅ Optimized';

        if (thirdVs) thirdVs.style.display = 'none';
        if (thirdItem) thirdItem.style.display = 'none';

        const greedyDistEl = document.getElementById('greedyDist');
        const aiDistEl = document.getElementById('aiDist');

        if (greedyDistEl) greedyDistEl.textContent = result.baselineDistance.toFixed(2) + ' km';
        if (aiDistEl) aiDistEl.textContent = result.aiDistance.toFixed(2) + ' km';
    }

    // Update technical details
    const algoUsedEl = document.getElementById('algoUsed');
    const calcTimeEl = document.getElementById('calcTime');
    const iterationsEl = document.getElementById('iterations');

    if (algoUsedEl) algoUsedEl.textContent = result.algorithm;
    if (calcTimeEl) calcTimeEl.textContent = result.calculationTime.toFixed(2) + ' ms';
    if (iterationsEl) iterationsEl.textContent = result.iterations || '-';

    // Update AI summary if available
    if (result.summary) {
        const aiSummaryEl = document.getElementById('aiSummary');
        if (aiSummaryEl) aiSummaryEl.textContent = result.summary;
    }

    // Update controls with new route
    populateRealtimeControls(result.route, result.route[0]);

    // Update Google Maps link
    const mapsLink = document.getElementById('mapsLink');
    if (mapsLink) {
        const mapsUrl = 'https://www.google.com/maps/dir/' + result.route.map(c => encodeURIComponent(c + ', India')).join('/');
        mapsLink.href = mapsUrl;
    }
}

function showRealtimeStatus(message, type) {
    const statusEl = document.getElementById('realtimeStatus');
    statusEl.textContent = message;
    statusEl.className = 'realtime-status ' + type;

    // Auto-hide success messages after 3 seconds
    if (type === 'success') {
        setTimeout(() => {
            statusEl.textContent = '';
            statusEl.className = 'realtime-status';
        }, 3000);
    }
}

// ========== Toggle Technical Details ==========
function toggleTechnicalDetails() {
    const content = document.getElementById('techDetailsContent');
    const btn = document.getElementById('techToggleBtn');
    const toggleText = btn.querySelector('.toggle-text');

    if (content.classList.contains('hidden')) {
        content.classList.remove('hidden');
        btn.classList.add('expanded');
        toggleText.textContent = 'Hide Technical Details';
    } else {
        content.classList.add('hidden');
        btn.classList.remove('expanded');
        toggleText.textContent = 'Show Technical Details';
    }
}
