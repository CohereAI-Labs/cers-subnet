import pytest
from fastapi.testclient import TestClient
from app.main import app  # Make sure the import path is correct

@pytest.fixture
async def client():
    with TestClient(app) as client:
        yield client

# Basic test to check API accessibility
def test_api_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()

# Test pour vérifier les endpoints de l'API
def test_api_endpoints(client):
    # Replace these endpoints with those of your API
    endpoints = ["/api/health", "/api/docs"]
    
    for endpoint in endpoints:
        response = client.get(endpoint)
        assert response.status_code == 200

# Test to verify error response
def test_api_error_handling(client):
    response = client.get("/api/non_existent_endpoint")
    assert response.status_code == 404
    assert "detail" in response.json()

# Test to verify authentication (adapt according to your implementation)
@pytest.mark.asyncio
async def test_api_auth(client):
    # Test with invalid token
    headers = {"Authorization": "Bearer invalid_token"}
    response = client.get("/api/protected", headers=headers)
    assert response.status_code == 401
    
    # Test with valid token (adapt with your test token)
    # headers = {"Authorization": "Bearer valid_test_token"}
    # response = client.get("/api/protected", headers=headers)
    # assert response.status_code == 200
