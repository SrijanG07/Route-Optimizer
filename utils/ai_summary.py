"""
AI-powered route summary generation using Google Gemini.
Provides natural language explanations of optimized routes.
"""

import os
from typing import Dict, Any
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)


def generate_ai_summary(result: Dict[str, Any]) -> str:
    """
    Generate natural language summary using Google Gemini AI.
    
    Args:
        result: Optimization result dictionary containing:
            - route: List of cities in optimized order
            - total_distance: Total route distance in km
            - distance_saved: Distance saved vs baseline
            - improvement_percentage: Percentage improvement
            - algorithm: Algorithm used
            - priorities: Optional priority mapping
    
    Returns:
        AI-generated summary string explaining the route optimization
    """
    if not GEMINI_API_KEY:
        print("Warning: GEMINI_API_KEY not found, using fallback summary")
        return _generate_fallback_summary(result)
    
    try:
        # Extract route details
        route = result["route"]
        distance = result["total_distance"]
        savings = result.get("distance_saved", 0)
        improvement = result.get("improvement_percentage", 0)
        algorithm = result["algorithm"]
        priorities = result.get("priorities", {})
        
        # AI vs Greedy comparison (if available)
        greedy_distance = result.get("greedy_distance")
        ai_improvement = result.get("ai_improvement_over_greedy", 0)
        ai_saved = result.get("ai_saved_over_greedy", 0)
        
        # Build context for AI
        priority_info = ""
        if priorities:
            high_priority = [city for city, p in priorities.items() if p == 1]
            if high_priority:
                priority_info = f"\nHigh-priority deliveries: {', '.join(high_priority)}"
        
        # AI vs Greedy comparison info
        ga_comparison = ""
        if algorithm == "Evolutionary Optimizer" and greedy_distance and ai_saved > 0:
            ga_comparison = f"\nGreedy algorithm distance: {greedy_distance:.1f} km\nGenetic Algorithm (AI) found {ai_saved:.1f} km shorter route ({ai_improvement}% better)"
        
        prompt = f"""You are a logistics optimization expert. Generate a professional, concise summary (2-3 sentences) for this delivery route optimization:

Route: {' → '.join(route)}
Total Distance: {distance:.1f} km
Distance Saved: {savings:.1f} km ({improvement}% improvement over baseline)
Algorithm Used: {algorithm}{priority_info}{ga_comparison}

IMPORTANT: If Genetic Algorithm data is provided, emphasize how the AI-powered evolutionary approach found a better solution than the greedy nearest-neighbor algorithm by exploring multiple route variations and selecting the optimal one. Explain the route choice in a professional tone. If there are priority deliveries, mention how they were handled. Highlight the efficiency gains and AI advantages. Be specific and concise."""

        # Generate summary using Gemini
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)
        
        if response and response.text:
            return response.text.strip()
        else:
            return _generate_fallback_summary(result)
    
    except Exception as e:
        print(f"Gemini API error: {e}")
        return _generate_fallback_summary(result)


def _generate_fallback_summary(result: Dict[str, Any]) -> str:
    """
    Fallback template-based summary if Gemini API fails.
    Provides basic route information without AI generation.
    """
    route = result["route"]
    distance = result["total_distance"]
    savings = result.get("distance_saved", 0)
    improvement = result.get("improvement_percentage", 0)
    algorithm = result["algorithm"]
    
    summary = f"Optimized route from {route[0]} through {len(route)-2} cities to {route[-1]} using {algorithm}. "
    summary += f"Total distance: {distance:.2f} km. "
    
    if savings > 0:
        summary += f"This route saves {savings:.2f} km ({improvement}% improvement) compared to baseline routing."
    
    return summary
