# Evaluation endpoint tests
import json
import tempfile
import os

import pytest
from fastapi import status
from httpx import AsyncClient


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
