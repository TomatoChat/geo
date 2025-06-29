# Evidentia - Generative Engine Optimization (GEO) Tool

🤖 A comprehensive GEO analysis platform that helps brands understand their positioning in LLM responses and optimize for generative AI engines.

## What is GEO?

**Generative Engine Optimization (GEO)** is the practice of optimizing content and brand positioning for Large Language Models (LLMs) and AI-powered responses, rather than traditional search engines. As users increasingly rely on AI assistants for recommendations and information, GEO becomes crucial for brand visibility.

## 🚀 Key Features

### Core Analysis Capabilities
- **🧠 Advanced LLM Brand Analysis**: Comprehensive analysis of how your brand appears across multiple AI models
- **📊 Multi-Model GEO Testing**: Test brand positioning across GPT-4, GPT-3.5, and other LLM models simultaneously
- **💭 Intelligent Query Generation**: AI-powered generation of test queries tailored to your industry and brand
- **🎯 Sentiment & Positioning Analysis**: Deep understanding of how AI portrays your brand (positive/neutral/negative)
- **🥊 Competitive Intelligence**: Advanced competitor analysis and positioning comparison
- **📈 Performance Metrics**: Comprehensive metrics including mention rates, positioning scores, and visibility analytics
- **🔍 Real-Time Web Search**: OpenAI Responses API integration with web search capabilities for current market intelligence

### Real-Time Experience
- **⚡ Real-time Streaming Analysis**: Watch analysis progress with live updates and detailed logs
- **📱 Interactive Web Interface**: Modern, responsive UI with progress tracking and detailed visualizations
- **🔄 Streaming Progress Updates**: Real-time status updates with color-coded progress indicators
- **📋 Detailed Analysis Reports**: Comprehensive reports with actionable insights

### Advanced Capabilities
- **🎯 Smart Optimization Suggestions**: AI-generated recommendations for improving GEO performance
- **🌍 Geographic Market Analysis**: Country-specific brand analysis and market positioning
- **🔍 Query Performance Insights**: Detailed analysis of individual query performance
- **📊 Brand Visibility Scoring**: Proprietary scoring system for brand visibility in AI responses
- **🤖 Multi-LLM Testing Framework**: Support for testing across different AI models and providers

## Prerequisites

- Python 3.11 or higher
- OpenAI API key

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd evidentia
   ```

2. **Create and activate virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your API keys:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   PROJECT_DIRECTORY=/path/to/your/evidentia/directory
   
   # Optional - for real Google search results (100 free searches/month)
   SERPAPI_KEY=your_serpapi_key_here
   ```

## 🎯 Usage

### 🌐 Interactive Web Interface

1. **Start the server**
   ```bash
   source venv/bin/activate
   python server.py
   ```

2. **Open your browser**
   Navigate to `http://127.0.0.1:5000`

3. **Complete GEO Analysis Workflow**

   **Step 1: Brand Discovery & Analysis**
   - Enter brand name (e.g., "jethr")
   - Enter brand website (e.g., "jethr.com")
   - Optionally specify country (defaults to "world")
   - Click "🚀 Analyze Brand" to get comprehensive company information
   - Watch real-time progress with streaming updates

   **Step 2: Intelligent Query Generation**
   - Adjust the number of test queries (1-100)
   - Click "📝 Generate Queries" to create AI-optimized test queries
   - Review generated queries tailored to your industry and brand positioning

   **Step 3: Advanced GEO Testing & Rankings**
   - Select LLM models to test (GPT-4, GPT-3.5, etc.)
   - Click "🌍 Test Queries & Rankings" to start comprehensive GEO analysis
   - Monitor real-time analysis progress with detailed streaming logs
   - Review comprehensive results including:
     - Brand mention rates across different AI models
     - Sentiment analysis and positioning insights
     - Competitor analysis and market positioning
     - Optimization suggestions for improved GEO performance

### 📊 Real-Time Analysis Features

- **Live Progress Tracking**: Watch each step of the analysis with color-coded progress indicators
- **Streaming Logs**: Detailed real-time logs showing LLM requests, responses, and analysis steps
- **Interactive Results**: Comprehensive results with expandable sections and detailed metrics
- **Multi-Model Comparison**: Side-by-side comparison of brand performance across different AI models

