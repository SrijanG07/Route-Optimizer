/* ========================================
   MAPBOX INTEGRATION
   Interactive map visualization for routes
   ======================================== */

// Mapbox access token - Get free token at https://account.mapbox.com/
// Note: This is a public token, safe to use in frontend code
const MAPBOX_TOKEN = 'pk.eyJ1IjoibWFwYm94IiwiYSI6ImNpejY4NXVycTA2emYycXBndHRqcmZ3N3gifQ.rJcFIG214AriISLbB6B5aw'; // Demo token

let map = null;
let routeSource = null;
let markersLayer = [];

/**
 * Initialize Mapbox map
 */
function initializeMap() {
    // Check if mapboxgl is loaded
    if (!window.mapboxgl) {
        console.error('Mapbox GL JS not loaded');
        return;
    }

    mapboxgl.accessToken = MAPBOX_TOKEN;

    map = new mapboxgl.Map({
        container: 'map-container',
        style: 'mapbox://styles/mapbox/dark-v11', // Dark theme
        center: [78.9629, 20.5937], // Center of India
        zoom: 4,
        pitch: 0,
        bearing: 0,
        antialias: true
    });

    // Add navigation controls
    map.addControl(new mapboxgl.NavigationControl(), 'top-right');

    // Add fullscreen control
    map.addControl(new mapboxgl.FullscreenControl(), 'top-right');

    // Add scale control
    map.addControl(new mapboxgl.ScaleControl({
        maxWidth: 100,
        unit: 'metric'
    }), 'bottom-left');

    // Custom styling after map loads
    map.on('load', () => {
        console.log('✅ Mapbox map loaded successfully');

        // Add route source (initially empty)
        map.addSource('route', {
            type: 'geojson',
            data: {
                type: 'Feature',
                properties: {},
                geometry: {
                    type: 'LineString',
                    coordinates: []
                }
            }
        });

        // Add route layer with gradient effect
        map.addLayer({
            id: 'route-line',
            type: 'line',
            source: 'route',
            layout: {
                'line-join': 'round',
                'line-cap': 'round'
            },
            paint: {
                'line-color': '#06b6d4',
                'line-width': 4,
                'line-opacity': 0.8
            }
        });

        // Add route glow effect
        map.addLayer({
            id: 'route-glow',
            type: 'line',
            source: 'route',
            layout: {
                'line-join': 'round',
                'line-cap': 'round'
            },
            paint: {
                'line-color': '#06b6d4',
                'line-width': 12,
                'line-opacity': 0.3,
                'line-blur': 6
            }
        });
    });

    return map;
}

/**
 * Draw route on map with animation
 * @param {Array} cities - Array of city names in route order
 */
function drawRoute(cities) {
    if (!map || !cities || cities.length < 2) {
        console.warn('Map not initialized or invalid cities');
        return;
    }

    // Clear existing markers
    clearMarkers();

    // Get coordinates for each city
    const coordinates = cities.map(city => {
        const coords = CITIES[city];
        if (!coords) {
            console.warn(`City ${city} not found in CITIES data`);
            return null;
        }
        return [coords.lng, coords.lat];
    }).filter(coord => coord !== null);

    if (coordinates.length < 2) {
        console.warn('Not enough valid coordinates to draw route');
        return;
    }

    // Update route source
    const routeGeojson = {
        type: 'Feature',
        properties: {},
        geometry: {
            type: 'LineString',
            coordinates: coordinates
        }
    };

    map.getSource('route').setData(routeGeojson);

    // Add markers for each city
    cities.forEach((city, index) => {
        const coords = CITIES[city];
        if (!coords) return;

        const priority = cityPriorities[city] || (index === 0 ? null : 3);
        addMarker([coords.lng, coords.lat], city, index, priority, index === 0, index === cities.length - 1);
    });

    // Fit map bounds to show entire route (with slight delay to ensure route is rendered)
    setTimeout(() => {
        fitMapToBounds(coordinates);
    }, 100);

    // Animate route drawing
    animateRouteLine();
}

/**
 * Add marker to map
 */
