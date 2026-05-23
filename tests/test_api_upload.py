from io import BytesIO

from fastapi.testclient import TestClient

from app.main import app


class StubAzureBlobClient:
    def upload_with_retry(self, filename: str, content: bytes, retries: int = 3) -> str:
        return "https://example.blob.core.windows.net/rfid-files/rfid/2026-01-01/sample.txt"

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        return filename


client = TestClient(app)


def test_upload_rfid_success(monkeypatch) -> None:
    monkeypatch.setattr("app.api.rfid.AzureBlobClient", StubAzureBlobClient)

    response = client.post(
        "/upload-rfid",
        files={"file": ("sample.txt", BytesIO(b"ABC123\nXYZ999\n"), "text/plain")},
        data={"deviceId": "dev-1", "timestamp": "2026-05-23T10:00:00Z"},
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
        files={"file": ("sample.csv", BytesIO(b"ABC123"), "text/csv")},
    )

    assert response.status_code == 400
