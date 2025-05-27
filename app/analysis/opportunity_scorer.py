"""
Business Opportunity Scoring and Ranking System

Analyzes companies and their identified opportunities to calculate composite scores
for prioritizing outreach and business development efforts.
"""

import math
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import logging

from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app.models.business_intelligence import (
    Company, BusinessOpportunity, CompanyTechStack, DecisionMaker, 
    WebsiteAudit, OutreachRecord
)

logger = logging.getLogger(__name__)


class OpportunityScorer:
    """
    Score and rank business opportunities for maximum ROI
    """
    
    def __init__(self, session: Session):
        self.session = session
        
        # Scoring weights (should sum to 1.0)
        self.scoring_weights = {
            'urgency': 0.25,        # How urgent is the problem
            'value': 0.20,          # Potential revenue/value
            'feasibility': 0.15,    # How easy to implement
            'competition': 0.10,    # How competitive the space
            'company_fit': 0.15,    # How well company fits our ideal profile
            'timing': 0.10,         # Is now a good time to approach
            'relationship': 0.05    # Existing relationship strength
        }
        
        # Company size value multipliers
        self.company_size_multipliers = {
            '1-10': 1.0,      # Small companies - good fit for solo consultant
            '11-50': 1.3,     # Sweet spot - have budget, need help
            '51-200': 1.1,    # Larger but may have internal resources
            '201-500': 0.8,   # May prefer established agencies
            '500+': 0.5       # Likely have internal teams
        }
        
        # Industry value multipliers
        self.industry_multipliers = {
            'software': 1.4,
            'web design': 1.3,
            'digital agency': 1.3,
            'marketing': 1.2,
            'consulting': 1.2,
            'real estate': 1.1,
            'law': 1.1,
            'accounting': 1.0,
            'healthcare': 0.9,
            'retail': 0.8
        }
    
    def score_opportunity(self, opportunity: BusinessOpportunity) -> float:
        """
        Calculate composite score for a single opportunity
        """
        try:
            company = self.session.query(Company).get(opportunity.company_id)
            if not company:
                return 0.0
            
            # Get component scores
            urgency_score = self._calculate_urgency_score(opportunity, company)
            value_score = self._calculate_value_score(opportunity, company)
            feasibility_score = self._calculate_feasibility_score(opportunity, company)
            competition_score = self._calculate_competition_score(opportunity, company)
            company_fit_score = self._calculate_company_fit_score(company)
            timing_score = self._calculate_timing_score(opportunity, company)
            relationship_score = self._calculate_relationship_score(company)
            
            # Calculate weighted composite score
            composite_score = (
                urgency_score * self.scoring_weights['urgency'] +
                value_score * self.scoring_weights['value'] +
                feasibility_score * self.scoring_weights['feasibility'] +
                competition_score * self.scoring_weights['competition'] +
                company_fit_score * self.scoring_weights['company_fit'] +
                timing_score * self.scoring_weights['timing'] +
                relationship_score * self.scoring_weights['relationship']
            )
            
            # Store component scores in opportunity
            opportunity.urgency_score = urgency_score
            opportunity.value_score = value_score
            opportunity.feasibility_score = feasibility_score
            opportunity.competition_score = competition_score
            opportunity.total_score = composite_score
            
            self.session.commit()
            
            logger.debug(f"Scored opportunity {opportunity.id}: {composite_score:.2f}")
            return composite_score
            
        except Exception as e:
            logger.error(f"Error scoring opportunity {opportunity.id}: {e}")
            return 0.0
    
    def _calculate_urgency_score(self, opportunity: BusinessOpportunity, company: Company) -> float:
        """
        Score how urgent this opportunity is (1-10 scale)
        """
        base_urgency = opportunity.urgency_score or 5.0
        
        # Increase urgency for security issues
        if opportunity.opportunity_type in ['security_upgrade', 'security_audit']:
            base_urgency = min(10.0, base_urgency + 2.0)
        
        # Increase urgency for broken/slow websites
        if opportunity.opportunity_type == 'performance_optimization':
            # Check latest website audit
            latest_audit = self.session.query(WebsiteAudit).filter(
                WebsiteAudit.company_id == company.id
            ).order_by(desc(WebsiteAudit.audit_date)).first()
            
            if latest_audit and latest_audit.page_load_time:
                if latest_audit.page_load_time > 5:
                    base_urgency = min(10.0, base_urgency + 2.0)
                elif latest_audit.page_load_time > 3:
                    base_urgency = min(10.0, base_urgency + 1.0)
        
        # Increase urgency for outdated technology
        if opportunity.opportunity_type == 'tech_modernization':
            # Check for severely outdated tech
            outdated_tech = self.session.query(CompanyTechStack).filter(
                CompanyTechStack.company_id == company.id,
                CompanyTechStack.is_outdated == True
            ).count()
            
            if outdated_tech > 2:
                base_urgency = min(10.0, base_urgency + 1.5)
        
        return min(10.0, max(1.0, base_urgency))
    
    def _calculate_value_score(self, opportunity: BusinessOpportunity, company: Company) -> float:
        """
        Score the potential value of this opportunity (1-10 scale)
        """
        estimated_value = opportunity.estimated_value or 1000
        
        # Base score from estimated value
        if estimated_value >= 10000:
            value_score = 10.0
        elif estimated_value >= 5000:
            value_score = 8.0
        elif estimated_value >= 2500:
            value_score = 6.0
        elif estimated_value >= 1000:
            value_score = 4.0
        else:
            value_score = 2.0
        
        # Apply company size multiplier
        size_multiplier = self.company_size_multipliers.get(company.size_estimate, 1.0)
        value_score *= size_multiplier
        
        # Apply industry multiplier
        industry_multiplier = self.industry_multipliers.get(company.industry, 1.0)
        value_score *= industry_multiplier
        
        # Bonus for recurring revenue potential
        if opportunity.opportunity_type in ['automation', 'integration', 'hosting_migration']:
            value_score *= 1.2  # These often lead to ongoing work
        
        return min(10.0, max(1.0, value_score))
    
    def _calculate_feasibility_score(self, opportunity: BusinessOpportunity, company: Company) -> float:
        """
        Score how feasible this opportunity is to execute (1-10 scale)
        """
        effort_hours = opportunity.effort_estimate_hours or 20
        
        # Base score from effort estimate
        if effort_hours <= 8:
            feasibility_score = 10.0  # Quick wins
        elif effort_hours <= 20:
            feasibility_score = 8.0
        elif effort_hours <= 40:
            feasibility_score = 6.0
        elif effort_hours <= 80:
            feasibility_score = 4.0
        else:
            feasibility_score = 2.0  # Large projects
        
        # Adjust based on opportunity type complexity
        complexity_adjustments = {
            'security_upgrade': 1.2,    # Often straightforward
            'performance_optimization': 1.1,
            'website_rebuild': 0.8,    # More complex
            'automation': 0.7,         # Requires custom development
            'integration': 0.6         # Most complex
        }
        
        adjustment = complexity_adjustments.get(opportunity.opportunity_type, 1.0)
        feasibility_score *= adjustment
        
        # Consider our expertise/portfolio fit
        if opportunity.opportunity_type in ['website_rebuild', 'performance_optimization']:
            feasibility_score *= 1.3  # Our strength
        
        return min(10.0, max(1.0, feasibility_score))
    
    def _calculate_competition_score(self, opportunity: BusinessOpportunity, company: Company) -> float:
        """
        Score based on competition level (higher = less competition) (1-10 scale)
        """
        # Base competition level by opportunity type
        competition_levels = {
            'website_rebuild': 3.0,      # Very competitive
            'seo_improvement': 2.0,      # Extremely competitive
            'automation': 8.0,           # Less competitive - specialized
            'integration': 8.5,          # Very specialized
            'security_audit': 7.0,       # Moderately competitive
            'performance_optimization': 6.0,
            'tech_modernization': 7.5,
            'mobile_optimization': 4.0
        }
        
        base_score = competition_levels.get(opportunity.opportunity_type, 5.0)
        
        # Adjust based on company location (local advantage)
        if company.city and 'grass valley' in company.city.lower():
            base_score += 2.0  # Local advantage
        elif company.state and company.state.lower() == 'ca':
            base_score += 1.0  # Regional advantage
        
        # Adjust based on company size (smaller = less competition)
        if company.size_estimate in ['1-10', '11-50']:
            base_score += 1.0  # Less competition for small companies
        
        return min(10.0, max(1.0, base_score))
    
    def _calculate_company_fit_score(self, company: Company) -> float:
        """
        Score how well this company fits our ideal client profile (1-10 scale)
        """
        fit_score = 5.0  # Base score
        
        # Industry fit
        preferred_industries = [
            'software', 'web design', 'digital agency', 'marketing', 
            'consulting', 'real estate', 'law'
        ]
        
        if company.industry in preferred_industries:
            fit_score += 2.0
        
        # Size fit (sweet spot for solo consultant)
        if company.size_estimate in ['11-50', '51-200']:
            fit_score += 2.0
        elif company.size_estimate == '1-10':
            fit_score += 1.0
        
        # Location fit
        if company.city and 'grass valley' in company.city.lower():
            fit_score += 2.0  # Local is ideal
        elif company.state and company.state.lower() == 'ca':
            fit_score += 1.0  # California is good
        
        # Digital presence fit (companies with websites are better fits)
        if company.website_url:
            fit_score += 1.0
        
        # Existing tech stack fit
        tech_count = self.session.query(CompanyTechStack).filter(
            CompanyTechStack.company_id == company.id
        ).count()
        
        if tech_count > 0:
            fit_score += 1.0  # Has existing tech infrastructure
        
        return min(10.0, max(1.0, fit_score))
    
    def _calculate_timing_score(self, opportunity: BusinessOpportunity, company: Company) -> float:
        """
        Score based on timing factors (1-10 scale)
        """
        timing_score = 5.0  # Base score
        
        # Check when company was last contacted
        last_contact = self.session.query(OutreachRecord).filter(
            OutreachRecord.company_id == company.id
        ).order_by(desc(OutreachRecord.sent_date)).first()
        
        if last_contact:
            days_since_contact = (datetime.now() - last_contact.sent_date).days
            
            if days_since_contact < 30:
                timing_score -= 3.0  # Too soon to contact again
            elif days_since_contact < 60:
                timing_score -= 1.0  # Recently contacted
            elif days_since_contact > 180:
                timing_score += 1.0  # Good time for follow-up
        else:
            timing_score += 2.0  # Never contacted - good time
        
        # Seasonal factors
        current_month = datetime.now().month
        if current_month in [1, 9]:  # January and September - budget planning time
            timing_score += 1.0
        elif current_month in [11, 12]:  # End of year - budget use-it-or-lose-it
            timing_score += 0.5
        
        # Urgency-based timing
        if opportunity.urgency_score >= 8.0:
            timing_score += 1.0  # Urgent issues are always good timing
        
        return min(10.0, max(1.0, timing_score))
    
    def _calculate_relationship_score(self, company: Company) -> float:
        """
        Score based on existing relationship strength (1-10 scale)
        """
        relationship_score = 1.0  # Base score (no relationship)
        
        # Check decision makers
        decision_makers = self.session.query(DecisionMaker).filter(
            DecisionMaker.company_id == company.id
        ).all()
        
        if decision_makers:
            relationship_score += 2.0  # Have contact info
            
            # Check engagement history
            for dm in decision_makers:
                if dm.response_rate > 0:
                    relationship_score += 2.0  # They've responded before
                    break
        
        # Check outreach history
        outreach_count = self.session.query(OutreachRecord).filter(
            OutreachRecord.company_id == company.id
        ).count()
        
        if outreach_count > 0:
            relationship_score += 1.0  # Have attempted contact
        
        # Check for positive responses
        positive_responses = self.session.query(OutreachRecord).filter(
            OutreachRecord.company_id == company.id,
            OutreachRecord.response_received == True,
            OutreachRecord.response_sentiment.in_(['positive', 'interested'])
        ).count()
        
        relationship_score += min(3.0, positive_responses * 1.5)
        
        return min(10.0, max(1.0, relationship_score))
    
    def score_all_opportunities(self) -> Dict[str, int]:
        """
        Score all opportunities in the database
        """
        try:
            opportunities = self.session.query(BusinessOpportunity).filter(
                BusinessOpportunity.status.in_(['identified', 'researched', 'validated'])
            ).all()
            
            scored_count = 0
            for opportunity in opportunities:
                score = self.score_opportunity(opportunity)
                if score > 0:
                    scored_count += 1
            
            # Update company opportunity scores
            self._update_company_opportunity_scores()
            
            logger.info(f"Scored {scored_count} opportunities")
            
            return {
                'total_opportunities': len(opportunities),
                'scored_opportunities': scored_count
            }
            
        except Exception as e:
            logger.error(f"Error scoring opportunities: {e}")
            return {'error': str(e)}
    
    def _update_company_opportunity_scores(self):
        """
        Update each company's overall opportunity score based on their best opportunities
        """
        try:
            companies = self.session.query(Company).all()
            
            for company in companies:
                # Get company's best opportunity scores
                best_opportunities = self.session.query(BusinessOpportunity).filter(
                    BusinessOpportunity.company_id == company.id
                ).order_by(desc(BusinessOpportunity.total_score)).limit(3).all()
                
                if best_opportunities:
                    # Use weighted average of top 3 opportunities
                    total_score = 0.0
                    weights = [0.5, 0.3, 0.2]  # Weight top opportunities more heavily
                    
                    for i, opp in enumerate(best_opportunities):
                        weight = weights[i] if i < len(weights) else 0.1
                        total_score += (opp.total_score or 0) * weight
                    
                    company.opportunity_score = total_score
                    
                    # Set priority level based on score
                    if total_score >= 8.0:
                        company.priority_level = 'urgent'
                    elif total_score >= 6.5:
                        company.priority_level = 'high'
                    elif total_score >= 5.0:
                        company.priority_level = 'medium'
                    else:
                        company.priority_level = 'low'
                else:
                    company.opportunity_score = 0.0
                    company.priority_level = 'low'
            
            self.session.commit()
            logger.info("Updated company opportunity scores")
            
        except Exception as e:
            logger.error(f"Error updating company scores: {e}")
            self.session.rollback()
    
    def get_top_opportunities(self, limit: int = 20) -> List[BusinessOpportunity]:
        """
        Get the highest-scoring opportunities for action
        """
        try:
            return self.session.query(BusinessOpportunity).filter(
                BusinessOpportunity.status.in_(['identified', 'researched', 'validated']),
                BusinessOpportunity.total_score.isnot(None)
            ).order_by(desc(BusinessOpportunity.total_score)).limit(limit).all()
            
        except Exception as e:
            logger.error(f"Error getting top opportunities: {e}")
            return []
    
    def get_top_companies(self, limit: int = 20) -> List[Company]:
        """
        Get the highest-scoring companies for outreach
        """
        try:
            return self.session.query(Company).filter(
                Company.opportunity_score > 0,
                Company.business_status == 'active'
            ).order_by(desc(Company.opportunity_score)).limit(limit).all()
            
        except Exception as e:
            logger.error(f"Error getting top companies: {e}")
            return []


