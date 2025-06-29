import os
import json
from typing import List, Dict, Any
import time
from openai import OpenAI
from langchain.prompts import PromptTemplate

def analyze_llm_brand_positioning_streaming(brand_name: str, competitors: List[str], queries: List[str], llm_models: List[str] = None, progress_callback=None) -> Dict[str, Any]:
    """
    Streaming version of LLM brand positioning analysis with progress updates.
    
    Args:
        brand_name (str): The brand to analyze
        competitors (List[str]): List of competitor names
        queries (List[str]): List of queries to test
        llm_models (List[str]): List of LLM models to test
        progress_callback: Function to call with progress updates
        
    Returns:
        Dict: GEO analysis results
    """
    if llm_models is None:
        llm_models = ["gpt-4o-mini-2024-07-18", "gpt-3.5-turbo"]
    
    def log_progress(message, step=None, progress=None, **kwargs):
        if progress_callback:
            progress_callback(message, step, progress, **kwargs)
    
    log_progress(f"Starting GEO analysis for {len(queries)} queries across {len(llm_models)} models", "init", 0)
    
    analysis_results = {
        "brand_name": brand_name,
        "total_queries_tested": len(queries),
        "llm_models_tested": llm_models,
        "query_performance": [],
        "model_performance": {},
        "competitor_analysis": {},
        "overall_metrics": {
            "mention_rate": 0,
            "positive_positioning": 0,
            "neutral_positioning": 0,
            "negative_positioning": 0,
            "average_mention_position": 0,
            "brand_visibility_score": 0
        }
    }
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set")
    
    client = OpenAI(api_key=api_key)
    
    total_mentions = 0
    mention_positions = []
    sentiment_scores = {"positive": 0, "neutral": 0, "negative": 0}
    
    total_tests = len(queries) * len(llm_models)
    current_test = 0
    
    for model in llm_models:
        log_progress(f"Starting analysis with {model}", "model_start", current_test / total_tests * 100, model=model)
        
        analysis_results["model_performance"][model] = {
            "queries_tested": len(queries),
            "mention_rate": 0,
            "average_position": 0,
            "sentiment_distribution": {"positive": 0, "neutral": 0, "negative": 0}
        }
        
        model_mentions = 0
        model_positions = []
        model_sentiments = {"positive": 0, "neutral": 0, "negative": 0}
        
        for query_data in queries:
            query = query_data.get("query", str(query_data)) if isinstance(query_data, dict) else str(query_data)
            current_test += 1
            progress = (current_test / total_tests) * 100
            
            log_progress(f"Asking {model}: \"{query}\"", "query_start", progress, model=model, query=query)
            
            # Generate LLM response for the query
            llm_response = get_llm_response_streaming(client, query, model, log_progress)
            
            log_progress(f"Analyzing brand positioning in response", "analysis_start", progress, model=model, query=query)
            
            # Analyze brand positioning in the response
            brand_analysis = analyze_brand_in_response_streaming(client, llm_response, brand_name, competitors, log_progress)
            
            # Log the results
            if brand_analysis["brand_mentioned"]:
                position_text = f"at position #{brand_analysis['mention_position']}" if brand_analysis["mention_position"] else "mentioned"
                log_progress(f"✅ Found \"{brand_name}\" {position_text} with {brand_analysis['sentiment']} sentiment", 
                           "brand_found", progress, model=model, query=query, 
                           position=brand_analysis["mention_position"], sentiment=brand_analysis["sentiment"])
            else:
                log_progress(f"❌ \"{brand_name}\" not mentioned in response", "brand_not_found", progress, model=model, query=query)
            
            # Store query performance
            query_performance = {
                "query": query,
                "model": model,
                "llm_response": llm_response[:500] + "..." if len(llm_response) > 500 else llm_response,
                "brand_mentioned": brand_analysis["brand_mentioned"],
                "mention_position": brand_analysis["mention_position"],
                "sentiment": brand_analysis["sentiment"],
                "context": brand_analysis["context"],
                "competitors_mentioned": brand_analysis["competitors_mentioned"],
                "response_length": len(llm_response.split())
            }
            
            analysis_results["query_performance"].append(query_performance)
            
            # Update metrics
            if brand_analysis["brand_mentioned"]:
                total_mentions += 1
                model_mentions += 1
                
                if brand_analysis["mention_position"] is not None:
                    mention_positions.append(brand_analysis["mention_position"])
                    model_positions.append(brand_analysis["mention_position"])
                
                sentiment_scores[brand_analysis["sentiment"]] += 1
                model_sentiments[brand_analysis["sentiment"]] += 1
        
        # Calculate model-specific metrics
        if len(queries) > 0:
            analysis_results["model_performance"][model]["mention_rate"] = (model_mentions / len(queries)) * 100
            
        if model_positions:
            analysis_results["model_performance"][model]["average_position"] = sum(model_positions) / len(model_positions)
            
        for sentiment in model_sentiments:
            if model_mentions > 0:
                analysis_results["model_performance"][model]["sentiment_distribution"][sentiment] = (model_sentiments[sentiment] / model_mentions) * 100
        
        log_progress(f"Completed analysis with {model} - {model_mentions}/{len(queries)} mentions", 
                   "model_complete", current_test / total_tests * 100, model=model)
    
    log_progress("Calculating final metrics...", "calculating", 95)
    
    # Calculate overall metrics
    total_possible_mentions = len(queries) * len(llm_models)
    if total_possible_mentions > 0:
        analysis_results["overall_metrics"]["mention_rate"] = (total_mentions / total_possible_mentions) * 100
        analysis_results["overall_metrics"]["brand_visibility_score"] = (total_mentions / total_possible_mentions) * 100
    
    if mention_positions:
        analysis_results["overall_metrics"]["average_mention_position"] = sum(mention_positions) / len(mention_positions)
    
    if total_mentions > 0:
        analysis_results["overall_metrics"]["positive_positioning"] = (sentiment_scores["positive"] / total_mentions) * 100
        analysis_results["overall_metrics"]["neutral_positioning"] = (sentiment_scores["neutral"] / total_mentions) * 100
        analysis_results["overall_metrics"]["negative_positioning"] = (sentiment_scores["negative"] / total_mentions) * 100
    
    # Competitor analysis
    competitor_summary = {}
    for query_perf in analysis_results["query_performance"]:
        for comp in query_perf["competitors_mentioned"]:
            comp_name = comp["name"]
            if comp_name not in competitor_summary:
                competitor_summary[comp_name] = {
                    "mentions": 0,
                    "average_position": 0,
                    "positions": [],
                    "sentiment_distribution": {"positive": 0, "neutral": 0, "negative": 0}
                }
            competitor_summary[comp_name]["mentions"] += 1
            if comp.get("position") is not None:
                competitor_summary[comp_name]["positions"].append(comp["position"])
            if comp.get("sentiment"):
                competitor_summary[comp_name]["sentiment_distribution"][comp["sentiment"]] += 1
    
    # Calculate competitor averages
    for comp_name, data in competitor_summary.items():
        if data["positions"]:
            data["average_position"] = sum(data["positions"]) / len(data["positions"])
    
    analysis_results["competitor_analysis"] = competitor_summary
    
    log_progress("GEO analysis complete!", "complete", 100)
    
    return analysis_results

