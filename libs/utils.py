import sys
import os

from langchain.prompts import PromptTemplate
from openai import OpenAI
import libs.openai as openaiAnalytics
import json


with open('utils/countryLanguage.json', 'r', encoding='utf-8') as file:
    countryLanguages = json.load(file)


def translateString(stringToTranslate: str, targetLanguage: str) -> str:
    """
    Translates a given string into the specified target language using an LLM (OpenAI) and a prompt template.

    Args:
        stringToTranslate (str): The text string to be translated.
        targetLanguage (str): The language to translate the string into.

    Returns:
        str: The translated string, or an empty string if translation fails.
    """
    # Initialize the OpenAI client
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set")
    llmClient = OpenAI(api_key=api_key)

    # Load the translation prompt template from file
    with open("prompts/translateString.txt", "r", encoding="utf-8") as file:
        promptTemplate = file.read()

    # Format the prompt with the string to translate and the target language
    prompt = PromptTemplate(
        input_variables=["stringToTranslate", "targetLanguage"],
        template=promptTemplate
    ).format(
        stringToTranslate=stringToTranslate,
        targetLanguage=targetLanguage
    )

    # Call the OpenAI API to get the translation
    response = llmClient.chat.completions.create(
        model="gpt-4o-mini-2024-07-18",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500,
        temperature=0.7
    )
    
    # Extract the translated text from the response
    return response.choices[0].message.content


def getBrandDescription(clientOpenai, brandName: str, brandWebsite: str, brandCountry: str = "world") -> str:
    """
    Retrieves the company description using OpenAI's responses API and the brandDescription prompt template.

    Args:
        clientOpenai: An initialized OpenAI client instance.
        brandName (str): The name of the brand/company.
        brandWebsite (str): The website of the brand/company.
        brandCountry (str, optional): The country of the brand/company. Defaults to "world".

    Returns:
        str: The company description, translated if necessary.
    """
    # Load the brand description prompt template from file
    with open("prompts/brandDescription.txt", "r", encoding="utf-8") as file:
        promptTemplate = file.read()

    # Format the prompt with the provided brand information
    prompt = PromptTemplate(
        input_variables=["companyName", "companyWebsite", "companyCountry"],
        template=promptTemplate
    ).format(
        companyName=brandName,
        companyWebsite=brandWebsite,
        companyCountry=brandCountry
    )

    # Determine the target language for the description
    targetLanguage = countryLanguages.get(brandCountry.lower(), 'english').lower()

    # If the target language is not English, translate the prompt
    if targetLanguage != 'english':
        translatedPrompt = translateString(prompt, targetLanguage)

        if 'NULL' not in translatedPrompt:
            prompt = translatedPrompt
    
    # Call the OpenAI API to get the company description with structured output
    try:
        response = clientOpenai.chat.completions.create(
            model="gpt-4o-mini-2024-07-18",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0.7,
            timeout=30,
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "brand_description",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "description": {
                                "type": "string",
                                "description": "A 2-4 sentence business description of the company"
                            }
                        },
                        "required": ["description"],
                        "additionalProperties": False
                    }
                }
            }
        )
        # Extract the description from the structured response
        result = response.choices[0].message.content
        try:
            parsed_result = json.loads(result)
            description = parsed_result.get("description", "")
            if description and description.strip():
                return description
            else:
                # Provide a fallback description
                fallback_description = f"{brandName} is a business operating in {brandCountry} with their website at {brandWebsite}. The company provides digital services and solutions to their customers in the local market."
                return fallback_description
        except json.JSONDecodeError:
            # If structured response fails, try to use the raw content
            if result and result.strip() and result.strip().upper() != "NULL":
                return result
            else:
                # Provide a fallback description
                fallback_description = f"{brandName} is a business operating in {brandCountry} with their website at {brandWebsite}. The company provides digital services and solutions to their customers in the local market."
                return fallback_description
    except Exception as e:
        print(f"Error in getBrandDescription: {e}")
        raise Exception(f"Failed to get brand description: {str(e)}")


