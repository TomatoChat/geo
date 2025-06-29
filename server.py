import sys
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(override=True)

# Also try loading from explicit path
load_dotenv(dotenv_path='.env', override=True)

from flask import Flask, request, jsonify, render_template, Response
import json
import time
import libs.utils as utils
import libs.openai as openaiAnalytics
import libs.geo_analysis as geo_analysis
import libs.search_analysis as search_analysis

app = Flask(__name__)

# Print environment variables for debugging
print("=== Environment Variables ===")
api_key = os.getenv('OPENAI_API_KEY', 'NOT SET')
print(f"OPENAI_API_KEY: {api_key[:10] if api_key != 'NOT SET' else 'NOT SET'}{'*' * 20 if api_key != 'NOT SET' else ''}")
print(f"PROJECT_DIRECTORY: {os.getenv('PROJECT_DIRECTORY', 'NOT SET')}")
print(f"Current working directory: {os.getcwd()}")
print(f"API key length: {len(api_key) if api_key != 'NOT SET' else 0}")
print("=============================")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/brand-info', methods=['POST'])
def get_brand_info():
    try:
        data = request.json
        brand_name = data.get('brandName')
        brand_website = data.get('brandWebsite')
        brand_country = data.get('brandCountry', 'world')
        
        if not brand_name or not brand_website:
            return jsonify({'error': 'brandName and brandWebsite are required'}), 400
        
        brand_information = utils.getCompanyInfo(brand_name, brand_website, brand_country)
        return jsonify(brand_information)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/generate-queries', methods=['POST'])
def generate_queries():
    try:
        data = request.json
        brand_name = data.get('brandName')
        brand_country = data.get('brandCountry', 'world')
        brand_description = data.get('brandDescription')
        brand_industry = data.get('brandIndustry')
        total_queries = data.get('totalQueries', 10)
        
        if not all([brand_name, brand_description, brand_industry]):
            return jsonify({'error': 'brandName, brandDescription, and brandIndustry are required'}), 400
        
        queries = openaiAnalytics.getCoherentQueries(
            brand_name, brand_country, brand_description, brand_industry, total_queries
        )
        return jsonify({'queries': queries})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/test-queries', methods=['POST'])
def test_queries():
    try:
        data = request.json
        brand_name = data.get('brandName')
        queries = data.get('queries', [])
        competitors = data.get('competitors', [])
        locations = data.get('locations', ['United States'])
        
        if not brand_name or not queries:
            return jsonify({'error': 'brandName and queries are required'}), 400
        
        # Extract query strings from query objects if needed
        query_strings = []
        for q in queries:
            if isinstance(q, dict):
                query_strings.append(q.get('query', str(q)))
            else:
                query_strings.append(str(q))
        
        analysis = search_analysis.analyze_brand_presence(
            brand_name, competitors, query_strings, locations
        )
        return jsonify(analysis)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get-llm-models', methods=['GET'])
def get_llm_models():
    try:
        models = ["gpt-4o-mini-2024-07-18", "gpt-3.5-turbo", "gpt-4-turbo"]
        return jsonify({'models': models})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get-llm-suggestions', methods=['POST'])
def get_llm_suggestions():
    try:
        data = request.json
        brand_name = data.get('brandName')
        industry = data.get('industry', '')
        
        if not brand_name:
            return jsonify({'error': 'brandName is required'}), 400
        
        suggestions = geo_analysis.generate_llm_test_queries(brand_name, industry)
        return jsonify({'suggestions': suggestions})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/stream-brand-info', methods=['POST'])
def stream_brand_info():
    # Get request data outside the generator function
    data = request.json
    brand_name = data.get('brandName')
    brand_website = data.get('brandWebsite')
    brand_country = data.get('brandCountry', 'world')
    
    def generate():
        try:
            
            if not brand_name or not brand_website:
                yield f"data: {json.dumps({'error': 'brandName and brandWebsite are required'})}\n\n"
                return
            
            yield f"data: {json.dumps({'status': 'Starting brand analysis...', 'step': 'init'})}\n\n"
            time.sleep(0.1)
            
            yield f"data: {json.dumps({'status': 'Getting brand description...', 'step': 'description'})}\n\n"
            api_key = os.getenv("OPENAI_API_KEY")
            from openai import OpenAI
            client_openai = OpenAI(api_key=api_key)
            brand_description = utils.getBrandDescription(client_openai, brand_name, brand_website, brand_country)
            
            yield f"data: {json.dumps({'status': 'Analyzing industry...', 'step': 'industry'})}\n\n"
            brand_industry = utils.getBrandIndustry(client_openai, brand_name, brand_website, brand_description, brand_country)
            
            yield f"data: {json.dumps({'status': 'Finding competitors...', 'step': 'competitors'})}\n\n"
            brand_competitors = utils.getBrandCompetitors(client_openai, brand_name, brand_website, brand_description, brand_industry, brand_country)
            
            yield f"data: {json.dumps({'status': 'Extracting brand name...', 'step': 'name'})}\n\n"
            final_brand_name = utils.getBrandName(client_openai, brand_description)
            
            result = {
                "description": brand_description,
                "industry": brand_industry,
                "competitors": brand_competitors,
                "name": final_brand_name
            }
            
            yield f"data: {json.dumps({'status': 'Analysis complete!', 'step': 'complete', 'result': result})}\n\n"
            
        except Exception as e:
            error_msg = f"Brand analysis error: {str(e)}"
            print(f"ERROR in stream_brand_info: {error_msg}")
            print(f"Error type: {type(e).__name__}")
            import traceback
            traceback.print_exc()
            yield f"data: {json.dumps({'error': error_msg})}\n\n"
    
    return Response(generate(), mimetype='text/event-stream')