def analyze_llm_brand_positioning(brand_name: str, competitors: List[str], queries: List[str], llm_models: List[str] = None) -> Dict[str, Any]:
    """
    Analyze how a brand positions in LLM responses across different queries.
    This is the core of Generative Engine Optimization (GEO).
    
    Args:
        brand_name (str): The brand to analyze
        competitors (List[str]): List of competitor names
        queries (List[str]): List of queries to test
        llm_models (List[str]): List of LLM models to test (defaults to OpenAI models)
        
    Returns:
        Dict: GEO analysis results including brand mentions, positioning, and competitor comparison
    """
    if llm_models is None:
        llm_models = ["gpt-4o-mini-2024-07-18", "gpt-3.5-turbo"]
    
    analysis_results = {
        "brand_name": brand_name,
        "total_queries_tested": len(queries),
        "llm_models_tested": llm_models,
        "query_performance": [],
        "model_performance": {},
        "competitor_analysis": {},
        "overall_metrics": {
            "mention_rate": 0,
            "positive_positioning": 0,
            "neutral_positioning": 0,
            "negative_positioning": 0,
            "average_mention_position": 0,
            "brand_visibility_score": 0
        }
    }
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set")
    
    client = OpenAI(api_key=api_key)
    
    total_mentions = 0
    mention_positions = []
    sentiment_scores = {"positive": 0, "neutral": 0, "negative": 0}
    
    for model in llm_models:
        analysis_results["model_performance"][model] = {
            "queries_tested": len(queries),
            "mention_rate": 0,
            "average_position": 0,
            "sentiment_distribution": {"positive": 0, "neutral": 0, "negative": 0}
        }
        
        model_mentions = 0
        model_positions = []
        model_sentiments = {"positive": 0, "neutral": 0, "negative": 0}
        
        for query_data in queries:
            query = query_data.get("query", str(query_data)) if isinstance(query_data, dict) else str(query_data)
            
            # Generate LLM response for the query
            llm_response = get_llm_response(client, query, model)
            
            # Analyze brand positioning in the response
            brand_analysis = analyze_brand_in_response(client, llm_response, brand_name, competitors)
            
            # Store query performance
            query_performance = {
                "query": query,
                "model": model,
                "llm_response": llm_response[:500] + "..." if len(llm_response) > 500 else llm_response,
                "brand_mentioned": brand_analysis["brand_mentioned"],
                "mention_position": brand_analysis["mention_position"],
                "sentiment": brand_analysis["sentiment"],
                "context": brand_analysis["context"],
                "competitors_mentioned": brand_analysis["competitors_mentioned"],
                "response_length": len(llm_response.split())
            }
            
            analysis_results["query_performance"].append(query_performance)
            
            # Update metrics
            if brand_analysis["brand_mentioned"]:
                total_mentions += 1
                model_mentions += 1
                
                if brand_analysis["mention_position"] is not None:
                    mention_positions.append(brand_analysis["mention_position"])
                    model_positions.append(brand_analysis["mention_position"])
                
                sentiment_scores[brand_analysis["sentiment"]] += 1
                model_sentiments[brand_analysis["sentiment"]] += 1
        
        # Calculate model-specific metrics
        if len(queries) > 0:
            analysis_results["model_performance"][model]["mention_rate"] = (model_mentions / len(queries)) * 100
            
        if model_positions:
            analysis_results["model_performance"][model]["average_position"] = sum(model_positions) / len(model_positions)
            
        for sentiment in model_sentiments:
            if model_mentions > 0:
                analysis_results["model_performance"][model]["sentiment_distribution"][sentiment] = (model_sentiments[sentiment] / model_mentions) * 100
    
    # Calculate overall metrics
    total_possible_mentions = len(queries) * len(llm_models)
    if total_possible_mentions > 0:
        analysis_results["overall_metrics"]["mention_rate"] = (total_mentions / total_possible_mentions) * 100
        analysis_results["overall_metrics"]["brand_visibility_score"] = (total_mentions / total_possible_mentions) * 100
    
    if mention_positions:
        analysis_results["overall_metrics"]["average_mention_position"] = sum(mention_positions) / len(mention_positions)
    
    if total_mentions > 0:
        analysis_results["overall_metrics"]["positive_positioning"] = (sentiment_scores["positive"] / total_mentions) * 100
        analysis_results["overall_metrics"]["neutral_positioning"] = (sentiment_scores["neutral"] / total_mentions) * 100
        analysis_results["overall_metrics"]["negative_positioning"] = (sentiment_scores["negative"] / total_mentions) * 100
    
    # Competitor analysis
    competitor_summary = {}
    for query_perf in analysis_results["query_performance"]:
        for comp in query_perf["competitors_mentioned"]:
            comp_name = comp["name"]
            if comp_name not in competitor_summary:
                competitor_summary[comp_name] = {
                    "mentions": 0,
                    "average_position": 0,
                    "positions": [],
                    "sentiment_distribution": {"positive": 0, "neutral": 0, "negative": 0}
                }
            competitor_summary[comp_name]["mentions"] += 1
            if comp.get("position") is not None:
                competitor_summary[comp_name]["positions"].append(comp["position"])
            if comp.get("sentiment"):
                competitor_summary[comp_name]["sentiment_distribution"][comp["sentiment"]] += 1
    
    # Calculate competitor averages
    for comp_name, data in competitor_summary.items():
        if data["positions"]:
            data["average_position"] = sum(data["positions"]) / len(data["positions"])
    
    analysis_results["competitor_analysis"] = competitor_summary
    
    return analysis_results

