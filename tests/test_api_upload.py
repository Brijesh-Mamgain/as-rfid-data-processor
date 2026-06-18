from fastapi.testclient import TestClient

from app.main import app
from tests.conftest import AUTH_HEADERS


class StubAzureBlobClient:
    def upload_with_retry(self, filename: str, content: bytes, retries: int = 3) -> str:
        return "https://example.blob.core.windows.net/rfid-files/rfid/2026-01-01/sample.txt"

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        return filename


class StubAzureSQLClient:
    def insert_rfid_logs_batch(self, **kwargs: object) -> None:
        pass


client = TestClient(app)


def test_upload_rfid_success(monkeypatch) -> None:
    monkeypatch.setattr("app.api.rfid.AzureBlobClient", StubAzureBlobClient)
    monkeypatch.setattr("app.api.rfid.AzureSQLClient", StubAzureSQLClient)

    # Two valid 16-byte hex packets separated by newline.
    rfid_payload = (
        b"01 02 03 04 05 06 AA BB CC DD EE FF 0D 0E 0F 10\n"
        b"01 02 03 04 05 06 11 22 33 44 55 66 0D 0E 0F 10\n"
    )

    response = client.post(
        "/upload-rfid",
        content=rfid_payload,
        headers={
            **AUTH_HEADERS,
            "FileName": "sample.txt",
            "deviceId": "dev-1",
            "Timestamp": "2026-05-23T10:00:00Z",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "success"
    assert payload["recordsProcessed"] == 2
    assert payload["validRecords"] == 2
    assert payload["invalidRecords"] == 0


def test_upload_rfid_rejects_non_txt() -> None:
    response = client.post(
        "/upload-rfid",
        content=b"ABC123",
        headers={**AUTH_HEADERS, "FileName": "sample.csv"},
    )

    assert response.status_code == 400


def test_upload_rfid_missing_token() -> None:
    """Requests without Authorization header must be rejected with 401."""
    response = client.post(
        "/upload-rfid",
        content=b"ABC123\n",
        headers={"FileName": "sample.txt"},
    )

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


def test_upload_rfid_wrong_token() -> None:
    """Requests with an incorrect token must be rejected with 401."""
    response = client.post(
        "/upload-rfid",
        content=b"ABC123\n",
        headers={"FileName": "sample.txt", "Authorization": "Bearer wrong-token"},
    )

    assert response.status_code == 401
