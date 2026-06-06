import logging

try:
    from twilio.rest import Client as TwilioClient
except ImportError:  # pragma: no cover - depends on runtime environment
    TwilioClient = None  # type: ignore[assignment,misc]

from app.core.config import settings

logger = logging.getLogger(__name__)

TWILIO_SANDBOX_NUMBER = "whatsapp:+14155238886"


class TwilioWhatsAppClient:
    """Thin wrapper around the Twilio REST client for WhatsApp messaging."""

    def __init__(self) -> None:
        self._account_sid = settings.twilio_account_sid
        self._auth_token = settings.twilio_auth_token
        # Resolve sender: use configured number when present, else fall back to sandbox.
        configured = settings.twilio_whatsapp_number
        self.from_number = (
            f"whatsapp:{configured}" if configured else TWILIO_SANDBOX_NUMBER
        )

    def send_message(self, to_number: str, body: str) -> str:
        """
        Send a WhatsApp message via Twilio.

        Args:
            to_number: Recipient's phone number (e.g. '+911234567890').
            body:       Message text.

        Returns:
            Twilio message SID on success.

        Raises:
            RuntimeError: When Twilio is not installed or credentials are missing.
            Exception:    Propagates Twilio API errors so the caller can handle them.
        """
        if TwilioClient is None:
            raise RuntimeError("twilio package is not installed")

        if not self._account_sid or not self._auth_token:
            raise RuntimeError("TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN must be set")

        client = TwilioClient(self._account_sid, self._auth_token)
        to_whatsapp = f"whatsapp:{to_number}" if not to_number.startswith("whatsapp:") else to_number
        message = client.messages.create(
            from_=self.from_number,
            to=to_whatsapp,
            body=body,
        )
        logger.info("whatsapp_sent to=%s sid=%s", to_number, message.sid)
        return message.sid
