# 📄 instruction-rfid-parse-service.md

## 🎯 Objective
Implement a **parse-only RFID endpoint** that validates and processes uploaded `.txt` files without performing any storage or external integrations.

---

## 🔧 Scope of Work

### 1. Add New API Endpoint
Create a new endpoint:

POST /parse-rfid

Responsibilities:
- Accept file upload input
- Accept deviceid
- Accept timestamp
- Validate file type (.txt)
- Validate file size using configuration
- Invoke parsing service
- Return structured parsing response

Important: Do NOT invoke AzureBlobClient or perform any storage operation in this endpoint.

---

### 2. Create Response Model

Update: app/models/rfid.py

class ParseRFIDResponse:
    deviceid: str
    status: str
    message: str
    fileName: str
    recordsProcessed: int
    validRecords: int
    invalidRecords: int
    invalidSamples: Optional[List[str]]

---

### 3. Implement Parsing Service

Create: app/services/rfid_parser_service.py

- Move parsing logic from rfid_processor.py OR refactor existing class

---

### 4. Parsing Logic Requirements

- Decode file bytes safely
- Normalize lines
- Validate lines (pattern + max length)
- Track:
  - total records
  - valid records
  - invalid records
  - invalid samples

---

### 5. Update API Layer

Modify: app/api/rfid.py

Flow:
1. Validate file extension
2. Validate file size (max_upload_size_bytes)
3. Call parsing service
4. Return ParseRFIDResponse

---

### 6. Reuse Existing Validations

- File extension check
- File size check
- Max line length check

Use: InvalidRFIDFileError

---

### 7. Routing

No changes required in app/main.py

---

### 8. Testing

API Tests: tests/test_api_parse.py
Service Tests: tests/test_rfid_parser_service.py

---

### 9. Test Scenarios

- Valid txt file
- Mixed valid/invalid records
- Empty file
- Oversized file
- Non-txt file

---

### 10. Local Validation

- Start app
- Open /docs
- Test POST /parse-rfid
- Verify response

---

## ✅ Expected Outcome

- Dedicated parsing endpoint
- Clean service separation
- Reusable validation logic
- No storage dependency
- Fully tested implementation

