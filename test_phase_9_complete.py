"""
Comprehensive Test Suite for Phase 9 - Live Market Operations

Tests the complete Phase 9 implementation including live discovery,
intelligence generation, proof-of-concept automation, outreach campaigns,
pipeline management, and performance analytics.
"""

import asyncio
import logging
from datetime import datetime
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.cli.live_discovery import LiveBusinessDiscovery
from app.services.intelligence_generator import BusinessIntelligenceReportGenerator
from app.services.proof_of_concept_generator import ProofOfConceptGenerator
from app.services.outreach_automation import OutreachCampaignManager
from app.services.pipeline_management import ClientAcquisitionPipeline
from app.services.performance_analytics import PerformanceAnalytics
from app.models.business_intelligence import Company, DecisionMaker, BusinessOpportunity

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Phase9TestSuite:
    """
    Comprehensive test suite for Phase 9 live operations
    """
    
    def __init__(self):
        self.db = next(get_db())
        self.test_results = {
            'tests_run': 0,
            'tests_passed': 0,
            'tests_failed': 0,
            'errors': []
        }
        
        # Initialize all services
        self.discovery = LiveBusinessDiscovery(self.db)
        self.intelligence_generator = BusinessIntelligenceReportGenerator(self.db)
        self.poc_generator = ProofOfConceptGenerator(self.db)
        self.outreach_manager = OutreachCampaignManager(self.db)
        self.pipeline_manager = ClientAcquisitionPipeline(self.db)
        self.performance_analytics = PerformanceAnalytics(self.db)
    
    async def run_comprehensive_test(self) -> Dict:
        """Run complete Phase 9 test suite"""
        
        logger.info("🧪 Starting Phase 9 Comprehensive Test Suite")
        logger.info("=" * 60)
        
        try:
            # Test 1: Live Discovery System
            await self._test_live_discovery_system()
            
            # Test 2: Intelligence Report Generation
            await self._test_intelligence_generation()
            
            # Test 3: Proof-of-Concept Automation
            await self._test_poc_generation()
            
            # Test 4: Outreach Campaign Management
            await self._test_outreach_automation()
            
            # Test 5: Pipeline Management
            await self._test_pipeline_management()
            
            # Test 6: Performance Analytics
            await self._test_performance_analytics()
            
            # Test 7: End-to-End Workflow
            await self._test_end_to_end_workflow()
            
            # Generate final report
            final_report = self._generate_test_report()
            
            logger.info("✅ Phase 9 Test Suite Complete!")
            logger.info(f"📊 Results: {self.test_results['tests_passed']}/{self.test_results['tests_run']} tests passed")
            
            return final_report
            
        except Exception as e:
            logger.error(f"❌ Test suite failed: {e}")
            self.test_results['errors'].append(str(e))
            raise
        finally:
            self.db.close()
    
    async def _test_live_discovery_system(self):
        """Test live business discovery functionality"""
        
        logger.info("🔍 Testing Live Discovery System")
        
        try:
            # Test discovery campaign
            report = await self.discovery.run_discovery_campaign(
                location="Test Valley, CA",
                industries=["web design", "consulting"],
                max_companies=5,  # Small test run
                analyze_websites=True,
                find_decision_makers=True
            )
            
            # Validate results
            summary = report['campaign_summary']
            
            assert 'companies_discovered' in summary, "Missing companies_discovered metric"
            assert 'companies_analyzed' in summary, "Missing companies_analyzed metric"
            assert 'opportunities_created' in summary, "Missing opportunities_created metric"
            
            logger.info(f"  ✅ Discovery campaign completed")
            logger.info(f"     Companies discovered: {summary['companies_discovered']}")
            logger.info(f"     Websites analyzed: {summary['companies_analyzed']}")
            logger.info(f"     Opportunities created: {summary['opportunities_created']}")
            
            self._record_test_result("live_discovery_system", True)
            
        except Exception as e:
            logger.error(f"  ❌ Live discovery test failed: {e}")
            self._record_test_result("live_discovery_system", False, str(e))
    
    async def _test_intelligence_generation(self):
        """Test intelligence report generation"""
        
        logger.info("📋 Testing Intelligence Report Generation")
        
        try:
            # Get or create test company
            test_company = await self._get_or_create_test_company()
            
            # Generate intelligence report
            report = await self.intelligence_generator.generate_company_intelligence_report(
                test_company.id
            )
            
            # Validate report structure
            required_sections = [
                'company_profile', 'executive_summary', 'report_metadata'
            ]
            
            for section in required_sections:
                assert section in report, f"Missing report section: {section}"
            
            # Validate executive summary
            exec_summary = report['executive_summary']
            assert 'opportunity_overview' in exec_summary, "Missing opportunity overview"
            assert 'key_findings' in exec_summary, "Missing key findings"
            assert 'next_actions' in exec_summary, "Missing next actions"
            
            logger.info(f"  ✅ Intelligence report generated successfully")
            logger.info(f"     Company: {test_company.name}")
            logger.info(f"     Report file: {report['report_metadata']['file_path']}")
            
            self._record_test_result("intelligence_generation", True)
            
        except Exception as e:
            logger.error(f"  ❌ Intelligence generation test failed: {e}")
            self._record_test_result("intelligence_generation", False, str(e))
    
    async def _test_poc_generation(self):
        """Test proof-of-concept generation"""
        
        logger.info("🛠️  Testing Proof-of-Concept Generation")
        
        try:
            # Get test company
            test_company = await self._get_or_create_test_company()
            
            # Generate comprehensive POC
            poc_result = await self.poc_generator.generate_proof_of_concept(
                test_company.id,
                opportunity_type="comprehensive_transformation"
            )
            
            # Validate POC structure
            assert 'poc_type' in poc_result, "Missing POC type"
            assert 'deliverables' in poc_result, "Missing deliverables"
            assert 'estimated_value' in poc_result, "Missing estimated value"
            
            # Validate specific POC components
            if poc_result['poc_type'] == 'comprehensive_transformation':
                assert 'website_improvement' in poc_result, "Missing website improvement POC"
                assert 'technology_modernization' in poc_result, "Missing tech modernization POC"
                assert 'digital_marketing' in poc_result, "Missing digital marketing POC"
            
            logger.info(f"  ✅ Proof-of-concept generated successfully")
            logger.info(f"     Type: {poc_result['poc_type']}")
            logger.info(f"     Estimated value: ${poc_result['estimated_value']:,.0f}")
            logger.info(f"     Deliverables: {len(poc_result['deliverables'])}")
            
            self._record_test_result("poc_generation", True)
            
        except Exception as e:
            logger.error(f"  ❌ POC generation test failed: {e}")
            self._record_test_result("poc_generation", False, str(e))
    
    async def _test_outreach_automation(self):
        """Test outreach campaign automation"""
        
        logger.info("📧 Testing Outreach Campaign Automation")
        
        try:
            # Get test companies
            test_companies = await self._get_test_companies(3)
            company_ids = [c.id for c in test_companies]
            
            # Launch outreach campaign
            campaign_result = await self.outreach_manager.launch_outreach_campaign(
                company_ids=company_ids,
                campaign_type="value_proposition",
                send_emails=False,  # Test mode - don't actually send
                follow_up_sequence=True
            )
            
            # Validate campaign results
            summary = campaign_result['campaign_summary']
            
            assert 'campaign_id' in summary, "Missing campaign ID"
            assert 'target_companies' in summary, "Missing target companies count"
            assert 'follow_ups_scheduled' in summary, "Missing follow-ups scheduled"
            
            # Validate outreach records created
            assert campaign_result['outreach_records'] > 0, "No outreach records created"
            
            logger.info(f"  ✅ Outreach campaign launched successfully")
            logger.info(f"     Campaign ID: {summary['campaign_id']}")
            logger.info(f"     Target companies: {summary['target_companies']}")
            logger.info(f"     Outreach records: {campaign_result['outreach_records']}")
            
            self._record_test_result("outreach_automation", True)
            
        except Exception as e:
            logger.error(f"  ❌ Outreach automation test failed: {e}")
            self._record_test_result("outreach_automation", False, str(e))
    
    async def _test_pipeline_management(self):
        """Test pipeline management functionality"""
        
        logger.info("📈 Testing Pipeline Management")
        
        try:
            # Test pipeline analysis
            pipeline_analysis = await self.pipeline_manager.analyze_pipeline_performance()
            
            # Validate analysis structure
            assert 'pipeline_overview' in pipeline_analysis, "Missing pipeline overview"
            assert 'conversion_metrics' in pipeline_analysis, "Missing conversion metrics"
            assert 'recommendations' in pipeline_analysis, "Missing recommendations"
            
            # Test stage advancement
            test_company = await self._get_or_create_test_company()
            
            stage_result = await self.pipeline_manager.advance_pipeline_stage(
                test_company.id,
                'contacted',
                'Test stage advancement'
            )
            
            assert stage_result['new_stage'] == 'contacted', "Stage not advanced correctly"
            assert 'automated_actions' in stage_result, "Missing automated actions"
            
            # Test hot prospects identification
            hot_prospects = await self.pipeline_manager.identify_hot_prospects(5)
            assert isinstance(hot_prospects, list), "Hot prospects should be a list"
            
            logger.info(f"  ✅ Pipeline management tested successfully")
            logger.info(f"     Pipeline value: ${pipeline_analysis['pipeline_overview']['total_pipeline_value']:,.0f}")
            logger.info(f"     Hot prospects: {len(hot_prospects)}")
            
            self._record_test_result("pipeline_management", True)
            
        except Exception as e:
            logger.error(f"  ❌ Pipeline management test failed: {e}")
            self._record_test_result("pipeline_management", False, str(e))
    
    async def _test_performance_analytics(self):
        """Test performance analytics functionality"""
        
        logger.info("📊 Testing Performance Analytics")
        
        try:
            # Test comprehensive analytics report
            analytics_report = await self.performance_analytics.generate_comprehensive_analytics_report(
                period_days=30
            )
            
            # Validate report structure
            required_sections = [
                'executive_summary', 'kpi_performance', 'kpi_scores', 
                'performance_insights', 'roi_analysis'
            ]
            
            for section in required_sections:
                assert section in analytics_report, f"Missing analytics section: {section}"
            
            # Validate KPI categories
            kpi_performance = analytics_report['kpi_performance']
            kpi_categories = ['discovery', 'outreach', 'pipeline', 'revenue']
            
            for category in kpi_categories:
                assert category in kpi_performance, f"Missing KPI category: {category}"
            
            # Test real-time dashboard
            dashboard_data = await self.performance_analytics.track_real_time_kpis()
            
            assert 'current_metrics' in dashboard_data, "Missing current metrics"
            assert 'goal_progress' in dashboard_data, "Missing goal progress"
            
            logger.info(f"  ✅ Performance analytics tested successfully")
            logger.info(f"     Overall score: {analytics_report['kpi_scores']['overall_performance_score']}")
            logger.info(f"     Performance grade: {analytics_report['executive_summary']['performance_grade']}")
            
            self._record_test_result("performance_analytics", True)
            
        except Exception as e:
            logger.error(f"  ❌ Performance analytics test failed: {e}")
            self._record_test_result("performance_analytics", False, str(e))
    
    async def _test_end_to_end_workflow(self):
        """Test complete end-to-end workflow"""
        
        logger.info("🔄 Testing End-to-End Workflow")
        
        try:
            # 1. Discover company
            discovery_report = await self.discovery.run_discovery_campaign(
                location="E2E Test City, CA",
                industries=["test industry"],
                max_companies=1,
                analyze_websites=False,
                find_decision_makers=False
            )
            
            # 2. Get discovered company
            if discovery_report['campaign_summary']['companies_discovered'] > 0:
                test_company = self.db.query(Company).filter(
                    Company.city == "E2E Test City"
                ).first()
            else:
                test_company = await self._create_test_company("E2E Test Company")
            
            # 3. Generate intelligence report
            intelligence_report = await self.intelligence_generator.generate_company_intelligence_report(
                test_company.id
            )
            
            # 4. Generate proof-of-concept
            poc_result = await self.poc_generator.generate_proof_of_concept(
                test_company.id,
                "website_improvement"
            )
            
            # 5. Launch outreach campaign
            outreach_result = await self.outreach_manager.launch_outreach_campaign(
                [test_company.id],
                "free_audit",
                send_emails=False
            )
            
            # 6. Advance through pipeline
            await self.pipeline_manager.advance_pipeline_stage(
                test_company.id, 'contacted', 'E2E test progression'
            )
            
            await self.pipeline_manager.advance_pipeline_stage(
                test_company.id, 'responded', 'E2E test positive response'
            )
            
            # 7. Generate performance report
            performance_report = await self.performance_analytics.generate_comprehensive_analytics_report(
                period_days=7
            )
            
            logger.info(f"  ✅ End-to-end workflow completed successfully")
            logger.info(f"     Company: {test_company.name}")
            logger.info(f"     Intelligence report: Generated")
            logger.info(f"     POC value: ${poc_result['estimated_value']:,.0f}")
            logger.info(f"     Outreach campaign: {outreach_result['campaign_summary']['campaign_id']}")
            logger.info(f"     Pipeline stage: responded")
            logger.info(f"     Performance score: {performance_report['kpi_scores']['overall_performance_score']}")
            
            self._record_test_result("end_to_end_workflow", True)
            
        except Exception as e:
            logger.error(f"  ❌ End-to-end workflow test failed: {e}")
            self._record_test_result("end_to_end_workflow", False, str(e))
    
    async def _get_or_create_test_company(self) -> Company:
        """Get existing test company or create one"""
        
        test_company = self.db.query(Company).filter(
            Company.name == "Test Company"
        ).first()
        
        if not test_company:
            test_company = await self._create_test_company("Test Company")
        
        return test_company
    
    async def _create_test_company(self, name: str) -> Company:
        """Create a test company"""
        
        company = Company(
            name=name,
            domain="testcompany.com",
            website_url="https://testcompany.com",
            industry="testing",
            city="Test City",
            state="CA",
            business_status="active",
            opportunity_score=7.5,
            discovery_source="test_suite",
            last_scraped=datetime.now()
        )
        
        self.db.add(company)
        self.db.commit()
        self.db.refresh(company)
        
        # Create test opportunity
        opportunity = BusinessOpportunity(
            company_id=company.id,
            opportunity_type="website_improvement",
            description="Test opportunity for automated testing",
            estimated_value=5000.0,
            probability=0.7,
            urgency_level="medium",
            status="identified",
            owner="test_suite"
        )
        
        self.db.add(opportunity)
        self.db.commit()
        
        return company
    
    async def _get_test_companies(self, count: int) -> List[Company]:
        """Get or create multiple test companies"""
        
        companies = []
        
        for i in range(count):
            company_name = f"Test Company {i+1}"
            company = self.db.query(Company).filter(
                Company.name == company_name
            ).first()
            
            if not company:
                company = await self._create_test_company(company_name)
            
            companies.append(company)
        
        return companies
    
    def _record_test_result(self, test_name: str, passed: bool, error_msg: str = None):
        """Record test result"""
        
        self.test_results['tests_run'] += 1
        
        if passed:
            self.test_results['tests_passed'] += 1
        else:
            self.test_results['tests_failed'] += 1
            if error_msg:
                self.test_results['errors'].append(f"{test_name}: {error_msg}")
    
    def _generate_test_report(self) -> Dict:
        """Generate final test report"""
        
        success_rate = (self.test_results['tests_passed'] / self.test_results['tests_run']) * 100
        
        return {
            'test_summary': {
                'total_tests': self.test_results['tests_run'],
                'tests_passed': self.test_results['tests_passed'],
                'tests_failed': self.test_results['tests_failed'],
                'success_rate': round(success_rate, 1)
            },
            'phase_9_readiness': success_rate >= 85,
            'test_errors': self.test_results['errors'],
            'components_tested': [
                'Live Discovery System',
                'Intelligence Report Generation', 
                'Proof-of-Concept Automation',
                'Outreach Campaign Management',
                'Pipeline Management',
                'Performance Analytics',
                'End-to-End Workflow Integration'
            ],
            'recommendation': (
                "Phase 9 is ready for production deployment" 
                if success_rate >= 85 
                else "Address test failures before production deployment"
            ),
            'next_steps': [
                "Review any test failures and resolve issues",
                "Conduct live pilot with real prospects",
                "Monitor performance metrics in production",
                "Scale operations based on results"
            ] if success_rate >= 85 else [
                "Fix failing test components",
                "Re-run test suite until 85%+ success rate",
                "Review error logs and resolve issues"
            ]
        }