def get_llm_response_streaming(client: OpenAI, query: str, model: str, log_progress=None) -> str:
    """
    Get response from LLM for a given query with streaming progress updates and retry logic.
    
    Args:
        client: OpenAI client
        query: The query to ask
        model: The model to use
        log_progress: Progress logging function
        
    Returns:
        str: The LLM response
    """
    max_retries = 3
    base_delay = 2
    
    for attempt in range(max_retries):
        try:
            if log_progress:
                if attempt > 0:
                    log_progress(f"🔄 Retrying query to {model} (attempt {attempt + 1}/{max_retries})...", "llm_retry", None, model=model, query=query[:50] + "...", attempt=attempt+1)
                else:
                    log_progress(f"🤖 Sending query to {model}: \"{query[:50]}...\"", "llm_request", None, model=model, query=query[:50] + "...")
            
            # Create request with enhanced error handling
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "user", "content": query}
                ],
                max_tokens=500,
                temperature=0.7,
                timeout=45  # Increased timeout
            )
            
            result = response.choices[0].message.content
            
            if not result or result.strip() == "":
                raise ValueError("Empty response received from API")
            
            if log_progress:
                response_preview = result[:100] + "..." if len(result) > 100 else result
                log_progress(f"✅ Received response from {model}: \"{response_preview}\"", "llm_response", None, model=model, query=query[:50] + "...")
            
            return result
            
        except Exception as e:
            error_msg = str(e).lower()
            
            # Determine if this is a retryable error
            retryable_errors = ['timeout', 'network', 'connection', 'rate limit', 'server error', 'internal error']
            is_retryable = any(err in error_msg for err in retryable_errors)
            
            if attempt < max_retries - 1 and is_retryable:
                delay = base_delay * (2 ** attempt)  # Exponential backoff
                if log_progress:
                    log_progress(f"⚠️ {error_msg.title()} with {model}, retrying in {delay}s: {str(e)[:100]}", "llm_retry_warning", None, model=model, query=query[:50] + "...", error=str(e)[:100], delay=delay)
                time.sleep(delay)
            elif attempt < max_retries - 1:
                # Non-retryable error, but still try once more
                if log_progress:
                    log_progress(f"⚠️ Non-retryable error with {model}, trying once more: {str(e)[:100]}", "llm_retry_warning", None, model=model, query=query[:50] + "...", error=str(e)[:100])
                time.sleep(1)
            else:
                if log_progress:
                    log_progress(f"❌ Failed to get response from {model} after {max_retries} attempts: {str(e)[:100]}", "llm_error", None, model=model, query=query[:50] + "...", error=str(e)[:100])
                print(f"Error getting LLM response after {max_retries} attempts: {e}")
                return f"Error: Could not get response from {model} after {max_retries} attempts: {str(e)[:100]}"

