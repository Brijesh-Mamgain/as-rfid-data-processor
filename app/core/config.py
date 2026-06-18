from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AS RFID Data Processor"
    app_env: str = "dev"
    app_debug: bool = False

    azure_blob_connection_string: str | None = None
    azure_blob_account_url: str | None = None
    azure_blob_container_name: str = "rfid-files"

    azure_sql_connection_string: str | None = None
    azure_sql_database_name: str = "asautomationdb"

    max_upload_size_bytes: int = 5 * 1024 * 1024
    max_line_length: int = 256

    # Bearer token required on all RFID API endpoints.
    # Set via RFID_API_TOKEN environment variable.
    rfid_api_token: str | None = None

    twilio_account_sid: str | None = None
    twilio_auth_token: str | None = None
    # When set, used as the WhatsApp sender; otherwise falls back to Twilio sandbox number.
    twilio_whatsapp_number: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()