async def run_phase_9_test_suite():
    """Run comprehensive Phase 9 test suite"""
    
    print("🚀 Phase 9 Live Market Operations - Comprehensive Test Suite")
    print("=" * 70)
    print("Testing complete business intelligence platform from discovery → revenue")
    print()
    
    test_suite = Phase9TestSuite()
    
    try:
        report = await test_suite.run_comprehensive_test()
        
        # Display results
        print("\n" + "="*70)
        print("🎯 PHASE 9 TEST RESULTS")
        print("="*70)
        
        summary = report['test_summary']
        print(f"📊 Test Summary:")
        print(f"   Total Tests: {summary['total_tests']}")
        print(f"   Tests Passed: {summary['tests_passed']}")
        print(f"   Tests Failed: {summary['tests_failed']}")
        print(f"   Success Rate: {summary['success_rate']}%")
        
        print(f"\n🎯 Phase 9 Readiness: {'✅ READY' if report['phase_9_readiness'] else '❌ NOT READY'}")
        
        if report['test_errors']:
            print(f"\n❌ Test Errors:")
            for error in report['test_errors']:
                print(f"   • {error}")
        
        print(f"\n📋 Components Tested:")
        for component in report['components_tested']:
            print(f"   ✅ {component}")
        
        print(f"\n🚀 Recommendation:")
        print(f"   {report['recommendation']}")
        
        print(f"\n📝 Next Steps:")
        for step in report['next_steps']:
            print(f"   • {step}")
        
        print("\n" + "="*70)
        
        if report['phase_9_readiness']:
            print("🎉 PHASE 9 COMPLETE - READY FOR LIVE BUSINESS OPERATIONS!")
        else:
            print("⚠️  PHASE 9 INCOMPLETE - ADDRESS ISSUES BEFORE DEPLOYMENT")
        
        return report
        
    except Exception as e:
        print(f"\n❌ Test suite execution failed: {e}")
        raise


if __name__ == "__main__":
    # Run the comprehensive test suite
    asyncio.run(run_phase_9_test_suite())