### 🔌 API Endpoints

#### 📊 Streaming Brand Analysis (Recommended)
```bash
POST /stream-brand-info
Content-Type: application/json

{
  "brandName": "jethr",
  "brandWebsite": "jethr.com",
  "brandCountry": "italy"
}
```
Returns real-time streaming updates with progress tracking.

#### 📝 Streaming Query Generation
```bash
POST /stream-generate-queries
Content-Type: application/json

{
  "brandName": "Company Name",
  "brandCountry": "italy",
  "brandDescription": "Company description...",
  "brandIndustry": "Technology",
  "totalQueries": 10
}
```
Returns streaming progress updates during query generation.

#### 🌍 Advanced GEO Analysis (Streaming)
```bash
POST /stream-test-queries
Content-Type: application/json

{
  "brandName": "Company Name",
  "queries": ["What are the best tech companies?", "Recommend software tools"],
  "competitors": ["Competitor1", "Competitor2"],
  "models": ["gpt-4o-mini-2024-07-18", "gpt-3.5-turbo"]
}
```
Returns comprehensive streaming GEO analysis with real-time progress updates.

#### 🤖 Available LLM Models
```bash
GET /get-llm-models
```
Returns list of available LLM models for testing.

#### 💡 LLM Suggestions
```bash
POST /get-llm-suggestions
Content-Type: application/json

{
  "brandName": "Company Name",
  "industry": "Technology"
}
```

#### 🔍 Web Search & Analysis
```bash
POST /web-search
Content-Type: application/json

{
  "query": "latest trends in AI automation tools",
  "context": "small business market analysis"
}
```
Returns structured web search results with analysis and insights.

#### ⚡ Streaming Web Search
```bash
POST /stream-web-search
Content-Type: application/json

{
  "query": "competitor analysis for tech companies",
  "context": "market positioning research"
}
```
Returns real-time streaming web search with progress updates.

#### Legacy Endpoints (Non-Streaming)
```bash
POST /brand-info          # Basic brand information
POST /generate-queries    # Generate test queries
POST /test-queries       # Basic GEO analysis
GET /health             # Health check
```

### 🔍 Web Search Integration

The platform now includes advanced web search capabilities powered by OpenAI's Responses API:

- **Real-time web search** with current market data
- **Structured analysis** of search results with insights and sources
- **Quality assessment** of search information (high/medium/low)
- **Source attribution** with URLs and relevant excerpts
- **Streaming progress** updates during search operations

### Jupyter Notebook

You can also use the functionality directly in Jupyter notebooks:

```python
import libs.utils as utils
import libs.openai as openaiAnalytics

# Get brand information
brand_info = utils.getCompanyInfo("jethr", "jethr.com", "italy")

# Generate queries
queries = openaiAnalytics.getCoherentQueries(
    brand_info['name'], 
    "italy", 
    brand_info['description'], 
    brand_info['industry'], 
    10
)

# Perform web search and analysis
search_results = openaiAnalytics.webSearchAndAnalyze(
    "latest AI automation trends 2024",
    "market research for technology companies"
)
```

## 📁 Project Structure

```
evidentia/
├── libs/                   # Core analysis libraries
│   ├── geo_analysis.py     # 🌍 GEO analysis engine with streaming support
│   ├── search_analysis.py  # 🔍 Search analysis and ranking functions
│   ├── openai.py          # 🤖 OpenAI Responses API integration with web search
│   └── utils.py           # 🛠️ Brand analysis and utility functions
├── prompts/               # 📝 AI prompt templates
│   ├── brandDescription.txt    # Prompt for brand description extraction
│   ├── brandIndustry.txt      # Prompt for industry classification
│   ├── brandCompetitors.txt   # Prompt for competitor identification
│   ├── brandName.txt          # Prompt for brand name extraction
│   ├── brandPromptsGeneration.txt  # Prompt for query generation
│   └── translateString.txt    # Prompt for translation services
├── templates/             # 🎨 Web interface templates
│   └── index.html         # Interactive web interface with streaming support
├── utils/                 # 📊 Configuration and mapping files
│   └── countryLanguage.json   # Country-language mappings for localization
├── notebooks/             # 📓 Analysis notebooks
│   └── openAI.ipynb       # Example Jupyter notebook with GEO analysis
├── server.py              # 🖥️ Flask web server with streaming endpoints
├── requirements.txt       # 📦 Python dependencies
├── CLAUDE.md             # 🤖 AI development guidelines
├── LICENSE               # ⚖️ License information
├── .env.example          # 🔧 Environment variables template
└── README.md             # 📚 This documentation
```

