import os
import requests
from bs4 import BeautifulSoup
import json
from typing import List, Dict, Any
import time
import random
from urllib.parse import quote_plus, urljoin
import re
from serpapi.client import SerpAPI

def real_google_search(query: str, location: str = "United States", num_results: int = 10) -> List[Dict[str, Any]]:
    """
    Perform real Google search using SerpAPI.
    
    Args:
        query (str): The search query
        location (str): Geographic location for the search
        num_results (int): Number of results to return
        
    Returns:
        List[Dict]: List of search results with title, url, snippet, and position
    """
    serpapi_key = os.getenv("SERPAPI_KEY")
    
    if not serpapi_key:
        # Fall back to simulation if no API key
        return simulate_google_search(query, location, num_results)
    
    try:
        # Map location names to SerpAPI location codes
        location_mapping = {
            "United States": "us",
            "United Kingdom": "uk", 
            "Canada": "ca",
            "Australia": "au",
            "Germany": "de",
            "France": "fr",
            "Italy": "it",
            "Spain": "es",
            "Netherlands": "nl",
            "Sweden": "se",
            "Japan": "jp",
            "South Korea": "kr",
            "Singapore": "sg",
            "India": "in",
            "Brazil": "br"
        }
        
        location_code = location_mapping.get(location, "us")
        
        client = Client(api_key=serpapi_key)
        
        results = client.search({
            "q": query,
            "location": location,
            "gl": location_code,
            "num": min(num_results, 10),  # SerpAPI free tier limit
            "engine": "google"
        })
        
        if "error" in results:
            print(f"SerpAPI Error: {results['error']}")
            return simulate_google_search(query, location, num_results)
        
        organic_results = results.get("organic_results", [])
        
        search_results = []
        for i, result in enumerate(organic_results[:num_results]):
            search_results.append({
                "position": i + 1,
                "title": result.get("title", ""),
                "url": result.get("link", ""),
                "snippet": result.get("snippet", ""),
                "domain": result.get("displayed_link", "").split('/')[0] if result.get("displayed_link") else "",
                "location": location,
                "query": query
            })
        
        return search_results
        
    except Exception as e:
        print(f"SerpAPI search failed: {e}")
        # Fall back to simulation
        return simulate_google_search(query, location, num_results)

def simulate_google_search(query: str, location: str = "United States", num_results: int = 10) -> List[Dict[str, Any]]:
    """
    Simulate a Google search using web scraping (for demonstration purposes).
    In production, you should use Google Custom Search API or SerpAPI.
    
    Args:
        query (str): The search query
        location (str): Geographic location for the search
        num_results (int): Number of results to return
        
    Returns:
        List[Dict]: List of search results with title, url, snippet, and position
    """
    # Simulate search results (in production, replace with actual API calls)
    sample_results = [
        {
            "position": 1,
            "title": f"Official {query} Website",
            "url": "https://example.com/official",
            "snippet": f"Official website for {query}. Learn more about our products and services.",
            "domain": "example.com"
        },
        {
            "position": 2,
            "title": f"{query} - Wikipedia",
            "url": "https://en.wikipedia.org/wiki/" + quote_plus(query),
            "snippet": f"{query} is a company that specializes in various business areas.",
            "domain": "wikipedia.org"
        },
        {
            "position": 3,
            "title": f"{query} Reviews and Ratings",
            "url": "https://reviews.com/" + quote_plus(query),
            "snippet": f"Read customer reviews and ratings for {query}.",
            "domain": "reviews.com"
        },
        {
            "position": 4,
            "title": f"{query} News and Updates",
            "url": "https://news.com/" + quote_plus(query),
            "snippet": f"Latest news and updates about {query}.",
            "domain": "news.com"
        },
        {
            "position": 5,
            "title": f"Competitor Analysis - {query}",
            "url": "https://competitor.com/" + quote_plus(query),
            "snippet": f"Compare {query} with other similar companies.",
            "domain": "competitor.com"
        }
    ]
    
    # Add some randomization to make it more realistic
    random.shuffle(sample_results)
    for i, result in enumerate(sample_results[:num_results]):
        result["position"] = i + 1
        result["location"] = location
        result["query"] = query
    
    return sample_results[:num_results]

