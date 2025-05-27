"""
Test main application functionality
"""
import pytest
from fastapi.testclient import TestClient

def test_root_endpoint(client: TestClient):
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Business Intelligence Engine API is running"
    assert data["version"] == "1.0.0"

def test_health_endpoint(client: TestClient):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "business-intelligence-engine"
    assert data["version"] == "1.0.0"
    assert "database" in data

def test_api_root_endpoint(client: TestClient):
    """Test API v1 root endpoint"""
    response = client.get("/api/v1/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Business Intelligence Engine API v1"
    assert "endpoints" in data