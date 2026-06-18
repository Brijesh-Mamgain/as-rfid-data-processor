"""Shared pytest fixtures for the test suite."""

import pytest

from app.core.config import settings

# Fixed token used across all tests.  The autouse fixture below patches the
# live ``settings`` singleton before every test and restores it afterwards via
# monkeypatch, so no real env-var is required in CI.
TEST_API_TOKEN = "test-rfid-api-token-fixture"
AUTH_HEADERS = {"Authorization": f"Bearer {TEST_API_TOKEN}"}


@pytest.fixture(autouse=True)
def patch_rfid_api_token(monkeypatch: pytest.MonkeyPatch) -> None:
    """Patch settings.rfid_api_token for every test so the auth dependency
    has a configured token.  Tests that want to exercise the 401 path simply
    omit or corrupt the Authorization header in their request."""
    monkeypatch.setattr(settings, "rfid_api_token", TEST_API_TOKEN)
