from pydantic import BaseModel, Field, HttpUrl


class UploadRFIDResponse(BaseModel):
    status: str = Field(examples=["success"])
    message: str
    fileName: str
    recordsProcessed: int
    validRecords: int
    invalidRecords: int
    blobUrl: HttpUrl
