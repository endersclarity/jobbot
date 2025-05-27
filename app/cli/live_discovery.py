"""
Live Business Discovery CLI - Phase 9 Market Operations

Command-line interface for discovering and analyzing real businesses
using the complete Business Intelligence Engine.
"""

import asyncio
import click
import logging
from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.business_intelligence import Company, BusinessOpportunity
from app.scrapers.business_discovery import BusinessDirectoryScaper, LinkedInCompanyScraper
from app.analysis.tech_stack_detector import TechStackDetector
from app.analysis.opportunity_scorer import OpportunityScorer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class LiveBusinessDiscovery:
    """
    Live business discovery and analysis orchestrator
    """
    
    def __init__(self, db_session: Session):
        self.db = db_session
        self.directory_scraper = BusinessDirectoryScaper(db_session)
        self.linkedin_scraper = LinkedInCompanyScraper(db_session)
        self.tech_detector = TechStackDetector()
        self.opportunity_scorer = OpportunityScorer()
        
        self.stats = {
            'companies_discovered': 0,
            'companies_analyzed': 0,
            'opportunities_created': 0,
            'decision_makers_found': 0,
            'errors': 0
        }
    
    async def run_discovery_campaign(
        self, 
        location: str = "Grass Valley, CA",
        industries: Optional[List[str]] = None,
        max_companies: int = 100,
        analyze_websites: bool = True,
        find_decision_makers: bool = True
    ) -> dict:
        """
        Run complete discovery campaign for a target market
        """
        logger.info(f"🚀 Starting Live Discovery Campaign for {location}")
        logger.info(f"Target: {max_companies} companies across {len(industries or [])} industries")
        
        start_time = datetime.now()
        
        try:
            # Step 1: Discover companies from directories
            companies = await self._discover_companies(location, industries, max_companies)
            self.stats['companies_discovered'] = len(companies)
            
            # Step 2: Analyze websites and technology stacks
            if analyze_websites:
                await self._analyze_company_websites(companies)
            
            # Step 3: Find decision makers
            if find_decision_makers:
                await self._find_decision_makers(companies)
            
            # Step 4: Score opportunities
            await self._score_opportunities(companies)
            
            # Step 5: Generate summary report
            duration = datetime.now() - start_time
            report = self._generate_campaign_report(duration)
            
            logger.info("✅ Discovery Campaign Complete!")
            logger.info(f"📊 {self.stats['companies_discovered']} companies, {self.stats['opportunities_created']} opportunities, {duration.total_seconds():.1f}s")
            
            return report
            
        except Exception as e:
            logger.error(f"❌ Discovery campaign failed: {e}")
            self.stats['errors'] += 1
            raise
    
    async def _discover_companies(
        self, 
        location: str, 
        industries: Optional[List[str]], 
        max_companies: int
    ) -> List[Company]:
        """Discover companies from business directories"""
        
        if not industries:
            industries = [
                'web design', 'digital marketing', 'software development', 
                'consulting', 'real estate', 'law firm', 'accounting',
                'digital agency', 'architecture', 'construction',
                'restaurants', 'retail', 'automotive', 'healthcare'
            ]
        
        logger.info(f"🔍 Discovering companies in {location}")
        logger.info(f"Industries: {', '.join(industries)}")
        
        try:
            companies = await self.directory_scraper.discover_companies_in_location(
                location, industries
            )
            
            # Limit to max_companies
            if len(companies) > max_companies:
                companies = companies[:max_companies]
            
            logger.info(f"✅ Discovered {len(companies)} companies")
            
            # Log sample companies
            for i, company in enumerate(companies[:5]):
                logger.info(f"  {i+1}. {company.name} ({company.domain}) - {company.industry}")
            
            if len(companies) > 5:
                logger.info(f"  ... and {len(companies) - 5} more")
            
            return companies
            
        except Exception as e:
            logger.error(f"❌ Error discovering companies: {e}")
            return []
    
    async def _analyze_company_websites(self, companies: List[Company]) -> None:
        """Analyze company websites for technology stacks and opportunities"""
        
        logger.info(f"🔬 Analyzing {len(companies)} company websites")
        
        analyzed_count = 0
        
        for company in companies:
            if not company.website_url and not company.domain:
                continue
                
            try:
                # Get website URL
                website_url = company.website_url
                if not website_url and company.domain:
                    website_url = f"https://{company.domain}"
                
                if not website_url:
                    continue
                
                logger.info(f"  🌐 Analyzing {company.name}: {website_url}")
                
                # Detect technology stack
                tech_stack = await self.tech_detector.analyze_website(website_url)
                
                if tech_stack:
                    # Store technology stack in database
                    await self.tech_detector.store_tech_stack(company.id, tech_stack)
                    analyzed_count += 1
                    
                    # Log key findings
                    technologies = tech_stack.get('technologies', [])
                    if technologies:
                        tech_names = [tech.get('name', 'Unknown') for tech in technologies[:3]]
                        logger.info(f"    ✅ Found: {', '.join(tech_names)}")
                
                # Rate limiting
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.warning(f"    ⚠️  Error analyzing {company.name}: {e}")
                self.stats['errors'] += 1
                continue
        
        self.stats['companies_analyzed'] = analyzed_count
        logger.info(f"✅ Analyzed {analyzed_count} websites successfully")
    
    async def _find_decision_makers(self, companies: List[Company]) -> None:
        """Find decision makers for companies"""
        
        logger.info(f"👥 Finding decision makers for {len(companies)} companies")
        
        total_decision_makers = 0
        
        for company in companies[:20]:  # Limit to first 20 for LinkedIn rate limiting
            try:
                logger.info(f"  🔍 Finding decision makers for {company.name}")
                
                decision_makers = await self.linkedin_scraper.find_company_employees(company)
                total_decision_makers += len(decision_makers)
                
                if decision_makers:
                    for dm in decision_makers:
                        logger.info(f"    👤 {dm.name} - {dm.title}")
                
                # Rate limiting for LinkedIn
                await asyncio.sleep(2)
                
            except Exception as e:
                logger.warning(f"    ⚠️  Error finding decision makers for {company.name}: {e}")
                self.stats['errors'] += 1
                continue
        
        self.stats['decision_makers_found'] = total_decision_makers
        logger.info(f"✅ Found {total_decision_makers} decision makers")
    
    async def _score_opportunities(self, companies: List[Company]) -> None:
        """Score business opportunities for all companies"""
        
        logger.info(f"📈 Scoring opportunities for {len(companies)} companies")
        
        opportunities_created = 0
        
        for company in companies:
            try:
                # Calculate opportunity score
                score = await self.opportunity_scorer.calculate_company_score(company)
                
                # Update company opportunity score
                company.opportunity_score = score
                self.db.commit()
                
                # Create opportunity record if score is high enough
                if score >= 6.0:  # Threshold for viable opportunities
                    opportunity = await self._create_business_opportunity(company, score)
                    if opportunity:
                        opportunities_created += 1
                        logger.info(f"  🎯 High opportunity: {company.name} (Score: {score:.1f})")
                
            except Exception as e:
                logger.warning(f"  ⚠️  Error scoring {company.name}: {e}")
                self.stats['errors'] += 1
                continue
        
        self.stats['opportunities_created'] = opportunities_created
        logger.info(f"✅ Created {opportunities_created} high-value opportunities")
    
    async def _create_business_opportunity(self, company: Company, score: float) -> Optional[BusinessOpportunity]:
        """Create business opportunity record"""
        try:
            # Generate opportunity description based on analysis
            description = f"Business development opportunity for {company.name}"
            
            # Determine opportunity type based on company data
            opportunity_type = "website_modernization"
            if company.industry in ['consulting', 'software development']:
                opportunity_type = "technology_consulting"
            elif company.industry in ['marketing', 'digital agency']:
                opportunity_type = "digital_marketing"
            
            opportunity = BusinessOpportunity(
                company_id=company.id,
                opportunity_type=opportunity_type,
                description=description,
                estimated_value=self._estimate_opportunity_value(company, score),
                probability=min(score / 10.0, 0.9),  # Convert to probability
                urgency_level=self._determine_urgency(score),
                competitive_analysis="Low competition in local market",
                next_action="Initial outreach and discovery call",
                status='identified',
                owner='system'
            )
            
            self.db.add(opportunity)
            self.db.commit()
            self.db.refresh(opportunity)
            
            return opportunity
            
        except Exception as e:
            logger.error(f"Error creating opportunity for {company.name}: {e}")
            self.db.rollback()
            return None
    
    def _estimate_opportunity_value(self, company: Company, score: float) -> float:
        """Estimate opportunity value based on company and score"""
        base_value = 5000  # Base project value
        
        # Industry multipliers
        industry_multipliers = {
            'software development': 2.0,
            'consulting': 1.8,
            'digital agency': 1.6,
            'law firm': 1.5,
            'real estate': 1.3,
            'default': 1.0
        }
        
        multiplier = industry_multipliers.get(company.industry, industry_multipliers['default'])
        
        # Score multiplier (6.0-10.0 maps to 1.0-2.0)
        score_multiplier = 1.0 + (score - 6.0) / 4.0
        
        return base_value * multiplier * score_multiplier
    
    def _determine_urgency(self, score: float) -> str:
        """Determine urgency level based on opportunity score"""
        if score >= 8.5:
            return 'high'
        elif score >= 7.0:
            return 'medium'
        else:
            return 'low'
    
    def _generate_campaign_report(self, duration) -> dict:
        """Generate comprehensive campaign report"""
        
        # Query database for additional stats
        total_companies = self.db.query(Company).count()
        high_value_opportunities = self.db.query(BusinessOpportunity).filter(
            BusinessOpportunity.estimated_value > 10000
        ).count()
        
        report = {
            'campaign_summary': {
                'duration_seconds': duration.total_seconds(),
                'companies_discovered': self.stats['companies_discovered'],
                'companies_analyzed': self.stats['companies_analyzed'],
                'decision_makers_found': self.stats['decision_makers_found'],
                'opportunities_created': self.stats['opportunities_created'],
                'errors': self.stats['errors']
            },
            'database_totals': {
                'total_companies': total_companies,
                'high_value_opportunities': high_value_opportunities
            },
            'performance_metrics': {
                'companies_per_minute': self.stats['companies_discovered'] / (duration.total_seconds() / 60),
                'analysis_success_rate': (self.stats['companies_analyzed'] / max(self.stats['companies_discovered'], 1)) * 100,
                'opportunity_identification_rate': (self.stats['opportunities_created'] / max(self.stats['companies_discovered'], 1)) * 100
            },
            'next_actions': [
                "Review high-value opportunities in dashboard",
                "Begin outreach to top prospects",
                "Generate detailed company intelligence reports",
                "Create proof-of-concept demonstrations"
            ]
        }
        
        return report


