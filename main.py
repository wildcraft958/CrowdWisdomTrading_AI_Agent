"""
Main entry point for the CrowdWisdom Trading AI Agent.
"""
import os
import sys
import logging
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from crew import CrowdWisdomCrew

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('output/crowdwisdom_agent.log')
    ]
)
logger = logging.getLogger(__name__)

def load_environment():
    """Load environment variables from .env file."""
    
    # Check for .env file in configs directory
    env_file = Path("configs/.env")
    if env_file.exists():
        load_dotenv(env_file)
        logger.info("Loaded environment variables from configs/.env")
    else:
        # Try loading from root directory
        root_env = Path(".env")
        if root_env.exists():
            load_dotenv(root_env)
            logger.info("Loaded environment variables from .env")
        else:
            logger.warning("No .env file found. Using system environment variables.")
    
    # Validate critical environment variables
    required_vars = ['SEC_IDENTITY']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.warning(f"Missing environment variables: {', '.join(missing_vars)}")
        logger.warning("Some features may not work properly. Check configs/.env.example for reference.")

def get_default_config():
    """Get default configuration for the trading agent."""
    
    # Calculate default date range (last week)
    end_date = datetime.now() - timedelta(days=1)  # Yesterday
    start_date = end_date - timedelta(days=7)      # One week ago
    
    return {
        'symbols': [
            'AAPL',   # Apple Inc.
            'MSFT',   # Microsoft Corporation
            'GOOGL',  # Alphabet Inc.
            'AMZN',   # Amazon.com Inc.
            'TSLA',   # Tesla Inc.
            'NVDA',   # NVIDIA Corporation
            'META',   # Meta Platforms Inc.
            'NFLX',   # Netflix Inc.
            'AMD',    # Advanced Micro Devices
            'CRM'     # Salesforce Inc.
        ],
        'x_creators': [
            '@elonmusk',        # Elon Musk
            '@chamath',         # Chamath Palihapitiya
            '@cathiedwood',     # Cathie Wood
            '@jimcramer',       # Jim Cramer
            '@GaryBlack00',     # Gary Black
            '@ReformedBroker',  # Josh Brown
            '@TESLAcharts',     # Tesla Charts
            '@unusual_whales',  # Unusual Whales
            '@zerohedge',       # Zero Hedge
            '@StockMKTNewz'     # Stock Market News
        ],
        'start_date': start_date.strftime('%Y-%m-%d'),
        'end_date': end_date.strftime('%Y-%m-%d'),
        'days': 1  # Look at last 1 day for recent activity
    }

def validate_configuration(config):
    """Validate the configuration parameters."""
    
    errors = []
    
    # Validate symbols
    if not config.get('symbols') or not isinstance(config['symbols'], list):
        errors.append("symbols must be a non-empty list")
    elif len(config['symbols']) > 20:
        errors.append("symbols list should not exceed 20 items for performance reasons")
    
    # Validate creators
    if not config.get('x_creators') or not isinstance(config['x_creators'], list):
        errors.append("x_creators must be a non-empty list")
    elif len(config['x_creators']) > 15:
        errors.append("x_creators list should not exceed 15 items for performance reasons")
    
    # Validate dates
    try:
        start_date = datetime.strptime(config['start_date'], '%Y-%m-%d')
        end_date = datetime.strptime(config['end_date'], '%Y-%m-%d')
        
        if start_date >= end_date:
            errors.append("start_date must be before end_date")
        
        # Check if the date range is reasonable
        date_diff = (end_date - start_date).days
        if date_diff > 90:
            errors.append("date range should not exceed 90 days for performance reasons")
            
    except ValueError as e:
        errors.append(f"Invalid date format: {e}")
    
    # Validate days parameter
    if config.get('days') and (not isinstance(config['days'], int) or config['days'] < 1 or config['days'] > 30):
        errors.append("days must be an integer between 1 and 30")
    
    return errors

def print_banner():
    """Print the application banner."""
    
    banner = """
    ╔══════════════════════════════════════════════════════════════════════════════╗
    ║                        CrowdWisdom Trading AI Agent                          ║
    ║                                                                              ║
    ║    🔍 SEC Insider Trading Analysis   📊 Social Sentiment Analysis           ║
    ║    📈 Historical Trend Analysis      📋 Comprehensive Reporting             ║
    ║                                                                              ║
    ║                          Powered by CrewAI & OpenRouter                     ║
    ╚══════════════════════════════════════════════════════════════════════════════╝
    """
    print(banner)