## Configuration

The application uses the following environment variables:

- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `PROJECT_DIRECTORY`: Absolute path to the project directory (required)

### Understanding GEO vs SEO

**Traditional SEO** focuses on optimizing for search engine rankings (Google, Bing, etc.)
**GEO (Generative Engine Optimization)** focuses on optimizing for AI assistant responses (ChatGPT, Claude, etc.)

This tool helps you understand and improve your **GEO performance** - how your brand appears when users ask AI assistants for recommendations, comparisons, or information.

## 📦 Dependencies

- `openai>=1.0.0` - OpenAI API client for LLM interactions
- `langchain>=0.1.0` - LangChain framework for prompt templates and AI workflows
- `python-dotenv>=1.0.0` - Environment variable management and configuration
- `flask>=2.0.0` - Web framework with streaming support
- `requests>=2.25.0` - HTTP client for external API integrations
- `beautifulsoup4>=4.9.0` - HTML parsing for web scraping capabilities
- `pocketflow` - Workflow management for complex analysis pipelines

## 🎯 What Makes Evidentia Unique

### Advanced GEO Capabilities
- **First-of-its-kind streaming GEO analysis** with real-time progress tracking
- **Multi-model testing framework** supporting various LLM providers
- **Intelligent query generation** tailored to specific industries and markets
- **Comprehensive brand positioning analysis** with sentiment scoring

### Real-Time User Experience
- **Live streaming updates** during analysis with detailed progress indicators
- **Interactive web interface** with modern UI/UX design
- **Color-coded logging system** for easy monitoring of analysis steps
- **Responsive design** that works across all devices

### Enterprise-Ready Features
- **Scalable architecture** supporting multiple concurrent analyses
- **Comprehensive API** with both streaming and traditional endpoints
- **Detailed reporting** with actionable insights and optimization suggestions
- **Geographic market analysis** with country-specific insights

## Development

To run in development mode:

```bash
source venv/bin/activate
export FLASK_DEBUG=1
python server.py
```

The server will automatically reload when you make changes to the code.

## 📊 API Response Examples

### Streaming Brand Analysis Response
```json
{
  "status": "Analysis complete!",
  "step": "complete",
  "result": {
    "name": "Jethr",
    "description": "A technology company specializing in AI-powered solutions...",
    "industry": "Technology",
    "competitors": {
      "direct_competitors": ["Competitor1", "Competitor2"],
      "indirect_competitors": ["Alternative1", "Alternative2"]
    }
  }
}
```

### GEO Analysis Response
```json
{
  "status": "GEO Analysis complete!",
  "step": "complete",
  "progress": 100,
  "result": {
    "brand_name": "YourBrand",
    "total_queries_tested": 10,
    "llm_models_tested": ["gpt-4o-mini-2024-07-18", "gpt-3.5-turbo"],
    "overall_metrics": {
      "mention_rate": 75.5,
      "positive_positioning": 85.2,
      "neutral_positioning": 12.3,
      "negative_positioning": 2.5,
      "average_mention_position": 1.8,
      "brand_visibility_score": 82.4
    },
    "model_performance": {
      "gpt-4o-mini-2024-07-18": {
        "mention_rate": 80.0,
        "average_position": 1.5,
        "sentiment_distribution": {
          "positive": 90.0,
          "neutral": 10.0,
          "negative": 0.0
        }
      }
    },
    "query_performance": [
      {
        "query": "What are the best tech companies?",
        "model": "gpt-4o-mini-2024-07-18",
        "brand_mentioned": true,
        "mention_position": 1,
        "sentiment": "positive",
        "context": "recommendation",
        "competitors_mentioned": [],
        "llm_response": "YourBrand is a leading technology company..."
      }
    ],
    "competitor_analysis": {
      "Competitor1": {
        "mentions": 3,
        "average_position": 2.5
      }
    },
    "optimization_suggestions": [
      "🔍 Low mention rate detected. Consider creating more content...",
      "😊 Improve positive sentiment by highlighting customer success stories..."
    ]
  }
}
```