@app.route('/stream-generate-queries', methods=['POST'])
def stream_generate_queries():
    # Get request data outside the generator function
    data = request.json
    brand_name = data.get('brandName')
    brand_country = data.get('brandCountry', 'world')
    brand_description = data.get('brandDescription')
    brand_industry = data.get('brandIndustry')
    total_queries = data.get('totalQueries', 10)
    
    def generate():
        try:
            
            if not all([brand_name, brand_description, brand_industry]):
                yield f"data: {json.dumps({'error': 'brandName, brandDescription, and brandIndustry are required'})}\n\n"
                return
            
            yield f"data: {json.dumps({'status': 'Preparing query generation...', 'step': 'init'})}\n\n"
            time.sleep(0.1)
            
            yield f"data: {json.dumps({'status': f'Generating {total_queries} coherent queries...', 'step': 'generating'})}\n\n"
            queries = openaiAnalytics.getCoherentQueries(
                brand_name, brand_country, brand_description, brand_industry, total_queries
            )
            
            yield f"data: {json.dumps({'status': 'Query generation complete!', 'step': 'complete', 'result': {'queries': queries}})}\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return Response(generate(), mimetype='text/event-stream')

@app.route('/stream-test-queries', methods=['POST'])
def stream_test_queries():
    # Get request data outside the generator function
    data = request.json
    brand_name = data.get('brandName')
    queries = data.get('queries', [])
    competitors = data.get('competitors', [])
    llm_models = data.get('models', ['gpt-4o-mini-2024-07-18'])
    
    def generate():
        try:
            if not brand_name or not queries:
                yield f"data: {json.dumps({'error': 'brandName and queries are required'})}\n\n"
                return
            
            # Extract query strings from query objects if needed
            query_strings = []
            for q in queries:
                if isinstance(q, dict):
                    query_strings.append(q.get('query', str(q)))
                else:
                    query_strings.append(str(q))
            
            yield f"data: {json.dumps({'status': f'Starting GEO analysis for {len(query_strings)} queries across {len(llm_models)} LLM models...', 'step': 'init', 'progress': 0})}\n\n"
            
            # Use the regular (non-streaming) geo_analysis function for now
            analysis_results = geo_analysis.analyze_llm_brand_positioning(
                brand_name=brand_name,
                competitors=competitors,
                queries=query_strings,
                llm_models=llm_models
            )
            
            yield f"data: {json.dumps({'status': 'GEO analysis computation complete!', 'step': 'analysis_complete', 'progress': 85})}\n\n"
            
            # Generate optimization suggestions
            yield f"data: {json.dumps({'status': 'Generating optimization suggestions...', 'step': 'suggestions', 'progress': 95})}\n\n"
            suggestions = geo_analysis.get_geo_optimization_suggestions(analysis_results)
            analysis_results["optimization_suggestions"] = suggestions
            
            yield f"data: {json.dumps({'status': 'GEO Analysis complete!', 'step': 'complete', 'progress': 100, 'result': analysis_results})}\n\n"
            
        except Exception as e:
            print(f"Error in stream_test_queries: {e}")
            import traceback
            traceback.print_exc()
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return Response(generate(), mimetype='text/event-stream')

@app.route('/web-search', methods=['POST'])
def web_search():
    try:
        data = request.json
        query = data.get('query')
        context = data.get('context', '')
        
        if not query:
            return jsonify({'error': 'query is required'}), 400
        
        search_results = openaiAnalytics.webSearchAndAnalyze(query, context)
        return jsonify(search_results)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/stream-web-search', methods=['POST'])
def stream_web_search():
    # Get request data outside the generator function
    data = request.json
    query = data.get('query')
    context = data.get('context', '')
    
    def generate():
        try:
            if not query:
                yield f"data: {json.dumps({'error': 'query is required'})}\n\n"
                return
            
            yield f"data: {json.dumps({'status': 'Initializing web search...', 'step': 'init'})}\n\n"
            time.sleep(0.1)
            
            yield f"data: {json.dumps({'status': f'Searching for: {query}', 'step': 'searching'})}\n\n"
            
            # Perform the web search and analysis
            search_results = openaiAnalytics.webSearchAndAnalyze(query, context)
            
            if 'error' in search_results:
                yield f"data: {json.dumps({'error': search_results['error'], 'step': 'error'})}\n\n"
                return
            
            yield f"data: {json.dumps({'status': 'Processing search results...', 'step': 'processing'})}\n\n"
            time.sleep(0.2)
            
            yield f"data: {json.dumps({'status': 'Analyzing findings...', 'step': 'analyzing'})}\n\n"
            time.sleep(0.2)
            
            yield f"data: {json.dumps({'status': 'Web search complete!', 'step': 'complete', 'result': search_results})}\n\n"
            
        except Exception as e:
            error_msg = f"Web search error: {str(e)}"
            print(f"ERROR in stream_web_search: {error_msg}")
            import traceback
            traceback.print_exc()
            yield f"data: {json.dumps({'error': error_msg})}\n\n"
    
    return Response(generate(), mimetype='text/event-stream')

@app.route('/format-query-analysis', methods=['POST'])
def format_query_analysis():
    try:
        data = request.json
        raw_analysis = data.get('rawAnalysis')
        
        if not raw_analysis:
            return jsonify({'error': 'rawAnalysis is required'}), 400
        
        formatted_analysis = utils.formatQueryAnalysis(raw_analysis)
        return jsonify({'formatted_analysis': formatted_analysis})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)