# Backend Tests - Prompts API
import json
import base64
import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

# Import app modules
from backend.app.main import app
from backend.app.core.security import TokenData
from backend.app.core.database import get_db
from backend.app.models.prompt import Prompt
from backend.app.core.config import get_settings


# Fixture to enable demo mode for all tests
@pytest.fixture(autouse=True)
def enable_demo_mode(monkeypatch):
    """Enable demo mode by patching settings."""
    # Clear cache first so we get a fresh instance to patch
    get_settings.cache_clear()
    settings = get_settings()
    monkeypatch.setattr(settings, "DEMO_MODE", True)


# Fixture to initialize database for tests
@pytest.fixture(autouse=True)
async def init_test_db():
    """Initialize database tables for tests."""
    from backend.app.core.database import init_db, close_db
    await init_db()
    yield
    await close_db()
# Create valid JWT tokens for testing (manually encoded for demo mode)
def create_test_token(roles: list[str], sub: str = "test-user") -> str:
    """Create a test JWT token for demo mode (no signature verification)."""
    header = {"alg": "none", "typ": "JWT"}
    payload = {
        "sub": sub,
        "email": f"{sub}@test.com",
        "realm_access": {"roles": roles},
        "exp": int((datetime.now(timezone.utc) + timedelta(hours=1)).timestamp()),
    }
    # Manually create JWT with empty signature (demo mode doesn't verify)
    header_b64 = base64.urlsafe_b64encode(json.dumps(header).encode()).decode().rstrip('=')
    payload_b64 = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip('=')
    return f"{header_b64}.{payload_b64}."

# Mock user fixtures (kept for reference, but tokens are used instead)
@pytest.fixture
def admin_user():
    return TokenData(sub="test-user", email="admin@test.com", roles=["admin"], exp=9999999999)


@pytest.fixture
def operator_user():
    return TokenData(sub="test-operator", email="operator@test.com", roles=["operator"], exp=9999999999)


@pytest.fixture
def analyst_user():
    return TokenData(sub="test-analyst", email="analyst@test.com", roles=["analyst"], exp=9999999999)


@pytest.fixture
def viewer_user():
    return TokenData(sub="test-viewer", email="viewer@test.com", roles=["viewer"], exp=9999999999)


@pytest.fixture
def auth_headers_admin():
    return {"Authorization": f"Bearer {create_test_token(['admin'])}"}


@pytest.fixture
def auth_headers_operator():
    return {"Authorization": f"Bearer {create_test_token(['operator'])}"}


@pytest.fixture
def auth_headers_analyst():
    return {"Authorization": f"Bearer {create_test_token(['analyst'])}"}


@pytest.fixture
def auth_headers_viewer():
    return {"Authorization": f"Bearer {create_test_token(['viewer'])}"}


# Remove the mock_validate_token fixture since demo mode handles token validation
# (fixture removed - using real JWT tokens with demo mode)


@pytest.mark.asyncio
async def test_create_prompt_admin(auth_headers_admin):
    """Test creating a prompt as admin."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/prompts",
            json={
                "model_name": "test-model",
                "prompt_text": "Test prompt for jailbreak",
                "is_default": True,
                "tags": "test,jailbreak",
            },
            headers=auth_headers_admin,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["model_name"] == "test-model"
        assert data["prompt_text"] == "Test prompt for jailbreak"
        assert data["is_default"] is True
        assert data["tags"] == "test,jailbreak"


@pytest.mark.asyncio
async def test_create_prompt_forbidden_viewer(auth_headers_viewer):
    """Test that viewer cannot create prompt."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/prompts",
            json={"model_name": "test", "prompt_text": "test"},
            headers=auth_headers_viewer,
        )
        assert response.status_code == 403


@pytest.mark.asyncio
async def test_list_prompts_analyst(auth_headers_analyst):
    """Test listing prompts as analyst."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/prompts", headers=auth_headers_analyst)
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "page_size" in data


@pytest.mark.asyncio
async def test_get_prompt_not_found(auth_headers_admin):
    """Test getting non-existent prompt."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/prompts/999", headers=auth_headers_admin)
        assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_prompt_operator(auth_headers_operator):
    """Test updating a prompt as operator."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # First create a prompt
        create_resp = await client.post(
            "/api/prompts",
            json={"model_name": "update-test", "prompt_text": "Original", "is_default": False},
            headers=auth_headers_operator,
        )
        assert create_resp.status_code == 201
        prompt_id = create_resp.json()["id"]

        # Update it
        update_resp = await client.patch(
            f"/api/prompts/{prompt_id}",
            json={"prompt_text": "Updated", "is_default": True},
            headers=auth_headers_operator,
        )
        assert update_resp.status_code == 200
        data = update_resp.json()
        assert data["prompt_text"] == "Updated"
        assert data["is_default"] is True


@pytest.mark.asyncio
async def test_delete_prompt_admin_only(auth_headers_admin, auth_headers_operator):
    """Test that only admin can delete."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Create as operator
        create_resp = await client.post(
            "/api/prompts",
            json={"model_name": "delete-test", "prompt_text": "To delete"},
            headers=auth_headers_operator,
        )
        assert create_resp.status_code == 201
        prompt_id = create_resp.json()["id"]

        # Operator cannot delete
        del_resp = await client.delete(f"/api/prompts/{prompt_id}", headers=auth_headers_operator)
        assert del_resp.status_code == 403

        # Admin can delete
        del_resp = await client.delete(f"/api/prompts/{prompt_id}", headers=auth_headers_admin)
        assert del_resp.status_code == 204


@pytest.mark.asyncio
async def test_import_prompts(auth_headers_admin):
    """Test importing multiple prompts."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/prompts/import",
            json=[
                {"model_name": "import-model-1", "prompt_text": "Imported 1"},
                {"model_name": "import-model-2", "prompt_text": "Imported 2", "is_default": True},
            ],
            headers=auth_headers_admin,
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2


@pytest.mark.asyncio
async def test_unauthorized_without_token():
    """Test that requests without token are rejected."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/prompts")
        assert response.status_code == 401