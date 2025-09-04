# CrowdWisdomTrading AI Agent

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