# Convenience functions
def score_company_opportunities(company_id: int, session: Session) -> Dict:
    """Score all opportunities for a specific company"""
    scorer = OpportunityScorer(session)
    
    opportunities = session.query(BusinessOpportunity).filter(
        BusinessOpportunity.company_id == company_id
    ).all()
    
    results = []
    for opp in opportunities:
        score = scorer.score_opportunity(opp)
        results.append({
            'opportunity_id': opp.id,
            'title': opp.title,
            'type': opp.opportunity_type,
            'score': score
        })
    
    return {'company_id': company_id, 'opportunities': results}


def get_prioritized_opportunities(session: Session, limit: int = 50) -> List[Dict]:
    """Get prioritized list of opportunities for action"""
    scorer = OpportunityScorer(session)
    
    # Score all opportunities first
    scorer.score_all_opportunities()
    
    # Get top opportunities
    top_opportunities = scorer.get_top_opportunities(limit)
    
    results = []
    for opp in top_opportunities:
        company = session.query(Company).get(opp.company_id)
        
        results.append({
            'opportunity_id': opp.id,
            'company_name': company.name if company else 'Unknown',
            'company_domain': company.domain if company else None,
            'opportunity_title': opp.title,
            'opportunity_type': opp.opportunity_type,
            'estimated_value': opp.estimated_value,
            'effort_hours': opp.effort_estimate_hours,
            'total_score': opp.total_score,
            'urgency_score': opp.urgency_score,
            'value_score': opp.value_score,
            'feasibility_score': opp.feasibility_score,
            'status': opp.status
        })
    
    return results