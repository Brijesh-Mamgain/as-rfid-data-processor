from datetime import UTC, datetime
from pathlib import Path
import re
import time

from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient
from app.core.config import settings


class AzureBlobClient:
    def __init__(self) -> None:
        if settings.azure_blob_connection_string:
            self._blob_service_client = BlobServiceClient.from_connection_string(
                settings.azure_blob_connection_string
            )
        elif settings.azure_blob_account_url:
            self._blob_service_client = BlobServiceClient(
                account_url=settings.azure_blob_account_url,
                credential=DefaultAzureCredential(),
            )
        else:
            raise ValueError(
                "Configure azure_blob_connection_string or azure_blob_account_url"
            )

        self._container_name = settings.azure_blob_container_name

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        name = Path(filename).name
        return re.sub(r"[^A-Za-z0-9._-]", "_", name)

    def build_blob_path(self, filename: str) -> str:
        safe_name = self.sanitize_filename(filename)
        date_folder = datetime.now(UTC).strftime("%Y-%m-%d")
        return f"rfid/{date_folder}/{safe_name}"

    def upload_with_retry(self, filename: str, content: bytes, retries: int = 3) -> str:
        blob_path = self.build_blob_path(filename)
        container_client = self._blob_service_client.get_container_client(
            self._container_name
        )

        last_error: Exception | None = None
        for attempt in range(1, retries + 1):
            try:
                blob_client = container_client.get_blob_client(blob_path)
                blob_client.upload_blob(content, overwrite=True)
                return blob_client.url
            except Exception as exc:
                last_error = exc
                if attempt < retries:
                    time.sleep(2 ** (attempt - 1))

        raise RuntimeError("Failed to upload blob after retries") from last_error