@click.group()
def cli():
    """Live Business Discovery - Phase 9 Market Operations"""
    pass


@cli.command()
@click.option('--location', default='Grass Valley, CA', help='Target location for discovery')
@click.option('--industries', help='Comma-separated list of industries')
@click.option('--max-companies', default=50, help='Maximum companies to discover')
@click.option('--analyze-websites/--no-analyze-websites', default=True, help='Analyze company websites')
@click.option('--find-decision-makers/--no-find-decision-makers', default=True, help='Find decision makers')
def discover(location, industries, max_companies, analyze_websites, find_decision_makers):
    """Run live business discovery campaign"""
    
    # Parse industries
    industry_list = None
    if industries:
        industry_list = [i.strip() for i in industries.split(',')]
    
    # Get database session
    db = next(get_db())
    
    try:
        # Initialize discovery system
        discovery = LiveBusinessDiscovery(db)
        
        # Run discovery campaign
        report = asyncio.run(discovery.run_discovery_campaign(
            location=location,
            industries=industry_list,
            max_companies=max_companies,
            analyze_websites=analyze_websites,
            find_decision_makers=find_decision_makers
        ))
        
        # Display results
        click.echo("\n" + "="*60)
        click.echo("🎯 LIVE DISCOVERY CAMPAIGN COMPLETE")
        click.echo("="*60)
        
        summary = report['campaign_summary']
        click.echo(f"📍 Location: {location}")
        click.echo(f"⏱️  Duration: {summary['duration_seconds']:.1f} seconds")
        click.echo(f"🏢 Companies Discovered: {summary['companies_discovered']}")
        click.echo(f"🔬 Websites Analyzed: {summary['companies_analyzed']}")
        click.echo(f"👥 Decision Makers: {summary['decision_makers_found']}")
        click.echo(f"🎯 Opportunities Created: {summary['opportunities_created']}")
        
        if summary['errors'] > 0:
            click.echo(f"⚠️  Errors: {summary['errors']}")
        
        metrics = report['performance_metrics']
        click.echo(f"\n📊 Performance:")
        click.echo(f"  • {metrics['companies_per_minute']:.1f} companies/minute")
        click.echo(f"  • {metrics['analysis_success_rate']:.1f}% analysis success rate")
        click.echo(f"  • {metrics['opportunity_identification_rate']:.1f}% opportunity rate")
        
        click.echo(f"\n🚀 Next Actions:")
        for action in report['next_actions']:
            click.echo(f"  • {action}")
        
        click.echo("\n✅ Ready for live business development!")
        
    except Exception as e:
        click.echo(f"❌ Discovery failed: {e}")
        raise
    finally:
        db.close()