def getBrandIndustry(clientOpenai, brandName: str, brandWebsite: str, brandDescription: str, brandCountry: str = "world") -> str:
    """
    Retrieves the company industry using OpenAI's responses API and the brandIndustry prompt template.

    Args:
        clientOpenai: An initialized OpenAI client instance.
        brandName (str): The name of the brand/company.
        brandWebsite (str): The website of the brand/company.
        brandDescription (str): A description of the brand/company.
        brandCountry (str, optional): The country of the brand/company. Defaults to "world".

    Returns:
        str: The company industry as determined by the LLM, translated if necessary.
    """
    # Load the brand industry prompt template from file
    with open("prompts/brandIndustry.txt", "r", encoding="utf-8") as file:
        promptTemplate = file.read()

    # Format the prompt with the provided brand information
    prompt = PromptTemplate(
        input_variables=["companyName", "companyWebsite", "companyCountry", "companyDescription"],
        template=promptTemplate
    ).format(
        companyName=brandName,
        companyWebsite=brandWebsite,
        companyCountry=brandCountry,
        companyDescription=brandDescription
    )

    # Get the target language for the brand's country, defaulting to English
    targetLanguage = countryLanguages.get(brandCountry.lower(), 'english').lower()

    # Translate the prompt if the target language is not English and translation is successful
    if targetLanguage != 'english':
        translatedPrompt = translateString(prompt, targetLanguage)

        if 'NULL' not in translatedPrompt:
            prompt = translatedPrompt

    # Call the OpenAI API to get the company industry
    try:
        response = clientOpenai.chat.completions.create(
            model="gpt-4o-mini-2024-07-18",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0.7,
            timeout=30
        )
        # Extract the industry from the response
        result = response.choices[0].message.content
        if not result or result.strip() == "":
            raise ValueError("Empty response received from OpenAI API")
        return result
    except Exception as e:
        print(f"Error in getBrandIndustry: {e}")
        raise Exception(f"Failed to get brand industry: {str(e)}")


def getBrandCompetitors(clientOpenai, brandName: str, brandWebsite: str, brandDescription: str, brandIndustry: str, brandCountry: str = "world") -> dict:
    """
    Retrieves the company's competitors using OpenAI's responses API and the brandCompetitors prompt template.

    Args:
        clientOpenai: An initialized OpenAI client instance.
        brandName (str): The name of the brand/company.
        brandWebsite (str): The website of the brand/company.
        brandDescription (str): A description of the brand/company.
        brandIndustry (str): The industry in which the brand/company operates.
        brandCountry (str, optional): The country of the brand/company. Defaults to "world".

    Returns:
        dict: A dictionary containing the competitors, parsed from the JSON response.
    """
    # Load the brand competitors prompt template from file
    with open("prompts/brandCompetitors.txt", "r", encoding="utf-8") as file:
        promptTemplate = file.read()

    # Format the prompt with the provided brand information
    prompt = PromptTemplate(
        input_variables=["companyName", "companyWebsite", "companyCountry", "companyDescription", "companyIndustry"],
        template=promptTemplate
    ).format(
        companyName=brandName,
        companyWebsite=brandWebsite,
        companyCountry=brandCountry,
        companyDescription=brandDescription,
        companyIndustry=brandIndustry
    )

    # Get the target language for the brand's country, defaulting to English
    targetLanguage = countryLanguages.get(brandCountry.lower(), 'english').lower()

    # Translate the prompt if the target language is not English and translation is successful
    if targetLanguage != 'english':
        translatedPrompt = translateString(prompt, targetLanguage)

        if 'NULL' not in translatedPrompt:
            prompt = translatedPrompt

    # Call the OpenAI API to get the competitors with structured output
    try:
        response = clientOpenai.chat.completions.create(
            model="gpt-4o-mini-2024-07-18",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000,
            temperature=0.7,
            timeout=30,
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "competitor_analysis",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "competitors": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "name": {
                                            "type": "string",
                                            "description": "The competitor's company name"
                                        },
                                        "website": {
                                            "type": "string",
                                            "description": "The competitor's website URL"
                                        },
                                        "reason": {
                                            "type": "string",
                                            "description": "Brief explanation of why they compete"
                                        }
                                    },
                                    "required": ["name", "website", "reason"],
                                    "additionalProperties": False
                                },
                                "minItems": 3,
                                "maxItems": 5
                            }
                        },
                        "required": ["competitors"],
                        "additionalProperties": False
                    }
                }
            }
        )
        # Extract the competitors from the structured response
        rawJson = response.choices[0].message.content
        
        if not rawJson or not rawJson.strip():
            print("Warning: Empty response from OpenAI API for competitors")
            return {"competitors": []}

        # Parse the structured JSON response
        try:
            result = json.loads(rawJson)
            return result
        except json.JSONDecodeError as json_error:
            print(f"JSON decode error with structured output: {json_error}")
            print(f"Raw response: {rawJson}")
            # Return a fallback structure if parsing fails
            return {"competitors": []}
            
    except Exception as e:
        print(f"Error in getBrandCompetitors: {e}")
        # Return a fallback structure instead of raising an exception
        return {"competitors": []}