def print_results_summary(results):
    """Print a summary of the execution results."""
    
    print("\n" + "="*80)
    print("EXECUTION SUMMARY")
    print("="*80)
    
    # Basic status
    status = results.get('status', 'unknown')
    print(f"📊 Status: {status.upper()}")
    
    if status == 'error':
        print(f"❌ Error: {results.get('error', 'Unknown error')}")
        return
    
    # Summary metrics
    summary = results.get('summary', {})
    print(f"🎯 Symbols Analyzed: {summary.get('symbols_analyzed', 0)}")
    print(f"👥 Creators Analyzed: {summary.get('creators_analyzed', 0)}")
    print(f"📄 Recent Filings: {summary.get('recent_filings_found', 0)}")
    print(f"📚 Historical Filings: {summary.get('historical_filings_found', 0)}")
    
    # Investment analysis
    investment_grade = summary.get('investment_grade', 'N/A')
    risk_level = summary.get('risk_level', 'unknown')
    print(f"💎 Investment Grade: {investment_grade}")
    print(f"⚠️  Risk Level: {risk_level.title()}")
    
    # Sentiment analysis
    overall_sentiment = summary.get('overall_sentiment', {})
    sentiment = overall_sentiment.get('sentiment', 'neutral')
    sentiment_score = overall_sentiment.get('score', 0)
    print(f"🎭 Overall Sentiment: {sentiment.title()} ({sentiment_score:+.2f})")
    
    # Performance metrics
    performance = results.get('performance_metrics', {})
    success_rate = performance.get('agent_success_rate', 0)
    confidence = performance.get('confidence_score', 0)
    print(f"✅ Agent Success Rate: {success_rate:.1f}%")
    print(f"🎯 Confidence Score: {confidence:.1f}%")
    
    # Output files
    outputs = results.get('outputs', {})
    if outputs.get('report_path'):
        print(f"📋 Report: {outputs['report_path']}")
    if outputs.get('chart_path'):
        print(f"📊 Charts: {outputs['chart_path']}")
    
    print("="*80)

def print_key_findings(results):
    """Print key findings from the analysis."""
    
    key_findings = results.get('outputs', {}).get('key_findings', [])
    
    if key_findings:
        print("\n" + "="*80)
        print("KEY FINDINGS")
        print("="*80)
        
        for i, finding in enumerate(key_findings, 1):
            print(f"{i}. {finding}")
        
        print("="*80)

def main():
    """Main application entry point."""
    
    try:
        # Print banner
        print_banner()
        
        # Load environment
        load_environment()
        
        # Create output directories
        Path("output/reports").mkdir(parents=True, exist_ok=True)
        Path("output/charts").mkdir(parents=True, exist_ok=True)
        Path("data/cache").mkdir(parents=True, exist_ok=True)
        
        # Get configuration
        config = get_default_config()
        
        print(f"📅 Analysis Period: {config['start_date']} to {config['end_date']}")
        print(f"📈 Symbols: {', '.join(config['symbols'][:5])}{'...' if len(config['symbols']) > 5 else ''}")
        print(f"👥 Creators: {len(config['x_creators'])} financial influencers")
        print(f"🔍 Recent Activity: Last {config['days']} day(s)")
        
        # Validate configuration
        validation_errors = validate_configuration(config)
        if validation_errors:
            print(f"\n❌ Configuration errors:")
            for error in validation_errors:
                print(f"   - {error}")
            return 1
        
        print(f"\n🚀 Starting analysis...")
        start_time = datetime.now()
        
        # Initialize and run the crew
        crew = CrowdWisdomCrew()
        results = crew.kickoff(config)
        
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        
        print(f"⏱️  Execution time: {execution_time:.1f} seconds")
        
        # Print results
        print_results_summary(results)
        print_key_findings(results)
        
        # Success/failure return code
        return 0 if results.get('status') in ['success', 'partial_success'] else 1
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Analysis interrupted by user")
        return 130
        
    except Exception as e:
        logger.error(f"Unexpected error in main execution: {e}")
        print(f"\n❌ Unexpected error: {e}")
        print("Check the log file for more details: output/crowdwisdom_agent.log")
        return 1

def custom_analysis(symbols=None, creators=None, start_date=None, end_date=None, days=None):
    """
    Run custom analysis with specific parameters.
    
    Args:
        symbols: List of stock symbols
        creators: List of creator handles
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        days: Number of days for recent analysis
    
    Returns:
        Analysis results
    """
    load_environment()
    
    # Get default config and override with provided parameters
    config = get_default_config()
    
    if symbols:
        config['symbols'] = symbols
    if creators:
        config['x_creators'] = creators
    if start_date:
        config['start_date'] = start_date
    if end_date:
        config['end_date'] = end_date
    if days:
        config['days'] = days
    
    # Validate and run
    validation_errors = validate_configuration(config)
    if validation_errors:
        raise ValueError(f"Configuration errors: {', '.join(validation_errors)}")
    
    crew = CrowdWisdomCrew()
    return crew.kickoff(config)

if __name__ == "__main__":
    sys.exit(main())
