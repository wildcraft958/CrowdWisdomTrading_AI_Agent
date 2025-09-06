"""
Report Agent for generating comprehensive trading intelligence reports.
"""
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from tools.chart_tool import generate_chart
from tools.llm_tool import summarize_report

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ReportAgent:
    """Agent responsible for generating comprehensive trading intelligence reports."""
    
    def __init__(self):
        """Initialize Report Agent."""
        self.agent_name = "Report Generator"
        self.description = "Specialized agent for synthesizing data into comprehensive trading reports"
        logger.info(f"Initialized {self.agent_name}")
    
    def run(self, sec_data: Dict[str, Any], history_data: Dict[str, Any], 
            sentiment_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate comprehensive trading intelligence report.
        
        Args:
            sec_data: Recent SEC filing data from SEC agent
            history_data: Historical analysis data from History agent
            sentiment_results: Sentiment analysis results from Sentiment agent
        
        Returns:
            Dictionary containing comprehensive report with charts and summary
        """
        logger.info("Report Agent generating comprehensive trading intelligence report")
        
        try:
            # Extract raw data from agent results
            sec_raw_data = self._extract_raw_data(sec_data, 'sec')
            history_raw_data = self._extract_raw_data(history_data, 'history')
            sentiment_raw_data = self._extract_raw_data(sentiment_results, 'sentiment')
            
            # Generate visualizations
            chart_path = self._generate_visualizations(sec_raw_data, history_raw_data, sentiment_raw_data)
            
            # Generate comprehensive summary using LLM
            summary = self._generate_comprehensive_summary(sec_data, history_data, sentiment_results)
            
            # Create executive dashboard
            executive_summary = self._create_executive_summary(sec_data, history_data, sentiment_results)
            
            # Compile final report
            final_report = self._compile_final_report(
                sec_data, history_data, sentiment_results, 
                chart_path, summary, executive_summary
            )
            
            # Save report to file
            report_path = self._save_report(final_report)
            
            # Prepare agent results
            results = {
                'agent': self.agent_name,
                'execution_time': datetime.now().isoformat(),
                'report_path': report_path,
                'chart_path': chart_path,
                'executive_summary': executive_summary,
                'comprehensive_summary': summary,
                'final_report': final_report,
                'key_findings': self._extract_key_findings(sec_data, history_data, sentiment_results),
                'investment_grade': self._assign_investment_grade(sec_data, history_data, sentiment_results),
                'status': 'success'
            }
            
            logger.info(f"Report Agent completed: Report saved to {report_path}")
            return results
            
        except Exception as e:
            logger.error(f"Report Agent error: {e}")
            return {
                'agent': self.agent_name,
                'execution_time': datetime.now().isoformat(),
                'error': str(e),
                'status': 'error'
            }
    
    def _extract_raw_data(self, agent_data: Dict[str, Any], agent_type: str) -> Dict[str, Any]:
        """Extract raw data from agent results for visualization."""
        
        try:
            if agent_type == 'sec':
                return agent_data.get('raw_data', {})
            elif agent_type == 'history':
                return agent_data.get('raw_data', {})
            elif agent_type == 'sentiment':
                return agent_data.get('raw_sentiment', {})
            else:
                return agent_data
        except Exception as e:
            logger.warning(f"Error extracting raw data for {agent_type}: {e}")
            return {}
    
    def _generate_visualizations(self, sec_data: Dict[str, Any], history_data: Dict[str, Any], 
                               sentiment_data: Dict[str, Any]) -> str:
        """Generate charts and visualizations."""
        
        try:
            logger.info("Generating visualizations")
            chart_path = generate_chart(sec_data, history_data, sentiment_data)
            logger.info(f"Charts generated: {chart_path}")
            return chart_path
        except Exception as e:
            logger.error(f"Error generating visualizations: {e}")
            return "Error generating charts"
    
    def _generate_comprehensive_summary(self, sec_data: Dict[str, Any], history_data: Dict[str, Any], 
                                      sentiment_results: Dict[str, Any]) -> str:
        """Generate comprehensive LLM-powered summary."""
        
        try:
            logger.info("Generating LLM-powered summary")
            
            # Extract raw data for LLM analysis
            sec_raw = self._extract_raw_data(sec_data, 'sec')
            history_raw = self._extract_raw_data(history_data, 'history')
            sentiment_raw = self._extract_raw_data(sentiment_results, 'sentiment')
            
            summary = summarize_report(sec_raw, history_raw, sentiment_raw)
            logger.info("LLM summary generated successfully")
            return summary
        except Exception as e:
            logger.error(f"Error generating comprehensive summary: {e}")
            return self._generate_fallback_summary(sec_data, history_data, sentiment_results)
    
    def _create_executive_summary(self, sec_data: Dict[str, Any], history_data: Dict[str, Any], 
                                sentiment_results: Dict[str, Any]) -> Dict[str, Any]:
        """Create executive summary with key metrics."""
        
        executive_summary = {
            'overview': {},
            'key_metrics': {},
            'risk_assessment': {},
            'recommendations': {},
            'confidence_level': 'medium'
        }
        
        try:
            # Extract key data points
            sec_summary = sec_data.get('summary', {})
            history_summary = history_data.get('summary', {})
            sentiment_overall = sentiment_results.get('raw_sentiment', {}).get('overall_sentiment', {})
            
            # Overview
            executive_summary['overview'] = {
                'analysis_timestamp': datetime.now().isoformat(),
                'symbols_analyzed': len(set(
                    list(sec_summary.get('symbols_with_activity', [])) + 
                    list(history_summary.get('symbols_with_activity', []))
                )),
                'total_recent_filings': sec_summary.get('total_filings', 0),
                'total_historical_filings': history_summary.get('total_filings', 0),
                'sentiment_score': sentiment_overall.get('score', 0),
                'sentiment_direction': sentiment_overall.get('sentiment', 'neutral')
            }
            
            # Key metrics
            recent_buys = sec_summary.get('buy_transactions', 0)
            recent_sells = sec_summary.get('sell_transactions', 0)
            hist_buys = history_summary.get('buy_transactions', 0)
            hist_sells = history_summary.get('sell_transactions', 0)
            
            executive_summary['key_metrics'] = {
                'recent_buy_sell_ratio': recent_buys / max(recent_buys + recent_sells, 1),
                'historical_buy_sell_ratio': hist_buys / max(hist_buys + hist_sells, 1),
                'filing_activity_change': self._calculate_activity_change(sec_summary, history_summary),
                'sentiment_strength': abs(sentiment_overall.get('score', 0)),
                'unique_insiders_recent': sec_summary.get('unique_insider_count', 0),
                'unique_insiders_historical': history_summary.get('unique_insider_count', 0)
            }
            
            # Risk assessment
            executive_summary['risk_assessment'] = self._assess_overall_risk(
                sec_data, history_data, sentiment_results
            )
            
            # Recommendations
            executive_summary['recommendations'] = self._generate_executive_recommendations(
                sec_data, history_data, sentiment_results
            )
            
            # Confidence level
            executive_summary['confidence_level'] = self._calculate_confidence_level(
                sec_data, history_data, sentiment_results
            )
            
        except Exception as e:
            logger.warning(f"Error creating executive summary: {e}")
            executive_summary['error'] = str(e)
        
        return executive_summary
    
    def _calculate_activity_change(self, sec_summary: Dict[str, Any], 
                                  history_summary: Dict[str, Any]) -> float:
        """Calculate percentage change in filing activity."""
        
        try:
            recent_filings = sec_summary.get('total_filings', 0)
            historical_filings = history_summary.get('total_filings', 0)
            
            if historical_filings > 0:
                return round(((recent_filings - historical_filings) / historical_filings) * 100, 1)
            else:
                return 100.0 if recent_filings > 0 else 0.0
        except Exception:
            return 0.0
    
    def _assess_overall_risk(self, sec_data: Dict[str, Any], history_data: Dict[str, Any], 
                           sentiment_results: Dict[str, Any]) -> Dict[str, Any]:
        """Assess overall investment risk based on all data sources."""
        
        risk_assessment = {
            'overall_risk_level': 'medium',
            'risk_factors': [],
            'mitigating_factors': [],
            'risk_score': 5  # 1-10 scale
        }
        
        try:
            # Analyze SEC data risks
            sec_insights = sec_data.get('insights', {})
            if 'heavy_insider_selling' in sec_insights.get('risk_indicators', []):
                risk_assessment['risk_factors'].append('Heavy insider selling detected')
                risk_assessment['risk_score'] += 2
            
            # Analyze sentiment risks
            sentiment_assessment = sentiment_results.get('market_assessment', {})
            if sentiment_assessment.get('risk_level') == 'high':
                risk_assessment['risk_factors'].append('High sentiment risk level')
                risk_assessment['risk_score'] += 1
            
            # Analyze historical patterns
            history_insights = history_data.get('insights', {})
            if 'widespread_insider_selling' in history_insights.get('risk_indicators', []):
                risk_assessment['risk_factors'].append('Historical pattern of insider selling')
                risk_assessment['risk_score'] += 1
            
            # Identify mitigating factors
            if sec_insights.get('buy_sell_signal') == 'bullish':
                risk_assessment['mitigating_factors'].append('Recent insider buying activity')
                risk_assessment['risk_score'] -= 1
            
            if sentiment_assessment.get('market_mood') == 'optimistic':
                risk_assessment['mitigating_factors'].append('Positive market sentiment')
                risk_assessment['risk_score'] -= 1
            
            # Determine overall risk level
            if risk_assessment['risk_score'] >= 8:
                risk_assessment['overall_risk_level'] = 'high'
            elif risk_assessment['risk_score'] <= 3:
                risk_assessment['overall_risk_level'] = 'low'
            else:
                risk_assessment['overall_risk_level'] = 'medium'
            
            # Ensure risk score stays within bounds
            risk_assessment['risk_score'] = max(1, min(10, risk_assessment['risk_score']))
            
        except Exception as e:
            logger.warning(f"Error assessing overall risk: {e}")
            risk_assessment['assessment_error'] = str(e)
        
        return risk_assessment
    
    def _generate_executive_recommendations(self, sec_data: Dict[str, Any], history_data: Dict[str, Any], 
                                          sentiment_results: Dict[str, Any]) -> List[str]:
        """Generate executive-level recommendations."""
        
        recommendations = []
        
        try:
            # SEC-based recommendations
            sec_insights = sec_data.get('insights', {})
            if sec_insights.get('buy_sell_signal') == 'bullish':
                recommendations.append("Consider the positive insider trading signals in investment decisions")
            elif sec_insights.get('buy_sell_signal') == 'bearish':
                recommendations.append("Exercise caution due to negative insider trading patterns")
            
            # Sentiment-based recommendations
            sentiment_recs = sentiment_results.get('recommendations', {})
            if sentiment_recs.get('confidence_level') == 'high':
                recommendations.extend(sentiment_recs.get('immediate_actions', []))
            
            # Historical trend recommendations
            history_comparison = history_data.get('comparison', {})
            if history_comparison and history_comparison.get('trend_direction') == 'increasing':
                recommendations.append("Monitor the increasing trend in insider activity")
            
            # Risk management recommendations
            risk_assessment = self._assess_overall_risk(sec_data, history_data, sentiment_results)
            if risk_assessment['overall_risk_level'] == 'high':
                recommendations.append("Implement enhanced risk management due to elevated risk factors")
            
            # Default recommendation if none generated
            if not recommendations:
                recommendations.append("Continue monitoring insider activity and sentiment trends")
            
        except Exception as e:
            logger.warning(f"Error generating executive recommendations: {e}")
            recommendations.append("Review all data sources carefully before making investment decisions")
        
        return recommendations
    
    def _calculate_confidence_level(self, sec_data: Dict[str, Any], history_data: Dict[str, Any], 
                                  sentiment_results: Dict[str, Any]) -> str:
        """Calculate overall confidence level in the analysis."""
        
        try:
            confidence_score = 0
            
            # SEC data confidence
            if sec_data.get('status') == 'success' and sec_data.get('summary', {}).get('total_filings', 0) > 0:
                confidence_score += 3
            
            # Historical data confidence
            if history_data.get('status') == 'success' and history_data.get('summary', {}).get('total_filings', 0) > 0:
                confidence_score += 3
            
            # Sentiment data confidence
            sentiment_conf = sentiment_results.get('recommendations', {}).get('confidence_level', 'low')
            if sentiment_conf == 'high':
                confidence_score += 4
            elif sentiment_conf == 'medium':
                confidence_score += 2
            
            # Determine overall confidence
            if confidence_score >= 8:
                return 'high'
            elif confidence_score >= 5:
                return 'medium'
            else:
                return 'low'
                
        except Exception:
            return 'medium'
    
    def _extract_key_findings(self, sec_data: Dict[str, Any], history_data: Dict[str, Any], 
                            sentiment_results: Dict[str, Any]) -> List[str]:
        """Extract key findings from all data sources."""
        
        key_findings = []
        
        try:
            # SEC findings
            sec_summary = sec_data.get('summary', {})
            if sec_summary.get('total_filings', 0) > 0:
                key_findings.append(
                    f"Recent insider activity: {sec_summary['total_filings']} filings with "
                    f"{sec_summary.get('buy_transactions', 0)} buys and {sec_summary.get('sell_transactions', 0)} sells"
                )
            
            # Historical findings
            history_comparison = history_data.get('comparison', {})
            if history_comparison:
                change = history_comparison.get('filing_change', {}).get('percentage_change', 0)
                key_findings.append(f"Filing activity changed by {change:+.1f}% compared to historical period")
            
            # Sentiment findings
            sentiment_overall = sentiment_results.get('raw_sentiment', {}).get('overall_sentiment', {})
            if sentiment_overall:
                score = sentiment_overall.get('score', 0)
                sentiment = sentiment_overall.get('sentiment', 'neutral')
                key_findings.append(f"Social sentiment is {sentiment} with score {score:+.2f}")
            
            # Risk findings
            risk_assessment = self._assess_overall_risk(sec_data, history_data, sentiment_results)
            key_findings.append(f"Overall risk level assessed as {risk_assessment['overall_risk_level']}")
            
        except Exception as e:
            logger.warning(f"Error extracting key findings: {e}")
            key_findings.append("Analysis completed with limited data availability")
        
        return key_findings
    
    def _assign_investment_grade(self, sec_data: Dict[str, Any], history_data: Dict[str, Any], 
                               sentiment_results: Dict[str, Any]) -> Dict[str, Any]:
        """Assign overall investment grade based on analysis."""
        
        investment_grade = {
            'grade': 'B',  # A, B, C, D, F
            'score': 0,    # 0-100
            'rationale': [],
            'outlook': 'neutral'
        }
        
        try:
            score = 50  # Start with neutral score
            
            # SEC data impact
            sec_insights = sec_data.get('insights', {})
            if sec_insights.get('buy_sell_signal') == 'bullish':
                score += 15
                investment_grade['rationale'].append("Positive insider trading signals")
            elif sec_insights.get('buy_sell_signal') == 'bearish':
                score -= 15
                investment_grade['rationale'].append("Negative insider trading signals")
            
            # Sentiment impact
            sentiment_overall = sentiment_results.get('raw_sentiment', {}).get('overall_sentiment', {})
            sentiment_score = sentiment_overall.get('score', 0)
            if sentiment_score > 0.3:
                score += 10
                investment_grade['rationale'].append("Positive social sentiment")
            elif sentiment_score < -0.3:
                score -= 10
                investment_grade['rationale'].append("Negative social sentiment")
            
            # Historical trend impact
            history_comparison = history_data.get('comparison', {})
            if history_comparison:
                trend = history_comparison.get('trend_direction', 'neutral')
                if trend == 'increasing':
                    score += 10
                    investment_grade['rationale'].append("Increasing activity trend")
                elif trend == 'decreasing':
                    score -= 5
                    investment_grade['rationale'].append("Decreasing activity trend")
            
            # Risk adjustment
            risk_assessment = self._assess_overall_risk(sec_data, history_data, sentiment_results)
            risk_level = risk_assessment['overall_risk_level']
            if risk_level == 'low':
                score += 10
            elif risk_level == 'high':
                score -= 15
            
            # Assign grade based on score
            investment_grade['score'] = max(0, min(100, score))
            
            if score >= 80:
                investment_grade['grade'] = 'A'
                investment_grade['outlook'] = 'positive'
            elif score >= 70:
                investment_grade['grade'] = 'B'
                investment_grade['outlook'] = 'positive'
            elif score >= 50:
                investment_grade['grade'] = 'C'
                investment_grade['outlook'] = 'neutral'
            elif score >= 30:
                investment_grade['grade'] = 'D'
                investment_grade['outlook'] = 'negative'
            else:
                investment_grade['grade'] = 'F'
                investment_grade['outlook'] = 'negative'
            
        except Exception as e:
            logger.warning(f"Error assigning investment grade: {e}")
            investment_grade['grade'] = 'C'
            investment_grade['rationale'].append("Grade assigned with limited data")
        
        return investment_grade
    
    def _compile_final_report(self, sec_data: Dict[str, Any], history_data: Dict[str, Any], 
                            sentiment_results: Dict[str, Any], chart_path: str, 
                            summary: str, executive_summary: Dict[str, Any]) -> str:
        """Compile all components into final report."""
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        investment_grade = self._assign_investment_grade(sec_data, history_data, sentiment_results)
        key_findings = self._extract_key_findings(sec_data, history_data, sentiment_results)
        
        final_report = f"""
# CrowdWisdom Trading Intelligence Report
**Generated:** {timestamp}
**Investment Grade:** {investment_grade['grade']} (Score: {investment_grade['score']}/100)
**Outlook:** {investment_grade['outlook'].title()}

---

## Executive Summary

### Key Metrics
- **Symbols Analyzed:** {executive_summary['overview'].get('symbols_analyzed', 0)}
- **Recent Filings:** {executive_summary['overview'].get('total_recent_filings', 0)}
- **Historical Filings:** {executive_summary['overview'].get('total_historical_filings', 0)}
- **Sentiment Score:** {executive_summary['overview'].get('sentiment_score', 0):+.2f}
- **Sentiment Direction:** {executive_summary['overview'].get('sentiment_direction', 'neutral').title()}
- **Overall Risk Level:** {executive_summary['risk_assessment'].get('overall_risk_level', 'medium').title()}
- **Analysis Confidence:** {executive_summary.get('confidence_level', 'medium').title()}

### Key Findings
"""
        
        for finding in key_findings:
            final_report += f"- {finding}\n"
        
        final_report += f"""

### Investment Grade Rationale
"""
        for rationale in investment_grade['rationale']:
            final_report += f"- {rationale}\n"
        
        final_report += f"""

### Executive Recommendations
"""
        for rec in executive_summary['recommendations']:
            final_report += f"- {rec}\n"
        
        final_report += f"""

---

## Detailed Analysis

{summary}

---

## Risk Assessment

**Overall Risk Level:** {executive_summary['risk_assessment'].get('overall_risk_level', 'medium').title()}
**Risk Score:** {executive_summary['risk_assessment'].get('risk_score', 5)}/10

### Risk Factors
"""
        
        for risk in executive_summary['risk_assessment'].get('risk_factors', []):
            final_report += f"- {risk}\n"
        
        final_report += f"""

### Mitigating Factors
"""
        
        for factor in executive_summary['risk_assessment'].get('mitigating_factors', []):
            final_report += f"- {factor}\n"
        
        final_report += f"""

---

## Data Sources & Methodology

### SEC Insider Trading Data
- Source: SEC EDGAR database
- Recent Period: Last 24 hours
- Historical Period: Comparative analysis
- Forms Analyzed: Form 4 (Insider Trading)

### Social Sentiment Analysis
- Profiles Analyzed: {sentiment_results.get('raw_sentiment', {}).get('profiles_analyzed', 0)}
- Posts Analyzed: {sentiment_results.get('raw_sentiment', {}).get('overall_sentiment', {}).get('total_posts', 0)}
- Sentiment Engine: Multi-source analysis

### Visualizations
- Charts Generated: {chart_path}

---

## Disclaimer

This report is generated by the CrowdWisdom Trading AI Agent for informational purposes only. 
It should not be considered as financial advice. Always consult with qualified financial 
professionals before making investment decisions.

**Report ID:** {timestamp.replace(' ', '_').replace(':', '-')}
**Generated by:** CrowdWisdom Trading AI Agent v1.0
"""
        
        return final_report
    
    def _save_report(self, report_content: str) -> str:
        """Save the final report to file."""
        
        try:
            from pathlib import Path
            
            output_dir = Path("output/reports")
            output_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"crowdwisdom_trading_report_{timestamp}.md"
            report_path = output_dir / filename
            
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            logger.info(f"Final report saved: {report_path}")
            return str(report_path)
            
        except Exception as e:
            logger.error(f"Error saving report: {e}")
            return "Error saving report"
    
    def _generate_fallback_summary(self, sec_data: Dict[str, Any], history_data: Dict[str, Any], 
                                 sentiment_results: Dict[str, Any]) -> str:
        """Generate fallback summary when LLM is unavailable."""
        
        return f"""
## Analysis Summary (Fallback Mode)

### SEC Insider Trading Analysis
- Recent filings analyzed: {sec_data.get('summary', {}).get('total_filings', 0)}
- Buy transactions: {sec_data.get('summary', {}).get('buy_transactions', 0)}
- Sell transactions: {sec_data.get('summary', {}).get('sell_transactions', 0)}
- Unique insiders: {sec_data.get('summary', {}).get('unique_insider_count', 0)}

### Historical Trend Analysis
- Historical filings: {history_data.get('summary', {}).get('total_filings', 0)}
- Analysis period: {history_data.get('period', 'Not specified')}
- Trend direction: {history_data.get('comparison', {}).get('trend_direction', 'neutral').title()}

### Social Sentiment Analysis
- Overall sentiment: {sentiment_results.get('raw_sentiment', {}).get('overall_sentiment', {}).get('sentiment', 'neutral').title()}
- Sentiment score: {sentiment_results.get('raw_sentiment', {}).get('overall_sentiment', {}).get('score', 0):+.2f}
- Profiles analyzed: {sentiment_results.get('raw_sentiment', {}).get('profiles_analyzed', 0)}

This summary was generated using template analysis due to LLM unavailability.
"""
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get current agent status and capabilities."""
        return {
            'agent_name': self.agent_name,
            'status': 'ready',
            'capabilities': [
                'Comprehensive report generation',
                'Multi-source data synthesis',
                'Executive summary creation',
                'Risk assessment',
                'Investment grading',
                'Visualization integration',
                'LLM-powered analysis'
            ],
            'output_formats': [
                'markdown_report',
                'executive_summary',
                'investment_grade',
                'risk_assessment'
            ],
            'integration_points': [
                'SEC_agent_data',
                'History_agent_data',
                'Sentiment_agent_data',
                'Chart_generation',
                'LLM_summarization'
            ]
        }

if __name__ == "__main__":
    # Test the Report agent
    agent = ReportAgent()
    
    # Mock data for testing
    mock_sec_data = {
        'status': 'success',
        'summary': {'total_filings': 5, 'buy_transactions': 3, 'sell_transactions': 2, 'unique_insider_count': 4},
        'insights': {'buy_sell_signal': 'bullish'},
        'raw_data': {'AAPL': {'filings_count': 3}, 'MSFT': {'filings_count': 2}}
    }
    
    mock_history_data = {
        'status': 'success',
        'summary': {'total_filings': 8, 'buy_transactions': 2, 'sell_transactions': 6},
        'comparison': {'trend_direction': 'decreasing', 'filing_change': {'percentage_change': -20}},
        'raw_data': {'AAPL': {'filings_count': 5}, 'MSFT': {'filings_count': 3}}
    }
    
    mock_sentiment_data = {
        'status': 'success',
        'raw_sentiment': {
            'overall_sentiment': {'score': 0.3, 'sentiment': 'positive'},
            'profiles_analyzed': 5
        },
        'market_assessment': {'risk_level': 'medium', 'market_mood': 'optimistic'},
        'recommendations': {'confidence_level': 'medium'}
    }
    
    results = agent.run(mock_sec_data, mock_history_data, mock_sentiment_data)
    
    print(f"Agent Status: {results.get('status')}")
    print(f"Investment Grade: {results.get('investment_grade', {}).get('grade', 'unknown')}")
    print(f"Report Path: {results.get('report_path', 'unknown')}")
    print(f"Key Findings: {len(results.get('key_findings', []))}")