def analyze_brand_presence(brand_name: str, competitors: List[str], queries: List[str], locations: List[str]) -> Dict[str, Any]:
    """
    Analyze brand presence across different queries and locations.
    
    Args:
        brand_name (str): The brand to analyze
        competitors (List[str]): List of competitor names
        queries (List[str]): List of search queries to test
        locations (List[str]): List of geographic locations
        
    Returns:
        Dict: Analysis results including rankings, visibility, and competitor comparison
    """
    analysis_results = {
        "brand_name": brand_name,
        "total_queries_tested": len(queries),
        "locations_tested": locations,
        "query_performance": [],
        "location_performance": {},
        "competitor_analysis": {},
        "overall_metrics": {
            "average_position": 0,
            "visibility_score": 0,
            "queries_in_top_10": 0,
            "queries_not_found": 0
        }
    }
    
    all_positions = []
    queries_in_top_10 = 0
    queries_not_found = 0
    
    for location in locations:
        analysis_results["location_performance"][location] = {
            "queries_tested": len(queries),
            "average_position": 0,
            "visibility_score": 0
        }
        
        location_positions = []
        
        for query_data in queries:
            query = query_data.get("query", str(query_data)) if isinstance(query_data, dict) else str(query_data)
            
            # Search for this query in this location (real or simulated)
            search_results = real_google_search(query, location)
            
            # Find brand position
            brand_position = None
            brand_found = False
            
            for result in search_results:
                if brand_name.lower() in result["title"].lower() or brand_name.lower() in result["snippet"].lower():
                    brand_position = result["position"]
                    brand_found = True
                    break
            
            # Analyze competitor presence
            competitors_found = []
            for result in search_results:
                for competitor in competitors:
                    if competitor.lower() in result["title"].lower() or competitor.lower() in result["snippet"].lower():
                        competitors_found.append({
                            "name": competitor,
                            "position": result["position"],
                            "title": result["title"],
                            "url": result["url"]
                        })
            
            # Calculate metrics
            if brand_found:
                all_positions.append(brand_position)
                location_positions.append(brand_position)
                if brand_position <= 10:
                    queries_in_top_10 += 1
            else:
                queries_not_found += 1
            
            # Store query performance
            query_performance = {
                "query": query,
                "location": location,
                "brand_position": brand_position,
                "brand_found": brand_found,
                "competitors_found": competitors_found,
                "total_results": len(search_results),
                "search_results": search_results[:3]  # Store top 3 for reference
            }
            
            analysis_results["query_performance"].append(query_performance)
        
        # Calculate location-specific metrics
        if location_positions:
            analysis_results["location_performance"][location]["average_position"] = sum(location_positions) / len(location_positions)
            analysis_results["location_performance"][location]["visibility_score"] = (len(location_positions) / len(queries)) * 100
    
    # Calculate overall metrics
    if all_positions:
        analysis_results["overall_metrics"]["average_position"] = sum(all_positions) / len(all_positions)
    
    analysis_results["overall_metrics"]["visibility_score"] = ((len(queries) * len(locations) - queries_not_found) / (len(queries) * len(locations))) * 100
    analysis_results["overall_metrics"]["queries_in_top_10"] = queries_in_top_10
    analysis_results["overall_metrics"]["queries_not_found"] = queries_not_found
    
    # Competitor analysis summary
    competitor_summary = {}
    for query_perf in analysis_results["query_performance"]:
        for comp in query_perf["competitors_found"]:
            comp_name = comp["name"]
            if comp_name not in competitor_summary:
                competitor_summary[comp_name] = {
                    "appearances": 0,
                    "average_position": 0,
                    "positions": []
                }
            competitor_summary[comp_name]["appearances"] += 1
            competitor_summary[comp_name]["positions"].append(comp["position"])
    
    # Calculate competitor averages
    for comp_name, data in competitor_summary.items():
        if data["positions"]:
            data["average_position"] = sum(data["positions"]) / len(data["positions"])
    
    analysis_results["competitor_analysis"] = competitor_summary
    
    return analysis_results

def get_search_suggestions(brand_name: str, industry: str) -> List[str]:
    """
    Generate search query suggestions for brand analysis.
    
    Args:
        brand_name (str): The brand name
        industry (str): The industry sector
        
    Returns:
        List[str]: List of suggested search queries
    """
    base_queries = [
        f"{brand_name}",
        f"{brand_name} reviews",
        f"{brand_name} vs competitors",
        f"best {industry} companies",
        f"{industry} leaders",
        f"{brand_name} pricing",
        f"{brand_name} features",
        f"{brand_name} alternatives",
        f"top {industry} brands",
        f"{brand_name} comparison"
    ]
    
    return base_queries

def generate_geo_locations() -> List[str]:
    """
    Generate a list of geographic locations for testing.
    
    Returns:
        List[str]: List of geographic locations
    """
    return [
        "United States",
        "United Kingdom", 
        "Canada",
        "Australia",
        "Germany",
        "France",
        "Italy",
        "Spain",
        "Netherlands",
        "Sweden",
        "Japan",
        "South Korea",
        "Singapore",
        "India",
        "Brazil"
    ]