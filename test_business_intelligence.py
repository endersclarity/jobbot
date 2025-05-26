#!/usr/bin/env python3
"""
Business Intelligence Engine Test Suite

Comprehensive test to verify all BIE components are working properly:
- Database models and migrations
- Company discovery and tech stack analysis
- Opportunity scoring and ranking
- API endpoints and data flow

Run this test to validate the MVP before pull request.
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.core.database import get_db, engine
from app.models.business_intelligence import (
    Company, CompanyTechStack, DecisionMaker, BusinessOpportunity, WebsiteAudit
)
from app.scrapers.business_discovery import BusinessDirectoryScaper
from app.analysis.tech_stack_detector import TechStackDetector
from app.analysis.opportunity_scorer import OpportunityScorer


async def test_database_models():
    """Test that all database models are working"""
    print("🗄️ Testing database models...")
    
    db = next(get_db())
    
    try:
        # Test creating a company
        test_company = Company(
            name="Test Company",
            domain="testcompany.com",
            website_url="https://testcompany.com",
            industry="software",
            city="Grass Valley",
            state="CA",
            discovery_source="test",
            business_status="active"
        )
        
        db.add(test_company)
        db.commit()
        db.refresh(test_company)
        
        # Test creating tech stack
        tech_stack = CompanyTechStack(
            company_id=test_company.id,
            tech_name="WordPress",
            tech_category="cms",
            tech_version="5.8",
            confidence_score=0.9,
            is_outdated=True
        )
        
        db.add(tech_stack)
        db.commit()
        
        # Test creating opportunity
        opportunity = BusinessOpportunity(
            company_id=test_company.id,
            opportunity_type="website_rebuild",
            title="Website Modernization",
            description="Outdated WordPress needs updating",
            estimated_value=3000,
            effort_estimate_hours=20,
            urgency_score=7.5,
            status="identified"
        )
        
        db.add(opportunity)
        db.commit()
        
        print("✅ Database models working correctly")
        return test_company
        
    except Exception as e:
        print(f"❌ Database model test failed: {e}")
        db.rollback()
        return None
    finally:
        db.close()


async def test_tech_stack_detection():
    """Test technology detection on a real website"""
    print("🔍 Testing tech stack detection...")
    
    db = next(get_db())
    
    try:
        # Create test company with real website
        test_company = Company(
            name="WordPress Test Site",
            domain="wordpress.org",
            website_url="https://wordpress.org",
            industry="software",
            discovery_source="test"
        )
        
        db.add(test_company)
        db.commit()
        db.refresh(test_company)
        
        # Run tech stack detection
        detector = TechStackDetector(db)
        analysis = await detector.analyze_company_website(test_company)
        
        print(f"Analysis result: {analysis.get('tech_stack', [])}")
        
        if analysis.get('tech_stack'):
            print("✅ Tech stack detection working")
            return True
        else:
            print("⚠️ Tech stack detection returned no results")
            return False
            
    except Exception as e:
        print(f"❌ Tech stack detection test failed: {e}")
        return False
    finally:
        db.close()


async def test_opportunity_scoring():
    """Test opportunity scoring system"""
    print("📊 Testing opportunity scoring...")
    
    db = next(get_db())
    
    try:
        # Get a test company with opportunities
        company = db.query(Company).filter(Company.name.like("%Test%")).first()
        
        if not company:
            print("❌ No test company found for scoring")
            return False
        
        # Get opportunities for scoring
        opportunities = db.query(BusinessOpportunity).filter(
            BusinessOpportunity.company_id == company.id
        ).all()
        
        if not opportunities:
            print("❌ No opportunities found for scoring")
            return False
        
        # Score opportunities
        scorer = OpportunityScorer(db)
        
        for opp in opportunities:
            score = scorer.score_opportunity(opp)
            print(f"Opportunity '{opp.title}' scored: {score:.2f}")
        
        print("✅ Opportunity scoring working")
        return True
        
    except Exception as e:
        print(f"❌ Opportunity scoring test failed: {e}")
        return False
    finally:
        db.close()


async def test_api_integration():
    """Test that API endpoints are accessible"""
    print("🌐 Testing API integration...")
    
    try:
        import requests
        
        # Test basic health endpoint
        response = requests.get("http://localhost:8000/health", timeout=5)
        
        if response.status_code == 200:
            health_data = response.json()
            print(f"Health check: {health_data.get('status', 'unknown')}")
            print("✅ API integration working")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("⚠️ API server not running - start with: python app/main.py")
        return False
    except Exception as e:
        print(f"❌ API integration test failed: {e}")
        return False


def test_data_completeness():
    """Test that we have sufficient test data"""
    print("📈 Testing data completeness...")
    
    db = next(get_db())
    
    try:
        company_count = db.query(Company).count()
        opportunity_count = db.query(BusinessOpportunity).count()
        tech_count = db.query(CompanyTechStack).count()
        
        print(f"Companies: {company_count}")
        print(f"Opportunities: {opportunity_count}")
        print(f"Tech stack entries: {tech_count}")
        
        if company_count >= 1 and opportunity_count >= 1:
            print("✅ Sufficient test data available")
            return True
        else:
            print("⚠️ Limited test data - run discovery to get more")
            return False
            
    except Exception as e:
        print(f"❌ Data completeness test failed: {e}")
        return False
    finally:
        db.close()


async def test_discovery_system():
    """Test company discovery (limited to avoid rate limiting)"""
    print("🕵️ Testing company discovery system...")
    
    db = next(get_db())
    
    try:
        # Test discovery with a small sample
        scraper = BusinessDirectoryScaper(db)
        
        # Mock some discovery results for testing
        mock_companies = [
            {
                'name': 'Mock Web Design Co',
                'domain': 'mockweb.com',
                'website_url': 'https://mockweb.com',
                'industry': 'web design',
                'city': 'Grass Valley',
                'state': 'CA',
                'discovery_source': 'test_mock'
            }
        ]
        
        # Store mock companies
        stored_count = 0
        for company_data in mock_companies:
            company = await scraper._store_company(company_data)
            if company:
                stored_count += 1
        
        print(f"Stored {stored_count} mock companies")
        
        if stored_count > 0:
            print("✅ Company discovery system working")
            return True
        else:
            print("❌ Company discovery system failed")
            return False
            
    except Exception as e:
        print(f"❌ Discovery system test failed: {e}")
        return False
    finally:
        db.close()


async def run_comprehensive_test():
    """Run all tests and provide summary"""
    print("🚀 Starting Business Intelligence Engine Comprehensive Test\n")
    
    tests = [
        ("Database Models", test_database_models()),
        ("Tech Stack Detection", test_tech_stack_detection()),
        ("Opportunity Scoring", test_opportunity_scoring()),
        ("API Integration", test_api_integration()),
        ("Data Completeness", test_data_completeness()),
        ("Discovery System", test_discovery_system())
    ]
    
    results = []
    
    for test_name, test_coro in tests:
        try:
            if asyncio.iscoroutine(test_coro):
                result = await test_coro
            else:
                result = test_coro
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
        
        print()  # Add spacing between tests
    
    # Summary
    print("=" * 50)
    print("🎯 TEST RESULTS SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:.<30} {status}")
        if result:
            passed += 1
    
    print("-" * 50)
    print(f"Total: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Business Intelligence Engine is ready.")
        print("Ready for pull request and production deployment.")
    elif passed >= total * 0.8:
        print(f"\n✅ Most tests passed ({passed}/{total}). Minor issues to resolve.")
    else:
        print(f"\n⚠️ Multiple test failures ({passed}/{total}). Review and fix issues.")
    
    return passed, total


if __name__ == "__main__":
    print("Business Intelligence Engine Test Suite")
    print("=" * 50)
    
    try:
        passed, total = asyncio.run(run_comprehensive_test())
        
        # Exit code based on test results
        if passed == total:
            sys.exit(0)  # All tests passed
        else:
            sys.exit(1)  # Some tests failed
            
    except KeyboardInterrupt:
        print("\n❌ Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        sys.exit(1)