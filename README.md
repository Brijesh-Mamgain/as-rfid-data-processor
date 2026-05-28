# AS RFID Data Processor

Production-ready FastAPI microservice for uploading RFID text files, validating and processing records, and storing raw files in Azure Blob Storage.

## Features

- FastAPI endpoint: `POST /upload-rfid`
- Strict `.txt` upload validation and configurable size limits
- RFID parsing with valid/invalid record summary
- Azure Blob upload with retry and date-based folder path (`rfid/YYYY-MM-DD/<filename>`)
- Structured logging and centralized exception handling
- Unit and API tests using `pytest`
- Docker support for containerized deployment

## Project Structure

```text
as-rfid-data-processor/
|- app/
|  |- api/                # API routes/controllers
|  |- services/           # RFID business logic
|  |- models/             # Pydantic response models
|  |- core/               # Config, logging, exceptions
|  |- integrations/       # Azure Blob integration
|  `- main.py             # FastAPI entrypoint
|- tests/                 # Unit and API tests
|- Dockerfile
|- .dockerignore
|- requirements.txt
`- .env
```

## Requirements

- Python 3.10+
- Azure Blob Storage account and container

## Local Setup

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Configure environment values in `.env`.
4. Run the API:

```bash
uvicorn app.main:app --reload
```

5. Open Swagger docs:

```text
http://127.0.0.1:8000/docs
```

## Environment Variables

| Name | Description | Default |
|---|---|---|
| `APP_NAME` | Application name shown in docs | `AS RFID Data Processor` |
| `APP_ENV` | Environment label | `dev` |
| `APP_DEBUG` | FastAPI debug mode | `false` |
| `AZURE_BLOB_CONNECTION_STRING` | Azure Blob connection string | empty |
| `AZURE_BLOB_ACCOUNT_URL` | Blob account URL (for managed identity) | empty |
| `AZURE_BLOB_CONTAINER_NAME` | Blob container name | `rfid-files` |
| `MAX_UPLOAD_SIZE_BYTES` | Max accepted file size in bytes | `5242880` |
| `MAX_LINE_LENGTH` | Max length of one RFID record line | `256` |

Use either `AZURE_BLOB_CONNECTION_STRING` or `AZURE_BLOB_ACCOUNT_URL`.

## API

### `POST /parse-rfid`

Accepts multipart form-data:

- `file` (required): RFID text file (`.txt` only)
- `deviceid` (optional): source device identifier
- `timestamp` (optional): event timestamp string

Example request:

```bash
curl --request POST "http://127.0.0.1:8000/parse-rfid" \
	--form "file=@sample.txt" \
	--form "deviceid=device-001" \
	--form "timestamp=2026-05-23T10:00:00Z"
```

Example response:

```json
{
	"deviceid": "device-001",
	"status": "success",
	"message": "File parsed successfully",
	"fileName": "sample.txt",
	"recordsProcessed": 120,
	"validRecords": 115,
	"invalidRecords": 5,
	"invalidSamples": ["INVALID-RFID-1", "TOO-LONG-RFID-VALUE"]
}
```

### `POST /upload-rfid`

Accepts multipart form-data:

- `file` (required): RFID text file (`.txt` only)
- `deviceId` (optional): source device identifier
- `timestamp` (optional): event timestamp string

Example request:

```bash
curl --request POST "http://127.0.0.1:8000/upload-rfid" \
	--form "file=@sample.txt" \
	--form "deviceId=device-001" \
	--form "timestamp=2026-05-23T10:00:00Z"
```

Example response:

```json
{
	"status": "success",
	"message": "File uploaded and processed successfully",
	"fileName": "sample.txt",
	"recordsProcessed": 120,
	"validRecords": 115,
	"invalidRecords": 5,
	"blobUrl": "https://<account>.blob.core.windows.net/rfid-files/rfid/2026-05-23/sample.txt"
}
```

## Testing

Run all tests:

```bash
pytest -q
```

## Docker

Build image:

```bash
docker build -t as-rfid-data-processor:latest .
```

Run container:

```bash
docker run --rm -p 8000:8000 --env-file .env as-rfid-data-processor:latest
```

## Deployment Notes

- Suitable for Azure App Service or Azure Container Apps.
- For managed identity, set `AZURE_BLOB_ACCOUNT_URL` and assign blob data contributor role to the identity.
- Add observability with Azure Application Insights if required.

## Future Enhancements

- Async decoupling via Azure Service Bus
- Batch/stream processing for large uploads
- AI-assisted anomaly detection for RFID patterns
