from io import BytesIO

from fastapi.testclient import TestClient

from app.main import app
from tests.conftest import AUTH_HEADERS


client = TestClient(app)


def test_parse_rfid_success() -> None:
    payload = (
        b"01 02 03 04 05 06 AA BB CC DD EE FF 0D 0E 0F 10\n"
        b"ZZ 02 03 04 05 06 10 20 30 40 50 60 0D 0E 0F 10\n"
        b"01 02 03 04 05 06 11 22 33 44 55 66 0D 0E 0F 10\n"
    )
    response = client.post(
        "/parse-rfid",
        headers=AUTH_HEADERS,
        files={"file": ("sample.txt", BytesIO(payload), "text/plain")},
        data={"deviceid": "dev-1", "timestamp": "2026-05-25T10:00:00Z"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "success"
    assert payload["deviceid"] == "dev-1"
    assert payload["recordsProcessed"] == 3
    assert payload["validRecords"] == 2
    assert payload["invalidRecords"] == 1
    assert payload["validSamples"] == ["AABBCCDDEEFF", "112233445566"]
    assert payload["invalidSamples"] == ["ZZ 02 03 04 05 06 10 20 30 40 50 60 0D 0E 0F 10"]


def test_parse_rfid_rejects_non_txt() -> None:
    response = client.post(
        "/parse-rfid",
        headers=AUTH_HEADERS,
        files={"file": ("sample.csv", BytesIO(b"ABC123"), "text/csv")},
    )

    assert response.status_code == 400


def test_parse_rfid_missing_token() -> None:
    """Requests without Authorization header must be rejected with 401."""
    response = client.post(
        "/parse-rfid",
        files={"file": ("sample.txt", BytesIO(b"ABC123\n"), "text/plain")},
    )

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


def test_parse_rfid_wrong_token() -> None:
    """Requests with an incorrect token must be rejected with 401."""
    response = client.post(
        "/parse-rfid",
        headers={"Authorization": "Bearer wrong-token"},
        files={"file": ("sample.txt", BytesIO(b"ABC123\n"), "text/plain")},
    )

    assert response.status_code == 401
