"""
Automated Business Intelligence Report Generator

Generates comprehensive business intelligence reports with specific 
improvement recommendations, ROI calculations, and actionable insights.
"""

import json
from datetime import datetime
from typing import Dict, List
from sqlalchemy.orm import Session
from pathlib import Path

from app.models.business_intelligence import (
    Company, CompanyTechStack, DecisionMaker, BusinessOpportunity, WebsiteAudit
)
from app.analysis.tech_stack_detector import TechStackDetector
from app.analysis.opportunity_scorer import OpportunityScorer


class BusinessIntelligenceReportGenerator:
    """
    Generate comprehensive business intelligence reports for companies
    """
    
    def __init__(self, db_session: Session):
        self.db = db_session
        self.tech_detector = TechStackDetector()
        self.opportunity_scorer = OpportunityScorer()
        
        # Report templates directory
        self.templates_dir = Path("app/templates/reports")
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        
        # Output directory for generated reports
        self.reports_dir = Path("generated_reports")
        self.reports_dir.mkdir(exist_ok=True)
    
    async def generate_company_intelligence_report(
        self, 
        company_id: int,
        include_tech_analysis: bool = True,
        include_opportunity_analysis: bool = True,
        include_competitive_analysis: bool = True,
        include_outreach_recommendations: bool = True
    ) -> Dict:
        """
        Generate comprehensive intelligence report for a company
        """
        
        # Get company data
        company = self.db.query(Company).filter(Company.id == company_id).first()
        if not company:
            raise ValueError(f"Company with ID {company_id} not found")
        
        # Gather all intelligence data
        report_data = await self._gather_intelligence_data(company)
        
        # Generate report sections
        report = {
            'company_profile': self._generate_company_profile(company, report_data),
            'executive_summary': self._generate_executive_summary(company, report_data),
        }
        
        if include_tech_analysis:
            report['technology_analysis'] = await self._generate_technology_analysis(company, report_data)
        
        if include_opportunity_analysis:
            report['opportunity_analysis'] = await self._generate_opportunity_analysis(company, report_data)
        
        if include_competitive_analysis:
            report['competitive_analysis'] = self._generate_competitive_analysis(company, report_data)
        
        if include_outreach_recommendations:
            report['outreach_strategy'] = self._generate_outreach_strategy(company, report_data)
        
        # Add metadata
        report['report_metadata'] = {
            'generated_at': datetime.now().isoformat(),
            'company_id': company_id,
            'company_name': company.name,
            'report_version': '1.0',
            'data_sources': report_data.get('data_sources', [])
        }
        
        # Save report to file
        report_file = await self._save_report(company, report)
        report['report_metadata']['file_path'] = str(report_file)
        
        return report
    
    async def _gather_intelligence_data(self, company: Company) -> Dict:
        """Gather all available intelligence data for company"""
        
        data = {
            'data_sources': ['company_database'],
            'company': company,
            'tech_stacks': [],
            'decision_makers': [],
            'opportunities': [],
            'website_audits': []
        }
        
        # Get technology stacks
        tech_stacks = self.db.query(CompanyTechStack).filter(
            CompanyTechStack.company_id == company.id
        ).all()
        data['tech_stacks'] = tech_stacks
        if tech_stacks:
            data['data_sources'].append('technology_analysis')
        
        # Get decision makers
        decision_makers = self.db.query(DecisionMaker).filter(
            DecisionMaker.company_id == company.id
        ).all()
        data['decision_makers'] = decision_makers
        if decision_makers:
            data['data_sources'].append('decision_maker_research')
        
        # Get opportunities
        opportunities = self.db.query(BusinessOpportunity).filter(
            BusinessOpportunity.company_id == company.id
        ).all()
        data['opportunities'] = opportunities
        if opportunities:
            data['data_sources'].append('opportunity_analysis')
        
        # Get website audits
        website_audits = self.db.query(WebsiteAudit).filter(
            WebsiteAudit.company_id == company.id
        ).all()
        data['website_audits'] = website_audits
        if website_audits:
            data['data_sources'].append('website_audit')
        
        return data
    
    def _generate_company_profile(self, company: Company, data: Dict) -> Dict:
        """Generate company profile section"""
        
        # Calculate company size estimate
        company_size = "Unknown"
        if data['decision_makers']:
            dm_count = len(data['decision_makers'])
            if dm_count >= 10:
                company_size = "Large (50+ employees)"
            elif dm_count >= 5:
                company_size = "Medium (10-50 employees)"
            else:
                company_size = "Small (< 10 employees)"
        
        # Determine tech sophistication
        tech_sophistication = "Basic"
        if data['tech_stacks']:
            tech_count = sum(len(ts.technologies) for ts in data['tech_stacks'] if ts.technologies)
            if tech_count >= 10:
                tech_sophistication = "Advanced"
            elif tech_count >= 5:
                tech_sophistication = "Intermediate"
        
        return {
            'basic_info': {
                'name': company.name,
                'domain': company.domain,
                'website': company.website_url,
                'industry': company.industry,
                'location': f"{company.city}, {company.state}" if company.city else "Unknown",
                'phone': company.phone
            },
            'intelligence_summary': {
                'last_analyzed': company.last_scraped.isoformat() if company.last_scraped else None,
                'opportunity_score': company.opportunity_score,
                'estimated_size': company_size,
                'tech_sophistication': tech_sophistication,
                'business_status': company.business_status,
                'discovery_source': company.discovery_source
            },
            'contact_information': {
                'decision_makers_identified': len(data['decision_makers']),
                'key_contacts': [
                    {
                        'name': dm.name,
                        'title': dm.title,
                        'department': dm.department,
                        'influence_level': dm.influence_level,
                        'contact_priority': dm.contact_priority
                    }
                    for dm in data['decision_makers'][:3]  # Top 3 contacts
                ]
            }
        }
    
    def _generate_executive_summary(self, company: Company, data: Dict) -> Dict:
        """Generate executive summary section"""
        
        # Calculate summary metrics
        total_opportunities = len(data['opportunities'])
        high_value_opportunities = len([
            opp for opp in data['opportunities'] 
            if opp.estimated_value > 10000
        ])
        
        total_estimated_value = sum(opp.estimated_value for opp in data['opportunities'])
        
        # Determine engagement priority
        if company.opportunity_score >= 8.0:
            priority = "HIGH - Immediate engagement recommended"
        elif company.opportunity_score >= 6.0:
            priority = "MEDIUM - Strong potential, schedule discovery call"
        else:
            priority = "LOW - Monitor for future opportunities"
        
        # Key findings
        key_findings = []
        
        if data['tech_stacks']:
            outdated_tech = any(
                tech.get('outdated', False) 
                for ts in data['tech_stacks'] 
                for tech in (ts.technologies or [])
            )
            if outdated_tech:
                key_findings.append("Website uses outdated technology stack")
        
        if total_estimated_value > 15000:
            key_findings.append(f"High-value opportunity potential: ${total_estimated_value:,.0f}")
        
        if len(data['decision_makers']) >= 3:
            key_findings.append("Multiple decision maker contacts identified")
        
        if not key_findings:
            key_findings.append("Standard business profile with baseline opportunities")
        
        return {
            'opportunity_overview': {
                'total_opportunities': total_opportunities,
                'high_value_opportunities': high_value_opportunities,
                'estimated_total_value': total_estimated_value,
                'opportunity_score': company.opportunity_score,
                'engagement_priority': priority
            },
            'key_findings': key_findings,
            'recommended_approach': self._determine_recommended_approach(company, data),
            'next_actions': self._generate_next_actions(company, data)
        }
    
    async def _generate_technology_analysis(self, company: Company, data: Dict) -> Dict:
        """Generate technology analysis section"""
        
        if not data['tech_stacks']:
            return {
                'status': 'no_data',
                'message': 'No technology stack data available. Website analysis required.'
            }
        
        # Analyze all tech stacks
        all_technologies = []
        for tech_stack in data['tech_stacks']:
            if tech_stack.technologies:
                all_technologies.extend(tech_stack.technologies)
        
        # Categorize technologies
        categories = {
            'cms': [],
            'ecommerce': [],
            'analytics': [],
            'marketing': [],
            'security': [],
            'hosting': [],
            'other': []
        }
        
        for tech in all_technologies:
            category = tech.get('category', 'other').lower()
            if category in categories:
                categories[category].append(tech)
            else:
                categories['other'].append(tech)
        
        # Identify issues and opportunities
        issues = []
        opportunities = []
        
        # Check for outdated technologies
        outdated_tech = [tech for tech in all_technologies if tech.get('outdated', False)]
        if outdated_tech:
            issues.append({
                'type': 'outdated_technology',
                'severity': 'medium',
                'description': f"Using {len(outdated_tech)} outdated technologies",
                'technologies': [tech['name'] for tech in outdated_tech]
            })
            opportunities.append({
                'type': 'modernization',
                'value': 'high',
                'description': 'Technology stack modernization project',
                'estimated_effort': '2-4 weeks'
            })
        
        # Check for missing analytics
        if not categories['analytics']:
            issues.append({
                'type': 'missing_analytics',
                'severity': 'high',
                'description': 'No analytics tracking detected'
            })
            opportunities.append({
                'type': 'analytics_implementation',
                'value': 'medium',
                'description': 'Implement comprehensive analytics tracking',
                'estimated_effort': '1 week'
            })
        
        # Check for security issues
        security_tech = categories.get('security', [])
        if not security_tech:
            issues.append({
                'type': 'security_gaps',
                'severity': 'high',
                'description': 'Limited security technologies detected'
            })
            opportunities.append({
                'type': 'security_enhancement',
                'value': 'high',
                'description': 'Implement security monitoring and protection',
                'estimated_effort': '1-2 weeks'
            })
        
        return {
            'technology_inventory': categories,
            'technology_issues': issues,
            'improvement_opportunities': opportunities,
            'modernization_recommendations': self._generate_modernization_recommendations(categories),
            'estimated_improvement_value': self._calculate_tech_improvement_value(issues, opportunities)
        }
    
    async def _generate_opportunity_analysis(self, company: Company, data: Dict) -> Dict:
        """Generate opportunity analysis section"""
        
        opportunities = data['opportunities']
        
        if not opportunities:
            # Generate potential opportunities based on available data
            potential_opportunities = await self._identify_potential_opportunities(company, data)
            return {
                'existing_opportunities': [],
                'potential_opportunities': potential_opportunities,
                'opportunity_pipeline': self._analyze_opportunity_pipeline(potential_opportunities),
                'revenue_projections': self._calculate_revenue_projections(potential_opportunities)
            }
        
        # Analyze existing opportunities
        high_value = [opp for opp in opportunities if opp.estimated_value > 10000]
        medium_value = [opp for opp in opportunities if 5000 <= opp.estimated_value <= 10000]
        low_value = [opp for opp in opportunities if opp.estimated_value < 5000]
        
        return {
            'opportunity_breakdown': {
                'high_value': len(high_value),
                'medium_value': len(medium_value), 
                'low_value': len(low_value),
                'total_value': sum(opp.estimated_value for opp in opportunities)
            },
            'priority_opportunities': [
                {
                    'type': opp.opportunity_type,
                    'description': opp.description,
                    'estimated_value': opp.estimated_value,
                    'probability': opp.probability,
                    'urgency': opp.urgency_level,
                    'next_action': opp.next_action
                }
                for opp in sorted(opportunities, key=lambda x: x.estimated_value, reverse=True)[:3]
            ],
            'conversion_analysis': self._analyze_conversion_potential(opportunities),
            'timeline_projections': self._project_opportunity_timeline(opportunities)
        }
    
    def _generate_competitive_analysis(self, company: Company, data: Dict) -> Dict:
        """Generate competitive analysis section"""
        
        # This would typically involve analyzing competitors
        # For now, provide general market analysis
        
        industry = company.industry or "general business"
        
        return {
            'market_position': {
                'industry': industry,
                'local_market_size': 'Medium',
                'competition_level': 'Moderate',
                'market_trends': [
                    'Increasing demand for digital transformation',
                    'Growing focus on cybersecurity',
                    'Shift toward cloud-based solutions'
                ]
            },
            'competitive_advantages': self._identify_competitive_advantages(company, data),
            'market_opportunities': [
                'Digital marketing automation',
                'Website optimization and modernization',
                'Security enhancement services',
                'Performance optimization'
            ],
            'differentiation_strategy': self._suggest_differentiation_strategy(company, data)
        }
    
    def _generate_outreach_strategy(self, company: Company, data: Dict) -> Dict:
        """Generate outreach strategy section"""
        
        # Determine primary contact
        primary_contact = None
        if data['decision_makers']:
            # Find highest priority contact
            primary_contact = max(data['decision_makers'], key=lambda dm: dm.contact_priority)
        
        # Determine outreach approach
        approach = "email"
        if primary_contact and primary_contact.linkedin_url:
            approach = "linkedin"
        
        # Generate personalized messaging strategy
        messaging_strategy = self._create_messaging_strategy(company, data, primary_contact)
        
        return {
            'recommended_approach': {
                'primary_channel': approach,
                'primary_contact': {
                    'name': primary_contact.name if primary_contact else 'Unknown',
                    'title': primary_contact.title if primary_contact else 'Decision Maker',
                    'contact_method': approach
                } if primary_contact else None,
                'timing': 'Business hours (9 AM - 5 PM PST)',
                'follow_up_sequence': [
                    'Initial value-focused outreach',
                    'Follow-up with specific insights (3 days)',
                    'Phone call attempt (1 week)',
                    'Final value proposition (2 weeks)'
                ]
            },
            'messaging_strategy': messaging_strategy,
            'value_proposition': self._create_value_proposition(company, data),
            'success_metrics': {
                'response_rate_target': '15%',
                'meeting_conversion_target': '30%',
                'expected_timeline': '2-4 weeks to initial meeting'
            }
        }
    
    def _determine_recommended_approach(self, company: Company, data: Dict) -> str:
        """Determine recommended approach based on company analysis"""
        
        if company.opportunity_score >= 8.0:
            return "Direct outreach with specific value proposition and immediate meeting request"
        elif company.opportunity_score >= 6.0:
            return "Educational outreach with free assessment offer to build trust"
        else:
            return "Long-term nurturing with valuable content until opportunity emerges"
    
    def _generate_next_actions(self, company: Company, data: Dict) -> List[str]:
        """Generate specific next actions"""
        
        actions = []
        
        # Always include research verification
        actions.append("Verify company information and decision maker contacts")
        
        # Add technology-specific actions
        if data['tech_stacks'] and any(
            tech.get('outdated', False) 
            for ts in data['tech_stacks'] 
            for tech in (ts.technologies or [])
        ):
            actions.append("Prepare technology modernization proposal")
        
        # Add outreach actions
        if data['decision_makers']:
            actions.append(f"Initiate outreach to {data['decision_makers'][0].name}")
        else:
            actions.append("Research and identify key decision makers")
        
        # Add opportunity-specific actions
        if data['opportunities']:
            high_value_opp = max(data['opportunities'], key=lambda o: o.estimated_value)
            actions.append(f"Develop proposal for {high_value_opp.opportunity_type}")
        
        # Add demo/proof-of-concept action
        actions.append("Create proof-of-concept demonstration or audit")
        
        return actions
    
    async def _identify_potential_opportunities(self, company: Company, data: Dict) -> List[Dict]:
        """Identify potential opportunities when none exist"""
        
        opportunities = []
        
        # Website improvement opportunity (always applicable)
        opportunities.append({
            'type': 'website_audit_and_optimization',
            'description': 'Comprehensive website audit with performance and security improvements',
            'estimated_value': 3000,
            'probability': 0.7,
            'timeline': '2-3 weeks'
        })
        
        # Industry-specific opportunities
        if company.industry in ['law firm', 'accounting', 'consulting']:
            opportunities.append({
                'type': 'client_portal_development',
                'description': 'Secure client portal for document sharing and communication',
                'estimated_value': 8000,
                'probability': 0.5,
                'timeline': '4-6 weeks'
            })
        
        if company.industry in ['real estate', 'retail']:
            opportunities.append({
                'type': 'lead_generation_system',
                'description': 'Automated lead capture and nurturing system',
                'estimated_value': 5000,
                'probability': 0.6,
                'timeline': '3-4 weeks'
            })
        
        return opportunities
    
    def _create_messaging_strategy(self, company: Company, data: Dict, primary_contact) -> Dict:
        """Create personalized messaging strategy"""
        
        # Base message components
        company_specific_insight = f"researched {company.name}'s digital presence"
        
        if data['tech_stacks']:
            tech_insight = "identified opportunities for technology modernization"
        else:
            tech_insight = "would like to discuss digital strategy optimization"
        
        value_hook = f"help {company.name} increase operational efficiency and revenue"
        
        return {
            'opening_hook': f"I've {company_specific_insight} and {tech_insight}",
            'value_statement': f"I specialize in helping {company.industry or 'businesses'} like yours {value_hook}",
            'credibility_builder': "I've successfully implemented similar solutions for local businesses",
            'call_to_action': "Would you be open to a brief conversation about growth opportunities?",
            'personalization_notes': [
                f"Reference {company.name} specifically",
                f"Mention {company.industry or 'their industry'} expertise",
                f"Use {primary_contact.name if primary_contact else 'professional'} tone"
            ]
        }
    
    def _create_value_proposition(self, company: Company, data: Dict) -> Dict:
        """Create compelling value proposition"""
        
        primary_benefits = []
        supporting_benefits = []
        
        # Technology benefits
        if data['tech_stacks']:
            primary_benefits.append("Modernize technology stack for improved performance")
            supporting_benefits.append("Reduce security vulnerabilities")
        
        # Industry-specific benefits
        if company.industry:
            if 'law' in company.industry.lower():
                primary_benefits.append("Streamline client communication and case management")
            elif 'real estate' in company.industry.lower():
                primary_benefits.append("Automate lead generation and client nurturing")
            else:
                primary_benefits.append("Optimize digital operations for better ROI")
        
        # Default benefits
        if not primary_benefits:
            primary_benefits.append("Increase online visibility and lead generation")
        
        supporting_benefits.extend([
            "Professional expertise with proven track record",
            "Local market knowledge and understanding",
            "Comprehensive support and maintenance"
        ])
        
        return {
            'primary_benefits': primary_benefits,
            'supporting_benefits': supporting_benefits,
            'unique_differentiators': [
                "Specialized in small-to-medium business optimization",
                "Results-driven approach with measurable outcomes",
                "Ongoing partnership rather than one-time project"
            ],
            'risk_mitigation': [
                "Free initial consultation and assessment",
                "Transparent pricing with no hidden costs",
                "Satisfaction guarantee on all deliverables"
            ]
        }
    
    def _generate_modernization_recommendations(self, tech_categories: Dict) -> List[Dict]:
        """Generate technology modernization recommendations"""
        
        recommendations = []
        
        # CMS recommendations
        if not tech_categories.get('cms'):
            recommendations.append({
                'category': 'Content Management',
                'recommendation': 'Implement modern CMS (WordPress, Webflow, or custom)',
                'priority': 'high',
                'estimated_cost': '$2,000 - $5,000'
            })
        
        # Analytics recommendations
        if not tech_categories.get('analytics'):
            recommendations.append({
                'category': 'Analytics & Tracking',
                'recommendation': 'Install Google Analytics 4 and conversion tracking',
                'priority': 'high',
                'estimated_cost': '$500 - $1,000'
            })
        
        # Security recommendations
        if not tech_categories.get('security'):
            recommendations.append({
                'category': 'Security',
                'recommendation': 'Implement SSL, security monitoring, and backup systems',
                'priority': 'critical',
                'estimated_cost': '$1,000 - $2,000'
            })
        
        return recommendations
    
    def _calculate_tech_improvement_value(self, issues: List[Dict], opportunities: List[Dict]) -> Dict:
        """Calculate estimated value of technology improvements"""
        
        base_value = 3000  # Base website improvement value
        
        # Add value based on issues
        for issue in issues:
            if issue['severity'] == 'critical':
                base_value += 2000
            elif issue['severity'] == 'high':
                base_value += 1500
            elif issue['severity'] == 'medium':
                base_value += 1000
        
        # Add value based on opportunities
        opportunity_value = len(opportunities) * 1500
        
        total_value = base_value + opportunity_value
        
        return {
            'base_improvement_value': base_value,
            'opportunity_value': opportunity_value,
            'total_estimated_value': total_value,
            'roi_timeframe': '6-12 months',
            'value_drivers': [
                'Improved website performance and user experience',
                'Enhanced security and reduced risk',
                'Better analytics and decision-making capability',
                'Modernized technology stack for future growth'
            ]
        }
    
    def _analyze_opportunity_pipeline(self, opportunities: List[Dict]) -> Dict:
        """Analyze opportunity pipeline"""
        
        if not opportunities:
            return {'status': 'no_opportunities'}
        
        total_value = sum(opp.get('estimated_value', 0) for opp in opportunities)
        avg_probability = sum(opp.get('probability', 0.5) for opp in opportunities) / len(opportunities)
        
        return {
            'total_opportunities': len(opportunities),
            'total_potential_value': total_value,
            'weighted_value': total_value * avg_probability,
            'average_probability': avg_probability,
            'pipeline_strength': 'strong' if avg_probability > 0.6 else 'moderate' if avg_probability > 0.3 else 'developing'
        }
    
    def _calculate_revenue_projections(self, opportunities: List[Dict]) -> Dict:
        """Calculate revenue projections"""
        
        if not opportunities:
            return {'status': 'no_projections'}
        
        # Conservative, realistic, optimistic scenarios
        conservative = sum(opp.get('estimated_value', 0) * 0.3 for opp in opportunities)
        realistic = sum(opp.get('estimated_value', 0) * opp.get('probability', 0.5) for opp in opportunities)
        optimistic = sum(opp.get('estimated_value', 0) * 0.8 for opp in opportunities)
        
        return {
            'conservative_projection': conservative,
            'realistic_projection': realistic,
            'optimistic_projection': optimistic,
            'timeframe': '3-6 months',
            'confidence_level': 'medium'
        }
    
    def _analyze_conversion_potential(self, opportunities: List) -> Dict:
        """Analyze opportunity conversion potential"""
        
        high_probability = len([o for o in opportunities if o.probability > 0.7])
        medium_probability = len([o for o in opportunities if 0.4 <= o.probability <= 0.7])
        low_probability = len([o for o in opportunities if o.probability < 0.4])
        
        return {
            'high_probability_count': high_probability,
            'medium_probability_count': medium_probability,
            'low_probability_count': low_probability,
            'overall_conversion_likelihood': 'high' if high_probability > 0 else 'medium' if medium_probability > 0 else 'low'
        }
    
    def _project_opportunity_timeline(self, opportunities: List) -> Dict:
        """Project opportunity timeline"""
        
        immediate = len([o for o in opportunities if o.urgency_level == 'high'])
        short_term = len([o for o in opportunities if o.urgency_level == 'medium'])
        long_term = len([o for o in opportunities if o.urgency_level == 'low'])
        
        return {
            'immediate_opportunities': immediate,
            'short_term_opportunities': short_term,
            'long_term_opportunities': long_term,
            'recommended_focus': 'immediate' if immediate > 0 else 'short_term' if short_term > 0 else 'long_term'
        }
    
    def _identify_competitive_advantages(self, company: Company, data: Dict) -> List[str]:
        """Identify potential competitive advantages"""
        
        advantages = []
        
        if company.opportunity_score > 7.0:
            advantages.append("Strong digital foundation with growth potential")
        
        if data['decision_makers']:
            advantages.append("Accessible leadership team")
        
        if data['tech_stacks']:
            advantages.append("Existing technology investment")
        
        if company.industry:
            advantages.append(f"Established presence in {company.industry} market")
        
        if not advantages:
            advantages.append("Opportunity for significant digital transformation")
        
        return advantages
    
    def _suggest_differentiation_strategy(self, company: Company, data: Dict) -> List[str]:
        """Suggest differentiation strategy"""
        
        strategies = []
        
        # Technology-based differentiation
        if data['tech_stacks']:
            strategies.append("Leverage technology modernization for competitive edge")
        else:
            strategies.append("Pioneer digital transformation in local market")
        
        # Industry-specific strategies
        if company.industry:
            strategies.append(f"Become the digital leader in {company.industry} locally")
        
        # Service differentiation
        strategies.append("Focus on exceptional customer experience and service")
        strategies.append("Develop unique value propositions for target market")
        
        return strategies
    
    async def _save_report(self, company: Company, report: Dict) -> Path:
        """Save report to file"""
        
        # Create filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        company_name_clean = "".join(c for c in company.name if c.isalnum() or c in (' ', '-', '_')).strip()
        company_name_clean = company_name_clean.replace(' ', '_')
        
        filename = f"business_intelligence_report_{company_name_clean}_{timestamp}.json"
        file_path = self.reports_dir / filename
        
        # Save report
        with open(file_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        return file_path


async def generate_report_for_company(company_id: int) -> Dict:
    """
    Convenience function to generate report for a company
    """
    from app.core.database import get_db
    
    db = next(get_db())
    try:
        generator = BusinessIntelligenceReportGenerator(db)
        report = await generator.generate_company_intelligence_report(company_id)
        return report
    finally:
        db.close()