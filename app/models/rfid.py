from typing import Optional

from pydantic import BaseModel, Field, HttpUrl


class WhatsAppNotificationResult(BaseModel):
    account_name: str
    user_name: str
    user_id: int
    whatsapp: str
    rfid: str
    scan_timestamp_utc: str
    status: str = Field(examples=["sent", "skipped", "failed"])
    error: Optional[str] = None


class WhatsAppNotificationResponse(BaseModel):
    status: str = Field(examples=["success"])
    message: str
    sent: int
    skipped: int
    failed: int
    notifications: list[WhatsAppNotificationResult] = []


class UploadRFIDResponse(BaseModel):
    status: str = Field(examples=["success"])
    message: str
    fileName: str
    recordsProcessed: int
    validRecords: int
    invalidRecords: int
    blobUrl: HttpUrl


class ParseRFIDResponse(BaseModel):
    deviceid: str | None = None
    status: str = Field(examples=["success"])
    message: str
    fileName: str
    recordsProcessed: int
    validRecords: int
    invalidRecords: int
    validSamples: Optional[list[str]] = None
    invalidSamples: Optional[list[str]] = None