function addMarker(lngLat, cityName, index, priority, isStart, isEnd) {
    const el = document.createElement('div');
    el.className = 'custom-marker';

    // Determine marker color based on priority or position
    let color = '#06b6d4'; // Default cyan
    let label = index + 1;

    if (isStart) {
        color = '#10b981'; // Green for start
        label = '🏁';
    } else if (isEnd) {
        color = '#06b6d4'; // Cyan for end
        label = '🎯';
    } else if (priority) {
        if (priority === 1) {
            color = '#ef4444'; // Red for urgent
            label = `${index + 1}🔴`;
        } else if (priority === 2) {
            color = '#f59e0b'; // Orange for medium
            label = `${index + 1}🟡`;
        } else {
            color = '#10b981'; // Green for low
            label = `${index + 1}🟢`;
        }
    }

    el.style.cssText = `
    width: 40px;
    height: 40px;
    background: ${color};
    border: 3px solid white;
    border-radius: 50% 50% 50% 0;
    transform: rotate(-45deg);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 14px;
    font-weight: bold;
    color: white;
    cursor: pointer;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    transition: transform 0.2s;
  `;

    el.innerHTML = `<span style="transform: rotate(45deg);">${label}</span>`;

    el.addEventListener('mouseenter', () => {
        el.style.transform = 'rotate(-45deg) scale(1.2)';
    });

    el.addEventListener('mouseleave', () => {
        el.style.transform = 'rotate(-45deg) scale(1)';
    });

    // Create popup
    const priorityText = priority === 1 ? '🔴 Urgent' : priority === 2 ? '🟡 Medium' : priority === 3 ? '🟢 Low' : '';
    const positionText = isStart ? '🏁 Starting Point' : isEnd ? '🎯 Final Destination' : `Stop #${index + 1}`;

    const popup = new mapboxgl.Popup({ offset: 25 })
        .setHTML(`
      <div style="padding: 8px; font-family: Inter, sans-serif;">
        <h3 style="margin: 0 0 4px 0; font-size: 16px; font-weight: 600;">${cityName}</h3>
        <p style="margin: 0; font-size: 12px; color: #64748b;">${positionText}</p>
        ${priorityText ? `<p style="margin: 4px 0 0 0; font-size: 12px; font-weight: 500;">${priorityText}</p>` : ''}
      </div>
    `);

    // Create and add marker
    const marker = new mapboxgl.Marker(el)
        .setLngLat(lngLat)
        .setPopup(popup)
        .addTo(map);

    // Animate marker drop
    setTimeout(() => {
        el.classList.add('marker-drop');
    }, index * 100);

    markersLayer.push(marker);
}

/**
 * Clear all markers from map
 */
function clearMarkers() {
    markersLayer.forEach(marker => marker.remove());
    markersLayer = [];
}

/**
 * Fit map bounds to show all coordinates
 */
function fitMapToBounds(coordinates) {
    if (!coordinates || coordinates.length === 0) return;

    const bounds = coordinates.reduce((bounds, coord) => {
        return bounds.extend(coord);
    }, new mapboxgl.LngLatBounds(coordinates[0], coordinates[0]));

    map.fitBounds(bounds, {
        padding: { top: 80, bottom: 80, left: 80, right: 80 },
        maxZoom: 6, // Prevent extreme zoom-in, ensure entire route is visible
        duration: 1500,
        essential: true
    });
}

/**
 * Animate route line drawing
 */
function animateRouteLine() {
    // This would require more complex implementation with map.setPaintProperty
    // For now, the route appears animated via CSS if needed
    console.log('Route line drawn');
}

/**
 * Update map theme
 */
function setMapTheme(isDark) {
    if (!map) return;

    const style = isDark
        ? 'mapbox://styles/mapbox/dark-v11'
        : 'mapbox://styles/mapbox/light-v11';

    map.setStyle(style);
}

/**
 * Resize map (call after container size changes)
 */
function resizeMap() {
    if (map) {
        map.resize();
    }
}

// Export functions for use in app.js
window.MapboxIntegration = {
    initializeMap,
    drawRoute,
    clearMarkers,
    fitMapToBounds,
    setMapTheme,
    resizeMap
};
