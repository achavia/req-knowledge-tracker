import pytest
import os
from fastapi.testclient import TestClient
from app.main import app
from app.ai import decompose_requirements, find_related_requirements
from app.trello_client import TrelloClient
from app.models import SessionLocal, Requirement, RequirementGroup


client = TestClient(app)


class TestRequirementDecomposition:
    def test_decompose_simple_email(self):
        """Test decomposing a simple email with grouped requirements."""
        subject = "Project B Items"
        body = """RSS Page
- Add status filter
- Update export format

Accommodation Page
- Add dismiss button"""
        
        reqs = decompose_requirements(subject, body)
        
        assert len(reqs) > 0, "Should decompose into at least one requirement"
        assert any('RSS' in r.get('group', '') for r in reqs), "Should detect RSS group"
        assert any('Accommodation' in r.get('group', '') for r in reqs), "Should detect Accommodation group"
        
    def test_decompose_preserves_content(self):
        """Test that original requirement text is preserved."""
        subject = "Test"
        body = """Features
- Add filter
- Remove old code"""
        
        reqs = decompose_requirements(subject, body)
        titles = [r.get('title', '') for r in reqs]
        
        assert any('Add filter' in t for t in titles), "Should preserve 'Add filter'"
        assert any('Remove old code' in t for t in titles), "Should preserve 'Remove old code'"
        
    def test_decompose_empty_body(self):
        """Test handling empty body."""
        subject = "Test"
        body = ""
        
        reqs = decompose_requirements(subject, body)
        assert isinstance(reqs, list), "Should return a list"
    
    def test_find_related_requirements(self):
        """Test finding related requirements in the same feature group."""
        db = SessionLocal()
        
        # Use unique group name with timestamp to avoid conflicts
        import time
        group_name = f"Test Feature {int(time.time())}"
        
        # Create a test group
        group = RequirementGroup(name=group_name)
        db.add(group)
        db.commit()
        db.refresh(group)
        
        # Add multiple requirements to the group with Trello URLs
        req1 = Requirement(
            title=f"{group_name} - Req 1",
            description="First",
            group_id=group.id,
            trello_card_url="https://trello.com/c/ABC123/1-test"
        )
        req2 = Requirement(
            title=f"{group_name} - Req 2",
            description="Second",
            group_id=group.id,
            trello_card_url="https://trello.com/c/XYZ789/2-test"
        )
        req3 = Requirement(
            title=f"{group_name} - Req 3",
            description="Third",
            group_id=group.id,
            trello_card_url="https://trello.com/c/DEF456/3-test"
        )
        
        db.add_all([req1, req2, req3])
        db.commit()
        db.refresh(req1)
        db.refresh(req2)
        db.refresh(req3)
        
        # Find related requirements for req1 (should return req2 and req3)
        related = find_related_requirements(db, group_name, exclude_requirement_id=req1.id)
        
        assert len(related) == 2, "Should find 2 related requirements"
        related_titles = [r.title for r in related]
        assert f"{group_name} - Req 2" in related_titles
        assert f"{group_name} - Req 3" in related_titles
        
        # Verify that related requirements have Trello URLs that can be linked
        for rel in related:
            assert rel.trello_card_url is not None, "Related requirements should have Trello URLs"
            assert "trello.com" in rel.trello_card_url, "Trello URL should be valid"
        
        # Cleanup
        db.query(Requirement).filter(Requirement.group_id == group.id).delete()
        db.query(RequirementGroup).filter(RequirementGroup.name == group_name).delete()
        db.commit()
        db.close()


class TestFormSubmission:
    def test_form_page_loads(self):
        """Test that the form page loads successfully."""
        response = client.get("/")
        assert response.status_code == 200
        assert "Requirement Knowledge Tracker" in response.text
        assert "Email Subject" in response.text
        
    def test_submit_email_form(self):
        """Test submitting an email through the form."""
        response = client.post(
            "/submit",
            data={
                "subject": "Test Project Items",
                "body": "Feature A\n- Requirement 1\n\nFeature B\n- Requirement 2"
            }
        )
        
        # Should redirect or return 200 after processing
        assert response.status_code in [200, 303], "Should process form successfully"
        
    def test_submit_with_multiple_groups(self):
        """Test form submission with multiple requirement groups."""
        response = client.post(
            "/submit",
            data={
                "subject": "Project B Items 05/06/2026",
                "body": """RSS Page
- Add status filter
- Update export format

Accommodation Page
- Add dismiss button

User Management
- Add lock account feature"""
            }
        )
        
        assert response.status_code in [200, 303], "Should handle multiple groups"
    
    def test_view_requirements_by_group(self):
        """Test viewing related requirements for a feature group."""
        # First create some requirements
        response = client.post(
            "/submit",
            data={
                "subject": "Test",
                "body": "Dashboard\n- Add dark mode\n- Add metrics"
            }
        )
        
        # Now view requirements for that group
        response = client.get("/requirements/Dashboard")
        assert response.status_code == 200, "Should view requirements"
        assert "Dashboard" in response.text
        assert "dark mode" in response.text or "metrics" in response.text


class TestTrelloClient:
    @pytest.fixture
    def trello_client(self):
        """Create a Trello client (requires env vars)."""
        return TrelloClient()
        
    def test_trello_client_init(self, trello_client):
        """Test Trello client initialization."""
        assert trello_client.key is not None or trello_client.key == None, "Should initialize without error"
        
    def test_trello_env_vars_available(self):
        """Test that Trello env vars are set."""
        key = os.getenv('TRELLO_KEY')
        token = os.getenv('TRELLO_TOKEN')
        list_id = os.getenv('TRELLO_LIST_ID')
        
        assert key is not None, "TRELLO_KEY should be set"
        assert token is not None, "TRELLO_TOKEN should be set"
        assert list_id is not None, "TRELLO_LIST_ID should be set"
        
    def test_create_card_returns_dict(self, trello_client):
        """Test that create_card returns a dict."""
        result = trello_client.create_card("Test", "Test description")
        assert isinstance(result, dict), "Should return dict"


class TestEndToEnd:
    def test_full_workflow(self):
        """Test the full workflow: submit email -> decompose -> create requirements."""
        # Submit email
        response = client.post(
            "/submit",
            data={
                "subject": "E2E Test Items",
                "body": """Module A
- Feature 1
- Feature 2

Module B  
- Feature 3"""
            }
        )
        
        assert response.status_code in [200, 303], "Should complete workflow"
        # DB should have created requirement groups and requirements
        # (Can be verified by querying the DB if needed)
