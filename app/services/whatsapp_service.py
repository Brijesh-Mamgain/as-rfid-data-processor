import logging

from app.integrations.azure_sql import AzureSQLClient
from app.integrations.twilio_whatsapp import TwilioWhatsAppClient
from app.models.rfid import WhatsAppNotificationResponse, WhatsAppNotificationResult

logger = logging.getLogger(__name__)

MESSAGE_TEMPLATE = (
    "RFID Alert 🚨\n\n"
    "Device detected your tag:\n"
    "RFID: {rfid}\n"
    "Time (UTC): {timestamp}"
)


class WhatsAppService:
    """Fetch today's latest RFID scans for opted-in users and send WhatsApp notifications."""

    def __init__(
        self,
        sql_client: AzureSQLClient | None = None,
        twilio_client: TwilioWhatsAppClient | None = None,
    ) -> None:
        self._sql = sql_client or AzureSQLClient()
        self._twilio = twilio_client or TwilioWhatsAppClient()

    def notify(self) -> WhatsAppNotificationResponse:
        """
        Run one notification pass:
        1. Fetch latest scan per opted-in user for today (UTC).
        2. Skip users with no WhatsApp number recorded.
        3. Send WhatsApp message via Twilio.
        4. Return aggregated summary.
        """
        candidates = self._sql.fetch_latest_rfid_scans_for_today()
        logger.info("whatsapp_notify candidates=%d", len(candidates))

        results: list[WhatsAppNotificationResult] = []
        sent = skipped = failed = 0

        for row in candidates:
            user_id = row.get("user_id")
            whatsapp = (row.get("user_whatsapp") or "").strip()
            rfid = row.get("rfid", "")
            timestamp = str(row.get("scan_timestamp_utc", ""))

            if not whatsapp:
                logger.info("whatsapp_skipped user_id=%s reason=no_number", user_id)
                results.append(
                    WhatsAppNotificationResult(
                        user_id=user_id,
                        whatsapp="",
                        rfid=rfid,
                        scan_timestamp_utc=timestamp,
                        status="skipped",
                        error="No WhatsApp number on record",
                    )
                )
                skipped += 1
                continue

            body = MESSAGE_TEMPLATE.format(rfid=rfid, timestamp=timestamp)
            try:
                self._twilio.send_message(whatsapp, body)
                results.append(
                    WhatsAppNotificationResult(
                        user_id=user_id,
                        whatsapp=whatsapp,
                        rfid=rfid,
                        scan_timestamp_utc=timestamp,
                        status="sent",
                    )
                )
                sent += 1
            except Exception as exc:  # noqa: BLE001
                logger.exception(
                    "whatsapp_failed user_id=%s whatsapp=%s error=%s",
                    user_id,
                    whatsapp,
                    str(exc),
                )
                results.append(
                    WhatsAppNotificationResult(
                        user_id=user_id,
                        whatsapp=whatsapp,
                        rfid=rfid,
                        scan_timestamp_utc=timestamp,
                        status="failed",
                        error=str(exc),
                    )
                )
                failed += 1

        logger.info(
            "whatsapp_notify_complete sent=%d skipped=%d failed=%d",
            sent,
            skipped,
            failed,
        )
        return WhatsAppNotificationResponse(
            status="success",
            message=f"Notification run complete: {sent} sent, {skipped} skipped, {failed} failed",
            sent=sent,
            skipped=skipped,
            failed=failed,
            notifications=results,
        )
