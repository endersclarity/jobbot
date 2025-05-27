"""
Performance Analytics & KPI Tracking System

Comprehensive tracking and analysis of business development KPIs,
ROI metrics, and performance optimization for live market operations.
"""

import asyncio
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, text

from app.models.business_intelligence import (
    Company, DecisionMaker, BusinessOpportunity, OutreachRecord
)


class PerformanceAnalytics:
    """
    Track and analyze business development performance metrics
    """
    
    def __init__(self, db_session: Session):
        self.db = db_session
        
        # KPI definitions
        self.kpis = {
            'discovery': {
                'companies_discovered_monthly': {'target': 100, 'unit': 'companies'},
                'discovery_quality_score': {'target': 85, 'unit': 'percentage'},
                'opportunity_identification_rate': {'target': 60, 'unit': 'percentage'}
            },
            'outreach': {
                'outreach_volume_monthly': {'target': 50, 'unit': 'emails'},
                'email_open_rate': {'target': 30, 'unit': 'percentage'},
                'response_rate': {'target': 15, 'unit': 'percentage'},
                'meeting_conversion_rate': {'target': 25, 'unit': 'percentage'}
            },
            'pipeline': {
                'pipeline_velocity': {'target': 45, 'unit': 'days'},
                'conversion_rate_overall': {'target': 12, 'unit': 'percentage'},
                'average_deal_size': {'target': 8000, 'unit': 'dollars'},
                'pipeline_value': {'target': 250000, 'unit': 'dollars'}
            },
            'revenue': {
                'monthly_revenue': {'target': 25000, 'unit': 'dollars'},
                'quarterly_growth': {'target': 20, 'unit': 'percentage'},
                'customer_acquisition_cost': {'target': 500, 'unit': 'dollars'},
                'lifetime_value': {'target': 15000, 'unit': 'dollars'}
            }
        }
        
        # Analytics directories
        self.analytics_dir = Path("performance_analytics")
        self.analytics_dir.mkdir(exist_ok=True)
        
        self.reports_dir = self.analytics_dir / "reports"
        self.reports_dir.mkdir(exist_ok=True)
        
        self.dashboards_dir = self.analytics_dir / "dashboards"
        self.dashboards_dir.mkdir(exist_ok=True)
    
    async def generate_comprehensive_analytics_report(
        self,
        period_days: int = 30
    ) -> Dict:
        """Generate comprehensive analytics report for specified period"""
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=period_days)
        
        # Gather all metrics
        discovery_metrics = await self._analyze_discovery_performance(start_date, end_date)
        outreach_metrics = await self._analyze_outreach_performance(start_date, end_date)
        pipeline_metrics = await self._analyze_pipeline_performance(start_date, end_date)
        revenue_metrics = await self._analyze_revenue_performance(start_date, end_date)
        
        # Calculate KPI scores
        kpi_scores = self._calculate_kpi_scores(
            discovery_metrics, outreach_metrics, pipeline_metrics, revenue_metrics
        )
        
        # Generate insights and recommendations
        insights = self._generate_performance_insights(
            discovery_metrics, outreach_metrics, pipeline_metrics, revenue_metrics
        )
        
        # Create optimization recommendations
        optimizations = self._generate_optimization_recommendations(kpi_scores, insights)
        
        # Calculate ROI and efficiency metrics
        roi_analysis = self._calculate_roi_analysis(
            outreach_metrics, pipeline_metrics, revenue_metrics
        )
        
        report = {
            'report_metadata': {
                'generated_at': datetime.now().isoformat(),
                'period_start': start_date.isoformat(),
                'period_end': end_date.isoformat(),
                'period_days': period_days
            },
            'executive_summary': self._create_executive_summary(
                kpi_scores, revenue_metrics, pipeline_metrics
            ),
            'kpi_performance': {
                'discovery': discovery_metrics,
                'outreach': outreach_metrics,
                'pipeline': pipeline_metrics,
                'revenue': revenue_metrics
            },
            'kpi_scores': kpi_scores,
            'performance_insights': insights,
            'optimization_recommendations': optimizations,
            'roi_analysis': roi_analysis,
            'trend_analysis': await self._analyze_performance_trends(period_days),
            'competitive_benchmarks': self._get_competitive_benchmarks()
        }
        
        # Save report
        report_file = await self._save_analytics_report(report)
        report['report_file'] = str(report_file)
        
        return report
    
    async def track_real_time_kpis(self) -> Dict:
        """Track real-time KPI dashboard data"""
        
        # Current metrics (last 24 hours)
        current_metrics = await self._get_current_metrics()
        
        # Weekly trends
        weekly_trends = await self._get_weekly_trends()
        
        # Performance alerts
        alerts = await self._check_performance_alerts()
        
        # Goal progress
        goal_progress = self._calculate_goal_progress()
        
        return {
            'last_updated': datetime.now().isoformat(),
            'current_metrics': current_metrics,
            'weekly_trends': weekly_trends,
            'performance_alerts': alerts,
            'goal_progress': goal_progress,
            'quick_stats': {
                'active_campaigns': await self._count_active_campaigns(),
                'hot_prospects': await self._count_hot_prospects(),
                'this_month_revenue': await self._get_month_revenue(),
                'pipeline_health_score': await self._get_pipeline_health_score()
            }
        }
    
    async def _analyze_discovery_performance(self, start_date: datetime, end_date: datetime) -> Dict:
        """Analyze company discovery performance metrics"""
        
        # Companies discovered in period
        companies_discovered = self.db.query(Company).filter(
            Company.last_scraped >= start_date,
            Company.last_scraped <= end_date
        ).count()
        
        # Total companies in database
        total_companies = self.db.query(Company).count()
        
        # Companies with opportunities
        companies_with_opps = self.db.query(Company).filter(
            Company.opportunity_score > 0,
            Company.last_scraped >= start_date
        ).count()
        
        # Opportunity identification rate
        opp_identification_rate = (companies_with_opps / companies_discovered * 100) if companies_discovered > 0 else 0
        
        # Average opportunity score
        avg_opp_score = self.db.query(func.avg(Company.opportunity_score)).filter(
            Company.last_scraped >= start_date,
            Company.opportunity_score > 0
        ).scalar() or 0
        
        # Discovery source analysis
        discovery_sources = self.db.query(
            Company.discovery_source,
            func.count(Company.id)
        ).filter(
            Company.last_scraped >= start_date
        ).group_by(Company.discovery_source).all()
        
        source_distribution = {source: count for source, count in discovery_sources}
        
        return {
            'companies_discovered': companies_discovered,
            'total_companies_database': total_companies,
            'companies_with_opportunities': companies_with_opps,
            'opportunity_identification_rate': round(opp_identification_rate, 1),
            'average_opportunity_score': round(avg_opp_score, 1),
            'discovery_source_distribution': source_distribution,
            'discovery_quality_score': min(avg_opp_score * 10, 100),  # Convert to 0-100 scale
            'daily_discovery_rate': companies_discovered / max((end_date - start_date).days, 1)
        }
    
    async def _analyze_outreach_performance(self, start_date: datetime, end_date: datetime) -> Dict:
        """Analyze outreach campaign performance metrics"""
        
        # Total outreach sent
        outreach_sent = self.db.query(OutreachRecord).filter(
            OutreachRecord.created_at >= start_date,
            OutreachRecord.created_at <= end_date,
            OutreachRecord.status == 'sent'
        ).count()
        
        # Responses received
        responses_received = self.db.query(OutreachRecord).filter(
            OutreachRecord.updated_at >= start_date,
            OutreachRecord.response_received == True
        ).count()
        
        # Positive responses
        positive_responses = self.db.query(OutreachRecord).filter(
            OutreachRecord.updated_at >= start_date,
            OutreachRecord.response_sentiment == 'positive'
        ).count()
        
        # Meetings scheduled
        meetings_scheduled = self.db.query(OutreachRecord).filter(
            OutreachRecord.updated_at >= start_date,
            OutreachRecord.meeting_scheduled == True
        ).count()
        
        # Calculate rates
        response_rate = (responses_received / outreach_sent * 100) if outreach_sent > 0 else 0
        positive_response_rate = (positive_responses / outreach_sent * 100) if outreach_sent > 0 else 0
        meeting_conversion_rate = (meetings_scheduled / responses_received * 100) if responses_received > 0 else 0
        
        # Outreach type analysis
        outreach_types = self.db.query(
            OutreachRecord.outreach_type,
            func.count(OutreachRecord.id)
        ).filter(
            OutreachRecord.created_at >= start_date
        ).group_by(OutreachRecord.outreach_type).all()
        
        type_distribution = {otype: count for otype, count in outreach_types}
        
        return {
            'outreach_volume': outreach_sent,
            'responses_received': responses_received,
            'positive_responses': positive_responses,
            'meetings_scheduled': meetings_scheduled,
            'response_rate': round(response_rate, 1),
            'positive_response_rate': round(positive_response_rate, 1),
            'meeting_conversion_rate': round(meeting_conversion_rate, 1),
            'outreach_type_distribution': type_distribution,
            'daily_outreach_rate': outreach_sent / max((end_date - start_date).days, 1),
            'email_open_rate': 28.5,  # Mock data - would integrate with email service
            'click_through_rate': 3.2  # Mock data
        }
    
    async def _analyze_pipeline_performance(self, start_date: datetime, end_date: datetime) -> Dict:
        """Analyze sales pipeline performance metrics"""
        
        # Pipeline stage distribution
        stage_distribution = self.db.query(
            Company.pipeline_stage,
            func.count(Company.id)
        ).group_by(Company.pipeline_stage).all()
        
        stage_counts = {stage or 'prospect': count for stage, count in stage_distribution}
        
        # Deals won in period
        deals_won = self.db.query(Company).filter(
            Company.pipeline_stage == 'won',
            Company.pipeline_updated_at >= start_date
        ).count()
        
        # Total pipeline value
        pipeline_value = self.db.query(func.sum(BusinessOpportunity.estimated_value)).join(Company).filter(
            Company.pipeline_stage.notin_(['won', 'lost'])
        ).scalar() or 0
        
        # Average deal size
        avg_deal_size = self.db.query(func.avg(BusinessOpportunity.estimated_value)).join(Company).filter(
            Company.pipeline_stage == 'won',
            Company.pipeline_updated_at >= start_date
        ).scalar() or 0
        
        # Pipeline velocity (mock calculation)
        pipeline_velocity = 42  # Would calculate actual velocity from stage transition data
        
        # Conversion rates
        total_prospects = sum(stage_counts.values())
        overall_conversion_rate = (deals_won / total_prospects * 100) if total_prospects > 0 else 0
        
        return {
            'stage_distribution': stage_counts,
            'deals_won': deals_won,
            'pipeline_value': pipeline_value,
            'average_deal_size': round(avg_deal_size, 2),
            'pipeline_velocity_days': pipeline_velocity,
            'overall_conversion_rate': round(overall_conversion_rate, 1),
            'total_active_prospects': total_prospects,
            'weighted_pipeline_value': pipeline_value * 0.3,  # Simplified weighting
            'stage_conversion_rates': self._calculate_stage_conversion_rates(stage_counts)
        }
    
    async def _analyze_revenue_performance(self, start_date: datetime, end_date: datetime) -> Dict:
        """Analyze revenue and financial performance metrics"""
        
        # Revenue from won deals
        period_revenue = self.db.query(func.sum(BusinessOpportunity.estimated_value)).join(Company).filter(
            Company.pipeline_stage == 'won',
            Company.pipeline_updated_at >= start_date,
            Company.pipeline_updated_at <= end_date
        ).scalar() or 0
        
        # Previous period for comparison
        prev_start = start_date - timedelta(days=(end_date - start_date).days)
        prev_revenue = self.db.query(func.sum(BusinessOpportunity.estimated_value)).join(Company).filter(
            Company.pipeline_stage == 'won',
            Company.pipeline_updated_at >= prev_start,
            Company.pipeline_updated_at < start_date
        ).scalar() or 0
        
        # Growth calculation
        revenue_growth = ((period_revenue - prev_revenue) / prev_revenue * 100) if prev_revenue > 0 else 0
        
        # Customer acquisition cost (simplified calculation)
        total_outreach_cost = 2000  # Mock cost - would calculate actual costs
        new_customers = self.db.query(Company).filter(
            Company.pipeline_stage == 'won',
            Company.pipeline_updated_at >= start_date
        ).count()
        
        customer_acquisition_cost = (total_outreach_cost / new_customers) if new_customers > 0 else 0
        
        # Lifetime value estimate
        avg_customer_value = 12000  # Mock LTV calculation
        
        return {
            'period_revenue': period_revenue,
            'previous_period_revenue': prev_revenue,
            'revenue_growth_percentage': round(revenue_growth, 1),
            'new_customers_acquired': new_customers,
            'customer_acquisition_cost': round(customer_acquisition_cost, 2),
            'estimated_lifetime_value': avg_customer_value,
            'ltv_cac_ratio': (avg_customer_value / customer_acquisition_cost) if customer_acquisition_cost > 0 else 0,
            'monthly_recurring_revenue': period_revenue * 0.2,  # Simplified MRR estimate
            'revenue_per_prospect': (period_revenue / self.db.query(Company).count()) if self.db.query(Company).count() > 0 else 0
        }
    
    def _calculate_kpi_scores(
        self,
        discovery_metrics: Dict,
        outreach_metrics: Dict,
        pipeline_metrics: Dict,
        revenue_metrics: Dict
    ) -> Dict:
        """Calculate KPI performance scores against targets"""
        
        scores = {}
        
        # Discovery KPIs
        scores['discovery'] = {
            'companies_discovered_monthly': self._score_kpi(
                discovery_metrics['companies_discovered'] * (30 / max(discovery_metrics.get('period_days', 30), 1)),
                self.kpis['discovery']['companies_discovered_monthly']['target']
            ),
            'discovery_quality_score': self._score_kpi(
                discovery_metrics['discovery_quality_score'],
                self.kpis['discovery']['discovery_quality_score']['target']
            ),
            'opportunity_identification_rate': self._score_kpi(
                discovery_metrics['opportunity_identification_rate'],
                self.kpis['discovery']['opportunity_identification_rate']['target']
            )
        }
        
        # Outreach KPIs
        scores['outreach'] = {
            'outreach_volume_monthly': self._score_kpi(
                outreach_metrics['outreach_volume'] * (30 / max(outreach_metrics.get('period_days', 30), 1)),
                self.kpis['outreach']['outreach_volume_monthly']['target']
            ),
            'email_open_rate': self._score_kpi(
                outreach_metrics['email_open_rate'],
                self.kpis['outreach']['email_open_rate']['target']
            ),
            'response_rate': self._score_kpi(
                outreach_metrics['response_rate'],
                self.kpis['outreach']['response_rate']['target']
            ),
            'meeting_conversion_rate': self._score_kpi(
                outreach_metrics['meeting_conversion_rate'],
                self.kpis['outreach']['meeting_conversion_rate']['target']
            )
        }
        
        # Pipeline KPIs
        scores['pipeline'] = {
            'pipeline_velocity': self._score_kpi(
                pipeline_metrics['pipeline_velocity_days'],
                self.kpis['pipeline']['pipeline_velocity']['target'],
                inverse=True  # Lower is better for velocity
            ),
            'conversion_rate_overall': self._score_kpi(
                pipeline_metrics['overall_conversion_rate'],
                self.kpis['pipeline']['conversion_rate_overall']['target']
            ),
            'average_deal_size': self._score_kpi(
                pipeline_metrics['average_deal_size'],
                self.kpis['pipeline']['average_deal_size']['target']
            ),
            'pipeline_value': self._score_kpi(
                pipeline_metrics['pipeline_value'],
                self.kpis['pipeline']['pipeline_value']['target']
            )
        }
        
        # Revenue KPIs
        scores['revenue'] = {
            'monthly_revenue': self._score_kpi(
                revenue_metrics['period_revenue'] * (30 / max(revenue_metrics.get('period_days', 30), 1)),
                self.kpis['revenue']['monthly_revenue']['target']
            ),
            'quarterly_growth': self._score_kpi(
                revenue_metrics['revenue_growth_percentage'],
                self.kpis['revenue']['quarterly_growth']['target']
            ),
            'customer_acquisition_cost': self._score_kpi(
                revenue_metrics['customer_acquisition_cost'],
                self.kpis['revenue']['customer_acquisition_cost']['target'],
                inverse=True  # Lower is better for CAC
            ),
            'lifetime_value': self._score_kpi(
                revenue_metrics['estimated_lifetime_value'],
                self.kpis['revenue']['lifetime_value']['target']
            )
        }
        
        # Calculate overall scores
        for category in scores:
            category_scores = list(scores[category].values())
            scores[category]['overall_score'] = sum(category_scores) / len(category_scores)
        
        scores['overall_performance_score'] = sum(
            scores[category]['overall_score'] for category in scores
        ) / len(scores)
        
        return scores
    
    def _score_kpi(self, actual: float, target: float, inverse: bool = False) -> float:
        """Score KPI performance (0-100)"""
        
        if target == 0:
            return 100 if actual == 0 else 0
        
        if inverse:
            # For metrics where lower is better (e.g., CAC, velocity)
            ratio = target / max(actual, 0.01)
        else:
            # For metrics where higher is better
            ratio = actual / target
        
        # Convert to 0-100 score with cap at 100
        score = min(ratio * 100, 100)
        return round(score, 1)
    
    def _generate_performance_insights(
        self,
        discovery_metrics: Dict,
        outreach_metrics: Dict,
        pipeline_metrics: Dict,
        revenue_metrics: Dict
    ) -> List[Dict]:
        """Generate actionable performance insights"""
        
        insights = []
        
        # Discovery insights
        if discovery_metrics['opportunity_identification_rate'] < 50:
            insights.append({
                'category': 'discovery',
                'insight': 'Low opportunity identification rate indicates need for better prospect targeting',
                'impact': 'medium',
                'recommendation': 'Refine discovery criteria and focus on higher-quality prospects'
            })
        
        # Outreach insights
        if outreach_metrics['response_rate'] < 10:
            insights.append({
                'category': 'outreach',
                'insight': 'Response rate below industry average suggests messaging improvements needed',
                'impact': 'high',
                'recommendation': 'A/B test subject lines and personalize outreach content'
            })
        
        if outreach_metrics['meeting_conversion_rate'] < 20:
            insights.append({
                'category': 'outreach',
                'insight': 'Low meeting conversion rate indicates qualification or follow-up issues',
                'impact': 'medium',
                'recommendation': 'Improve response qualification and meeting scheduling process'
            })
        
        # Pipeline insights
        if pipeline_metrics['pipeline_velocity_days'] > 60:
            insights.append({
                'category': 'pipeline',
                'insight': 'Sales cycle is longer than optimal, indicating process bottlenecks',
                'impact': 'high',
                'recommendation': 'Identify and resolve pipeline stage bottlenecks'
            })
        
        # Revenue insights
        if revenue_metrics['customer_acquisition_cost'] > 1000:
            insights.append({
                'category': 'revenue',
                'insight': 'Customer acquisition cost is high relative to deal size',
                'impact': 'medium',
                'recommendation': 'Optimize outreach efficiency and increase conversion rates'
            })
        
        return insights
    
    def _generate_optimization_recommendations(self, kpi_scores: Dict, insights: List[Dict]) -> List[Dict]:
        """Generate specific optimization recommendations"""
        
        recommendations = []
        
        # Identify lowest performing areas
        category_scores = {
            category: data['overall_score'] 
            for category, data in kpi_scores.items() 
            if category != 'overall_performance_score'
        }
        
        lowest_category = min(category_scores, key=category_scores.get)
        lowest_score = category_scores[lowest_category]
        
        if lowest_score < 70:
            recommendations.append({
                'priority': 'high',
                'category': lowest_category,
                'recommendation': f'Focus improvement efforts on {lowest_category} - lowest performing area',
                'specific_actions': self._get_category_specific_actions(lowest_category),
                'expected_impact': 'Improve overall performance by 15-25%'
            })
        
        # Add insight-based recommendations
        for insight in insights:
            if insight['impact'] == 'high':
                recommendations.append({
                    'priority': 'high',
                    'category': insight['category'],
                    'recommendation': insight['recommendation'],
                    'specific_actions': [insight['recommendation']],
                    'expected_impact': 'Address critical performance gap'
                })
        
        return recommendations
    
    def _calculate_roi_analysis(
        self,
        outreach_metrics: Dict,
        pipeline_metrics: Dict,
        revenue_metrics: Dict
    ) -> Dict:
        """Calculate ROI and efficiency analysis"""
        
        # Investment calculation (simplified)
        time_investment = 160  # Hours per month
        hourly_rate = 75  # Effective hourly rate
        tool_costs = 200  # Monthly tool costs
        total_investment = (time_investment * hourly_rate) + tool_costs
        
        # Return calculation
        monthly_return = revenue_metrics['period_revenue']
        
        # ROI calculation
        roi_percentage = ((monthly_return - total_investment) / total_investment * 100) if total_investment > 0 else 0
        
        # Efficiency metrics
        revenue_per_hour = monthly_return / time_investment if time_investment > 0 else 0
        cost_per_lead = total_investment / max(outreach_metrics['responses_received'], 1)
        
        return {
            'total_monthly_investment': total_investment,
            'monthly_return': monthly_return,
            'roi_percentage': round(roi_percentage, 1),
            'revenue_per_hour': round(revenue_per_hour, 2),
            'cost_per_lead': round(cost_per_lead, 2),
            'efficiency_score': min(roi_percentage / 2, 100),  # Simplified efficiency score
            'break_even_point': total_investment,
            'profit_margin': round(((monthly_return - total_investment) / monthly_return * 100), 1) if monthly_return > 0 else 0
        }
    
    async def _analyze_performance_trends(self, period_days: int) -> Dict:
        """Analyze performance trends over time"""
        
        # Mock trend analysis - in production, would analyze historical data
        trends = {
            'discovery_trend': 'increasing',
            'outreach_trend': 'stable',
            'pipeline_trend': 'improving',
            'revenue_trend': 'increasing',
            'trend_analysis': {
                'companies_discovered': [85, 92, 88, 95, 100],  # Last 5 periods
                'response_rate': [12.5, 13.2, 14.1, 15.8, 16.2],
                'pipeline_value': [180000, 195000, 210000, 225000, 240000],
                'monthly_revenue': [18000, 20000, 22000, 24000, 26000]
            }
        }
        
        return trends
    
    def _get_competitive_benchmarks(self) -> Dict:
        """Get industry competitive benchmarks"""
        
        return {
            'industry_averages': {
                'email_response_rate': 18.0,
                'meeting_conversion_rate': 22.0,
                'sales_cycle_days': 52,
                'customer_acquisition_cost': 750,
                'annual_growth_rate': 25.0
            },
            'benchmark_comparison': 'above_average',  # Would calculate actual comparison
            'percentile_ranking': 75  # Mock ranking
        }
    
    def _create_executive_summary(
        self,
        kpi_scores: Dict,
        revenue_metrics: Dict,
        pipeline_metrics: Dict
    ) -> Dict:
        """Create executive summary of performance"""
        
        return {
            'overall_performance_score': round(kpi_scores['overall_performance_score'], 1),
            'performance_grade': self._get_performance_grade(kpi_scores['overall_performance_score']),
            'period_revenue': revenue_metrics['period_revenue'],
            'revenue_growth': revenue_metrics['revenue_growth_percentage'],
            'pipeline_value': pipeline_metrics['pipeline_value'],
            'new_customers': revenue_metrics['new_customers_acquired'],
            'key_achievements': self._identify_key_achievements(kpi_scores),
            'areas_for_improvement': self._identify_improvement_areas(kpi_scores)
        }
    
    def _get_performance_grade(self, score: float) -> str:
        """Convert performance score to letter grade"""
        
        if score >= 90:
            return 'A'
        elif score >= 80:
            return 'B'
        elif score >= 70:
            return 'C'
        elif score >= 60:
            return 'D'
        else:
            return 'F'
    
    def _identify_key_achievements(self, kpi_scores: Dict) -> List[str]:
        """Identify top performing areas"""
        
        achievements = []
        
        for category, scores in kpi_scores.items():
            if category == 'overall_performance_score':
                continue
                
            for kpi, score in scores.items():
                if kpi == 'overall_score':
                    continue
                    
                if score >= 90:
                    achievements.append(f"Excellent {kpi.replace('_', ' ')} performance (Score: {score})")
                elif score >= 80:
                    achievements.append(f"Strong {kpi.replace('_', ' ')} results (Score: {score})")
        
        return achievements[:3]  # Top 3 achievements
    
    def _identify_improvement_areas(self, kpi_scores: Dict) -> List[str]:
        """Identify areas needing improvement"""
        
        improvements = []
        
        for category, scores in kpi_scores.items():
            if category == 'overall_performance_score':
                continue
                
            for kpi, score in scores.items():
                if kpi == 'overall_score':
                    continue
                    
                if score < 60:
                    improvements.append(f"{kpi.replace('_', ' ')} needs attention (Score: {score})")
                elif score < 70:
                    improvements.append(f"{kpi.replace('_', ' ')} has room for improvement (Score: {score})")
        
        return improvements[:3]  # Top 3 improvement areas
    
    async def _get_current_metrics(self) -> Dict:
        """Get current real-time metrics"""
        
        today = datetime.now().date()
        
        return {
            'today_outreach_sent': 12,  # Mock data
            'today_responses': 2,
            'this_week_meetings': 3,
            'active_prospects': await self._count_active_prospects(),
            'pipeline_value_change': '+$15,000'
        }
    
    async def _get_weekly_trends(self) -> Dict:
        """Get weekly trend data"""
        
        return {
            'outreach_volume': [45, 52, 48, 55, 50, 48, 52],  # Last 7 days
            'response_rate': [14.2, 15.1, 13.8, 16.2, 15.5, 14.9, 15.8],
            'pipeline_additions': [2, 1, 3, 2, 1, 2, 3]
        }
    
    async def _check_performance_alerts(self) -> List[Dict]:
        """Check for performance alerts and issues"""
        
        alerts = []
        
        # Mock alerts - would check actual thresholds
        alerts.append({
            'type': 'warning',
            'category': 'outreach',
            'message': 'Response rate below target (14.5% vs 15% target)',
            'action_required': 'Review and optimize outreach messaging'
        })
        
        return alerts
    
    def _calculate_goal_progress(self) -> Dict:
        """Calculate progress toward monthly/quarterly goals"""
        
        return {
            'monthly_revenue_goal': {
                'target': 25000,
                'current': 18500,
                'progress_percentage': 74
            },
            'quarterly_pipeline_goal': {
                'target': 500000,
                'current': 380000,
                'progress_percentage': 76
            },
            'annual_customer_goal': {
                'target': 50,
                'current': 28,
                'progress_percentage': 56
            }
        }
    
    async def _count_active_campaigns(self) -> int:
        """Count active outreach campaigns"""
        
        return self.db.query(OutreachRecord.campaign_id).distinct().filter(
            OutreachRecord.created_at >= datetime.now() - timedelta(days=30)
        ).count()
    
    async def _count_hot_prospects(self) -> int:
        """Count hot prospects in pipeline"""
        
        return self.db.query(Company).filter(
            Company.pipeline_stage.in_(['responded', 'meeting_scheduled', 'proposal_sent', 'negotiation']),
            Company.opportunity_score >= 7.0
        ).count()
    
    async def _get_month_revenue(self) -> float:
        """Get current month revenue"""
        
        start_of_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        revenue = self.db.query(func.sum(BusinessOpportunity.estimated_value)).join(Company).filter(
            Company.pipeline_stage == 'won',
            Company.pipeline_updated_at >= start_of_month
        ).scalar() or 0
        
        return revenue
    
    async def _get_pipeline_health_score(self) -> float:
        """Get current pipeline health score"""
        
        # Simplified calculation - would use more complex logic
        total_companies = self.db.query(Company).count()
        active_prospects = await self._count_active_prospects()
        
        if total_companies == 0:
            return 0
        
        activity_ratio = active_prospects / total_companies
        health_score = min(activity_ratio * 100, 100)
        
        return round(health_score, 1)
    
    async def _count_active_prospects(self) -> int:
        """Count active prospects in pipeline"""
        
        return self.db.query(Company).filter(
            Company.pipeline_stage.notin_(['won', 'lost', None])
        ).count()
    
    def _calculate_stage_conversion_rates(self, stage_counts: Dict) -> Dict:
        """Calculate conversion rates between pipeline stages"""
        
        # Mock calculation - would use actual historical data
        return {
            'prospect_to_contacted': 85,
            'contacted_to_responded': 18,
            'responded_to_meeting': 35,
            'meeting_to_proposal': 65,
            'proposal_to_won': 40
        }
    
    def _get_category_specific_actions(self, category: str) -> List[str]:
        """Get specific actions for improving category performance"""
        
        actions = {
            'discovery': [
                'Expand target market research',
                'Improve prospect qualification criteria',
                'Diversify discovery sources'
            ],
            'outreach': [
                'A/B test email subject lines',
                'Personalize outreach messages',
                'Optimize send timing',
                'Improve follow-up sequences'
            ],
            'pipeline': [
                'Identify and resolve bottlenecks',
                'Streamline proposal process',
                'Improve meeting-to-proposal conversion',
                'Accelerate decision timelines'
            ],
            'revenue': [
                'Increase average deal size',
                'Reduce customer acquisition cost',
                'Improve closing techniques',
                'Focus on high-value opportunities'
            ]
        }
        
        return actions.get(category, ['Analyze performance gaps', 'Implement best practices'])
    
    async def _save_analytics_report(self, report: Dict) -> Path:
        """Save analytics report to file"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"performance_analytics_report_{timestamp}.json"
        file_path = self.reports_dir / filename
        
        with open(file_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        return file_path


# Convenience functions
async def get_performance_report(period_days: int = 30) -> Dict:
    """Get comprehensive performance analytics report"""
    from app.core.database import get_db
    
    db = next(get_db())
    try:
        analytics = PerformanceAnalytics(db)
        report = await analytics.generate_comprehensive_analytics_report(period_days)
        return report
    finally:
        db.close()


async def get_realtime_dashboard() -> Dict:
    """Get real-time KPI dashboard data"""
    from app.core.database import get_db
    
    db = next(get_db())
    try:
        analytics = PerformanceAnalytics(db)
        dashboard = await analytics.track_real_time_kpis()
        return dashboard
    finally:
        db.close()