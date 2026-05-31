import logging
from pathlib import Path

from fastapi import APIRouter, Body, File, Form, Header, UploadFile
from starlette import status

from app.core.config import settings
from app.core.exceptions import InvalidRFIDFileError
from app.integrations.azure_blob import AzureBlobClient
from app.integrations.azure_sql import AzureSQLClient
from app.models.rfid import ParseRFIDResponse, UploadRFIDResponse
from app.services.rfid_processor import RFIDProcessor

logger = logging.getLogger(__name__)
router = APIRouter(tags=["RFID"])


@router.post(
    "/upload-rfid",
    response_model=UploadRFIDResponse,
    status_code=status.HTTP_200_OK,
)
async def upload_rfid(
    filecontent: bytes = Body(...),
    deviceid: str | None = Header(default=None, alias="deviceId"),
    filename: str | None = Header(default=None, alias="FileName"),
    timestamp: str | None = Header(default=None, alias="Timestamp"),
) -> UploadRFIDResponse:
    raw_filename = filename or "rfid.txt"
    safe_filename = Path(raw_filename).name
    suffix = Path(safe_filename).suffix.lower()

    if suffix != ".txt":
        raise InvalidRFIDFileError("Only .txt files are allowed")

    if len(filecontent) > settings.max_upload_size_bytes:
        raise InvalidRFIDFileError("File exceeds configured size limit")

    resolved_device_id = deviceid or "unknown"

    processor = RFIDProcessor()
    processing_result = processor.parse(
        filecontent,
        device_id=resolved_device_id,
        file_name=safe_filename,
    )

    blob_client = AzureBlobClient()
    blob_url = blob_client.upload_with_retry(safe_filename, filecontent)

    # Insert RFID records into database
    sql_client = AzureSQLClient()
    sql_client.insert_rfid_logs_batch(
        device_id=resolved_device_id,
        valid_rfids=processing_result.valid_samples,
        invalid_rfids=processing_result.invalid_samples,
        file_name=safe_filename,
    )

    logger.info(
        "rfid_upload_success file=%s deviceId=%s timestamp=%s processed=%s valid=%s invalid=%s",
        safe_filename,
        deviceid,
        timestamp,
        processing_result.total_records,
        processing_result.valid_records,
        processing_result.invalid_records,
    )

    return UploadRFIDResponse(
        status="success",
        message="File uploaded and processed successfully",
        fileName=blob_client.sanitize_filename(safe_filename),
        recordsProcessed=processing_result.total_records,
        validRecords=processing_result.valid_records,
        invalidRecords=processing_result.invalid_records,
        blobUrl=blob_url,
    )


@router.post(
    "/parse-rfid",
    response_model=ParseRFIDResponse,
    status_code=status.HTTP_200_OK,
)
async def parse_rfid(
    file: UploadFile = File(...),
    deviceid: str | None = Form(default=None),
    timestamp: str | None = Form(default=None),
) -> ParseRFIDResponse:
    suffix = Path(file.filename or "").suffix.lower()
    if suffix != ".txt":
        raise InvalidRFIDFileError("Only .txt files are allowed")

    file_content = await file.read()
    if len(file_content) > settings.max_upload_size_bytes:
        raise InvalidRFIDFileError("File exceeds configured size limit")

    resolved_device_id = deviceid or "unknown"

    processor = RFIDProcessor()
    processing_result = processor.parse(
        file_content,
        device_id=resolved_device_id,
        file_name=Path(file.filename or "rfid.txt").name,
    )

    # Insert RFID records into database
    sql_client = AzureSQLClient()
    sql_client.insert_rfid_logs_batch(
        device_id=resolved_device_id,
        valid_rfids=processing_result.valid_samples,
        invalid_rfids=processing_result.invalid_samples,
        file_name=Path(file.filename or "rfid.txt").name,
    )

    return ParseRFIDResponse(
        deviceid=deviceid,
        status="success",
        message="File parsed successfully",
        fileName=Path(file.filename or "rfid.txt").name,
        recordsProcessed=processing_result.total_records,
        validRecords=processing_result.valid_records,
        invalidRecords=processing_result.invalid_records,
        validSamples=processing_result.valid_samples or None,
        invalidSamples=processing_result.invalid_samples or None,
    )