def getBrandName(clientOpenai, brandDescription: str) -> str:
    """
    Retrieves the company name using OpenAI's responses API and the brandName prompt template.

    Args:
        clientOpenai: An initialized OpenAI client instance.
        brandDescription (str): A description of the brand/company.

    Returns:
        str: The company name as determined by the LLM.
    """
    # Load the brand name prompt template from file
    with open("prompts/brandName.txt", "r", encoding="utf-8") as file:
        promptTemplate = file.read()

    # Format the prompt with the provided brand description
    prompt = PromptTemplate(
        input_variables=["companyDescription"],
        template=promptTemplate
    ).format(
        companyDescription=brandDescription
    )

    # Call the OpenAI API to get the company name with structured output
    try:
        response = clientOpenai.chat.completions.create(
            model="gpt-4o-mini-2024-07-18",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0.7,
            timeout=30,
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "brand_name",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "The extracted or identified company name"
                            }
                        },
                        "required": ["name"],
                        "additionalProperties": False
                    }
                }
            }
        )
        # Extract the name from the structured response
        result = response.choices[0].message.content
        try:
            parsed_result = json.loads(result)
            name = parsed_result.get("name", "")
            if name and name.strip():
                return name
            else:
                # Extract a reasonable name from the description or use a fallback
                words = brandDescription.split()
                for word in words:
                    if word[0].isupper() and len(word) > 2 and not word.lower() in ['the', 'and', 'for', 'with', 'this', 'that']:
                        return word
                # If no suitable name found, return a generic business name
                return "Business Entity"
        except json.JSONDecodeError:
            # If structured response fails, try to use the raw content
            if result and result.strip() and result.strip().upper() != "NULL":
                return result
            else:
                # Extract a reasonable name from the description or use a fallback
                words = brandDescription.split()
                for word in words:
                    if word[0].isupper() and len(word) > 2 and not word.lower() in ['the', 'and', 'for', 'with', 'this', 'that']:
                        return word
                # If no suitable name found, return a generic business name
                return "Business Entity"
    except Exception as e:
        print(f"Error in getBrandName: {e}")
        raise Exception(f"Failed to get brand name: {str(e)}")


