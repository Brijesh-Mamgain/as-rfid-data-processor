"""
Tests for POST /notify-whatsapp endpoint.

WhatsAppService is monkeypatched at the router level so no real DB or Twilio
calls are made.
"""

from fastapi.testclient import TestClient

from app.main import app
from app.models.rfid import WhatsAppNotificationResponse, WhatsAppNotificationResult

client = TestClient(app)


# ---------------------------------------------------------------------------
# Stub service
# ---------------------------------------------------------------------------

class StubWhatsAppServiceAllSent:
    def notify(self) -> WhatsAppNotificationResponse:
        return WhatsAppNotificationResponse(
            status="success",
            message="Notification run complete: 2 sent, 0 skipped, 0 failed",
            sent=2,
            skipped=0,
            failed=0,
            notifications=[
                WhatsAppNotificationResult(
                    user_id=1,
                    whatsapp="+911111111111",
                    rfid="TAG0001",
                    scan_timestamp_utc="2026-06-06 03:00:00",
                    status="sent",
                ),
                WhatsAppNotificationResult(
                    user_id=2,
                    whatsapp="+912222222222",
                    rfid="TAG0002",
                    scan_timestamp_utc="2026-06-06 04:00:00",
                    status="sent",
                ),
            ],
        )


class StubWhatsAppServiceNoRecords:
    def notify(self) -> WhatsAppNotificationResponse:
        return WhatsAppNotificationResponse(
            status="success",
            message="Notification run complete: 0 sent, 0 skipped, 0 failed",
            sent=0,
            skipped=0,
            failed=0,
        )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_notify_whatsapp_success(monkeypatch) -> None:
    monkeypatch.setattr("app.api.rfid.WhatsAppService", StubWhatsAppServiceAllSent)

    response = client.post("/notify-whatsapp")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "success"
    assert payload["sent"] == 2
    assert payload["skipped"] == 0
    assert payload["failed"] == 0
    assert len(payload["notifications"]) == 2


def test_notify_whatsapp_no_records(monkeypatch) -> None:
    monkeypatch.setattr("app.api.rfid.WhatsAppService", StubWhatsAppServiceNoRecords)

    response = client.post("/notify-whatsapp")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "success"
    assert payload["sent"] == 0
    assert payload["notifications"] == []


def test_notify_whatsapp_response_shape(monkeypatch) -> None:
    """Verify required response fields are always present."""
    monkeypatch.setattr("app.api.rfid.WhatsAppService", StubWhatsAppServiceAllSent)

    response = client.post("/notify-whatsapp")

    payload = response.json()
    for field in ("status", "message", "sent", "skipped", "failed", "notifications"):
        assert field in payload, f"Missing field: {field}"
