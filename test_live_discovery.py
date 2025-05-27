"""
Test Live Discovery System - Phase 9 Market Operations

Test the complete live business discovery and intelligence generation system.
"""

import asyncio
import logging

from app.core.database import get_db
from app.cli.live_discovery import LiveBusinessDiscovery
from app.services.intelligence_generator import BusinessIntelligenceReportGenerator
from app.models.business_intelligence import Company

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_live_discovery_system():
    """Test the complete live discovery system"""
    
    logger.info("🧪 Testing Live Discovery System - Phase 9")
    
    # Get database session
    db = next(get_db())
    
    try:
        # Initialize discovery system
        discovery = LiveBusinessDiscovery(db)
        
        # Test discovery with limited scope
        logger.info("🔍 Running test discovery campaign...")
        report = await discovery.run_discovery_campaign(
            location="Grass Valley, CA",
            industries=["web design", "marketing", "consulting"],
            max_companies=10,  # Limited for testing
            analyze_websites=True,
            find_decision_makers=True
        )
        
        logger.info("✅ Discovery campaign completed")
        
        # Display results
        summary = report['campaign_summary']
        logger.info(f"📊 Results:")
        logger.info(f"  Companies Discovered: {summary['companies_discovered']}")
        logger.info(f"  Websites Analyzed: {summary['companies_analyzed']}")
        logger.info(f"  Decision Makers: {summary['decision_makers_found']}")
        logger.info(f"  Opportunities Created: {summary['opportunities_created']}")
        
        if summary['companies_discovered'] > 0:
            # Test intelligence report generation
            logger.info("📋 Testing intelligence report generation...")
            
            # Get first company
            company = db.query(Company).filter(
                Company.opportunity_score > 0
            ).first()
            
            if company:
                logger.info(f"🎯 Generating intelligence report for {company.name}")
                
                # Generate report
                report_generator = BusinessIntelligenceReportGenerator(db)
                intelligence_report = await report_generator.generate_company_intelligence_report(
                    company.id
                )
                
                logger.info("✅ Intelligence report generated successfully")
                logger.info(f"📄 Report saved: {intelligence_report['report_metadata']['file_path']}")
                
                # Display key insights
                exec_summary = intelligence_report['executive_summary']
                logger.info(f"🎯 Opportunity Score: {exec_summary['opportunity_overview']['opportunity_score']:.1f}")
                logger.info(f"💰 Estimated Value: ${exec_summary['opportunity_overview']['estimated_total_value']:,.0f}")
                logger.info(f"🚀 Priority: {exec_summary['opportunity_overview']['engagement_priority']}")
                
            else:
                logger.warning("⚠️  No companies with opportunity scores found for report testing")
        
        logger.info("✅ Live discovery system test completed successfully!")
        return report
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        raise
    finally:
        db.close()


async def test_existing_data_analysis():
    """Test intelligence generation on existing data"""
    
    logger.info("🔬 Testing intelligence generation on existing data")
    
    db = next(get_db())
    
    try:
        # Get existing companies
        companies = db.query(Company).limit(5).all()
        
        if not companies:
            logger.warning("⚠️  No existing companies found. Run discovery first.")
            return
        
        logger.info(f"📊 Found {len(companies)} existing companies")
        
        # Generate reports for each company
        report_generator = BusinessIntelligenceReportGenerator(db)
        
        for company in companies:
            try:
                logger.info(f"📋 Generating report for {company.name}")
                
                report = await report_generator.generate_company_intelligence_report(
                    company.id
                )
                
                # Display summary
                exec_summary = report['executive_summary']
                logger.info(f"  💰 Value: ${exec_summary['opportunity_overview']['estimated_total_value']:,.0f}")
                logger.info(f"  🎯 Score: {exec_summary['opportunity_overview']['opportunity_score']:.1f}")
                logger.info(f"  📄 Report: {report['report_metadata']['file_path']}")
                
            except Exception as e:
                logger.warning(f"  ⚠️  Failed to generate report for {company.name}: {e}")
                continue
        
        logger.info("✅ Existing data analysis completed")
        
    finally:
        db.close()


if __name__ == "__main__":
    print("🚀 Phase 9 Live Discovery System Test")
    print("=" * 50)
    
    # Choose test mode
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "existing":
        # Test with existing data
        asyncio.run(test_existing_data_analysis())
    else:
        # Test live discovery
        asyncio.run(test_live_discovery_system())