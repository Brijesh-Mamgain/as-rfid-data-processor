# 📄 instruction.md – WhatsApp Notification Service (RFID Use Case)

## 🎯 Objective
Build a **WhatsApp notification service** that:
- Reads latest RFID scan data
- Joins required tables from `asautomationschema.sql`
- Sends WhatsApp messages using **Twilio API**

---

## 🧩 Data Source

### Tables Used
- `rfid_device_logs`
- `account_user`

---

## 🔗 Join Logic

Fetch required fields by joining tables:

```sql
SELECT 
    au.user_id,
    au.user_whatsapp,
    rdl.rfid,
    au.user_opt_msg,
    rdl.timestamp_utc AS scan_timestamp_utc
FROM rfid_device_logs rdl
JOIN account_user au 
    ON rdl.rfid = au.rfid
WHERE 
    au.user_opt_msg = 1
    AND CAST(rdl.timestamp_utc AS DATE) = CAST(GETUTCDATE() AS DATE);
```

---

## ⚙️ Business Logic

### ✅ Filter Conditions
- Only users where:
  - `user_opt_msg = 1`
- Only records for:
  - **current UTC date**

---

### ✅ Latest Record Logic

For each user:
- Fetch **latest scan record** using:

```sql
ROW_NUMBER() OVER (PARTITION BY au.user_id ORDER BY rdl.timestamp_utc DESC)
```

---

## 🚀 WhatsApp Service Design

### ✅ Create New Service

Create:
```
app/services/whatsapp_service.py
```

---

### ✅ Responsibilities

- Fetch RFID records from DB
- Identify latest records
- Send WhatsApp message via Twilio

---

## 📡 Twilio Integration

### ✅ Configuration

Environment variables:

```
TWILIO_ACCOUNT_SID
TWILIO_AUTH_TOKEN
TWILIO_WHATSAPP_NUMBER
```

---

### ✅ Python Implementation

```python
from twilio.rest import Client
import os

class WhatsAppService:

    def __init__(self):
        self.client = Client(
            os.getenv("TWILIO_ACCOUNT_SID"),
            os.getenv("TWILIO_AUTH_TOKEN")
        )
        self.from_number = "whatsapp:+14155238886"

    def send_message(self, to_number: str, message: str):
        self.client.messages.create(
            from_=self.from_number,
            to=f"whatsapp:{to_number}",
            body=message
        )
```

---

## 🧠 Message Format

Example:

```text
RFID Alert 🚨

Device detected your tag:
RFID: {rfid}
Time (UTC): {timestamp}
```

---

## 🔄 Processing Flow

1. Fetch data from DB
2. Filter by:
   - current date (UTC)
   - opt-in users
3. Select latest record per user
4. Send WhatsApp message

---

## 🛠 Suggested Scheduler

- Run service every **1–5 minutes**
- Use:
  - Azure WebJob / Function
  - Cron job

---

## ✅ Expected Outcome

- Users receive WhatsApp alert only if:
  - Opted in
  - RFID scanned today
- No duplicate messages (latest record only)

---

## 🚀 Future Enhancements

- Add retry logic for failed messages
- Store message delivery status
- Support bulk batching
- Add device/location info in message

---

## ✅ Summary

- Join RFID + User tables
- Filter valid users + current date
- Select latest record
- Send WhatsApp notification via Twilio

