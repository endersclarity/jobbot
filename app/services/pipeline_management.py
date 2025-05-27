"""
Client Acquisition Pipeline Management System

Manages the complete sales pipeline from initial contact through 
contract signing, with CRM integration and automated workflow management.
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
from sqlalchemy.orm import Session

from app.models.business_intelligence import (
    Company, BusinessOpportunity, OutreachRecord
)


class ClientAcquisitionPipeline:
    """
    Manage complete client acquisition pipeline with CRM functionality
    """
    
    def __init__(self, db_session: Session):
        self.db = db_session
        
        # Pipeline stage definitions
        self.pipeline_stages = {
            'prospect': {
                'name': 'Prospect',
                'description': 'Initial company identified',
                'expected_duration_days': 7,
                'next_stage': 'contacted'
            },
            'contacted': {
                'name': 'Contacted',
                'description': 'Initial outreach sent',
                'expected_duration_days': 14,
                'next_stage': 'responded'
            },
            'responded': {
                'name': 'Responded',
                'description': 'Prospect has responded positively',
                'expected_duration_days': 7,
                'next_stage': 'meeting_scheduled'
            },
            'meeting_scheduled': {
                'name': 'Meeting Scheduled',
                'description': 'Discovery call or meeting booked',
                'expected_duration_days': 3,
                'next_stage': 'meeting_completed'
            },
            'meeting_completed': {
                'name': 'Meeting Completed',
                'description': 'Initial discovery call completed',
                'expected_duration_days': 7,
                'next_stage': 'proposal_sent'
            },
            'proposal_sent': {
                'name': 'Proposal Sent',
                'description': 'Formal proposal delivered',
                'expected_duration_days': 14,
                'next_stage': 'negotiation'
            },
            'negotiation': {
                'name': 'Negotiation',
                'description': 'Terms being negotiated',
                'expected_duration_days': 10,
                'next_stage': 'contract_sent'
            },
            'contract_sent': {
                'name': 'Contract Sent',
                'description': 'Contract sent for signature',
                'expected_duration_days': 7,
                'next_stage': 'won'
            },
            'won': {
                'name': 'Won',
                'description': 'Contract signed, client acquired',
                'expected_duration_days': 0,
                'next_stage': None
            },
            'lost': {
                'name': 'Lost',
                'description': 'Opportunity lost',
                'expected_duration_days': 0,
                'next_stage': None
            },
            'on_hold': {
                'name': 'On Hold',
                'description': 'Temporarily paused',
                'expected_duration_days': 30,
                'next_stage': 'contacted'
            }
        }
        
        # Pipeline tracking directory
        self.pipeline_dir = Path("pipeline_tracking")
        self.pipeline_dir.mkdir(exist_ok=True)
    
    async def analyze_pipeline_performance(self) -> Dict:
        """Analyze complete pipeline performance and health"""
        
        # Get all companies with opportunities
        companies_with_opps = self.db.query(Company).join(BusinessOpportunity).all()
        
        # Pipeline stage analysis
        stage_distribution = {}
        for stage_key in self.pipeline_stages.keys():
            count = len([c for c in companies_with_opps if c.pipeline_stage == stage_key])
            stage_distribution[stage_key] = count
        
        # Calculate conversion rates
        conversion_rates = self._calculate_conversion_rates(companies_with_opps)
        
        # Identify bottlenecks
        bottlenecks = self._identify_pipeline_bottlenecks(stage_distribution, companies_with_opps)
        
        # Calculate pipeline value
        pipeline_value = self._calculate_pipeline_value(companies_with_opps)
        
        # Generate pipeline health score
        health_score = self._calculate_pipeline_health_score(
            stage_distribution, conversion_rates, pipeline_value
        )
        
        # Revenue projections
        revenue_projections = self._calculate_revenue_projections(companies_with_opps)
        
        return {
            'pipeline_overview': {
                'total_companies': len(companies_with_opps),
                'stage_distribution': stage_distribution,
                'total_pipeline_value': pipeline_value['total_value'],
                'weighted_pipeline_value': pipeline_value['weighted_value'],
                'health_score': health_score
            },
            'conversion_metrics': conversion_rates,
            'bottleneck_analysis': bottlenecks,
            'revenue_projections': revenue_projections,
            'recommendations': self._generate_pipeline_recommendations(
                stage_distribution, conversion_rates, bottlenecks
            )
        }
    
    async def advance_pipeline_stage(
        self,
        company_id: int,
        new_stage: str,
        notes: Optional[str] = None
    ) -> Dict:
        """Advance company to next pipeline stage"""
        
        company = self.db.query(Company).filter(Company.id == company_id).first()
        if not company:
            raise ValueError(f"Company {company_id} not found")
        
        if new_stage not in self.pipeline_stages:
            raise ValueError(f"Invalid pipeline stage: {new_stage}")
        
        old_stage = company.pipeline_stage or 'prospect'
        
        # Update company stage
        company.pipeline_stage = new_stage
        company.pipeline_updated_at = datetime.now()
        
        # Add stage change notes
        if notes:
            company.notes = (company.notes or '') + f"\n{datetime.now().date()}: {notes}"
        
        self.db.commit()
        
        # Log stage change
        await self._log_stage_change(company_id, old_stage, new_stage, notes)
        
        # Trigger automated actions for new stage
        automated_actions = await self._trigger_stage_automation(company, new_stage)
        
        return {
            'company_id': company_id,
            'company_name': company.name,
            'old_stage': old_stage,
            'new_stage': new_stage,
            'stage_info': self.pipeline_stages[new_stage],
            'automated_actions': automated_actions,
            'next_expected_date': (
                datetime.now() + timedelta(days=self.pipeline_stages[new_stage]['expected_duration_days'])
            ).isoformat()
        }
    
    async def generate_sales_forecast(self, months_ahead: int = 3) -> Dict:
        """Generate sales forecast based on pipeline data"""
        
        companies_with_opps = self.db.query(Company).join(BusinessOpportunity).all()
        
        # Calculate historical conversion rates
        historical_rates = self._calculate_historical_conversion_rates()
        
        # Project closures by month
        monthly_projections = {}
        
        for month_offset in range(months_ahead):
            target_date = datetime.now() + timedelta(days=30 * (month_offset + 1))
            month_key = target_date.strftime("%Y-%m")
            
            # Conservative projection
            conservative = self._project_monthly_revenue(
                companies_with_opps, target_date, scenario='conservative'
            )
            
            # Realistic projection
            realistic = self._project_monthly_revenue(
                companies_with_opps, target_date, scenario='realistic'
            )
            
            # Optimistic projection
            optimistic = self._project_monthly_revenue(
                companies_with_opps, target_date, scenario='optimistic'
            )
            
            monthly_projections[month_key] = {
                'conservative': conservative,
                'realistic': realistic,
                'optimistic': optimistic,
                'target_date': target_date.isoformat()
            }
        
        # Calculate quarterly summary
        quarterly_summary = self._calculate_quarterly_summary(monthly_projections)
        
        return {
            'forecast_period': f"{months_ahead} months",
            'generated_at': datetime.now().isoformat(),
            'monthly_projections': monthly_projections,
            'quarterly_summary': quarterly_summary,
            'confidence_factors': {
                'historical_data_quality': 'medium',  # Would be calculated from actual data
                'pipeline_maturity': 'developing',
                'market_stability': 'stable'
            },
            'key_assumptions': [
                f"Historical conversion rates apply to current pipeline",
                f"Average sales cycle of {self._calculate_average_sales_cycle()} days",
                f"No major market disruptions",
                f"Current outreach effectiveness continues"
            ]
        }
    
    async def identify_hot_prospects(self, limit: int = 10) -> List[Dict]:
        """Identify hottest prospects for immediate focus"""
        
        # Get companies in active pipeline stages
        active_companies = self.db.query(Company).join(BusinessOpportunity).filter(
            Company.pipeline_stage.in_(['responded', 'meeting_scheduled', 'meeting_completed', 'proposal_sent', 'negotiation'])
        ).all()
        
        hot_prospects = []
        
        for company in active_companies:
            # Calculate hotness score
            hotness_score = self._calculate_prospect_hotness(company)
            
            # Get latest activity
            latest_outreach = self.db.query(OutreachRecord).filter(
                OutreachRecord.company_id == company.id
            ).order_by(OutreachRecord.created_at.desc()).first()
            
            # Get primary opportunity
            primary_opp = self.db.query(BusinessOpportunity).filter(
                BusinessOpportunity.company_id == company.id
            ).order_by(BusinessOpportunity.estimated_value.desc()).first()
            
            hot_prospects.append({
                'company': {
                    'id': company.id,
                    'name': company.name,
                    'domain': company.domain,
                    'pipeline_stage': company.pipeline_stage,
                    'opportunity_score': company.opportunity_score
                },
                'hotness_score': hotness_score,
                'opportunity_value': primary_opp.estimated_value if primary_opp else 0,
                'days_in_current_stage': (
                    datetime.now() - (company.pipeline_updated_at or company.last_scraped or datetime.now())
                ).days,
                'latest_activity': {
                    'type': latest_outreach.outreach_type if latest_outreach else 'none',
                    'date': latest_outreach.created_at.isoformat() if latest_outreach else None,
                    'response_received': latest_outreach.response_received if latest_outreach else False
                },
                'recommended_action': self._get_recommended_action(company, hotness_score),
                'urgency_level': self._get_urgency_level(hotness_score, company.pipeline_stage)
            })
        
        # Sort by hotness score and return top prospects
        hot_prospects.sort(key=lambda x: x['hotness_score'], reverse=True)
        return hot_prospects[:limit]
    
    async def generate_pipeline_report(self) -> Dict:
        """Generate comprehensive pipeline report"""
        
        # Get pipeline performance
        pipeline_performance = await self.analyze_pipeline_performance()
        
        # Get hot prospects
        hot_prospects = await self.identify_hot_prospects(5)
        
        # Get sales forecast
        sales_forecast = await self.generate_sales_forecast(3)
        
        # Get pipeline activities summary
        activities_summary = await self._get_pipeline_activities_summary()
        
        # Generate action items
        action_items = self._generate_pipeline_action_items(
            pipeline_performance, hot_prospects, activities_summary
        )
        
        report = {
            'report_generated': datetime.now().isoformat(),
            'executive_summary': {
                'total_pipeline_value': pipeline_performance['pipeline_overview']['total_pipeline_value'],
                'active_prospects': len(hot_prospects),
                'pipeline_health': pipeline_performance['pipeline_overview']['health_score'],
                'next_month_forecast': sales_forecast['monthly_projections'][
                    list(sales_forecast['monthly_projections'].keys())[0]
                ]['realistic']
            },
            'pipeline_performance': pipeline_performance,
            'hot_prospects': hot_prospects,
            'sales_forecast': sales_forecast,
            'recent_activities': activities_summary,
            'action_items': action_items,
            'recommendations': self._generate_strategic_recommendations(
                pipeline_performance, hot_prospects, sales_forecast
            )
        }
        
        # Save report
        report_file = await self._save_pipeline_report(report)
        report['report_file'] = str(report_file)
        
        return report
    
    def _calculate_conversion_rates(self, companies: List[Company]) -> Dict:
        """Calculate conversion rates between pipeline stages"""
        
        conversion_rates = {}
        
        stage_keys = list(self.pipeline_stages.keys())
        for i, stage in enumerate(stage_keys[:-2]):  # Exclude 'won', 'lost'
            current_stage_count = len([c for c in companies if c.pipeline_stage == stage])
            next_stage = stage_keys[i + 1] if i + 1 < len(stage_keys) else None
            
            if next_stage and current_stage_count > 0:
                next_stage_count = len([c for c in companies if c.pipeline_stage == next_stage])
                conversion_rate = (next_stage_count / (current_stage_count + next_stage_count)) * 100
                conversion_rates[f"{stage}_to_{next_stage}"] = round(conversion_rate, 1)
        
        # Overall prospect to won conversion
        total_prospects = len(companies)
        won_deals = len([c for c in companies if c.pipeline_stage == 'won'])
        if total_prospects > 0:
            conversion_rates['overall_win_rate'] = round((won_deals / total_prospects) * 100, 1)
        
        return conversion_rates
    
    def _identify_pipeline_bottlenecks(self, stage_distribution: Dict, companies: List[Company]) -> List[Dict]:
        """Identify bottlenecks in the pipeline"""
        
        bottlenecks = []
        
        # Find stages with high volume and low conversion
        for stage_key, count in stage_distribution.items():
            if count > 5:  # Significant volume threshold
                # Calculate average time in stage
                companies_in_stage = [c for c in companies if c.pipeline_stage == stage_key]
                if companies_in_stage:
                    avg_time_in_stage = sum(
                        (datetime.now() - (c.pipeline_updated_at or c.last_scraped or datetime.now())).days
                        for c in companies_in_stage
                    ) / len(companies_in_stage)
                    
                    expected_duration = self.pipeline_stages[stage_key]['expected_duration_days']
                    
                    if avg_time_in_stage > expected_duration * 1.5:  # 50% longer than expected
                        bottlenecks.append({
                            'stage': stage_key,
                            'stage_name': self.pipeline_stages[stage_key]['name'],
                            'companies_count': count,
                            'avg_time_in_stage': round(avg_time_in_stage, 1),
                            'expected_duration': expected_duration,
                            'severity': 'high' if avg_time_in_stage > expected_duration * 2 else 'medium',
                            'recommended_actions': self._get_bottleneck_recommendations(stage_key)
                        })
        
        return bottlenecks
    
    def _calculate_pipeline_value(self, companies: List[Company]) -> Dict:
        """Calculate total and weighted pipeline value"""
        
        total_value = 0
        weighted_value = 0
        
        stage_weights = {
            'prospect': 0.1,
            'contacted': 0.15,
            'responded': 0.3,
            'meeting_scheduled': 0.5,
            'meeting_completed': 0.6,
            'proposal_sent': 0.75,
            'negotiation': 0.85,
            'contract_sent': 0.95,
            'won': 1.0,
            'lost': 0.0,
            'on_hold': 0.1
        }
        
        for company in companies:
            opportunities = self.db.query(BusinessOpportunity).filter(
                BusinessOpportunity.company_id == company.id
            ).all()
            
            company_value = sum(opp.estimated_value for opp in opportunities)
            total_value += company_value
            
            stage_weight = stage_weights.get(company.pipeline_stage or 'prospect', 0.1)
            weighted_value += company_value * stage_weight
        
        return {
            'total_value': total_value,
            'weighted_value': weighted_value,
            'average_deal_size': total_value / len(companies) if companies else 0
        }
    
    def _calculate_pipeline_health_score(
        self,
        stage_distribution: Dict,
        conversion_rates: Dict,
        pipeline_value: Dict
    ) -> float:
        """Calculate overall pipeline health score (0-100)"""
        
        score = 0
        
        # Stage distribution health (0-30 points)
        # Healthy pipeline has prospects distributed across multiple stages
        active_stages = len([count for count in stage_distribution.values() if count > 0])
        stage_score = min(active_stages * 5, 30)
        score += stage_score
        
        # Conversion rate health (0-40 points)
        # Good overall win rate indicates healthy pipeline
        win_rate = conversion_rates.get('overall_win_rate', 0)
        conversion_score = min(win_rate * 2, 40)  # 20% win rate = 40 points
        score += conversion_score
        
        # Pipeline value health (0-30 points)
        # Higher weighted value indicates better pipeline quality
        if pipeline_value['total_value'] > 0:
            value_efficiency = (pipeline_value['weighted_value'] / pipeline_value['total_value']) * 100
            value_score = min(value_efficiency, 30)
            score += value_score
        
        return round(score, 1)
    
    def _calculate_revenue_projections(self, companies: List[Company]) -> Dict:
        """Calculate revenue projections based on pipeline"""
        
        projections = {
            'next_30_days': 0,
            'next_60_days': 0,
            'next_90_days': 0,
            'next_quarter': 0
        }
        
        # Simple projection based on stage probability and timeline
        stage_probabilities = {
            'contract_sent': 0.9,
            'negotiation': 0.7,
            'proposal_sent': 0.5,
            'meeting_completed': 0.3,
            'meeting_scheduled': 0.2,
            'responded': 0.15,
            'contacted': 0.1,
            'prospect': 0.05
        }
        
        stage_days_to_close = {
            'contract_sent': 7,
            'negotiation': 17,
            'proposal_sent': 31,
            'meeting_completed': 38,
            'meeting_scheduled': 41,
            'responded': 48,
            'contacted': 62,
            'prospect': 69
        }
        
        for company in companies:
            if company.pipeline_stage in stage_probabilities:
                opportunities = self.db.query(BusinessOpportunity).filter(
                    BusinessOpportunity.company_id == company.id
                ).all()
                
                company_value = sum(opp.estimated_value for opp in opportunities)
                probability = stage_probabilities[company.pipeline_stage]
                expected_close_days = stage_days_to_close[company.pipeline_stage]
                
                projected_value = company_value * probability
                
                if expected_close_days <= 30:
                    projections['next_30_days'] += projected_value
                if expected_close_days <= 60:
                    projections['next_60_days'] += projected_value
                if expected_close_days <= 90:
                    projections['next_90_days'] += projected_value
                    projections['next_quarter'] += projected_value
        
        return projections
    
    def _calculate_prospect_hotness(self, company: Company) -> float:
        """Calculate prospect hotness score (0-100)"""
        
        score = 0
        
        # Base opportunity score (0-40 points)
        score += min(company.opportunity_score * 4, 40)
        
        # Pipeline stage value (0-30 points)
        stage_values = {
            'negotiation': 30,
            'proposal_sent': 25,
            'meeting_completed': 20,
            'meeting_scheduled': 15,
            'responded': 10,
            'contacted': 5,
            'prospect': 2
        }
        score += stage_values.get(company.pipeline_stage or 'prospect', 0)
        
        # Recent activity (0-20 points)
        if company.pipeline_updated_at:
            days_since_update = (datetime.now() - company.pipeline_updated_at).days
            if days_since_update <= 3:
                score += 20
            elif days_since_update <= 7:
                score += 15
            elif days_since_update <= 14:
                score += 10
            elif days_since_update <= 30:
                score += 5
        
        # Response history (0-10 points)
        positive_responses = self.db.query(OutreachRecord).filter(
            OutreachRecord.company_id == company.id,
            OutreachRecord.response_sentiment == 'positive'
        ).count()
        
        score += min(positive_responses * 3, 10)
        
        return min(score, 100)
    
    def _get_recommended_action(self, company: Company, hotness_score: float) -> str:
        """Get recommended action for prospect"""
        
        stage = company.pipeline_stage or 'prospect'
        
        if hotness_score >= 80:
            if stage == 'negotiation':
                return "Close immediately - send final proposal"
            elif stage == 'proposal_sent':
                return "Follow up urgently - schedule decision call"
            else:
                return "Accelerate process - schedule immediate meeting"
        elif hotness_score >= 60:
            if stage == 'responded':
                return "Schedule discovery call within 48 hours"
            elif stage == 'meeting_scheduled':
                return "Prepare thoroughly for upcoming meeting"
            else:
                return "Maintain regular contact - provide value"
        else:
            return "Nurture relationship with valuable content"
    
    def _get_urgency_level(self, hotness_score: float, stage: str) -> str:
        """Determine urgency level for prospect"""
        
        if hotness_score >= 80 and stage in ['negotiation', 'proposal_sent', 'contract_sent']:
            return 'critical'
        elif hotness_score >= 60:
            return 'high'
        elif hotness_score >= 40:
            return 'medium'
        else:
            return 'low'
    
    async def _get_pipeline_activities_summary(self) -> Dict:
        """Get summary of recent pipeline activities"""
        
        # Get recent outreach activities
        recent_outreach = self.db.query(OutreachRecord).filter(
            OutreachRecord.created_at >= datetime.now() - timedelta(days=30)
        ).count()
        
        # Get recent responses
        recent_responses = self.db.query(OutreachRecord).filter(
            OutreachRecord.response_received == True,
            OutreachRecord.updated_at >= datetime.now() - timedelta(days=30)
        ).count()
        
        # Get recent stage changes
        companies_with_recent_updates = self.db.query(Company).filter(
            Company.pipeline_updated_at >= datetime.now() - timedelta(days=30)
        ).count()
        
        return {
            'last_30_days': {
                'outreach_sent': recent_outreach,
                'responses_received': recent_responses,
                'stage_progressions': companies_with_recent_updates,
                'response_rate': (recent_responses / recent_outreach * 100) if recent_outreach > 0 else 0
            }
        }
    
    def _generate_pipeline_action_items(
        self,
        pipeline_performance: Dict,
        hot_prospects: List[Dict],
        activities_summary: Dict
    ) -> List[Dict]:
        """Generate specific action items for pipeline management"""
        
        action_items = []
        
        # High priority prospects
        critical_prospects = [p for p in hot_prospects if p['urgency_level'] == 'critical']
        if critical_prospects:
            action_items.append({
                'priority': 'high',
                'category': 'sales',
                'action': f"Immediate follow-up required for {len(critical_prospects)} critical prospects",
                'details': [p['company']['name'] for p in critical_prospects],
                'due_date': (datetime.now() + timedelta(days=1)).isoformat()
            })
        
        # Bottleneck resolution
        bottlenecks = pipeline_performance.get('bottleneck_analysis', [])
        for bottleneck in bottlenecks:
            if bottleneck['severity'] == 'high':
                action_items.append({
                    'priority': 'medium',
                    'category': 'process',
                    'action': f"Resolve bottleneck in {bottleneck['stage_name']} stage",
                    'details': bottleneck['recommended_actions'],
                    'due_date': (datetime.now() + timedelta(days=7)).isoformat()
                })
        
        # Low activity warning
        if activities_summary['last_30_days']['outreach_sent'] < 10:
            action_items.append({
                'priority': 'medium',
                'category': 'outreach',
                'action': "Increase outreach activity - below target volume",
                'details': ["Launch new outreach campaign", "Identify additional prospects"],
                'due_date': (datetime.now() + timedelta(days=3)).isoformat()
            })
        
        return action_items
    
    def _generate_strategic_recommendations(
        self,
        pipeline_performance: Dict,
        hot_prospects: List[Dict],
        sales_forecast: Dict
    ) -> List[str]:
        """Generate strategic recommendations for pipeline improvement"""
        
        recommendations = []
        
        # Pipeline health recommendations
        health_score = pipeline_performance['pipeline_overview']['health_score']
        if health_score < 50:
            recommendations.append("Focus on improving pipeline quality and conversion rates")
        elif health_score < 70:
            recommendations.append("Optimize pipeline stages with lowest conversion rates")
        
        # Volume recommendations
        total_companies = pipeline_performance['pipeline_overview']['total_companies']
        if total_companies < 20:
            recommendations.append("Increase prospecting activity to build pipeline volume")
        
        # Hot prospects recommendations
        if len(hot_prospects) < 5:
            recommendations.append("Identify and nurture more high-potential prospects")
        
        # Revenue forecast recommendations
        next_month_forecast = list(sales_forecast['monthly_projections'].values())[0]['realistic']
        if next_month_forecast < 10000:
            recommendations.append("Accelerate sales cycles to increase short-term revenue")
        
        return recommendations
    
    async def _trigger_stage_automation(self, company: Company, new_stage: str) -> List[str]:
        """Trigger automated actions when stage changes"""
        
        automated_actions = []
        
        # Stage-specific automations
        if new_stage == 'responded':
            automated_actions.append("Schedule discovery call follow-up email")
            automated_actions.append("Add to high-priority prospect list")
        
        elif new_stage == 'meeting_scheduled':
            automated_actions.append("Send meeting confirmation and preparation materials")
            automated_actions.append("Create calendar reminder for post-meeting follow-up")
        
        elif new_stage == 'meeting_completed':
            automated_actions.append("Schedule proposal preparation task")
            automated_actions.append("Send thank you and next steps email")
        
        elif new_stage == 'proposal_sent':
            automated_actions.append("Schedule proposal follow-up sequence")
            automated_actions.append("Set decision timeline reminder")
        
        elif new_stage == 'won':
            automated_actions.append("Initiate client onboarding process")
            automated_actions.append("Send contract and project kickoff materials")
        
        return automated_actions
    
    async def _log_stage_change(
        self,
        company_id: int,
        old_stage: str,
        new_stage: str,
        notes: Optional[str]
    ) -> None:
        """Log pipeline stage changes for tracking"""
        
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'company_id': company_id,
            'old_stage': old_stage,
            'new_stage': new_stage,
            'notes': notes
        }
        
        # Save to tracking file
        log_file = self.pipeline_dir / "stage_changes.jsonl"
        with open(log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
    
    async def _save_pipeline_report(self, report: Dict) -> Path:
        """Save pipeline report to file"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"pipeline_report_{timestamp}.json"
        file_path = self.pipeline_dir / filename
        
        with open(file_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        return file_path
    
    def _get_bottleneck_recommendations(self, stage_key: str) -> List[str]:
        """Get specific recommendations for stage bottlenecks"""
        
        recommendations = {
            'contacted': [
                "Improve email subject lines and open rates",
                "Try alternative contact methods (LinkedIn, phone)",
                "Personalize outreach messaging further"
            ],
            'responded': [
                "Reduce time between response and meeting scheduling",
                "Streamline calendar booking process",
                "Improve response qualification criteria"
            ],
            'meeting_scheduled': [
                "Reduce no-show rates with better preparation",
                "Send meeting reminders and preparation materials",
                "Optimize meeting scheduling process"
            ],
            'proposal_sent': [
                "Follow up more consistently on proposals",
                "Improve proposal quality and personalization",
                "Schedule proposal review calls"
            ],
            'negotiation': [
                "Streamline contract negotiation process",
                "Address common objections proactively",
                "Set clear decision timelines"
            ]
        }
        
        return recommendations.get(stage_key, ["Analyze stage-specific bottlenecks", "Improve process efficiency"])
    
    def _calculate_historical_conversion_rates(self) -> Dict:
        """Calculate historical conversion rates (mock data for now)"""
        
        # In production, this would analyze historical data
        return {
            'prospect_to_contacted': 85,
            'contacted_to_responded': 25,
            'responded_to_meeting': 60,
            'meeting_to_proposal': 70,
            'proposal_to_won': 40,
            'overall_win_rate': 12
        }
    
    def _project_monthly_revenue(
        self,
        companies: List[Company],
        target_date: datetime,
        scenario: str
    ) -> float:
        """Project revenue for specific month and scenario"""
        
        scenario_multipliers = {
            'conservative': 0.7,
            'realistic': 1.0,
            'optimistic': 1.4
        }
        
        multiplier = scenario_multipliers.get(scenario, 1.0)
        
        # Simple projection based on pipeline value and time
        base_projection = self._calculate_pipeline_value(companies)['weighted_value']
        monthly_projection = (base_projection / 3) * multiplier  # Spread over 3 months
        
        return round(monthly_projection, 2)
    
    def _calculate_quarterly_summary(self, monthly_projections: Dict) -> Dict:
        """Calculate quarterly summary from monthly projections"""
        
        quarterly_totals = {
            'conservative': 0,
            'realistic': 0,
            'optimistic': 0
        }
        
        for month_data in monthly_projections.values():
            for scenario in quarterly_totals.keys():
                quarterly_totals[scenario] += month_data[scenario]
        
        return quarterly_totals
    
    def _calculate_average_sales_cycle(self) -> int:
        """Calculate average sales cycle length in days"""
        
        # Mock calculation - in production, analyze historical data
        return 45  # 45 days average


# Convenience functions
async def get_pipeline_report() -> Dict:
    """Get comprehensive pipeline report"""
    from app.core.database import get_db
    
    db = next(get_db())
    try:
        pipeline = ClientAcquisitionPipeline(db)
        report = await pipeline.generate_pipeline_report()
        return report
    finally:
        db.close()


async def advance_company_stage(company_id: int, new_stage: str, notes: str = None) -> Dict:
    """Advance company to next pipeline stage"""
    from app.core.database import get_db
    
    db = next(get_db())
    try:
        pipeline = ClientAcquisitionPipeline(db)
        result = await pipeline.advance_pipeline_stage(company_id, new_stage, notes)
        return result
    finally:
        db.close()