def get_llm_response(client: OpenAI, query: str, model: str) -> str:
    """
    Get response from LLM for a given query.
    
    Args:
        client: OpenAI client
        query: The query to ask
        model: The model to use
        
    Returns:
        str: The LLM response
    """
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": query}
            ],
            max_tokens=500,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error getting LLM response: {e}")
        return f"Error: Could not get response from {model}"

def analyze_brand_in_response_streaming(client: OpenAI, response: str, brand_name: str, competitors: List[str], log_progress=None) -> Dict[str, Any]:
    """
    Analyze how a brand is positioned within an LLM response with streaming updates.
    
    Args:
        client: OpenAI client
        response: The LLM response to analyze
        brand_name: The brand to look for
        competitors: List of competitor names
        log_progress: Progress logging function
        
    Returns:
        Dict: Analysis of brand positioning
    """
    if log_progress:
        log_progress(f"🔍 Analyzing brand positioning for \"{brand_name}\"...", "brand_analysis_start")
    
    # Create analysis prompt
    analysis_prompt = f"""
    Analyze the following text response and determine:
    1. Is the brand "{brand_name}" mentioned? (yes/no)
    2. If mentioned, what position in the response (1=first mention, 2=second, etc.)?
    3. What is the sentiment toward "{brand_name}"? (positive/neutral/negative)
    4. What is the context of the mention? (recommendation, comparison, criticism, etc.)
    5. Which of these competitors are mentioned: {competitors}
    
    Text to analyze: "{response}"
    
    Respond in JSON format:
    {{
        "brand_mentioned": true/false,
        "mention_position": number or null,
        "sentiment": "positive"/"neutral"/"negative",
        "context": "brief description",
        "competitors_mentioned": [
            {{"name": "competitor", "position": number, "sentiment": "positive/neutral/negative"}}
        ]
    }}
    """
    
    try:
        if log_progress:
            log_progress(f"🤖 Asking analysis LLM to examine response...", "brand_analysis_llm")
            
        analysis_response = client.chat.completions.create(
            model="gpt-4o-mini-2024-07-18",
            messages=[
                {"role": "user", "content": analysis_prompt}
            ],
            max_tokens=300,
            temperature=0.1
        )
        
        analysis_text = analysis_response.choices[0].message.content
        
        if log_progress:
            log_progress(f"✅ Brand analysis complete", "brand_analysis_complete")
        
        # Clean up JSON response
        if analysis_text.startswith("```json"):
            analysis_text = analysis_text[7:-3].strip()
        elif analysis_text.startswith("```"):
            analysis_text = analysis_text[3:-3].strip()
        
        return json.loads(analysis_text)
        
    except Exception as e:
        if log_progress:
            log_progress(f"❌ Brand analysis failed, using fallback: {str(e)}", "brand_analysis_fallback")
        print(f"Error analyzing brand in response: {e}")
        # Fallback analysis
        brand_mentioned = brand_name.lower() in response.lower()
        return {
            "brand_mentioned": brand_mentioned,
            "mention_position": 1 if brand_mentioned else None,
            "sentiment": "neutral",
            "context": "automatic analysis failed",
            "competitors_mentioned": []
        }

