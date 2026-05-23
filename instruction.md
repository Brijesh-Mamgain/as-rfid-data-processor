Here is a **fully enhanced, enterprise-grade prompt** tailored for a robust Python microservice—aligned with your architecture, AI adoption mindset, and engineering discipline:

***

## **Enhanced Prompt: Python Microservice for RFID File Processing**

Navigate to the folder **`as-rfid-data-processor`** and create a **production-ready Python microservice project** following clean architecture and best practices.

### **1. Technology Stack**

* Framework: **FastAPI** (preferred for performance and async support)
* Language: Python 3.10+
* Storage: **Azure Blob Storage**
* Packaging: `poetry` or `pip + requirements.txt`
* Containerization: **Docker**
* API Documentation: Swagger (auto-generated via FastAPI)

***

### **2. Project Architecture**

Follow a **layered / clean microservice architecture**:

```
as-rfid-data-processor/
│
├── app/
│   ├── api/                # API routes/controllers
│   ├── services/           # Business logic (RFID processing)
│   ├── models/             # Request/response schemas (Pydantic)
│   ├── core/               # Config, logging, constants
│   ├── integrations/       # Azure Blob client
│   └── main.py             # FastAPI entry point
│
├── tests/                  # Unit & integration tests
├── Dockerfile
├── requirements.txt / pyproject.toml
├── .env
└── README.md
```

***

### **3. Core Functional Requirements**

#### **RFID Upload API**

* Create a REST endpoint:
  * `POST /upload-rfid`
* Accept:
  * RFID text file (`.txt`)
  * Optional metadata (e.g., deviceId, timestamp)
* Validate:
  * File format
  * Size limits
  * Content structure (if applicable)

***

#### **RFID Processing Service**

* Extract and validate RFID entries from file
* Provide:
  * Basic parsing logic (line-by-line or structured format)
  * Error handling for malformed entries
* Return summary:
  * Total records processed
  * Valid vs invalid records

***

#### **Azure Blob Integration**

* Upload the file to Azure Blob Storage:
  * Container: configurable via environment variable
  * Folder structure: `/rfid/<date>/<filename>`
* Use:
  * `azure-storage-blob` SDK
* Ensure:
  * Secure authentication (connection string / managed identity)
  * Retry logic for failures

***

### **4. API Response Structure**

Return a structured JSON response:

```json
{
  "status": "success",
  "message": "File uploaded and processed successfully",
  "fileName": "sample.txt",
  "recordsProcessed": 120,
  "validRecords": 115,
  "invalidRecords": 5,
  "blobUrl": "<azure_blob_url>"
}
```

***

### **5. Non-Functional Requirements**

#### **Logging & Monitoring**

* Implement structured logging (INFO, ERROR)
* Log:
  * Upload events
  * Processing summary
  * Failures
* Optional: Integrate with Azure Application Insights

***

#### **Error Handling**

* Graceful API error responses
* Centralized exception handling middleware

***

#### **Configuration Management**

* Use `.env` for:
  * Azure connection string
  * Container name
  * File size limits
* Load via `pydantic-settings` or similar

***

### **6. Security**

* Validate file type (strict `.txt`)
* Protect against large file uploads
* Sanitize file names
* Optional:
  * API key or JWT authentication

***

### **7. Testing**

* Unit tests:
  * RFID parsing logic
  * Blob upload service
* API tests using `pytest` and `httpx`

***

### **8. DevOps & Deployment**

* Dockerize the application
* Provide:
  * `Dockerfile`
  * `.dockerignore`
* Optional:
  * CI/CD pipeline (GitHub Actions / Azure DevOps)
  * Deployment to Azure App Service or Container Apps

***

### **9. Documentation**

* Update `README.md` with:
  * Setup instructions
  * API usage (curl/Postman example)
  * Environment variables
  * Deployment steps

***

### **10. Future Enhancements (Optional)**

* Asynchronous processing using queue (Azure Service Bus)
* Batch processing for large files
* Dashboard integration (Power BI or UI)
* AI-based anomaly detection on RFID scans

***

### ✅ **Expected Outcome**

A **scalable, production-ready Python microservice** capable of:

* Uploading RFID text files via API
* Processing and validating data
* Storing files securely in Azure Blob
* Providing structured, traceable responses

***

If you want, I can next:
✅ Generate the **starter code template**  
✅ Provide **Azure setup steps**  
✅ Create a **CI/CD pipeline YAML** for this project

Just tell me 👍
