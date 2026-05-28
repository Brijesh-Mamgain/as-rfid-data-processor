from io import BytesIO

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_parse_rfid_success() -> None:
    response = client.post(
        "/parse-rfid",
        files={"file": ("sample.txt", BytesIO(b"ABC123\ninvalid line\nTAG_0001\n"), "text/plain")},
        data={"deviceid": "dev-1", "timestamp": "2026-05-25T10:00:00Z"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "success"
    assert payload["deviceid"] == "dev-1"
    assert payload["recordsProcessed"] == 3
    assert payload["validRecords"] == 2
    assert payload["invalidRecords"] == 1
    assert payload["invalidSamples"] == ["invalid line"]


def test_parse_rfid_rejects_non_txt() -> None:
    response = client.post(
        "/parse-rfid",
        files={"file": ("sample.csv", BytesIO(b"ABC123"), "text/csv")},
    )

    assert response.status_code == 400