def analyze_brand_in_response(client: OpenAI, response: str, brand_name: str, competitors: List[str]) -> Dict[str, Any]:
    """
    Analyze how a brand is positioned within an LLM response.
    
    Args:
        client: OpenAI client
        response: The LLM response to analyze
        brand_name: The brand to look for
        competitors: List of competitor names
        
    Returns:
        Dict: Analysis of brand positioning
    """
    # Create analysis prompt
    analysis_prompt = f"""
    Analyze the following text response and determine:
    1. Is the brand "{brand_name}" mentioned? (yes/no)
    2. If mentioned, what position in the response (1=first mention, 2=second, etc.)?
    3. What is the sentiment toward "{brand_name}"? (positive/neutral/negative)
    4. What is the context of the mention? (recommendation, comparison, criticism, etc.)
    5. Which of these competitors are mentioned: {competitors}
    
    Text to analyze: "{response}"
    
    Respond in JSON format:
    {{
        "brand_mentioned": true/false,
        "mention_position": number or null,
        "sentiment": "positive"/"neutral"/"negative",
        "context": "brief description",
        "competitors_mentioned": [
            {{"name": "competitor", "position": number, "sentiment": "positive/neutral/negative"}}
        ]
    }}
    """
    
    try:
        analysis_response = client.chat.completions.create(
            model="gpt-4o-mini-2024-07-18",
            messages=[
                {"role": "user", "content": analysis_prompt}
            ],
            max_tokens=300,
            temperature=0.1
        )
        
        analysis_text = analysis_response.choices[0].message.content
        
        # Clean up JSON response
        if analysis_text.startswith("```json"):
            analysis_text = analysis_text[7:-3].strip()
        elif analysis_text.startswith("```"):
            analysis_text = analysis_text[3:-3].strip()
        
        return json.loads(analysis_text)
        
    except Exception as e:
        print(f"Error analyzing brand in response: {e}")
        # Fallback analysis
        brand_mentioned = brand_name.lower() in response.lower()
        return {
            "brand_mentioned": brand_mentioned,
            "mention_position": 1 if brand_mentioned else None,
            "sentiment": "neutral",
            "context": "automatic analysis failed",
            "competitors_mentioned": []
        }

