"""Tests para la API REST del AI Companion."""

from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from ai_companion.api.main import app
from ai_companion.api.session_manager import SessionManager


@pytest.fixture()
def client():
    """Cliente de test para la API."""
    return TestClient(app)


@pytest.fixture(autouse=True)
def _reset_session_manager():
    """Resetea el session manager entre tests."""
    from ai_companion.api import session_manager as sm_module

    sm_module.session_manager = SessionManager()
    # Also patch the one imported in main
    with patch("ai_companion.api.main.session_manager", sm_module.session_manager):
        yield


def test_health(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_get_profile_new_user(client):
    response = client.get("/api/v1/profile/test_user_new")
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == "test_user_new"
    assert data["name"] is None
    assert data["likes"] == []
    assert data["events"] == []


@patch("ai_companion.session.get_llm")
def test_chat_returns_response(mock_get_llm, client):
    mock_llm = MagicMock()
    mock_llm.invoke.return_value = MagicMock(content="Hola, soy tu companion!")
    mock_get_llm.return_value = mock_llm

    response = client.post(
        "/api/v1/chat",
        json={"user_id": "test_user", "message": "Hola"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert len(data["response"]) > 0


def test_end_session_no_active(client):
    response = client.post(
        "/api/v1/session/end",
        json={"user_id": "nonexistent_user"},
    )
    assert response.status_code == 404
