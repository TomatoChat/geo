import os
import json
from langchain.prompts import PromptTemplate
from openai import OpenAI
import logging


with open('utils/countryLanguage.json', 'r', encoding='utf-8') as file:
    countryLanguages = json.load(file)


def getResponseInfo(response) -> tuple[dict, dict]:
    """
    Extracts annotation and text information from an OpenAI responses.create API call.

    This function processes the response object returned by OpenAI"s responses.create endpoint.
    It filters for outputs of type "message", then extracts the "output_text" content, 
    collecting both the text and any associated annotations for each message.

    Args:
        response (OpenAI.responses.response.Response): 
            The response object returned by OpenAI's responses.create API call.

    Returns:
        tuple:
            - messagesAnnotations (dict): 
                A dictionary mapping each message ID to its list of annotations.
            - messagesTexts (dict): 
                A dictionary mapping each message ID to its output text.
    """
    response = response.to_dict()
    outputMessages = [output for output in response["output"] if output.get("type") == "message"]
    messageTextContents = {message["id"]: content for message in outputMessages for content in message.get("content", []) if content.get("type") == "output_text"}
    messagesAnnotations = {messageId: textContent["annotations"] for messageId, textContent in messageTextContents.items()}
    messagesTexts = {messageId: textContent["text"] for messageId, textContent in messageTextContents.items()}

    return messagesAnnotations, messagesTexts


def getCoherentQueries(brandName: str, brandCountry: str, brandDescription: str, brandIndustry: str, totalQueries: int = 100):
    """
    Generates a set of coherent queries related to a brand using an LLM (OpenAI) with web search capabilities.

    Args:
        brandName (str): The name of the brand/company.
        brandCountry (str): The country where the brand/company is based.
        brandDescription (str): A description of the brand/company.
        brandIndustry (str): The industry in which the brand/company operates.
        totalQueries (int, optional): The total number of queries to generate. Defaults to 100.

    Returns:
        list: A list of dictionaries containing the generated queries, parsed from the JSON response.
    """
    # Initialize the OpenAI client
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set")
    llmClient = OpenAI(api_key=api_key)

    try:
        # Load the prompt template for generating queries from file
        with open("prompts/brandPromptsGeneration.txt", "r", encoding="utf-8") as file:
            promptTemplate = file.read()

        # Format the prompt with the provided brand information and total queries
        prompt = PromptTemplate(
            input_variables=["companyName", "companyCountry", "companyDescription", "companyIndustry", "totalQueries"],
            template=promptTemplate
        ).format(
            companyName=brandName,
            companyCountry=brandCountry,
            companyDescription=brandDescription,
            companyIndustry=brandIndustry,
            totalQueries=totalQueries
        )

        # Call the OpenAI Responses API with web search enabled for better query generation
        response = llmClient.responses.create(
            model="gpt-4o-mini-2024-07-18",
            tools=[{"type": "web_search_preview"}],
            input=prompt,
        )
        
        # Extract response information
        messagesAnnotations, messagesTexts = getResponseInfo(response)
        rawJson = next(iter(messagesTexts.values()), "")

        # Clean up JSON formatting
        if rawJson.startswith("```json"):
            rawJson = rawJson[len("```json"):].strip()
        if rawJson.endswith("```"):
            rawJson = rawJson[:-3].strip()

        if not rawJson.strip():
            raise ValueError("No JSON output received from OpenAI API.")

        # Parse and return the JSON as a Python dictionary
        queries_result = json.loads(rawJson)
        
        # Log web search annotations if available for debugging
        if messagesAnnotations:
            logging.info(f"Web search annotations available for query generation: {len(messagesAnnotations)} messages")
        
        return queries_result
        
    except json.JSONDecodeError as e:
        logging.error(f"Failed to parse JSON from query generation response: {e}")
        raise ValueError(f"Invalid JSON response from OpenAI API: {e}")
    except FileNotFoundError:
        logging.error("Brand prompt template file not found")
        raise ValueError("Brand prompt template file 'prompts/brandPromptsGeneration.txt' not found")
    except Exception as e:
        logging.error(f"Query generation failed: {e}")
        raise ValueError(f"Failed to generate queries: {e}")


def webSearchAndAnalyze(query: str, context: str = "") -> dict:
    """
    Performs web search using OpenAI's Responses API and analyzes the results.
    
    Args:
        query (str): The search query to execute
        context (str, optional): Additional context for the analysis
    
    Returns:
        dict: Contains search results, analysis, and web search annotations
    """
    # Initialize the OpenAI client
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set")
    llmClient = OpenAI(api_key=api_key)
    
    # Construct the prompt for web search and analysis
    prompt = f"""
    Please search the web for information about: {query}
    
    {f"Additional context: {context}" if context else ""}
    
    After searching, please provide:
    1. A summary of the key findings
    2. The most relevant sources and URLs
    3. Any important insights or trends identified
    
    Format your response as JSON with the following structure:
    {{
        "summary": "Brief summary of findings",
        "key_insights": ["insight 1", "insight 2", "insight 3"],
        "sources": [
            {{"title": "Source title", "url": "https://example.com", "snippet": "relevant excerpt"}},
            {{"title": "Source title 2", "url": "https://example2.com", "snippet": "relevant excerpt"}}
        ],
        "search_quality": "high/medium/low",
        "last_updated": "recent/moderate/outdated"
    }}
    """
    
    try:
        # Call the OpenAI Responses API with web search enabled
        response = llmClient.responses.create(
            model="gpt-4o-mini-2024-07-18",
            tools=[{"type": "web_search_preview"}],
            input=prompt,
        )
        
        # Extract response information including web search annotations
        messagesAnnotations, messagesTexts = getResponseInfo(response)
        
        # Get the main response text
        rawJson = next(iter(messagesTexts.values()), "")
        
        # Clean up JSON formatting
        if rawJson.startswith("```json"):
            rawJson = rawJson[len("```json"):].strip()
        if rawJson.endswith("```"):
            rawJson = rawJson[:-3].strip()
            
        if not rawJson.strip():
            raise ValueError("No JSON output received from web search.")
        
        # Parse the JSON response
        analysis_result = json.loads(rawJson)
        
        # Add web search annotations to the result
        analysis_result["web_search_annotations"] = messagesAnnotations
        analysis_result["raw_response"] = messagesTexts
        
        return analysis_result
        
    except json.JSONDecodeError as e:
        logging.error(f"Failed to parse JSON from web search response: {e}")
        return {
            "error": "Failed to parse search results",
            "raw_response": rawJson,
            "summary": "Search completed but response format was invalid",
            "key_insights": [],
            "sources": [],
            "search_quality": "low",
            "last_updated": "unknown"
        }
    except Exception as e:
        logging.error(f"Web search failed: {e}")
        return {
            "error": str(e),
            "summary": "Web search failed to complete",
            "key_insights": [],
            "sources": [],
            "search_quality": "failed",
            "last_updated": "unknown"
        }