### Available Models Response
```json
{
  "models": [
    "gpt-4o-mini-2024-07-18",
    "gpt-3.5-turbo",
    "gpt-4-turbo"
  ]
}
```

### Web Search Analysis Response
```json
{
  "summary": "Latest AI automation trends show increased adoption of conversational AI, workflow automation platforms, and no-code solutions for small businesses.",
  "key_insights": [
    "70% increase in small business AI tool adoption in 2024",
    "Conversational AI and chatbots leading market growth",
    "No-code automation platforms becoming dominant"
  ],
  "sources": [
    {
      "title": "AI Automation Trends 2024 Report",
      "url": "https://example.com/ai-trends-2024",
      "snippet": "Small businesses are rapidly adopting AI automation tools..."
    },
    {
      "title": "Market Research: Business Automation Growth",
      "url": "https://example.com/automation-market",
      "snippet": "The automation market is expected to reach $35B by 2025..."
    }
  ],
  "search_quality": "high",
  "last_updated": "recent",
  "web_search_annotations": {
    "msg_001": [
      {
        "type": "web_search",
        "search_query": "AI automation trends 2024 small business",
        "results_count": 15
      }
    ]
  }
}
```

### Formatted Query Analysis Report

Here's how to format detailed query analysis results for better readability:

```markdown
# 📊 Detailed Query Analysis Report

## Query Performance Summary
- **Total Queries Tested**: 2
- **LLM Model**: gpt-4o-mini-2024-07-18
- **Brand**: Jethr
- **Overall Performance**: ❌ No mentions detected

---

## 🔍 Individual Query Results

### Query #1: Workflow Automation Discovery
**Topic**: Discover workflow automation tools  
**Prompt**: "Find me a software tool that automates workflow processes for small businesses in Italy."

| Metric | Result |
|--------|--------|
| **Status** | ❌ Not Mentioned |
| **Sentiment** | 😐 Neutral |
| **Brand Context** | No mention of Jethr in the response |

**LLM Response Preview**:
> "Here are some software tools that can help automate workflow processes for small businesses in Italy: 1. **Zapier**: This tool allows you to connect..."

**Analysis**: The response focused on established automation platforms like Zapier, without mentioning Jethr. This indicates low brand awareness in the workflow automation space.

---

### Query #2: Implementation Strategy Guide
**Topic**: Step-by-step implementation plan  
**Prompt**: "Create a step-by-step guide for implementing a business automation strategy in a local Italian company."

| Metric | Result |
|--------|--------|
| **Status** | ❌ Not Mentioned |
| **Sentiment** | 😐 Neutral |
| **Brand Context** | No mention of the brand Jethr |

**LLM Response Preview**:
> "### Step-by-Step Implementation Plan for a Business Automation Strategy in a Local Italian Company Implementing a business automation strategy can st..."

**Analysis**: The response provided generic implementation guidance without referencing Jethr as a potential solution provider.

---

## 📈 Optimization Recommendations

1. **🎯 Increase Content Marketing**: Create more content around workflow automation for Italian SMBs
2. **🔍 SEO & GEO Strategy**: Optimize for queries about "Italian business automation" and "workflow tools Italy"
3. **📝 Case Studies**: Develop Italian customer success stories and implementation guides
4. **🤝 Partnerships**: Consider partnerships with Italian business organizations
5. **🌍 Local Presence**: Strengthen Italian market presence and localization
```

## Troubleshooting

1. **"No module named 'libs'"** - Make sure `PROJECT_DIRECTORY` is set correctly in `.env`
2. **OpenAI API errors** - Verify your API key is valid and has sufficient credits
3. **Permission errors** - Ensure the virtual environment is activated
4. **Port already in use** - The server runs on port 5000 by default

## License

[Add your license information here]