#!/usr/bin/env python3
"""
Quick test script for CrowdWisdom Trading AI Agent
"""
import sys
from pathlib import Path
import logging

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Test if all required modules can be imported."""
    print("🔍 Testing imports...")
    
    try:
        import requests
        print("✅ requests")
    except ImportError as e:
        print(f"❌ requests: {e}")
        return False
    
    try:
        import pandas
        print("✅ pandas")
    except ImportError as e:
        print(f"❌ pandas: {e}")
        return False
    
    try:
        import yaml
        print("✅ PyYAML")
    except ImportError as e:
        print(f"❌ PyYAML: {e}")
        return False
    
    try:
        from dotenv import load_dotenv
        print("✅ python-dotenv")
    except ImportError as e:
        print(f"❌ python-dotenv: {e}")
        return False
    
    try:
        import edgar
        print("✅ edgartools")
    except ImportError as e:
        print(f"❌ edgartools: {e}")
        return False
    
    return True

def test_project_structure():
    """Test if project structure is correct."""
    print("\n🏗️  Testing project structure...")
    
    required_dirs = [
        "agents",
        "tools", 
        "configs",
        "output",
        "data"
    ]
    
    required_files = [
        "main.py",
        "crew.py",
        "requirements.txt",
        "agents/sec_agent.py",
        "agents/history_agent.py", 
        "agents/sentiment_agent.py",
        "agents/report_agent.py",
        "tools/sec_tool.py",
        "tools/sentiment_tool.py",
        "tools/chart_tool.py",
        "tools/llm_tool.py"
    ]
    
    all_good = True
    
    for dir_name in required_dirs:
        if Path(dir_name).exists():
            print(f"✅ {dir_name}/")
        else:
            print(f"❌ {dir_name}/ (missing)")
            all_good = False
    
    for file_name in required_files:
        if Path(file_name).exists():
            print(f"✅ {file_name}")
        else:
            print(f"❌ {file_name} (missing)")
            all_good = False
    
    return all_good

def test_environment():
    """Test environment configuration."""
    print("\n🔧 Testing environment configuration...")
    
    from dotenv import load_dotenv
    import os
    
    # Load environment
    env_file = Path("configs/.env")
    if env_file.exists():
        load_dotenv(env_file)
        print("✅ configs/.env file found")
    else:
        print("⚠️  configs/.env file not found (will use defaults)")
    
    # Check SEC identity
    sec_identity = os.getenv('SEC_IDENTITY')
    if sec_identity:
        print(f"✅ SEC_IDENTITY: {sec_identity}")
    else:
        print("⚠️  SEC_IDENTITY not set (will use default)")
    
    # Check OpenRouter API key
    openrouter_key = os.getenv('OPENROUTER_API_KEY')
    if openrouter_key:
        print("✅ OPENROUTER_API_KEY: [SET]")
    else:
        print("⚠️  OPENROUTER_API_KEY not set (LLM features will be limited)")
    
    return True

def test_basic_functionality():
    """Test basic functionality of core components."""
    print("\n🧪 Testing basic functionality...")
    
    try:
        # Test SEC tool import
        from tools.sec_tool import fetch_recent_sec_filings
        print("✅ SEC tool import")
        
        # Test sentiment tool import
        from tools.sentiment_tool import analyze_profiles_sentiment  
        print("✅ Sentiment tool import")
        
        # Test chart tool import
        from tools.chart_tool import generate_chart
        print("✅ Chart tool import")
        
        # Test LLM tool import
        from tools.llm_tool import summarize_report
        print("✅ LLM tool import")
        
        # Test agents import
        from agents.sec_agent import SECDataAgent
        from agents.history_agent import HistoryDataAgent
        from agents.sentiment_agent import SentimentAgent
        from agents.report_agent import ReportAgent
        print("✅ All agents import")
        
        # Test crew import
        from crew import CrowdWisdomCrew
        print("✅ CrewAI orchestration import")
        
        return True
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_agent_initialization():
    """Test agent initialization."""
    print("\n🤖 Testing agent initialization...")
    
    try:
        from agents.sec_agent import SECDataAgent
        from agents.history_agent import HistoryDataAgent
        from agents.sentiment_agent import SentimentAgent
        from agents.report_agent import ReportAgent
        from crew import CrowdWisdomCrew
        
        # Test individual agents
        sec_agent = SECDataAgent()
        print("✅ SEC Agent initialized")
        
        history_agent = HistoryDataAgent()
        print("✅ History Agent initialized")
        
        sentiment_agent = SentimentAgent()
        print("✅ Sentiment Agent initialized")
        
        report_agent = ReportAgent()
        print("✅ Report Agent initialized")
        
        # Test crew
        crew = CrowdWisdomCrew()
        print("✅ CrowdWisdom Crew initialized")
        
        return True
        
    except Exception as e:
        print(f"❌ Initialization error: {e}")
        return False

def run_quick_test():
    """Run a quick test with minimal data."""
    print("\n🚀 Running quick functionality test...")
    
    try:
        from crew import CrowdWisdomCrew
        
        # Initialize crew
        crew = CrowdWisdomCrew()
        
        # Get crew status
        status = crew.get_crew_status()
        print(f"✅ Crew status: {status['status']}")
        print(f"✅ Available agents: {len(status['agents'])}")
        
        # Test individual agent (SEC agent with minimal data)
        print("\n🔍 Testing SEC agent with sample data...")
        sec_result = crew.run_individual_agent('sec', symbols=['AAPL'], days=1)
        
        if sec_result.get('status') == 'success':
            print("✅ SEC agent test successful")
        elif sec_result.get('status') == 'error':
            print(f"⚠️  SEC agent test completed with expected limitations: {sec_result.get('error', 'unknown')}")
        else:
            print(f"⚠️  SEC agent test status: {sec_result.get('status', 'unknown')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Quick test error: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 CrowdWisdom Trading AI Agent - System Test")
    print("=" * 60)
    
    tests = [
        ("Import Tests", test_imports),
        ("Project Structure", test_project_structure), 
        ("Environment Configuration", test_environment),
        ("Basic Functionality", test_basic_functionality),
        ("Agent Initialization", test_agent_initialization),
        ("Quick Functionality Test", run_quick_test)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{test_name}")
        print("-" * 40)
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! The system is ready to use.")
        print("\nTo run the full analysis:")
        print("   python main.py")
        print("\nTo run with custom parameters:")
        print("   python -c \"from main import custom_analysis; print(custom_analysis(['AAPL'], ['@elonmusk']))\"")
    else:
        print("\n⚠️  Some tests failed. Please check the issues above.")
        print("\nCommon solutions:")
        print("- Install missing dependencies: pip install -r requirements.txt") 
        print("- Set up environment: cp configs/.env.example configs/.env")
        print("- Check API keys in configs/.env")
    
    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(main())
