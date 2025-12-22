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
            - ai_metrics: Genetic algorithm metrics (iterations, etc.)
    
    Returns:
        AI-generated summary string explaining the route optimization
    """
    if not GEMINI_API_KEY:
        print("Warning: GEMINI_API_KEY not found, using enhanced fallback summary")
        return _generate_fallback_summary(result)
    
    try:
        # Extract route details
        route = result["route"]
        distance = result["total_distance"]
        savings = result.get("distance_saved", 0)
        improvement = result.get("improvement_percentage", 0)
        algorithm = result["algorithm"]
        priorities = result.get("priorities", {})
        
        # AI metrics (if Genetic Algorithm was used)
        ai_metrics = result.get("ai_metrics", {})
        iterations = ai_metrics.get("iterations", 0)
        violations = ai_metrics.get("priority_violations", 0)
        
        # Greedy comparison (if available)
        greedy_distance = result.get("greedy_distance", 0)
        
        # Build context for AI
        priority_info = ""
        if priorities:
            urgent = [city for city, p in priorities.items() if p == 1]
            medium = [city for city, p in priorities.items() if p == 2]            
            low = [city for city, p in priorities.items() if p == 3]
            
            priority_info = "\n\nPriority Constraints:"
            if urgent:
                priority_info += f"\n- 🔴 Urgent: {', '.join(urgent)}"
            if medium:
                priority_info += f"\n- 🟡 Medium: {', '.join(medium)}"
            if low:
                priority_info += f"\n- 🟢 Low: {', '.join(low)}"
            priority_info += f"\n- Priority Violations: {violations} (should be 0)"
        
        # GA details
        ga_details = ""
        if "Evolutionary" in algorithm and iterations > 0:
            ga_details = f"\n\nGenetic Algorithm Process:"
            ga_details += f"\n- Generations Evolved: {iterations}"
            ga_details += f"\n- Population Size: 40 routes per generation"
            ga_details += f"\n- Optimization Method: Crossover + Mutation + Selection"
            
            if greedy_distance > 0:
                ga_improvement = round((greedy_distance - distance) / greedy_distance * 100, 1)
                ga_details += f"\n- Greedy Distance: {greedy_distance:.1f} km"
                ga_details += f"\n- GA Distance: {distance:.1f} km"
                ga_details += f"\n- GA Improvement: {ga_improvement}% better than greedy"
        
        prompt = f"""You are an expert in logistics optimization and genetic algorithms. Generate a comprehensive, professional summary (3-4 sentences) explaining this delivery route optimization.

**Route Details:**
Route: {' → '.join(route)}
Total Distance: {distance:.1f} km
Distance Saved vs Random Baseline: {savings:.1f} km ({improvement}% improvement)
Algorithm Used: {algorithm}{priority_info}{ga_details}

**Instructions:**
1. Explain that this is a **Genetic Algorithm (Evolutionary Optimizer)** solution
2. Mention it explored **{iterations} generations** of route variations using population-based search
3. Explain how GA is better than greedy: it doesn't just pick nearest neighbor, it evolves multiple solutions and picks the best
4. If priority violations = 0, emphasize that it PERFECTLY respects priority constraints (Urgent first, then Medium, then Low)
5. If there's a greedy comparison, highlight the GA's superiority with specific numbers
6. Use technical but accessible language - this is for a hackathon demo
7. Be specific about HOW the algorithm worked, not just what it achieved

Write a compelling summary that shows the INTELLIGENCE of the genetic algorithm approach."""

        # Try multiple Gemini models (newest to oldest) for compatibility
        # Most users will have access to gemini-1.5-flash (free tier)
        models_to_try = [
            'gemini-1.5-flash',      # Free tier, widely available
            'gemini-1.5-pro',        # Better quality, may need paid tier
            'gemini-pro',            # Legacy, very widely available
        ]
        
        for model_name in models_to_try:
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(prompt)
                
                if response and response.text:
                    print(f"✅ Generated summary using {model_name}")
                    return response.text.strip()
            except Exception as model_error:
                print(f"⚠️  Model {model_name} failed: {model_error}")
                continue  # Try next model
        
        # All models failed, use fallback
        print("⚠️  All Gemini models failed, using enhanced fallback")
        return _generate_fallback_summary(result)
    
    except Exception as e:
        print(f"Gemini API error: {e}")
        return _generate_fallback_summary(result)


def _generate_fallback_summary(result: Dict[str, Any]) -> str:
    """
    Enhanced fallback summary that explains genetic algorithm process.
    Used when Gemini API is unavailable.
    """
    route = result["route"]
    distance = result["total_distance"]
    savings = result.get("distance_saved", 0)
    improvement = result.get("improvement_percentage", 0)
    algorithm = result["algorithm"]
    
    # Get GA metrics if available
    ai_metrics = result.get("ai_metrics", {})
    iterations = ai_metrics.get("iterations", 0)
    violations = ai_metrics.get("priority_violations", 0)
    
    # Get greedy comparison
    greedy_distance = result.get("greedy_distance", 0)
    
    summary = f"**Genetic Algorithm Route Optimization**\n\n"
    summary += f"Optimized route from **{route[0]}** through {len(route)-2} cities to **{route[-1]}**.\n\n"
    
    if "Evolutionary" in algorithm and iterations > 0:
        summary += f"**How the Genetic Algorithm Worked:**\n"
        summary += f"The optimizer explored **{iterations} generations** of route variations using evolutionary principles. "
        summary += f"In each generation, it maintained a population of 40 different routes, selecting the best performers "
        summary += f"and combining them through crossover and mutation to create improved offspring. "
        
        if greedy_distance > 0:
            ga_improvement = round((greedy_distance - distance) / greedy_distance * 100, 1)
            summary += f"This evolutionary approach found a route **{ga_improvement}% better** than the greedy "
            summary += f"nearest-neighbor algorithm ({greedy_distance:.1f} km vs {distance:.1f} km), demonstrating "
            summary += f"that exploring multiple solutions beats always picking the closest next city.\n\n"
        else:
            summary += f"\n\n"
        
        if violations == 0 and result.get("priorities"):
            summary += f"**Priority Handling:** All delivery constraints were **perfectly satisfied** "
            summary += f"(🔴 Urgent cities visited first, then 🟡 Medium, then 🟢 Low). "
            summary += f"The GA's fitness function heavily penalized priority violations, ensuring business requirements were met.\n\n"
    
    summary += f"**Results:**\n"
    summary += f"- Total Distance: {distance:.2f} km\n"
    
    if savings > 0:
        summary += f"- Distance Saved: {savings:.2f} km ({improvement}% improvement vs random baseline)\n"
    
    # Add priority info if available
    priorities = result.get("priorities", {})
    if priorities:
        urgent = [city for city, p in priorities.items() if p == 1]
        if urgent:
            summary += f"- Priority Deliveries: {', '.join(urgent)} (Urgent) routed optimally\n"
    
    return summary
