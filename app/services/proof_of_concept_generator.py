"""
Proof-of-Concept Automation Generator

Automatically generates working demonstrations, website improvements,
and proof-of-concept solutions for identified business opportunities.
"""

import asyncio
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from sqlalchemy.orm import Session

from app.models.business_intelligence import Company, BusinessOpportunity, CompanyTechStack
from app.services.intelligence_generator import BusinessIntelligenceReportGenerator


class ProofOfConceptGenerator:
    """
    Generate working demonstrations and proof-of-concept solutions
    """
    
    def __init__(self, db_session: Session):
        self.db = db_session
        
        # Output directories
        self.poc_dir = Path("generated_pocs")
        self.poc_dir.mkdir(exist_ok=True)
        
        self.demos_dir = self.poc_dir / "demos"
        self.demos_dir.mkdir(exist_ok=True)
        
        self.audits_dir = self.poc_dir / "audits"
        self.audits_dir.mkdir(exist_ok=True)
        
        self.proposals_dir = self.poc_dir / "proposals"
        self.proposals_dir.mkdir(exist_ok=True)
    
    async def generate_proof_of_concept(
        self, 
        company_id: int,
        opportunity_type: str = "website_improvement"
    ) -> Dict:
        """
        Generate comprehensive proof-of-concept for a company
        """
        
        # Get company data
        company = self.db.query(Company).filter(Company.id == company_id).first()
        if not company:
            raise ValueError(f"Company with ID {company_id} not found")
        
        poc_result = {
            'company': {
                'id': company.id,
                'name': company.name,
                'domain': company.domain,
                'website_url': company.website_url
            },
            'opportunity_type': opportunity_type,
            'generated_at': datetime.now().isoformat(),
            'deliverables': []
        }
        
        # Generate different types of proof-of-concepts based on opportunity
        if opportunity_type == "website_improvement":
            poc_result.update(await self._generate_website_improvement_poc(company))
        elif opportunity_type == "technology_audit":
            poc_result.update(await self._generate_technology_audit_poc(company))
        elif opportunity_type == "digital_marketing":
            poc_result.update(await self._generate_marketing_poc(company))
        elif opportunity_type == "security_assessment":
            poc_result.update(await self._generate_security_assessment_poc(company))
        else:
            # Default to comprehensive audit
            poc_result.update(await self._generate_comprehensive_poc(company))
        
        # Save POC summary
        poc_file = await self._save_poc_summary(company, poc_result)
        poc_result['summary_file'] = str(poc_file)
        
        return poc_result
    
    async def _generate_website_improvement_poc(self, company: Company) -> Dict:
        """Generate website improvement proof-of-concept"""
        
        # Analyze current website
        current_analysis = await self._analyze_current_website(company)
        
        # Create improved version mockup
        improved_mockup = await self._create_website_mockup(company, current_analysis)
        
        # Generate performance comparison
        performance_comparison = await self._generate_performance_comparison(
            current_analysis, improved_mockup
        )
        
        # Create implementation roadmap
        implementation_plan = self._create_implementation_roadmap(
            current_analysis, improved_mockup
        )
        
        return {
            'poc_type': 'website_improvement',
            'current_analysis': current_analysis,
            'improved_mockup': improved_mockup,
            'performance_comparison': performance_comparison,
            'implementation_plan': implementation_plan,
            'estimated_value': self._calculate_website_improvement_value(current_analysis),
            'deliverables': [
                'Website performance audit',
                'Improved design mockup',
                'Performance comparison report',
                'Implementation roadmap with timeline'
            ]
        }
    
    async def _generate_technology_audit_poc(self, company: Company) -> Dict:
        """Generate technology audit proof-of-concept"""
        
        # Get existing tech stack data
        tech_stacks = self.db.query(CompanyTechStack).filter(
            CompanyTechStack.company_id == company.id
        ).all()
        
        # Analyze technology gaps
        tech_analysis = await self._analyze_technology_stack(company, tech_stacks)
        
        # Generate modernization recommendations
        modernization_plan = self._create_modernization_plan(tech_analysis)
        
        # Create cost-benefit analysis
        cost_benefit = self._calculate_tech_modernization_roi(tech_analysis, modernization_plan)
        
        return {
            'poc_type': 'technology_audit',
            'current_tech_stack': tech_analysis,
            'modernization_recommendations': modernization_plan,
            'cost_benefit_analysis': cost_benefit,
            'implementation_phases': self._create_tech_implementation_phases(modernization_plan),
            'estimated_value': cost_benefit.get('total_value', 5000),
            'deliverables': [
                'Comprehensive technology audit',
                'Modernization roadmap',
                'Cost-benefit analysis',
                'Phased implementation plan'
            ]
        }
    
    async def _generate_marketing_poc(self, company: Company) -> Dict:
        """Generate digital marketing proof-of-concept"""
        
        # Analyze current digital presence
        digital_analysis = await self._analyze_digital_presence(company)
        
        # Create marketing strategy
        marketing_strategy = self._create_marketing_strategy(company, digital_analysis)
        
        # Generate sample campaigns
        sample_campaigns = await self._generate_sample_campaigns(company, marketing_strategy)
        
        # Calculate marketing ROI projections
        roi_projections = self._calculate_marketing_roi(marketing_strategy, sample_campaigns)
        
        return {
            'poc_type': 'digital_marketing',
            'current_digital_presence': digital_analysis,
            'marketing_strategy': marketing_strategy,
            'sample_campaigns': sample_campaigns,
            'roi_projections': roi_projections,
            'estimated_value': roi_projections.get('total_value', 8000),
            'deliverables': [
                'Digital presence audit',
                'Marketing strategy document',
                'Sample campaign materials',
                'ROI projections and KPIs'
            ]
        }
    
    async def _generate_security_assessment_poc(self, company: Company) -> Dict:
        """Generate security assessment proof-of-concept"""
        
        # Perform basic security scan
        security_scan = await self._perform_security_scan(company)
        
        # Identify vulnerabilities
        vulnerabilities = self._identify_security_vulnerabilities(security_scan)
        
        # Create security improvement plan
        security_plan = self._create_security_improvement_plan(vulnerabilities)
        
        # Calculate security ROI
        security_roi = self._calculate_security_roi(vulnerabilities, security_plan)
        
        return {
            'poc_type': 'security_assessment',
            'security_scan_results': security_scan,
            'identified_vulnerabilities': vulnerabilities,
            'security_improvement_plan': security_plan,
            'risk_mitigation_value': security_roi,
            'estimated_value': security_roi.get('total_value', 3000),
            'deliverables': [
                'Security vulnerability assessment',
                'Risk analysis report',
                'Security improvement roadmap',
                'Compliance recommendations'
            ]
        }
    
    async def _generate_comprehensive_poc(self, company: Company) -> Dict:
        """Generate comprehensive business transformation proof-of-concept"""
        
        # Combine multiple analyses
        website_poc = await self._generate_website_improvement_poc(company)
        tech_poc = await self._generate_technology_audit_poc(company)
        marketing_poc = await self._generate_marketing_poc(company)
        
        # Create integrated transformation plan
        transformation_plan = self._create_transformation_plan([
            website_poc, tech_poc, marketing_poc
        ])
        
        total_value = (
            website_poc.get('estimated_value', 0) +
            tech_poc.get('estimated_value', 0) +
            marketing_poc.get('estimated_value', 0)
        )
        
        return {
            'poc_type': 'comprehensive_transformation',
            'website_improvement': website_poc,
            'technology_modernization': tech_poc,
            'digital_marketing': marketing_poc,
            'integrated_transformation_plan': transformation_plan,
            'estimated_value': total_value,
            'deliverables': [
                'Complete business analysis',
                'Integrated transformation roadmap',
                'Multi-phase implementation plan',
                'Comprehensive ROI analysis'
            ]
        }
    
    async def _analyze_current_website(self, company: Company) -> Dict:
        """Analyze current website performance and structure"""
        
        if not company.website_url and not company.domain:
            return {
                'status': 'no_website',
                'issues': ['No website detected'],
                'recommendations': ['Create professional website']
            }
        
        website_url = company.website_url or f"https://{company.domain}"
        
        # Simulated analysis (in production, use actual tools)
        analysis = {
            'url': website_url,
            'performance_score': 65,  # Simulated
            'mobile_score': 58,
            'accessibility_score': 72,
            'seo_score': 61,
            'issues_found': [
                'Large image files slowing page load',
                'Missing mobile optimization',
                'Outdated design elements',
                'Limited SEO optimization',
                'No SSL certificate detected'
            ],
            'current_technologies': [
                {'name': 'WordPress', 'version': '5.8', 'status': 'outdated'},
                {'name': 'jQuery', 'version': '1.12', 'status': 'very_outdated'}
            ],
            'load_time': 4.2,  # seconds
            'mobile_friendly': False,
            'ssl_enabled': False
        }
        
        return analysis
    
    async def _create_website_mockup(self, company: Company, current_analysis: Dict) -> Dict:
        """Create improved website mockup design"""
        
        # Generate mockup specifications
        mockup = {
            'design_improvements': [
                'Modern, clean design with company branding',
                'Mobile-responsive layout',
                'Fast-loading optimized images',
                'Clear call-to-action buttons',
                'Professional typography and color scheme'
            ],
            'technical_improvements': [
                'SSL certificate installation',
                'Page speed optimization (target < 2 seconds)',
                'Mobile optimization',
                'SEO optimization',
                'Analytics tracking setup'
            ],
            'content_improvements': [
                'Clear value proposition on homepage',
                'Professional service descriptions',
                'Client testimonials section',
                'Contact forms with lead capture',
                'Local business optimization'
            ],
            'projected_scores': {
                'performance_score': 92,
                'mobile_score': 95,
                'accessibility_score': 88,
                'seo_score': 85
            },
            'estimated_load_time': 1.8,
            'mobile_friendly': True,
            'ssl_enabled': True
        }
        
        # Generate visual mockup file path
        mockup_file = self._create_mockup_file(company, mockup)
        mockup['mockup_file'] = str(mockup_file)
        
        return mockup
    
    async def _generate_performance_comparison(self, current: Dict, improved: Dict) -> Dict:
        """Generate before/after performance comparison"""
        
        comparison = {
            'performance_improvements': {
                'page_load_time': {
                    'before': current.get('load_time', 4.0),
                    'after': improved.get('estimated_load_time', 2.0),
                    'improvement': '50% faster'
                },
                'mobile_score': {
                    'before': current.get('mobile_score', 60),
                    'after': improved.get('projected_scores', {}).get('mobile_score', 90),
                    'improvement': '+30 points'
                },
                'seo_score': {
                    'before': current.get('seo_score', 65),
                    'after': improved.get('projected_scores', {}).get('seo_score', 85),
                    'improvement': '+20 points'
                }
            },
            'business_impact': {
                'estimated_traffic_increase': '40%',
                'conversion_rate_improvement': '25%',
                'lead_generation_increase': '60%',
                'search_ranking_improvement': '3-5 positions'
            },
            'competitive_advantages': [
                'Professional appearance builds trust',
                'Mobile optimization captures mobile traffic',
                'Fast loading improves user experience',
                'SEO optimization increases visibility'
            ]
        }
        
        return comparison
    
    def _create_implementation_roadmap(self, current: Dict, improved: Dict) -> Dict:
        """Create implementation roadmap for website improvements"""
        
        roadmap = {
            'total_timeline': '4-6 weeks',
            'phases': [
                {
                    'phase': 1,
                    'title': 'Foundation & Security',
                    'duration': '1 week',
                    'tasks': [
                        'SSL certificate installation',
                        'Backup current website',
                        'Set up development environment',
                        'Basic security hardening'
                    ]
                },
                {
                    'phase': 2,
                    'title': 'Design & Content',
                    'duration': '2 weeks',
                    'tasks': [
                        'Create new responsive design',
                        'Optimize and update content',
                        'Implement modern branding',
                        'Create mobile-friendly layout'
                    ]
                },
                {
                    'phase': 3,
                    'title': 'Performance & SEO',
                    'duration': '1 week',
                    'tasks': [
                        'Optimize images and media',
                        'Implement caching solutions',
                        'SEO optimization',
                        'Analytics setup'
                    ]
                },
                {
                    'phase': 4,
                    'title': 'Testing & Launch',
                    'duration': '1-2 weeks',
                    'tasks': [
                        'Cross-browser testing',
                        'Mobile device testing',
                        'Performance testing',
                        'Go-live and monitoring'
                    ]
                }
            ],
            'key_milestones': [
                'Week 1: Secure foundation established',
                'Week 3: New design implemented',
                'Week 4: Performance optimized',
                'Week 6: Site launched and monitored'
            ]
        }
        
        return roadmap
    
    def _calculate_website_improvement_value(self, current_analysis: Dict) -> float:
        """Calculate estimated value of website improvements"""
        
        base_value = 3000
        
        # Add value based on current issues
        issues = current_analysis.get('issues_found', [])
        value_per_issue = 500
        
        total_value = base_value + (len(issues) * value_per_issue)
        
        # Adjust based on current performance
        performance_score = current_analysis.get('performance_score', 70)
        if performance_score < 50:
            total_value *= 1.5  # Higher value for worse performance
        elif performance_score < 70:
            total_value *= 1.2
        
        return min(total_value, 15000)  # Cap at reasonable maximum
    
    async def _analyze_technology_stack(self, company: Company, tech_stacks: List) -> Dict:
        """Analyze company's technology stack"""
        
        if not tech_stacks:
            return {
                'status': 'no_data',
                'recommendations': ['Perform comprehensive technology audit']
            }
        
        # Aggregate all technologies
        all_technologies = []
        for ts in tech_stacks:
            if ts.technologies:
                all_technologies.extend(ts.technologies)
        
        # Categorize and analyze
        categories = {}
        outdated_count = 0
        security_issues = 0
        
        for tech in all_technologies:
            category = tech.get('category', 'other')
            if category not in categories:
                categories[category] = []
            categories[category].append(tech)
            
            if tech.get('outdated', False):
                outdated_count += 1
            if tech.get('security_risk', False):
                security_issues += 1
        
        return {
            'technology_categories': categories,
            'total_technologies': len(all_technologies),
            'outdated_technologies': outdated_count,
            'security_issues': security_issues,
            'modernization_priority': 'high' if outdated_count > 3 else 'medium' if outdated_count > 0 else 'low'
        }
    
    def _create_modernization_plan(self, tech_analysis: Dict) -> Dict:
        """Create technology modernization plan"""
        
        recommendations = []
        
        # Base recommendations
        recommendations.extend([
            {
                'category': 'Security',
                'recommendation': 'Implement comprehensive security monitoring',
                'priority': 'critical',
                'estimated_cost': '$1,000 - $2,000'
            },
            {
                'category': 'Performance',
                'recommendation': 'Optimize hosting and content delivery',
                'priority': 'high',
                'estimated_cost': '$500 - $1,000'
            },
            {
                'category': 'Analytics',
                'recommendation': 'Implement advanced analytics and tracking',
                'priority': 'medium',
                'estimated_cost': '$300 - $800'
            }
        ])
        
        # Add specific recommendations based on analysis
        if tech_analysis.get('outdated_technologies', 0) > 0:
            recommendations.append({
                'category': 'Modernization',
                'recommendation': 'Update outdated technologies and frameworks',
                'priority': 'high',
                'estimated_cost': '$2,000 - $5,000'
            })
        
        return {
            'recommendations': recommendations,
            'total_estimated_cost': '$3,800 - $8,800',
            'implementation_timeline': '3-6 weeks',
            'expected_benefits': [
                'Improved security and compliance',
                'Better performance and reliability',
                'Enhanced user experience',
                'Future-proofed technology stack'
            ]
        }
    
    def _calculate_tech_modernization_roi(self, tech_analysis: Dict, modernization_plan: Dict) -> Dict:
        """Calculate ROI for technology modernization"""
        
        # Estimate costs
        min_cost = 3800
        max_cost = 8800
        avg_cost = (min_cost + max_cost) / 2
        
        # Estimate benefits
        annual_benefits = {
            'reduced_security_risk': 2000,
            'improved_efficiency': 3000,
            'reduced_downtime': 1500,
            'better_user_experience': 2500
        }
        
        total_annual_benefit = sum(annual_benefits.values())
        roi_percentage = ((total_annual_benefit - avg_cost) / avg_cost) * 100
        
        return {
            'implementation_cost': avg_cost,
            'annual_benefits': annual_benefits,
            'total_annual_benefit': total_annual_benefit,
            'roi_percentage': roi_percentage,
            'payback_period_months': (avg_cost / total_annual_benefit) * 12,
            'total_value': total_annual_benefit
        }
    
    def _create_tech_implementation_phases(self, modernization_plan: Dict) -> List[Dict]:
        """Create phased implementation plan for tech modernization"""
        
        phases = [
            {
                'phase': 1,
                'title': 'Security & Backup',
                'duration': '1 week',
                'focus': 'Critical security implementations',
                'deliverables': [
                    'Security audit and hardening',
                    'Backup systems implementation',
                    'SSL and encryption setup'
                ]
            },
            {
                'phase': 2,
                'title': 'Performance Optimization',
                'duration': '1-2 weeks',
                'focus': 'Speed and reliability improvements',
                'deliverables': [
                    'Hosting optimization',
                    'Content delivery network setup',
                    'Database optimization'
                ]
            },
            {
                'phase': 3,
                'title': 'Analytics & Monitoring',
                'duration': '1 week',
                'focus': 'Data collection and insights',
                'deliverables': [
                    'Advanced analytics implementation',
                    'Performance monitoring setup',
                    'Reporting dashboard creation'
                ]
            }
        ]
        
        return phases
    
    async def _analyze_digital_presence(self, company: Company) -> Dict:
        """Analyze company's current digital marketing presence"""
        
        # Simulated analysis (in production, use real APIs)
        presence = {
            'website_traffic': {
                'monthly_visitors': 250,  # Estimated
                'bounce_rate': 68,
                'average_session_duration': '1:45',
                'conversion_rate': 2.1
            },
            'search_visibility': {
                'google_business_listing': True,
                'search_ranking_keywords': 3,
                'local_search_presence': 'limited',
                'review_count': 8,
                'average_rating': 4.2
            },
            'social_media': {
                'facebook_presence': 'basic',
                'linkedin_presence': 'none',
                'instagram_presence': 'none',
                'content_strategy': 'none'
            },
            'online_advertising': {
                'google_ads': False,
                'facebook_ads': False,
                'local_directory_listings': 'limited'
            }
        }
        
        return presence
    
    def _create_marketing_strategy(self, company: Company, digital_analysis: Dict) -> Dict:
        """Create comprehensive marketing strategy"""
        
        strategy = {
            'target_audience': {
                'primary': f"Local businesses needing {company.industry or 'professional'} services",
                'demographics': 'Business owners, decision makers, 25-55 years',
                'pain_points': [
                    'Need for reliable service providers',
                    'Limited time to research options',
                    'Desire for local, trusted partners'
                ]
            },
            'marketing_channels': [
                {
                    'channel': 'Search Engine Optimization',
                    'priority': 'high',
                    'focus': 'Local search optimization',
                    'expected_roi': '300%'
                },
                {
                    'channel': 'Google Business Profile',
                    'priority': 'high',
                    'focus': 'Local visibility and reviews',
                    'expected_roi': '250%'
                },
                {
                    'channel': 'Content Marketing',
                    'priority': 'medium',
                    'focus': 'Educational blog content',
                    'expected_roi': '200%'
                },
                {
                    'channel': 'Social Media',
                    'priority': 'medium',
                    'focus': 'LinkedIn and Facebook presence',
                    'expected_roi': '150%'
                }
            ],
            'content_strategy': {
                'blog_frequency': 'Weekly',
                'content_types': [
                    'Industry insights and tips',
                    'Case studies and success stories',
                    'Local market updates',
                    'Service explanations and FAQs'
                ],
                'seo_keywords': [
                    f"{company.industry} {company.city}",
                    f"best {company.industry} near me",
                    f"{company.industry} services"
                ]
            }
        }
        
        return strategy
    
    async def _generate_sample_campaigns(self, company: Company, marketing_strategy: Dict) -> List[Dict]:
        """Generate sample marketing campaigns"""
        
        campaigns = [
            {
                'campaign_name': 'Local SEO Domination',
                'type': 'SEO',
                'duration': '3 months',
                'budget': '$1,500/month',
                'objectives': [
                    'Rank #1 for primary local keywords',
                    'Increase organic traffic by 150%',
                    'Generate 20+ qualified leads/month'
                ],
                'tactics': [
                    'Local keyword optimization',
                    'Google Business Profile optimization',
                    'Local directory submissions',
                    'Review generation strategy'
                ],
                'expected_results': {
                    'traffic_increase': '150%',
                    'lead_increase': '200%',
                    'ranking_improvement': 'Top 3 positions'
                }
            },
            {
                'campaign_name': 'Social Proof Builder',
                'type': 'Reputation Management',
                'duration': '2 months',
                'budget': '$800/month',
                'objectives': [
                    'Increase online reviews to 25+',
                    'Improve average rating to 4.8+',
                    'Build social media presence'
                ],
                'tactics': [
                    'Automated review request system',
                    'Social media content calendar',
                    'Customer testimonial collection',
                    'Reputation monitoring setup'
                ],
                'expected_results': {
                    'review_count': '25+ reviews',
                    'rating_improvement': '4.8+ stars',
                    'social_engagement': '300% increase'
                }
            }
        ]
        
        return campaigns
    
    def _calculate_marketing_roi(self, marketing_strategy: Dict, sample_campaigns: List[Dict]) -> Dict:
        """Calculate marketing ROI projections"""
        
        # Calculate total campaign costs
        total_monthly_cost = 2300  # Sum of campaign budgets
        annual_cost = total_monthly_cost * 12
        
        # Estimate lead generation improvements
        current_leads = 5  # Estimated current monthly leads
        improved_leads = current_leads * 3  # 200% increase
        additional_leads = improved_leads - current_leads
        
        # Calculate revenue impact
        avg_client_value = 2000  # Estimated average client value
        conversion_rate = 0.2  # 20% lead-to-client conversion
        
        additional_clients = additional_leads * conversion_rate * 12  # Annual
        additional_revenue = additional_clients * avg_client_value
        
        roi_percentage = ((additional_revenue - annual_cost) / annual_cost) * 100
        
        return {
            'annual_marketing_investment': annual_cost,
            'additional_annual_revenue': additional_revenue,
            'roi_percentage': roi_percentage,
            'payback_period_months': (annual_cost / (additional_revenue / 12)),
            'total_value': additional_revenue,
            'lead_generation_improvement': {
                'current_monthly_leads': current_leads,
                'projected_monthly_leads': improved_leads,
                'improvement_percentage': 200
            }
        }
    
    async def _perform_security_scan(self, company: Company) -> Dict:
        """Perform basic security assessment"""
        
        if not company.website_url and not company.domain:
            return {
                'status': 'no_website',
                'message': 'No website to scan'
            }
        
        # Simulated security scan results
        scan_results = {
            'ssl_certificate': {
                'status': 'missing',
                'severity': 'high',
                'description': 'Website does not use HTTPS encryption'
            },
            'software_versions': {
                'status': 'outdated',
                'severity': 'medium',
                'description': 'Some software components are outdated'
            },
            'backup_system': {
                'status': 'unknown',
                'severity': 'medium',
                'description': 'No backup system detected'
            },
            'security_headers': {
                'status': 'missing',
                'severity': 'medium',
                'description': 'Important security headers not configured'
            },
            'access_controls': {
                'status': 'basic',
                'severity': 'low',
                'description': 'Basic access controls in place'
            }
        }
        
        return scan_results
    
    def _identify_security_vulnerabilities(self, security_scan: Dict) -> List[Dict]:
        """Identify security vulnerabilities from scan results"""
        
        vulnerabilities = []
        
        for check, result in security_scan.items():
            if result.get('status') in ['missing', 'outdated', 'weak']:
                vulnerability = {
                    'vulnerability': check,
                    'severity': result.get('severity', 'medium'),
                    'description': result.get('description', ''),
                    'risk_level': self._calculate_risk_level(result.get('severity', 'medium')),
                    'remediation_priority': self._get_remediation_priority(result.get('severity', 'medium'))
                }
                vulnerabilities.append(vulnerability)
        
        return vulnerabilities
    
    def _calculate_risk_level(self, severity: str) -> str:
        """Calculate risk level based on severity"""
        mapping = {
            'critical': 'very_high',
            'high': 'high',
            'medium': 'moderate',
            'low': 'low'
        }
        return mapping.get(severity, 'moderate')
    
    def _get_remediation_priority(self, severity: str) -> int:
        """Get remediation priority (1-5, 5 being highest)"""
        mapping = {
            'critical': 5,
            'high': 4,
            'medium': 3,
            'low': 2
        }
        return mapping.get(severity, 3)
    
    def _create_security_improvement_plan(self, vulnerabilities: List[Dict]) -> Dict:
        """Create security improvement plan"""
        
        # Sort by priority
        sorted_vulnerabilities = sorted(
            vulnerabilities, 
            key=lambda x: x.get('remediation_priority', 3), 
            reverse=True
        )
        
        plan = {
            'immediate_actions': [],
            'short_term_improvements': [],
            'long_term_enhancements': [],
            'estimated_timeline': '2-4 weeks',
            'implementation_phases': []
        }
        
        for vuln in sorted_vulnerabilities:
            if vuln['remediation_priority'] >= 4:
                plan['immediate_actions'].append({
                    'action': f"Fix {vuln['vulnerability']}",
                    'description': vuln['description'],
                    'timeline': '1 week'
                })
            elif vuln['remediation_priority'] == 3:
                plan['short_term_improvements'].append({
                    'action': f"Improve {vuln['vulnerability']}",
                    'description': vuln['description'],
                    'timeline': '2-3 weeks'
                })
            else:
                plan['long_term_enhancements'].append({
                    'action': f"Enhance {vuln['vulnerability']}",
                    'description': vuln['description'],
                    'timeline': '1-2 months'
                })
        
        return plan
    
    def _calculate_security_roi(self, vulnerabilities: List[Dict], security_plan: Dict) -> Dict:
        """Calculate ROI for security improvements"""
        
        # Estimate implementation costs
        base_cost = 1000
        cost_per_vulnerability = 500
        total_cost = base_cost + (len(vulnerabilities) * cost_per_vulnerability)
        
        # Estimate risk mitigation value
        risk_values = {
            'very_high': 10000,
            'high': 5000,
            'moderate': 2000,
            'low': 500
        }
        
        total_risk_mitigation = sum(
            risk_values.get(vuln.get('risk_level', 'moderate'), 2000)
            for vuln in vulnerabilities
        )
        
        # Additional benefits
        additional_benefits = {
            'customer_trust': 2000,
            'compliance_value': 1500,
            'business_continuity': 3000
        }
        
        total_value = total_risk_mitigation + sum(additional_benefits.values())
        roi_percentage = ((total_value - total_cost) / total_cost) * 100
        
        return {
            'implementation_cost': total_cost,
            'risk_mitigation_value': total_risk_mitigation,
            'additional_benefits': additional_benefits,
            'total_value': total_value,
            'roi_percentage': roi_percentage,
            'payback_period_months': 6  # Security benefits realized immediately
        }
    
    def _create_transformation_plan(self, poc_results: List[Dict]) -> Dict:
        """Create integrated transformation plan from multiple POCs"""
        
        total_value = sum(poc.get('estimated_value', 0) for poc in poc_results)
        
        # Create phased approach
        phases = [
            {
                'phase': 1,
                'title': 'Foundation & Security',
                'duration': '2-3 weeks',
                'focus': 'Critical infrastructure improvements',
                'components': ['website_improvement', 'security_assessment'],
                'investment': total_value * 0.3
            },
            {
                'phase': 2,
                'title': 'Technology Modernization',
                'duration': '3-4 weeks',
                'focus': 'Technology stack updates and optimization',
                'components': ['technology_audit'],
                'investment': total_value * 0.4
            },
            {
                'phase': 3,
                'title': 'Marketing & Growth',
                'duration': '4-6 weeks',
                'focus': 'Digital marketing and lead generation',
                'components': ['digital_marketing'],
                'investment': total_value * 0.3
            }
        ]
        
        return {
            'total_transformation_value': total_value,
            'implementation_phases': phases,
            'total_timeline': '9-13 weeks',
            'expected_roi': '250-400%',
            'key_benefits': [
                'Complete digital transformation',
                'Modernized technology infrastructure',
                'Enhanced security and compliance',
                'Improved marketing and lead generation',
                'Competitive advantage in local market'
            ]
        }
    
    def _create_mockup_file(self, company: Company, mockup: Dict) -> Path:
        """Create mockup file (placeholder for actual design)"""
        
        # Create mockup description file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        company_name_clean = "".join(c for c in company.name if c.isalnum() or c in (' ', '-', '_')).strip()
        company_name_clean = company_name_clean.replace(' ', '_')
        
        filename = f"website_mockup_{company_name_clean}_{timestamp}.json"
        file_path = self.demos_dir / filename
        
        with open(file_path, 'w') as f:
            json.dump(mockup, f, indent=2)
        
        return file_path
    
    async def _save_poc_summary(self, company: Company, poc_result: Dict) -> Path:
        """Save proof-of-concept summary to file"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        company_name_clean = "".join(c for c in company.name if c.isalnum() or c in (' ', '-', '_')).strip()
        company_name_clean = company_name_clean.replace(' ', '_')
        
        filename = f"poc_summary_{company_name_clean}_{timestamp}.json"
        file_path = self.poc_dir / filename
        
        with open(file_path, 'w') as f:
            json.dump(poc_result, f, indent=2, default=str)
        
        return file_path


async def generate_poc_for_company(company_id: int, opportunity_type: str = "comprehensive") -> Dict:
    """
    Convenience function to generate proof-of-concept for a company
    """
    from app.core.database import get_db
    
    db = next(get_db())
    try:
        generator = ProofOfConceptGenerator(db)
        poc = await generator.generate_proof_of_concept(company_id, opportunity_type)
        return poc
    finally:
        db.close()