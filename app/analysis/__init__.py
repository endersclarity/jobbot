"""
Analysis module for Business Intelligence Engine

Contains algorithms and tools for:
- Technology stack detection and website analysis
- Business opportunity scoring and ranking
- Company intelligence and opportunity identification
"""

from .tech_stack_detector import TechStackDetector, analyze_company_tech_stack
from .opportunity_scorer import OpportunityScorer, score_company_opportunities, get_prioritized_opportunities

__all__ = [
    'TechStackDetector',
    'analyze_company_tech_stack', 
    'OpportunityScorer',
    'score_company_opportunities',
    'get_prioritized_opportunities'
]