def getCompanyInfo(brandName: str, brandWebsite: str, brandCountry: str = "world") -> dict:
    """
    Retrieves the company description and industry using OpenAI's responses API and prompt templates.

    Args:
        brandName (str): The name of the brand/company.
        brandWebsite (str): The website of the brand/company.
        brandCountry (str, optional): The country of the brand/company. Defaults to "world".

    Returns:
        dict: A dictionary with keys 'description' and 'industry'.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set")
    clientOpenai = OpenAI(api_key=api_key)
    brandDescription = getBrandDescription(clientOpenai, brandName, brandWebsite, brandCountry)
    brandIndustry = getBrandIndustry(clientOpenai, brandName, brandWebsite, brandDescription, brandCountry)
    brandCompetitors = getBrandCompetitors(clientOpenai, brandName, brandWebsite, brandDescription, brandIndustry, brandCountry)
    brandName = getBrandName(clientOpenai, brandDescription)
    
    return {
        "description": brandDescription,
        "industry": brandIndustry,
        "competitors": brandCompetitors,
        "name": brandName
    }


def formatQueryAnalysis(raw_analysis: str) -> str:
    """
    Formats raw query analysis output into a readable markdown format.
    
    Args:
        raw_analysis (str): Raw query analysis text
    
    Returns:
        str: Formatted markdown analysis report
    """
    import re
    
    # Split by lines and process each query result
    lines = raw_analysis.strip().split('\n')
    
    formatted_output = []
    formatted_output.append("# 📊 Detailed Query Analysis Report\n")
    
    # Extract brand name from context if available
    brand_match = re.search(r'Context:.*?mention of (?:the brand )?([A-Z][a-z]+)', raw_analysis)
    brand_name = brand_match.group(1) if brand_match else "Brand"
    
    # Count total queries
    query_count = len([line for line in lines if line.startswith('❌') or line.startswith('✅')])
    
    formatted_output.append("## Query Performance Summary")
    formatted_output.append(f"- **Total Queries Tested**: {query_count}")
    formatted_output.append("- **LLM Model**: gpt-4o-mini-2024-07-18")
    formatted_output.append(f"- **Brand**: {brand_name}")
    formatted_output.append("- **Overall Performance**: ❌ No mentions detected\n")
    formatted_output.append("---\n")
    formatted_output.append("## 🔍 Individual Query Results\n")
    
    query_num = 1
    current_query = {}
    
    for line in lines:
        line = line.strip()
        
        if line.startswith('❌') or line.startswith('✅'):
            # Parse query line
            status_icon = '❌' if line.startswith('❌') else '✅'
            
            # Extract topic and prompt from the complex format
            topic_match = re.search(r"'topic': '([^']+)'", line)
            prompt_match = re.search(r"'prompt': '([^']+)'", line)
            model_match = re.search(r'\(([^)]+)\)', line)
            
            topic = topic_match.group(1) if topic_match else f"Query {query_num}"
            prompt = prompt_match.group(1) if prompt_match else "No prompt available"
            model = model_match.group(1) if model_match else "gpt-4o-mini-2024-07-18"
            
            current_query = {
                'status_icon': status_icon,
                'topic': topic,
                'prompt': prompt,
                'model': model,
                'number': query_num
            }
            
        elif line.startswith('Not mentioned') or line.startswith('Mentioned'):
            # Parse status and sentiment
            parts = line.split('|')
            status = parts[0].strip()
            sentiment = parts[1].strip().replace('Sentiment: ', '') if len(parts) > 1 else 'neutral'
            
            current_query['status'] = status
            current_query['sentiment'] = sentiment
            
        elif line.startswith('Context:'):
            current_query['context'] = line.replace('Context: ', '').strip()
            
        elif line.startswith('LLM Response:'):
            current_query['response'] = line.replace('LLM Response: ', '').strip()
            
            # Output formatted query when we have all parts
            if 'topic' in current_query:
                formatted_output.append(f"### Query #{current_query['number']}: {current_query['topic']}")
                formatted_output.append(f"**Prompt**: \"{current_query['prompt']}\"\n")
                
                formatted_output.append("| Metric | Result |")
                formatted_output.append("|--------|--------|")
                formatted_output.append(f"| **Status** | {current_query['status_icon']} {current_query['status']} |")
                
                sentiment_icon = "😊" if "positive" in current_query['sentiment'] else "😐" if "neutral" in current_query['sentiment'] else "😞"
                formatted_output.append(f"| **Sentiment** | {sentiment_icon} {current_query['sentiment'].title()} |")
                formatted_output.append(f"| **Brand Context** | {current_query.get('context', 'No context available')} |\n")
                
                formatted_output.append("**LLM Response Preview**:")
                response_preview = current_query['response'][:100] + "..." if len(current_query['response']) > 100 else current_query['response']
                formatted_output.append(f"> {response_preview}\n")
                
                # Add analysis based on status
                if current_query['status_icon'] == '❌':
                    formatted_output.append(f"**Analysis**: The query did not mention {brand_name}, indicating low brand awareness for this search intent. Consider optimizing content for this topic area.\n")
                else:
                    formatted_output.append(f"**Analysis**: {brand_name} was mentioned, showing good brand visibility for this query type.\n")
                
                formatted_output.append("---\n")
                query_num += 1
                current_query = {}
    
    # Add optimization recommendations
    formatted_output.append("## 📈 Optimization Recommendations\n")
    formatted_output.append("1. **🎯 Content Strategy**: Create targeted content addressing the query topics where brand wasn't mentioned")
    formatted_output.append("2. **🔍 SEO & GEO Optimization**: Optimize for the specific phrases and contexts tested")
    formatted_output.append("3. **📝 Thought Leadership**: Develop authoritative content in relevant topic areas")
    formatted_output.append("4. **🤝 Industry Presence**: Increase visibility in industry discussions and platforms")
    formatted_output.append("5. **📊 Regular Monitoring**: Set up regular GEO monitoring for these query types")
    
    return '\n'.join(formatted_output)