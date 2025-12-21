"""
Task 8: REST API for Route Optimization
FastAPI endpoints with Swagger documentation and input validation.

ENDPOINTS:
- POST /api/optimize - Main route optimization endpoint
# Main application entry point
# Hackathon Audit Fix applied: exposed cache stats
- POST /api/recalculate - Real-time route recalculation
- GET /api/cities - Get available cities list
- GET /health - Health check

DOCUMENTATION:
- Swagger UI: /docs
- ReDoc: /redoc
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from typing import Dict, Any
import time

from models.schemas import OptimizeRequest, OptimizeResponse, ErrorResponse, RecalculateRequest, AddCitiesRequest, RemoveCitiesRequest
from utils.algorithm import optimize_route
from utils.recalculation import recalculate_route, add_cities_to_route, remove_cities_from_route, update_priorities, bulk_update_route
from utils.cities import CITIES, validate_city
from utils.ai_summary import generate_ai_summary

# Initialize FastAPI app
app = FastAPI(
    title="Route Optimizer - Genetic Algorithm",
    description="Intelligent multi-city route optimization system using Genetic Algorithm for logistics companies",
    version="1.0.0",
    contact={
        "name": "Route Optimizer Team",
        "url": "https://github.com/SrijanG07/Route-Optimizer"
    }
)

# CORS Middleware (required for browser-based frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for frontend
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint - Returns frontend HTML"""
    from fastapi.responses import FileResponse
    return FileResponse("static/index.html")


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint for monitoring with cache statistics."""
    from utils.distance import get_cache_info, get_distance_method
    
    cache_info = get_cache_info()
    
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "service": "route-optimizer",
        "distance_method": get_distance_method(),
        "cache_stats": {
            "hits": cache_info.hits,
            "misses": cache_info.misses,
            "size": cache_info.currsize,
            "max_size": cache_info.maxsize,
            "hit_rate": round(cache_info.hits / (cache_info.hits + cache_info.misses) * 100, 2) if (cache_info.hits + cache_info.misses) > 0 else 0
        }
    }


@app.get("/api/cities", tags=["Cities"])
async def get_cities():
    """
    Get list of available cities for route planning.
    
    Returns:
        List of cities with coordinates
    """
    return {
        "success": True,
        "count": len(CITIES),
        "cities": list(CITIES.keys()),
        "details": CITIES
    }


@app.post("/api/optimize", response_model=OptimizeResponse, tags=["Optimization"])
async def optimize_delivery_route(request: OptimizeRequest):
    """
    Optimize delivery route using Genetic Algorithm.
    
    This endpoint takes a starting city and multiple destinations, then computes
    the most efficient delivery route using evolutionary optimization with
    priority constraint handling.
    
    **Features:**
    - Genetic Algorithm (Evolutionary Optimization)
    - Priority-based delivery handling (urgent/medium/low)
    - Distance and time estimation
    - Performance metrics
    
    **Example Request:**
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
            "use_ai": false
        }
    }
    ```
    
    **Response:**
    - Optimized route sequence
    - Total distance (km)
    - Estimated travel time (hours)
    - Distance savings vs baseline
    - AI metrics (if AI optimization used)
    """
    try:
        # Validate start city
        if not validate_city(request.start):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid start city: {request.start}. Use /api/cities to see available cities."
            )
        
        # Validate all destinations
        invalid_destinations = [city for city in request.destinations if not validate_city(city)]
        if invalid_destinations:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid destination cities: {', '.join(invalid_destinations)}"
            )
        
        # Check for duplicates
        if request.start in request.destinations:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Start city '{request.start}' cannot be in destinations list"
            )
        
        if len(request.destinations) != len(set(request.destinations)):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Duplicate cities found in destinations"
            )
        
        # Validate priorities if provided
        if request.priorities:
            for city, priority in request.priorities.items():
                if city not in request.destinations:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Priority specified for city '{city}' which is not in destinations"
                    )
                if priority not in [1, 2, 3]:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Invalid priority {priority} for city '{city}'. Must be 1 (urgent), 2 (medium), or 3 (low)"
                    )
        
        # Debug logging for priorities
        if request.priorities:
            print(f"🎯 Received priorities: {request.priorities}")
        
        # Run Genetic Algorithm optimization
        result = optimize_route(
            start=request.start,
            destinations=request.destinations,
            priorities=request.priorities,
            use_ai=True  # Always use Genetic Algorithm
        )
        
        greedy_distance = result.get("baseline_distance", result["total_distance"])
        ai_saved = result.get("distance_saved", 0)
        
        # Add priorities to result for AI summary context
        if request.priorities:
            result["priorities"] = request.priorities
        
        # Add baseline comparison data for summary
        result["greedy_distance"] = greedy_distance
        result["ai_saved_over_greedy"] = ai_saved
        
        # Generate Google Maps link
        maps_link = "https://www.google.com/maps/dir/" + "/".join(result["route"])
        
        # Format response
        optimization_data = {
            "algorithm": result["algorithm"],
            "calculationTimeMs": result["execution_time_ms"],
            "savedDistanceKm": result["distance_saved"],
            "improvementPercentage": result["improvement_percentage"],
            "citiesProcessed": result["cities_processed"],
            "baselineDistanceKm": result["baseline_distance"],  # Random baseline
            "greedyDistanceKm": greedy_distance  # Greedy comparison
        }
        
        # Add AI metrics if available
        if "ai_metrics" in result:
            optimization_data["aiMetrics"] = {
                "iterations": result["ai_metrics"].get("iterations", 0),
                "aiImprovementOverGreedy": result.get("improvement_percentage", 0)
            }
        
        return OptimizeResponse(
            success=True,
            route=result["route"],
            totalDistanceKm=result["total_distance"],
            estimatedHours=round(result["total_distance"] / 60, 2),  # Assume 60 km/h avg speed
            summary=generate_ai_summary(result),  # Use AI-generated summary
            optimization=optimization_data,
            mapsLink=maps_link
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@app.post("/api/recalculate", tags=["Recalculation"])
async def recalculate_delivery_route(request: RecalculateRequest):
    """
    Recalculate route from current position (mid-route optimization).
    
    **Use Cases:**
    - Driver completed some deliveries, need to optimize remaining route
    - New urgent delivery added mid-route
    - Priority changed for remaining cities
    
    **Example Request:**
    ```json
    {
        "current_position": "Pune",
        "remaining_destinations": ["Bangalore", "Chennai"],
        "priorities": {"Bangalore": 1},
        "use_ai": false
    }
    ```
    """
    try:
        # Validate cities
        if not validate_city(request.current_position):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid current position: {request.current_position}"
            )
        
        invalid_destinations = [city for city in request.remaining_destinations if not validate_city(city)]
        if invalid_destinations:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid destination cities: {', '.join(invalid_destinations)}"
            )
        
        # Recalculate
        result = recalculate_route(
            current_position=request.current_position,
            remaining_destinations=request.remaining_destinations,
            priorities=request.priorities,
            use_ai=request.use_ai
        )
        
        # Calculate baseline (random shuffle) for comparison
        import random
        from utils.algorithm import calculate_total_distance
        baseline_route = [request.current_position] + random.sample(request.remaining_destinations, len(request.remaining_destinations))
        baseline_distance = calculate_total_distance(baseline_route)
        
        # Calculate greedy for comparison if AI is used
        greedy_distance = result["total_distance"]
        ai_improvement = 0
        ai_saved = 0
        
        if request.use_ai:
            # Run greedy algorithm for comparison
            greedy_result = recalculate_route(
                current_position=request.current_position,
                remaining_destinations=request.remaining_destinations,
                priorities=request.priorities,
                use_ai=False
            )
            greedy_distance = greedy_result["total_distance"]
            ai_distance = result["total_distance"]
            ai_improvement = round((greedy_distance - ai_distance) / greedy_distance * 100, 1) if greedy_distance > 0 else 0
            ai_saved = round(greedy_distance - ai_distance, 2)
        
        # Format response similar to optimize endpoint
        return {
            "success": True,
            "route": result["route"],
            "totalDistanceKm": result["total_distance"],
            "estimatedHours": round(result["total_distance"] / 60, 2),
            "optimization": {
                "algorithm": result["algorithm"],
                "calculationTimeMs": result["execution_time_ms"],
                "savedDistanceKm": result.get("distance_saved", 0),
                "improvementPercentage": result.get("improvement_percentage", 0),
                "citiesProcessed": result["cities_processed"],
                "baselineDistanceKm": baseline_distance,
                "greedyDistanceKm": greedy_distance,
                "aiImprovementOverGreedy": ai_improvement,
                "aiSavedOverGreedy": ai_saved
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Recalculation failed: {str(e)}"
        )


@app.post("/api/add-cities", tags=["Recalculation"])
async def add_cities_endpoint(request: AddCitiesRequest):
    """
    Add new cities to existing route with reoptimization.
    
    **Example:**
    ```json
    {
        "current_position": "Pune",
        "existing_route": ["Mumbai", "Pune", "Bangalore"],
        "new_cities": ["Chennai"],
        "priorities": {"Chennai": 1},
        "use_ai": false
    }
    ```
    """
    try:
        result = add_cities_to_route(
            current_position=request.current_position,
            existing_route=request.existing_route,
            new_cities=request.new_cities,
            priorities=request.priorities,
            use_ai=request.use_ai
        )
        
        # Calculate baseline and greedy for comparison
        import random
        from utils.algorithm import calculate_total_distance
        
        all_cities = list(set(request.existing_route + request.new_cities))
        baseline_route = random.sample(all_cities, len(all_cities))
        baseline_distance = calculate_total_distance(baseline_route)
        
        greedy_distance = result["total_distance"]
        ai_improvement = 0
        ai_saved = 0
        
        if request.use_ai:
            greedy_result = add_cities_to_route(
                current_position=request.current_position,
                existing_route=request.existing_route,
                new_cities=request.new_cities,
                priorities=request.priorities,
                use_ai=False
            )
            greedy_distance = greedy_result["total_distance"]
            ai_distance = result["total_distance"]
            ai_improvement = round((greedy_distance - ai_distance) / greedy_distance * 100, 1) if greedy_distance > 0 else 0
            ai_saved = round(greedy_distance - ai_distance, 2)
        
        return {
            "success": True,
            "route": result["route"],
            "totalDistanceKm": result["total_distance"],
            "estimatedHours": round(result["total_distance"] / 60, 2),
            "optimization": {
                "algorithm": result.get("algorithm", "Nearest Neighbor"),
                "baselineDistanceKm": baseline_distance,
                "greedyDistanceKm": greedy_distance,
                "aiImprovementOverGreedy": ai_improvement,
                "aiSavedOverGreedy": ai_saved
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add cities: {str(e)}"
        )


@app.post("/api/remove-cities", tags=["Recalculation"])
async def remove_cities_endpoint(request: RemoveCitiesRequest):
    """
    Remove cities from existing route with reoptimization.
    
    **Example:**
    ```json
    {
        "current_position": "Pune",
        "existing_route": ["Mumbai", "Pune", "Bangalore", "Chennai"],
        "cities_to_remove": ["Chennai"]
    }
    ```
    """
    try:
        result = remove_cities_from_route(
            current_position=request.current_position,
            existing_route=request.existing_route,
            cities_to_remove=request.cities_to_remove
        )
        
        # Calculate baseline for comparison
        import random
        from utils.algorithm import calculate_total_distance
        
        remaining_cities = [c for c in request.existing_route if c not in request.cities_to_remove]
        baseline_route = random.sample(remaining_cities, len(remaining_cities))
        baseline_distance = calculate_total_distance(baseline_route)
        
        return {
            "success": True,
            "route": result["route"],
            "totalDistanceKm": result["total_distance"],
            "estimatedHours": round(result["total_distance"] / 60, 2),
            "optimization": {
                "algorithm": result.get("algorithm", "Nearest Neighbor"),
                "baselineDistanceKm": baseline_distance,
                "greedyDistanceKm": result["total_distance"],  # Remove uses greedy by default
                "aiImprovementOverGreedy": 0,
                "aiSavedOverGreedy": 0
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to remove cities: {str(e)}"
        )


# Error handler for validation errors
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.detail,
            "status_code": exc.status_code
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