def get_geo_optimization_suggestions(analysis_results: Dict[str, Any]) -> List[str]:
    """
    Generate GEO optimization suggestions based on analysis results.
    
    Args:
        analysis_results: Results from analyze_llm_brand_positioning
        
    Returns:
        List[str]: List of optimization suggestions
    """
    suggestions = []
    metrics = analysis_results["overall_metrics"]
    
    if metrics["mention_rate"] < 50:
        suggestions.append("🔍 Low mention rate detected. Consider creating more content that positions your brand as a solution to common queries.")
    
    if metrics["positive_positioning"] < 60:
        suggestions.append("😊 Improve positive sentiment by highlighting customer success stories and unique value propositions.")
    
    if metrics["average_mention_position"] > 3:
        suggestions.append("⬆️ Brand mentioned late in responses. Create authoritative content to become the primary reference.")
    
    # Analyze competitor performance
    competitor_analysis = analysis_results.get("competitor_analysis", {})
    strong_competitors = []
    for comp, data in competitor_analysis.items():
        if data["mentions"] > metrics["mention_rate"] / 100 * analysis_results["total_queries_tested"]:
            strong_competitors.append(comp)
    
    if strong_competitors:
        suggestions.append(f"🥊 Strong competitor presence detected: {', '.join(strong_competitors[:3])}. Consider differentiation strategies.")
    
    if not suggestions:
        suggestions.append("🎉 Strong GEO performance! Continue monitoring and optimizing content for emerging queries.")
    
    return suggestions

def generate_llm_test_queries(brand_name: str, industry: str, use_case: str = "general") -> List[str]:
    """
    Generate test queries specifically for LLM analysis (GEO focus).
    
    Args:
        brand_name: The brand name
        industry: The industry sector
        use_case: Specific use case or category
        
    Returns:
        List[str]: List of LLM-focused test queries
    """
    base_queries = [
        f"What are the best {industry} solutions?",
        f"Compare top {industry} companies",
        f"Recommend a {industry} tool for startups",
        f"What's the difference between {brand_name} and competitors?",
        f"Best practices for {industry}",
        f"How to choose a {industry} provider?",
        f"Problems with {industry} tools",
        f"Future of {industry}",
        f"Case studies in {industry}",
        f"ROI of {industry} solutions",
        f"Enterprise {industry} recommendations",
        f"Small business {industry} options",
        f"Open source vs commercial {industry} tools",
        f"Security considerations for {industry}",
        f"Integration capabilities of {industry} platforms"
    ]
    
    return base_queries