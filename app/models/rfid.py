from typing import Optional

from pydantic import BaseModel, Field, HttpUrl


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
