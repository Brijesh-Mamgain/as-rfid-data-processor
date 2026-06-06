"""
Tests for WhatsAppService orchestration logic.

All external I/O (SQL fetch + Twilio send) is replaced with in-process stubs so
the tests run without real credentials.
"""

from app.services.whatsapp_service import WhatsAppService


# ---------------------------------------------------------------------------
# Stubs
# ---------------------------------------------------------------------------

class StubSQLClient:
    def __init__(self, rows: list[dict]) -> None:
        self._rows = rows

    def fetch_latest_rfid_scans_for_today(self) -> list[dict]:
        return self._rows


class StubTwilioClient:
    def __init__(self, raise_on: set[str] | None = None) -> None:
        self.sent: list[tuple[str, str]] = []
        self._raise_on = raise_on or set()

    def send_message(self, to_number: str, body: str) -> str:
        if to_number in self._raise_on:
            raise RuntimeError("Twilio send error")
        self.sent.append((to_number, body))
        return "SM_test_sid"


# ---------------------------------------------------------------------------
# Test data
# ---------------------------------------------------------------------------

ROW_ALICE = {
    "user_id": 1,
    "user_whatsapp": "+911111111111",
    "rfid": "TAG0001",
    "scan_timestamp_utc": "2026-06-06 03:00:00",
}

ROW_BOB_NO_NUMBER = {
    "user_id": 2,
    "user_whatsapp": "",
    "rfid": "TAG0002",
    "scan_timestamp_utc": "2026-06-06 04:00:00",
}

ROW_CHARLIE = {
    "user_id": 3,
    "user_whatsapp": "+912222222222",
    "rfid": "TAG0003",
    "scan_timestamp_utc": "2026-06-06 05:00:00",
}


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_notify_sends_to_users_with_numbers() -> None:
    twilio = StubTwilioClient()
    service = WhatsAppService(sql_client=StubSQLClient([ROW_ALICE]), twilio_client=twilio)

    result = service.notify()

    assert result.sent == 1
    assert result.skipped == 0
    assert result.failed == 0
    assert len(twilio.sent) == 1
    sent_to, body = twilio.sent[0]
    assert sent_to == ROW_ALICE["user_whatsapp"]
    assert "TAG0001" in body
    assert "2026-06-06 03:00:00" in body


def test_notify_skips_users_without_whatsapp_number() -> None:
    twilio = StubTwilioClient()
    service = WhatsAppService(
        sql_client=StubSQLClient([ROW_BOB_NO_NUMBER]), twilio_client=twilio
    )

    result = service.notify()

    assert result.sent == 0
    assert result.skipped == 1
    assert result.failed == 0
    assert len(twilio.sent) == 0
    assert result.notifications[0].status == "skipped"


def test_notify_counts_failed_sends() -> None:
    twilio = StubTwilioClient(raise_on={ROW_CHARLIE["user_whatsapp"]})
    service = WhatsAppService(sql_client=StubSQLClient([ROW_CHARLIE]), twilio_client=twilio)

    result = service.notify()

    assert result.sent == 0
    assert result.failed == 1
    assert result.notifications[0].status == "failed"
    assert result.notifications[0].error is not None


def test_notify_mixed_results() -> None:
    rows = [ROW_ALICE, ROW_BOB_NO_NUMBER, ROW_CHARLIE]
    twilio = StubTwilioClient(raise_on={ROW_CHARLIE["user_whatsapp"]})
    service = WhatsAppService(sql_client=StubSQLClient(rows), twilio_client=twilio)

    result = service.notify()

    assert result.sent == 1
    assert result.skipped == 1
    assert result.failed == 1
    assert len(result.notifications) == 3


def test_notify_returns_success_status_always() -> None:
    """Service always returns status='success' (errors are counted, not raised)."""
    service = WhatsAppService(sql_client=StubSQLClient([]), twilio_client=StubTwilioClient())
    result = service.notify()
    assert result.status == "success"
    assert result.sent == 0


def test_notify_no_candidates() -> None:
    service = WhatsAppService(sql_client=StubSQLClient([]), twilio_client=StubTwilioClient())
    result = service.notify()
    assert result.sent == 0
    assert result.skipped == 0
    assert result.failed == 0
    assert result.notifications == []
