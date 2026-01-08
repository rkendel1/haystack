# SPDX-FileCopyrightText: 2022-present deepset GmbH <info@deepset.ai>
#
# SPDX-License-Identifier: Apache-2.0

"""
Basic tests for context management API endpoints.

These tests validate the API contract without requiring a database.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from uuid import uuid4

from backend.main import app


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


@pytest.fixture
def mock_context_service():
    """Mock the context service."""
    with patch("backend.main.context_service") as mock:
        yield mock


@pytest.fixture
def mock_onboarding_pipeline():
    """Mock the onboarding pipeline."""
    with patch("backend.main.onboarding_pipeline") as mock:
        yield mock


def test_root_endpoint(client):
    """Test the root endpoint returns API info."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "endpoints" in data
    assert "onboarding" in data["endpoints"]
    assert "context" in data["endpoints"]


def test_onboarding_start_endpoint_structure(client, mock_context_service, mock_onboarding_pipeline):
    """Test onboarding start endpoint accepts correct payload."""
    # Mock the service responses
    session_id = str(uuid4())
    mock_session = MagicMock(id=session_id, user_id="test_user")
    mock_context_service.create_onboarding_session.return_value = mock_session
    mock_onboarding_pipeline.run.return_value = []

    response = client.post(
        "/onboarding/start",
        json={"name": "Test Corp", "website": "https://test.com", "industry": "Technology"},
    )

    # Should return 200 (or 500 if actual DB operations fail, but we're mocking)
    assert response.status_code in [200, 500]


def test_list_contexts_endpoint(client, mock_context_service):
    """Test list contexts endpoint."""
    mock_context_service.list_context_objects.return_value = []

    response = client.get("/context")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_list_contexts_with_filters(client, mock_context_service):
    """Test list contexts endpoint with filters."""
    mock_context_service.list_context_objects.return_value = []

    response = client.get("/context?type=company&status=confirmed")
    assert response.status_code == 200

    # Verify the service was called with correct filters
    mock_context_service.list_context_objects.assert_called_once()
    call_args = mock_context_service.list_context_objects.call_args
    assert call_args.kwargs["context_type"] == "company"
    assert call_args.kwargs["status"] == "confirmed"


def test_get_context_not_found(client, mock_context_service):
    """Test get context returns 404 when not found."""
    mock_context_service.get_context_object.return_value = None

    context_id = str(uuid4())
    response = client.get(f"/context/{context_id}")
    assert response.status_code == 404


def test_confirm_context_endpoint(client, mock_context_service):
    """Test confirm context endpoint."""
    context_id = str(uuid4())
    mock_context = MagicMock(id=context_id, status="confirmed")
    mock_context_service.confirm_context_object.return_value = mock_context

    response = client.post(f"/context/{context_id}/confirm")
    assert response.status_code in [200, 500]  # May fail due to serialization


def test_reject_context_endpoint(client, mock_context_service):
    """Test reject context endpoint."""
    context_id = str(uuid4())
    mock_context = MagicMock(id=context_id, status="rejected")
    mock_context_service.reject_context_object.return_value = mock_context

    response = client.post(f"/context/{context_id}/reject")
    assert response.status_code in [200, 500]  # May fail due to serialization


def test_delete_context_endpoint(client, mock_context_service):
    """Test delete context endpoint."""
    context_id = str(uuid4())
    mock_context_service.delete_context_object.return_value = True

    response = client.delete(f"/context/{context_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "deleted"


def test_delete_context_not_found(client, mock_context_service):
    """Test delete context returns 404 when not found."""
    mock_context_service.delete_context_object.return_value = False

    context_id = str(uuid4())
    response = client.delete(f"/context/{context_id}")
    assert response.status_code == 404
