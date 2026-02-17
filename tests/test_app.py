import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


class TestActivitiesEndpoints:
    """Test suite for activities endpoints"""
    
    def test_get_activities(self, client):
        """Test getting all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        
        activities = response.json()
        assert isinstance(activities, dict)
        assert len(activities) > 0
        assert "Basketball Team" in activities
        assert "participants" in activities["Basketball Team"]
        assert "description" in activities["Basketball Team"]
        assert "schedule" in activities["Basketball Team"]
        assert "max_participants" in activities["Basketball Team"]
    
    def test_signup_for_activity_success(self, client):
        """Test successful signup for an activity"""
        email = "test@mergington.edu"
        activity = "Chess Club"
        
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]
        
        # Verify participant was added
        activities = client.get("/activities").json()
        assert email in activities[activity]["participants"]
    
    def test_signup_duplicate_not_allowed(self, client):
        """Test that duplicate signups are prevented"""
        email = "test@mergington.edu"
        activity = "Chess Club"
        
        # First signup should succeed
        response1 = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        assert response1.status_code == 200
        
        # Second signup should fail
        response2 = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        assert response2.status_code == 400
        assert "already signed up" in response2.json()["detail"]
    
    def test_signup_nonexistent_activity(self, client):
        """Test signup for non-existent activity"""
        response = client.post(
            "/activities/Nonexistent Activity/signup",
            params={"email": "test@mergington.edu"}
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_unregister_success(self, client):
        """Test successful unregistration from an activity"""
        email = "test@mergington.edu"
        activity = "Chess Club"
        
        # First signup
        client.post(f"/activities/{activity}/signup", params={"email": email})
        
        # Then unregister
        response = client.delete(
            f"/activities/{activity}/unregister",
            params={"email": email}
        )
        
        assert response.status_code == 200
        assert "Unregistered" in response.json()["message"]
        
        # Verify participant was removed
        activities = client.get("/activities").json()
        assert email not in activities[activity]["participants"]
    
    def test_unregister_not_registered(self, client):
        """Test unregistering someone who's not registered"""
        response = client.delete(
            "/activities/Chess Club/unregister",
            params={"email": "notregistered@mergington.edu"}
        )
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]
    
    def test_unregister_nonexistent_activity(self, client):
        """Test unregister from non-existent activity"""
        response = client.delete(
            "/activities/Nonexistent Activity/unregister",
            params={"email": "test@mergington.edu"}
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_redirect_root_to_static(self, client):
        """Test that root path redirects to static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]
    
    def test_activities_have_valid_structure(self, client):
        """Test that all activities have required fields"""
        response = client.get("/activities")
        activities = response.json()
        
        required_fields = ["description", "schedule", "max_participants", "participants"]
        
        for activity_name, activity_data in activities.items():
            for field in required_fields:
                assert field in activity_data, f"{activity_name} missing {field}"
                
            # Validate participants is a list
            assert isinstance(activity_data["participants"], list)
            # Validate max_participants is a positive integer
            assert isinstance(activity_data["max_participants"], int)
            assert activity_data["max_participants"] > 0
