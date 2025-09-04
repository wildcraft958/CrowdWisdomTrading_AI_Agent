"""
CrewAI orchestration for CrowdWisdom Trading AI Agent.
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import yaml
from pathlib import Path

# Import agents
from agents.sec_agent import SECDataAgent
from agents.history_agent import HistoryDataAgent
from agents.sentiment_agent import SentimentAgent
from agents.report_agent import ReportAgent

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CrowdWisdomCrew:
    """Main CrewAI orchestration class for the CrowdWisdom Trading AI Agent."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the CrowdWisdom crew with all agents.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.crew_name = "CrowdWisdom Trading Intelligence Crew"
        
        # Initialize all agents
        self.sec_agent = SECDataAgent()
        self.history_agent = HistoryDataAgent()
        self.sentiment_agent = SentimentAgent()
        self.report_agent = ReportAgent()
        
        # Load configurations if available
        self._load_configurations()
        
        logger.info(f"Initialized {self.crew_name} with 4 agents")
    
    def _load_configurations(self):
        """Load agent and task configurations from YAML files."""
        
        try:
            # Load agent configurations
            agents_config_path = Path("configs/agents.yaml")
            if agents_config_path.exists():
                with open(agents_config_path, 'r') as f:
                    self.agents_config = yaml.safe_load(f)
                logger.info("Loaded agent configurations")
            else:
                self.agents_config = {}
                logger.warning("Agent configuration file not found")
            
            # Load task configurations
            tasks_config_path = Path("configs/tasks.yaml")
            if tasks_config_path.exists():
                with open(tasks_config_path, 'r') as f:
                    self.tasks_config = yaml.safe_load(f)
                logger.info("Loaded task configurations")
            else:
                self.tasks_config = {}
                logger.warning("Task configuration file not found")
                
        except Exception as e:
            logger.warning(f"Error loading configurations: {e}")
            self.agents_config = {}
            self.tasks_config = {}
    
    def kickoff(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the complete CrowdWisdom trading intelligence workflow.
        
        Args:
            inputs: Dictionary containing:
                - symbols: List of stock symbols to analyze
                - x_creators: List of X/Twitter creator handles
                - start_date: Start date for historical analysis (YYYY-MM-DD)
                - end_date: End date for historical analysis (YYYY-MM-DD)
                - days: Number of days for recent analysis (optional, default: 1)
        
        Returns:
            Comprehensive analysis results
        """
        logger.info(f"Starting {self.crew_name} execution")
        
        # Validate inputs
        validation_result = self._validate_inputs(inputs)
        if not validation_result['valid']:
            return {
                'status': 'error',
                'error': validation_result['error'],
                'execution_time': datetime.now().isoformat()
            }
        
        try:
            # Extract input parameters
            symbols = inputs['symbols']
            x_creators = inputs['x_creators']
            start_date = inputs['start_date']
            end_date = inputs['end_date']
            days = inputs.get('days', 1)
            
            logger.info(f"Analyzing {len(symbols)} symbols and {len(x_creators)} creators")
            
            # Task 1: Collect recent SEC data
            logger.info("Task 1: Collecting recent SEC insider trading data")
            sec_results = self.sec_agent.run(symbols, days)
            
            # Task 2: Analyze historical trends
            logger.info("Task 2: Analyzing historical trading patterns")
            history_results = self.history_agent.run(
                symbols, start_date, end_date, sec_results
            )
            
            # Task 3: Analyze social sentiment
            logger.info("Task 3: Analyzing social media sentiment")
            sentiment_results = self.sentiment_agent.run(x_creators, symbols)
            
            # Task 4: Generate comprehensive report
            logger.info("Task 4: Generating comprehensive report")
            report_results = self.report_agent.run(
                sec_results, history_results, sentiment_results
            )
            
            # Compile final results
            final_results = self._compile_results(
                sec_results, history_results, sentiment_results, report_results, inputs
            )
            
            logger.info(f"{self.crew_name} execution completed successfully")
            return final_results
            
        except Exception as e:
            logger.error(f"Error in crew execution: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'execution_time': datetime.now().isoformat(),
                'partial_results': locals().get('partial_results', {})
            }
    
    def _validate_inputs(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Validate input parameters for the crew execution."""
        
        validation = {'valid': True, 'error': None}
        
        try:
            # Check required fields
            required_fields = ['symbols', 'x_creators', 'start_date', 'end_date']
            for field in required_fields:
                if field not in inputs:
                    validation['valid'] = False
                    validation['error'] = f"Missing required field: {field}"
                    return validation
            
            # Validate symbols
            symbols = inputs['symbols']
            if not isinstance(symbols, list) or len(symbols) == 0:
                validation['valid'] = False
                validation['error'] = "Symbols must be a non-empty list"
                return validation
            
            # Validate creators
            x_creators = inputs['x_creators']
            if not isinstance(x_creators, list) or len(x_creators) == 0:
                validation['valid'] = False
                validation['error'] = "X creators must be a non-empty list"
                return validation
            
            # Validate dates
            try:
                start_date = datetime.strptime(inputs['start_date'], '%Y-%m-%d')
                end_date = datetime.strptime(inputs['end_date'], '%Y-%m-%d')
                
                if start_date >= end_date:
                    validation['valid'] = False
                    validation['error'] = "Start date must be before end date"
                    return validation
                
                # Check if dates are reasonable (not too far in the future or past)
                now = datetime.now()
                if end_date > now:
                    validation['valid'] = False
                    validation['error'] = "End date cannot be in the future"
                    return validation
                
                if start_date < now - timedelta(days=365*2):
                    validation['valid'] = False
                    validation['error'] = "Start date cannot be more than 2 years ago"
                    return validation
                    
            except ValueError as e:
                validation['valid'] = False
                validation['error'] = f"Invalid date format (use YYYY-MM-DD): {e}"
                return validation
            
            # Validate optional days parameter
            if 'days' in inputs:
                days = inputs['days']
                if not isinstance(days, int) or days < 1 or days > 30:
                    validation['valid'] = False
                    validation['error'] = "Days must be an integer between 1 and 30"
                    return validation
            
            logger.info("Input validation passed")
            
        except Exception as e:
            validation['valid'] = False
            validation['error'] = f"Validation error: {e}"
        
        return validation
    
    def _compile_results(self, sec_results: Dict[str, Any], history_results: Dict[str, Any], 
                        sentiment_results: Dict[str, Any], report_results: Dict[str, Any], 
                        inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Compile all agent results into final output."""
        
        final_results = {
            'crew_name': self.crew_name,
            'execution_time': datetime.now().isoformat(),
            'status': 'success',
            'inputs': inputs,
            'agent_results': {
                'sec_agent': sec_results,
                'history_agent': history_results,
                'sentiment_agent': sentiment_results,
                'report_agent': report_results
            },
            'summary': {},
            'outputs': {},
            'performance_metrics': {}
        }
        
        try:
            # Extract key outputs
            final_results['outputs'] = {
                'report_path': report_results.get('report_path', ''),
                'chart_path': report_results.get('chart_path', ''),
                'investment_grade': report_results.get('investment_grade', {}),
                'key_findings': report_results.get('key_findings', []),
                'executive_summary': report_results.get('executive_summary', {})
            }
            
            # Generate execution summary
            final_results['summary'] = {
                'symbols_analyzed': len(inputs['symbols']),
                'creators_analyzed': len(inputs['x_creators']),
                'recent_filings_found': sec_results.get('summary', {}).get('total_filings', 0),
                'historical_filings_found': history_results.get('summary', {}).get('total_filings', 0),
                'overall_sentiment': sentiment_results.get('raw_sentiment', {}).get('overall_sentiment', {}),
                'investment_grade': report_results.get('investment_grade', {}).get('grade', 'N/A'),
                'risk_level': report_results.get('executive_summary', {}).get('risk_assessment', {}).get('overall_risk_level', 'unknown')
            }
            
            # Calculate performance metrics
            final_results['performance_metrics'] = self._calculate_performance_metrics(
                sec_results, history_results, sentiment_results, report_results
            )
            
            # Check for any agent failures
            agent_statuses = [
                sec_results.get('status'),
                history_results.get('status'),
                sentiment_results.get('status'),
                report_results.get('status')
            ]
            
            if 'error' in agent_statuses:
                final_results['status'] = 'partial_success'
                final_results['warnings'] = 'Some agents encountered errors'
            
        except Exception as e:
            logger.error(f"Error compiling results: {e}")
            final_results['compilation_error'] = str(e)
        
        return final_results
    
    def _calculate_performance_metrics(self, sec_results: Dict[str, Any], history_results: Dict[str, Any], 
                                     sentiment_results: Dict[str, Any], report_results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate performance metrics for the crew execution."""
        
        metrics = {
            'data_quality_score': 0,
            'analysis_completeness': 0,
            'confidence_score': 0,
            'agent_success_rate': 0
        }
        
        try:
            # Agent success rate
            successful_agents = sum(1 for result in [sec_results, history_results, sentiment_results, report_results] 
                                  if result.get('status') == 'success')
            metrics['agent_success_rate'] = (successful_agents / 4) * 100
            
            # Data quality score based on data availability
            data_quality = 0
            if sec_results.get('summary', {}).get('total_filings', 0) > 0:
                data_quality += 25
            if history_results.get('summary', {}).get('total_filings', 0) > 0:
                data_quality += 25
            if sentiment_results.get('raw_sentiment', {}).get('profiles_analyzed', 0) > 0:
                data_quality += 25
            if report_results.get('status') == 'success':
                data_quality += 25
            metrics['data_quality_score'] = data_quality
            
            # Analysis completeness
            completeness = 0
            if 'insights' in sec_results:
                completeness += 25
            if 'trend_analysis' in history_results:
                completeness += 25
            if 'market_assessment' in sentiment_results:
                completeness += 25
            if 'investment_grade' in report_results:
                completeness += 25
            metrics['analysis_completeness'] = completeness
            
            # Overall confidence score
            confidence_levels = []
            if 'confidence_level' in report_results.get('executive_summary', {}):
                conf = report_results['executive_summary']['confidence_level']
                if conf == 'high':
                    confidence_levels.append(90)
                elif conf == 'medium':
                    confidence_levels.append(70)
                else:
                    confidence_levels.append(50)
            
            if confidence_levels:
                metrics['confidence_score'] = sum(confidence_levels) / len(confidence_levels)
            else:
                metrics['confidence_score'] = 60  # Default medium confidence
            
        except Exception as e:
            logger.warning(f"Error calculating performance metrics: {e}")
        
        return metrics
    
    def get_crew_status(self) -> Dict[str, Any]:
        """Get current crew status and agent information."""
        
        return {
            'crew_name': self.crew_name,
            'status': 'ready',
            'agents': {
                'sec_agent': self.sec_agent.get_agent_status(),
                'history_agent': self.history_agent.get_agent_status(),
                'sentiment_agent': self.sentiment_agent.get_agent_status(),
                'report_agent': self.report_agent.get_agent_status()
            },
            'capabilities': [
                'SEC insider trading analysis',
                'Historical trend analysis',
                'Social sentiment analysis',
                'Comprehensive report generation',
                'Risk assessment',
                'Investment grading'
            ],
            'workflow': [
                'Collect recent SEC filings',
                'Analyze historical patterns',
                'Assess social sentiment',
                'Generate comprehensive report'
            ]
        }
    
    def run_individual_agent(self, agent_name: str, **kwargs) -> Dict[str, Any]:
        """
        Run an individual agent for testing or partial analysis.
        
        Args:
            agent_name: Name of the agent to run ('sec', 'history', 'sentiment', 'report')
            **kwargs: Agent-specific parameters
        
        Returns:
            Agent execution results
        """
        logger.info(f"Running individual agent: {agent_name}")
        
        try:
            if agent_name == 'sec':
                return self.sec_agent.run(kwargs.get('symbols', []), kwargs.get('days', 1))
            elif agent_name == 'history':
                return self.history_agent.run(
                    kwargs.get('symbols', []), 
                    kwargs.get('start_date', ''), 
                    kwargs.get('end_date', ''),
                    kwargs.get('compare_to_recent')
                )
            elif agent_name == 'sentiment':
                return self.sentiment_agent.run(
                    kwargs.get('profile_list', []), 
                    kwargs.get('symbols')
                )
            elif agent_name == 'report':
                return self.report_agent.run(
                    kwargs.get('sec_data', {}),
                    kwargs.get('history_data', {}),
                    kwargs.get('sentiment_results', {})
                )
            else:
                return {
                    'error': f"Unknown agent: {agent_name}",
                    'available_agents': ['sec', 'history', 'sentiment', 'report']
                }
                
        except Exception as e:
            logger.error(f"Error running individual agent {agent_name}: {e}")
            return {
                'agent': agent_name,
                'status': 'error',
                'error': str(e)
            }

if __name__ == "__main__":
    # Test the crew with sample data
    crew = CrowdWisdomCrew()
    
    # Sample inputs
    test_inputs = {
        'symbols': ['AAPL', 'MSFT', 'GOOGL'],
        'x_creators': ['@elonmusk', '@chamath', '@cathiedwood'],
        'start_date': '2024-08-01',
        'end_date': '2024-08-31',
        'days': 1
    }
    
    print("Testing CrowdWisdom Crew...")
    results = crew.kickoff(test_inputs)
    
    print(f"Execution Status: {results.get('status')}")
    print(f"Investment Grade: {results.get('summary', {}).get('investment_grade', 'N/A')}")
    print(f"Recent Filings Found: {results.get('summary', {}).get('recent_filings_found', 0)}")
    print(f"Performance Score: {results.get('performance_metrics', {}).get('agent_success_rate', 0):.1f}%")
