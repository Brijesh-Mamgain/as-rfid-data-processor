from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AS RFID Data Processor"
    app_env: str = "dev"
    app_debug: bool = False

    azure_blob_connection_string: str | None = None
    azure_blob_account_url: str | None = None
    azure_blob_container_name: str = "rfid-files"
    max_upload_size_bytes: int = 5 * 1024 * 1024
    max_line_length: int = 256

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()
