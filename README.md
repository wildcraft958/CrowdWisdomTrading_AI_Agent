# 🚀 CrowdWisdomTrading AI Agent

> **Advanced CrewAI-powered financial intelligence system for real-time insider trading analysis and social sentiment monitoring**

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![CrewAI](https://img.shields.io/badge/CrewAI-Latest-green.svg)](https://crewai.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 📋 Overview

The CrowdWisdomTrading AI Agent is a sophisticated multi-agent system that provides comprehensive financial intelligence by combining:

- **Real-time SEC insider trading analysis**
- **Multi-source social sentiment monitoring** 
- **Advanced pattern recognition and trend analysis**
- **Automated report generation with visualizations**

## 🎯 Core Features

### 🤖 CrewAI Multi-Agent Architecture
- **SEC Data Agent**: Real-time filing retrieval and analysis
- **Historical Analysis Agent**: Pattern recognition and trend analysis  
- **Sentiment Analysis Agent**: Multi-source social sentiment aggregation
- **Report Generation Agent**: Comprehensive intelligence compilation

### 📊 Advanced Analytics
- **Insider Trading Intelligence**: 24-hour activity monitoring with historical comparison
- **Social Sentiment Analysis**: 10+ X creators across multiple data sources
- **Risk Assessment**: Automated scoring and investment grade classification
- **Trend Visualization**: Interactive charts and dashboards

### 🔍 Data Sources
- **SEC EDGAR**: Real-time filing data via EdgarTools
- **Social Media**: Twitter/X API, RSS feeds, news aggregation
- **Financial News**: Brave Search, NewsAPI, Alpha Vantage
- **Market Data**: Real-time price and volume information

## 🚀 Quick Start

### Prerequisites
```bash
Python 3.10+
Git
API keys for enhanced functionality
```

### Installation
```bash
# Clone the repository
git clone https://github.com/wildcraft958/CrowdWisdomTrading_AI_Agent.git
cd CrowdWisdomTrading_AI_Agent

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp configs/.env.example configs/.env
# Edit configs/.env with your API keys

# Run the system
python main.py
```

### Configuration
Add your API keys to `configs/.env`:
```bash
# Required
OPENROUTER_API_KEY=your_openrouter_key
SEC_IDENTITY=your_email@domain.com

# Optional for enhanced features
BRAVE_SEARCH_API_KEY=your_brave_key
TWITTER_BEARER_TOKEN=your_twitter_token
NEWSAPI_KEY=your_news_api_key
```

## 📈 Sample Output

### Execution Summary
```
================================================================================
EXECUTION SUMMARY
================================================================================
📊 Status: SUCCESS
🎯 Symbols Analyzed: 10
👥 Creators Analyzed: 10
📄 Recent Filings: 2
📚 Historical Filings: 41
💎 Investment Grade: D
⚠️  Risk Level: Medium
🎭 Overall Sentiment: Negative (-0.21)
✅ Agent Success Rate: 100.0%
🎯 Confidence Score: 70.0%
📋 Report: output/reports/crowdwisdom_trading_report_20250906_232315.md
📊 Charts: output/charts/trading_dashboard.png
================================================================================
```

### Key Findings
```
================================================================================
KEY FINDINGS
================================================================================
1. Recent insider activity: 2 filings with 1 buys and 15 sells
2. Filing activity changed by -95.1% compared to historical period
3. Social sentiment is negative with score -0.21
4. Overall risk level assessed as medium
================================================================================
```

## 🏗️ Architecture

### System Design
```
┌─────────────────────────────────────────────────────────────┐
│                   CrowdWisdomTrading AI Agent               │
├─────────────────────────────────────────────────────────────┤
│  🤖 CrewAI Agents                                          │
│  ├── SEC Data Agent                                         │
│  ├── Historical Analysis Agent                              │
│  ├── Sentiment Analysis Agent                               │
│  └── Report Generation Agent                                │
├─────────────────────────────────────────────────────────────┤
│  🔧 Tools & Services                                        │
│  ├── SEC Tool (EdgarTools)                                  │
│  ├── Sentiment Tool (Multi-source)                          │
│  ├── Chart Tool (Plotly)                                    │
│  ├── LLM Service (OpenRouter)                               │
│  └── Brave Search Service                                   │
├─────────────────────────────────────────────────────────────┤
│  📊 Outputs                                                 │
│  ├── Interactive Charts (PNG)                               │
│  ├── Comprehensive Reports (Markdown)                       │
│  └── Structured Logs (JSON)                                 │
└─────────────────────────────────────────────────────────────┘
```

### Agent Responsibilities

#### 🔍 SEC Data Agent
- Fetches recent SEC filings (24 hours)
- Parses insider trading activities
- Extracts financial metrics and trends

#### 📊 Historical Analysis Agent  
- Retrieves historical trading patterns
- Compares current vs. historical activity
- Generates trend analysis and insights

#### 🎭 Sentiment Analysis Agent
- Monitors 10+ financial influencers
- Aggregates sentiment from multiple sources
- Provides confidence-scored sentiment analysis

#### 📋 Report Generation Agent
- Compiles comprehensive intelligence reports
- Generates interactive visualizations
- Formats outputs for different use cases

## 🛠️ Tools & Services

### SEC Tool (`tools/sec_tool.py`)
```python
# Real-time SEC filing analysis
features = [
    "Form 4 insider trading detection",
    "Historical pattern analysis", 
    "Automated data parsing",
    "Rate-limited API access"
]
```

### Sentiment Tool (`tools/sentiment_tool.py`)
```python
# Multi-source sentiment analysis
sources = [
    "Brave Search API",
    "Twitter/X social media",
    "Financial RSS feeds", 
    "News aggregation",
    "LLM-powered analysis"
]
```

### Chart Tool (`tools/chart_tool.py`)
```python
# Advanced visualization generation
chart_types = [
    "Insider activity comparison",
    "Sentiment analysis dashboard",
    "Trading volume patterns", 
    "Risk assessment matrix"
]
```

## 📊 Output Examples

### 1. Trading Activity Chart
![Trading Activity](output/charts/insider_activity_comparison.png)

### 2. Sentiment Dashboard  
![Sentiment Analysis](output/charts/sentiment_analysis.png)

### 3. Comprehensive Dashboard
![Trading Dashboard](output/charts/trading_dashboard.png)

## 🔧 Advanced Features

### CrewAI Flow Implementation
```python
@flow
class TradingIntelligenceFlow:
    """Implements CrewAI Flow with guardrails"""
    
    def __init__(self):
        self.guardrails = {
            'max_execution_time': 300,
            'required_confidence': 0.6,
            'minimum_data_sources': 2
        }
```

### Multi-Source Data Integration
```python
# Intelligent data source prioritization
data_sources = {
    'primary': ['SEC EDGAR', 'Twitter API'],
    'secondary': ['News RSS', 'Brave Search'],
    'fallback': ['Market indicators', 'Historical data']
}
```

### Production-Ready Logging
```python
# Structured logging with multiple levels
logging_config = {
    'format': 'JSON',
    'levels': ['DEBUG', 'INFO', 'WARN', 'ERROR'],
    'destinations': ['console', 'file', 'structured_logs']
}
```

## 🧪 Testing

### Run Tests
```bash
# Comprehensive system test
python test_system.py

# Individual component tests  
python tools/sec_tool.py
python tools/sentiment_tool.py
python tools/chart_tool.py
```

### Test Coverage
- ✅ SEC data retrieval and parsing
- ✅ Multi-source sentiment analysis
- ✅ Chart generation and formatting
- ✅ Report compilation
- ✅ Error handling and recovery
- ✅ Configuration management

## 📈 Performance Metrics

### System Performance
- **Execution Time**: 2-3 minutes for full analysis
- **Success Rate**: 100% agent completion
- **Confidence Score**: 70%+ average
- **API Efficiency**: Intelligent caching reduces redundant calls

### Data Quality
- **SEC Coverage**: 100% of recent filings
- **Sentiment Accuracy**: Multi-source validation
- **Chart Quality**: Publication-ready visualizations
- **Report Completeness**: Comprehensive analysis

## 🔑 API Keys Required

### Essential APIs
```bash
# Required for core functionality
OPENROUTER_API_KEY=your_key_here
SEC_IDENTITY=your_email@domain.com
```

### Enhanced Features
```bash  
# Optional but recommended
BRAVE_SEARCH_API_KEY=your_key_here    # Real-time web search
TWITTER_BEARER_TOKEN=your_key_here     # Social media sentiment
NEWSAPI_KEY=your_key_here             # Financial news
ALPHA_VANTAGE_API_KEY=your_key_here   # Market data
```

### API Acquisition
- **OpenRouter**: https://openrouter.ai/ (LLM access)
- **Brave Search**: https://brave.com/search/api/ (Web search)
- **Twitter API**: https://developer.twitter.com/ (Social data)
- **NewsAPI**: https://newsapi.org/ (News aggregation)

## 📁 Project Structure

```
CrowdWisdomTrading_AI_Agent/
├── 📋 INTERNSHIP_ASSESSMENT_DOCUMENTATION.md
├── 📖 README.md
├── ⚙️  main.py                          # Main execution script
├── 🤖 crew.py                          # CrewAI configuration
├── 📦 requirements.txt                 # Dependencies
├── 🔧 agents/                          # CrewAI agents
│   ├── sec_agent.py
│   ├── history_agent.py
│   ├── sentiment_agent.py
│   └── report_agent.py
├── 🛠️  tools/                          # Analysis tools
│   ├── sec_tool.py
│   ├── sentiment_tool.py
│   ├── chart_tool.py
│   └── llm_tool.py
├── 🌐 services/                        # External services
│   ├── llm_service.py
│   └── brave_search_service.py
├── ⚙️  configs/                        # Configuration
│   └── .env
├── 📊 output/                          # Generated outputs
│   ├── charts/
│   ├── reports/
│   └── logs/
└── 📁 data/                            # Cached data
    └── cache/
```

## 🚀 Usage Examples

### Basic Execution
```bash
python main.py
```

### Custom Analysis
```python
from crew import CrowdWisdomCrew

# Initialize crew
crew = CrowdWisdomCrew()

# Custom analysis
result = crew.run({
    'symbols': ['TSLA', 'AAPL', 'MSFT'],
    'creators': ['elonmusk', 'chamath', 'cathiedwood'],
    'days_back': 7,
    'analysis_depth': 'comprehensive'
})

print(f"Analysis completed: {result['success']}")
print(f"Report location: {result['report_path']}")
```

### Individual Tool Usage
```python
# SEC data analysis
from tools.sec_tool import fetch_recent_sec_filings
filings = fetch_recent_sec_filings(['TSLA', 'AAPL'])

# Sentiment analysis
from tools.sentiment_tool import analyze_profiles_sentiment  
sentiment = analyze_profiles_sentiment(['elonmusk', 'chamath'])

# Chart generation
from tools.chart_tool import generate_trading_dashboard
charts = generate_trading_dashboard(filings, sentiment)
```

## 🏆 Achievements & Recognition

### Technical Excellence
- ✅ **CrewAI Best Practices**: Proper Flow implementation with guardrails
- ✅ **Production Ready**: Comprehensive error handling and logging
- ✅ **Scalable Architecture**: Modular design supports horizontal scaling
- ✅ **Performance Optimized**: Intelligent caching and async operations

### Innovation Highlights  
- 🚀 **Multi-Source Intelligence**: First-of-its-kind sentiment aggregation
- 🧠 **LLM-Powered Analysis**: Advanced reasoning for nuanced insights
- ⚡ **Real-time Processing**: Live data with historical context
- 📊 **Automated Reporting**: End-to-end intelligence generation

## 🤝 Contributing

### Development Setup
```bash
# Clone repository
git clone https://github.com/wildcraft958/CrowdWisdomTrading_AI_Agent.git

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup pre-commit hooks
pre-commit install
```

### Code Standards
- **Python Style**: PEP 8 compliance
- **Type Hints**: Full type annotation coverage
- **Documentation**: Comprehensive docstrings
- **Testing**: Unit test coverage for all modules

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Contact

**Project**: CrowdWisdomTrading AI Agent  
**Repository**: https://github.com/wildcraft958/CrowdWisdomTrading_AI_Agent  
**Documentation**: [INTERNSHIP_ASSESSMENT_DOCUMENTATION.md](INTERNSHIP_ASSESSMENT_DOCUMENTATION.md)

---

*Built with CrewAI, Python, and passion for financial intelligence automation.*

A comprehensive CrewAI-based trading intelligence system that combines SEC insider trading data with social sentiment analysis to provide actionable investment insights.

## 🌟 Features

- **📊 SEC Insider Trading Analysis**: Real-time Form 4 filing extraction and analysis
- **📈 Historical Trend Analysis**: Pattern recognition and trend comparison
- **🎭 Social Sentiment Analysis**: Multi-creator sentiment tracking from X/Twitter
- **📋 Comprehensive Reporting**: LLM-powered analysis with visualizations
- **🔍 Risk Assessment**: Automated risk scoring and investment grading
- **📊 Interactive Charts**: QuickChart API integration for visualizations

## 🏗️ Architecture

The system follows a modular, agent-based architecture using CrewAI:

- **SEC Agent**: Collects and processes SEC insider trading data
- **History Agent**: Analyzes historical trends and patterns
- **Sentiment Agent**: Analyzes social media sentiment from financial creators
- **Report Agent**: Synthesizes all data into comprehensive reports

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/wildcraft958/CrowdWisdomTrading_AI_Agent.git
   cd CrowdWisdomTrading_AI_Agent
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp configs/.env.example configs/.env
   # Edit configs/.env with your API keys
   ```

4. **Run the analysis**
   ```bash
   python main.py
   ```

## ⚙️ Configuration

### Environment Variables

Create a `configs/.env` file with the following variables:

```ini
# Required for OpenRouter LLM
OPENROUTER_API_KEY=sk-or-your-key

# SEC data (EdgarTools - no API key required)
SEC_IDENTITY=your.email@example.com

# Social sentiment APIs (optional)
TWINWORD_API_KEY=your-twinword-key
SCRAPINGDOG_API_KEY=your-scrapingdog-key

# Twitter API (optional for enhanced sentiment)
TWITTER_BEARER_TOKEN=your-twitter-bearer-token

# Chart generation
QUICKCHART_BASE_URL=https://quickchart.io/chart

# LLM settings
DEFAULT_LLM_MODEL=anthropic/claude-3-haiku
```

### API Keys Setup

#### 1. OpenRouter API (Required for LLM analysis)
- Visit [OpenRouter](https://openrouter.ai/)
- Sign up and get your API key
- Add to `OPENROUTER_API_KEY` in your `.env` file

#### 2. SEC Identity (Required)
- Set your email address in `SEC_IDENTITY`
- Required for SEC EDGAR API compliance

#### 3. Social Sentiment APIs (Optional)
- **Twinword**: Visit [Twinword API](https://www.twinword.com/api/)
- **ScrapingDog**: Visit [ScrapingDog](https://scrapingdog.com/)
- **Twitter API**: Visit [Twitter Developer Portal](https://developer.twitter.com/)

## 🎯 Usage

### Basic Usage

Run with default configuration (analyzes top 10 tech stocks and financial creators):

```bash
python main.py
```

### Custom Analysis

```python
from main import custom_analysis

# Analyze specific symbols and creators
results = custom_analysis(
    symbols=['AAPL', 'TSLA', 'NVDA'],
    creators=['@elonmusk', '@cathiedwood'],
    start_date='2024-08-01',
    end_date='2024-08-31',
    days=1
)

print(f"Investment Grade: {results['summary']['investment_grade']}")
```

### Individual Agent Testing

```python
from crew import CrowdWisdomCrew

crew = CrowdWisdomCrew()

# Test SEC agent only
sec_results = crew.run_individual_agent('sec', 
    symbols=['AAPL', 'MSFT'], 
    days=7
)

# Test sentiment agent only
sentiment_results = crew.run_individual_agent('sentiment', 
    profile_list=['@elonmusk', '@chamath'],
    symbols=['TSLA', 'AAPL']
)
```

## 📊 Output

The system generates several types of output:

### 1. Console Summary
- Investment grade and risk assessment
- Key findings and recommendations
- Performance metrics

### 2. Detailed Report
- Location: `output/reports/crowdwisdom_trading_report_YYYYMMDD_HHMMSS.md`
- Comprehensive markdown report with analysis

### 3. Charts and Visualizations
- Location: `output/charts/`
- Trading activity comparisons
- Sentiment analysis charts
- Dashboard visualizations

### 4. Raw Data Cache
- Location: `data/cache/`
- Cached API responses for faster re-runs
- Individual agent outputs

## 🛠️ Development

### Project Structure

```
├── main.py                 # Main entry point
├── crew.py                 # CrewAI orchestration
├── agents/                 # Individual agents
│   ├── sec_agent.py       # SEC data collection
│   ├── history_agent.py   # Historical analysis
│   ├── sentiment_agent.py # Sentiment analysis
│   └── report_agent.py    # Report generation
├── tools/                  # Utility tools
│   ├── sec_tool.py        # SEC API integration
│   ├── sentiment_tool.py  # Sentiment analysis
│   ├── chart_tool.py      # Chart generation
│   └── llm_tool.py        # LLM integration
├── configs/               # Configuration files
│   ├── agents.yaml        # Agent configurations
│   ├── tasks.yaml         # Task definitions
│   └── .env.example       # Environment template
├── output/                # Generated outputs
│   ├── reports/           # Analysis reports
│   └── charts/            # Generated charts
└── data/                  # Data storage
    ├── cache/             # Cached responses
    └── temp/              # Temporary files
```

### Adding New Features

1. **New Data Sources**: Extend tools in the `tools/` directory
2. **Custom Agents**: Add new agents in the `agents/` directory
3. **Enhanced Analysis**: Modify existing agents or add new analysis methods
4. **Output Formats**: Extend the report agent for new output types

### Testing

Run individual components for testing:

```bash
# Test SEC tool
python tools/sec_tool.py

# Test sentiment analysis
python tools/sentiment_tool.py

# Test chart generation
python tools/chart_tool.py

# Test individual agents
python agents/sec_agent.py
python agents/sentiment_agent.py
```

## 🔧 Troubleshooting

### Common Issues

1. **EdgarTools Installation Error**
   ```bash
   pip install --upgrade edgartools
   ```

2. **API Rate Limits**
   - Check API quotas and limits
   - Implement delays between requests
   - Use cached data when available

3. **Missing Environment Variables**
   - Verify all required variables in `.env`
   - Check `.env.example` for reference

4. **Chart Generation Fails**
   - Verify QuickChart URL accessibility
   - Check chart data format

### Logging

Check logs for detailed error information:
- Console output for real-time feedback
- `output/crowdwisdom_agent.log` for detailed logs

## 📈 Performance Optimization

- **Caching**: Results are cached to reduce API calls
- **Parallel Processing**: Agents can run independently
- **Rate Limiting**: Built-in delays prevent API throttling
- **Data Filtering**: Symbol and date range limits for performance

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This tool is for informational purposes only and should not be considered as financial advice. Always consult with qualified financial professionals before making investment decisions.

## 🙏 Acknowledgments

- **CrewAI**: Multi-agent framework
- **EdgarTools**: SEC data access
- **OpenRouter**: LLM API access
- **QuickChart**: Chart generation
- **Free API providers**: Enabling cost-effective analysis

## 📞 Support

For questions and support:
- Create an issue on GitHub
- Check the documentation
- Review the troubleshooting guide

---

**Made with ❤️ for the trading community**