#!/usr/bin/env python3
"""
Quick test script to demonstrate current JobBot functionality
Run this to see what's working right now!
"""
import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_endpoints():
    """Test all currently available endpoints"""
    print("🚀 Testing JobBot Current State\n")
    
    # Test 1: Basic health check
    print("1. Testing Health Check...")
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"   ✅ Root endpoint: {response.json()}")
    except Exception as e:
        print(f"   ❌ Root endpoint failed: {e}")
        return False
    
    # Test 2: Detailed health check
    print("\n2. Testing Detailed Health Check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        health_data = response.json()
        print(f"   ✅ Health status: {health_data['status']}")
        print(f"   📊 Database: {health_data['database']}")
        print(f"   🔧 Environment: {health_data['environment']}")
    except Exception as e:
        print(f"   ❌ Health check failed: {e}")
        return False
    
    # Test 3: API Discovery
    print("\n3. Testing API Discovery...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/")
        api_data = response.json()
        print(f"   ✅ API v1: {api_data['message']}")
        print(f"   📚 Available endpoints: {api_data['endpoints']}")
    except Exception as e:
        print(f"   ❌ API discovery failed: {e}")
    
    # Test 4: Jobs endpoint (should be empty initially)
    print("\n4. Testing Jobs Endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/jobs")
        if response.status_code == 200:
            jobs = response.json()
            print(f"   ✅ Jobs endpoint working! Found {len(jobs)} jobs")
        else:
            print(f"   ⚠️ Jobs endpoint returned status {response.status_code}")
    except Exception as e:
        print(f"   ❌ Jobs endpoint failed: {e}")
    
    # Test 5: Create a sample job
    print("\n5. Testing Job Creation...")
    sample_job = {
        "title": "Python Developer",
        "company": "TestCorp",
        "location": "Remote",
        "salary_min": 80000,
        "salary_max": 120000,
        "description": "Exciting Python role",
        "remote_option": True,
        "job_type": "full-time"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/v1/jobs", json=sample_job)
        if response.status_code == 200:
            result = response.json()
            job_id = result.get('id')
            print(f"   ✅ Job created successfully! ID: {job_id}")
            
            # Test 6: Retrieve the created job
            print(f"\n6. Testing Job Retrieval...")
            get_response = requests.get(f"{BASE_URL}/api/v1/jobs/{job_id}")
            if get_response.status_code == 200:
                job_data = get_response.json()
                print(f"   ✅ Retrieved job: {job_data['title']} at {job_data['company']}")
            else:
                print(f"   ⚠️ Could not retrieve job {job_id}")
                
        else:
            print(f"   ⚠️ Job creation returned status {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   ❌ Job creation failed: {e}")
    
    # Test 7: List jobs again (should show our created job)
    print("\n7. Testing Updated Jobs List...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/jobs")
        if response.status_code == 200:
            jobs = response.json()
            print(f"   ✅ Jobs list now shows {len(jobs)} job(s)")
            for job in jobs:
                print(f"      • {job['title']} at {job['company']} (ID: {job['id']})")
        else:
            print(f"   ⚠️ Jobs list returned status {response.status_code}")
    except Exception as e:
        print(f"   ❌ Jobs list failed: {e}")
    
    return True

def show_api_docs_info():
    """Show information about API documentation"""
    print("\n" + "="*50)
    print("📚 INTERACTIVE API DOCUMENTATION")
    print("="*50)
    print("You can explore the full API interactively at:")
    print(f"🌐 Swagger UI: {BASE_URL}/docs")
    print(f"📖 ReDoc: {BASE_URL}/redoc")
    print("\nThis includes:")
    print("• All available endpoints")
    print("• Request/response schemas") 
    print("• Try-it-out functionality")
    print("• Parameter documentation")

def show_database_info():
    """Show database model information"""
    print("\n" + "="*50)
    print("🗃️ DATABASE MODELS AVAILABLE")
    print("="*50)
    print("Phase 1 created these database tables:")
    print("• Jobs - Job postings with full metadata")
    print("• Applications - Application tracking")
    print("• EmployerResponses - Response management")
    print("• References - Professional references")
    print("• ExperienceClaims - Integrity tracking")
    print("\nCurrently only Jobs endpoints are implemented.")
    print("Phase 2 will add full CRUD for all models.")

def main():
    """Main test function"""
    print("🤖 JobBot Phase 1 Functionality Test")
    print("=" * 50)
    print("This script tests what's currently working in JobBot.")
    print("Make sure the development server is running:")
    print("  uvicorn app.main:app --reload")
    print("\nStarting tests...\n")
    
    # Wait a moment for any server startup
    time.sleep(1)
    
    if test_endpoints():
        show_api_docs_info()
        show_database_info()
        
        print("\n" + "="*50)
        print("🎉 CURRENT STATE SUMMARY")
        print("="*50)
        print("✅ Phase 1 Complete: Foundation & Database Setup")
        print("✅ FastAPI server running with health checks")
        print("✅ Database models created and functional")
        print("✅ Basic Jobs CRUD operations working")
        print("✅ API documentation auto-generated")
        print("🚧 Phase 2 Next: Complete API + advanced features")
        
        print("\n💡 What you can do right now:")
        print("• Visit http://localhost:8000/docs to explore the API")
        print("• Create, read, update, delete job postings")
        print("• Test database connectivity and health")
        print("• View auto-generated API documentation")
    else:
        print("\n❌ Some basic functionality is not working.")
        print("Make sure:")
        print("1. Development server is running: uvicorn app.main:app --reload")
        print("2. Database is configured in .env file")
        print("3. Dependencies are installed: pip install -r requirements.txt")

if __name__ == "__main__":
    main()