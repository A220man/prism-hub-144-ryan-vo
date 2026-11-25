# Evaluation endpoint tests
import json
import tempfile
import os

import pytest
from fastapi import status
# Fixture to enable demo mode for all tests
@pytest.fixture(autouse=True)
def enable_demo_mode(monkeypatch):
    """Enable demo mode by patching settings."""
    from backend.app.core.config import get_settings
    # Clear cache first so we get a fresh instance to patch
    get_settings.cache_clear()
    settings = get_settings()
    monkeypatch.setattr(settings, "DEMO_MODE", True)
from httpx import AsyncClient


def create_test_token(roles: list[str], sub: str = "test-user") -> str:
    """Create a test JWT token for demo mode (no signature verification)."""
    header = {"alg": "none", "typ": "JWT"}
    payload = {
        "sub": sub,
        "email": f"{sub}@test.com",
        "realm_access": {"roles": roles},
        "exp": 9999999999,
    }
    import base64
    import json as json_mod
    header_b64 = json_mod.dumps(header)
    # Actually let me just use the pattern from test_prompts.py
    header_b64 = base64.urlsafe_b64encode(json_mod.dumps(header).encode()).decode().rstrip('=')
    payload_b64 = base64.urlsafe_b64encode(json_mod.dumps(payload).encode()).decode().rstrip('=')
    return f"{header_b64}.{payload_b64}."

@pytest.fixture
def normal_user_token():
    """Create a normal user JWT token."""
    return create_test_token(['user'])

@pytest.fixture(scope="module")
def client_ac():
    """Async client for testing."""
    from backend.app.main import app
    from httpx import AsyncClient, ASGITransport
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://test")


@pytest.mark.asyncio
async def test_run_evaluation_endpoint_no_auth(client_ac):
    """Endpoint requires authentication."""
    response = await client_ac.get("/api/prompts/evaluate")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_run_evaluation_endpoint_with_auth(client_ac, normal_user_token):
    """Endpoint returns evaluation summary with valid auth."""
    response = await client_ac.get(
        "/api/prompts/evaluate",
        headers={"Authorization": f"Bearer {normal_user_token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "total" in data
    assert "successful" in data
    assert "failed" in data
    assert "avg_latency_ms" in data
    assert "by_model" in data


@pytest.mark.asyncio
async def test_run_evaluation_endpoint_with_model_filter(client_ac, normal_user_token):
    """Endpoint supports model filtering."""
    response = await client_ac.get(
        "/api/prompts/evaluate?model_filter=xiaoma-la",
        headers={"Authorization": f"Bearer {normal_user_token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["total"] == 4  # 4 xiaoma-la test cases
    assert data["successful"] == 4
    assert data["failed"] == 0


@pytest.mark.asyncio
async def test_run_evaluation_endpoint_summary_fields(client_ac, normal_user_token):
    """Evaluation summary has all expected fields."""
    response = await client_ac.get(
        "/api/prompts/evaluate",
        headers={"Authorization": f"Bearer {normal_user_token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    # Check top-level summary fields
    expected_fields = {"total", "successful", "failed", "avg_latency_ms", "by_model"}
    assert set(data.keys()) == expected_fields
    # Check by_model structure
    for model, stats in data["by_model"].items():
        assert set(stats.keys()) == {"total", "successful", "failed"}


@pytest.mark.asyncio
async def test_run_evaluation_endpoint_filtered_results(client_ac, normal_user_token):
    """Filtered evaluation returns correct counts."""
    response = await client_ac.get(
        "/api/prompts/evaluate?model_filter=gpt-4",
        headers={"Authorization": f"Bearer {normal_user_token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["total"] == 4  # 4 gpt-4 test cases
    assert data["successful"] == 0  # gpt-4 has 45% susceptibility, likely 0 with deterministic hash
    assert data["failed"] == 4
