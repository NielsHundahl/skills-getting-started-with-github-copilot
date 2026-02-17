import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to a known state before each test"""
    from src.app import activities
    
    # Save original state
    original = {k: {"participants": list(v["participants"])} for k, v in activities.items()}
    
    yield
    
    # Restore original state
    for activity_name in activities:
        activities[activity_name]["participants"] = original[activity_name]["participants"]