@cli.command()
@click.option('--min-score', default=7.0, help='Minimum opportunity score')
@click.option('--limit', default=10, help='Number of top opportunities to show')
def top_opportunities(min_score, limit):
    """Show top business opportunities"""
    
    db = next(get_db())
    
    try:
        opportunities = db.query(BusinessOpportunity).join(Company).filter(
            BusinessOpportunity.estimated_value > min_score * 1000
        ).order_by(BusinessOpportunity.estimated_value.desc()).limit(limit).all()
        
        if not opportunities:
            click.echo("No high-value opportunities found. Run discovery first.")
            return
        
        click.echo(f"\n🎯 TOP {limit} BUSINESS OPPORTUNITIES")
        click.echo("="*50)
        
        for i, opp in enumerate(opportunities, 1):
            company = opp.company
            click.echo(f"\n{i}. {company.name}")
            click.echo(f"   💰 Value: ${opp.estimated_value:,.0f}")
            click.echo(f"   📈 Probability: {opp.probability:.1%}")
            click.echo(f"   🏭 Industry: {company.industry}")
            click.echo(f"   🌐 Website: {company.website_url or 'N/A'}")
            click.echo(f"   📧 Next Action: {opp.next_action}")
        
    finally:
        db.close()


@cli.command()
def status():
    """Show current discovery system status"""
    
    db = next(get_db())
    
    try:
        total_companies = db.query(Company).count()
        analyzed_companies = db.query(Company).filter(Company.opportunity_score > 0).count()
        total_opportunities = db.query(BusinessOpportunity).count()
        high_value_opps = db.query(BusinessOpportunity).filter(
            BusinessOpportunity.estimated_value > 10000
        ).count()
        
        click.echo("\n📊 DISCOVERY SYSTEM STATUS")
        click.echo("="*40)
        click.echo(f"🏢 Total Companies: {total_companies}")
        click.echo(f"🔬 Analyzed Companies: {analyzed_companies}")
        click.echo(f"🎯 Total Opportunities: {total_opportunities}")
        click.echo(f"💰 High-Value Opportunities: {high_value_opps}")
        
        if total_companies > 0:
            analysis_rate = (analyzed_companies / total_companies) * 100
            click.echo(f"📈 Analysis Coverage: {analysis_rate:.1f}%")
        
        click.echo("\n✅ System operational and ready for business development")
        
    finally:
        db.close()


if __name__ == '__main__':
    cli()