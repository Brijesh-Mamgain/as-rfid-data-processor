"""Static DB schema context injected into every NL → SQL prompt.

Keep this in sync with asautomationschema.sql whenever the schema evolves.
"""

DB_SCHEMA_CONTEXT = """
Database: asautomationdb  (Azure SQL Server / T-SQL)

-- ────────────────────────────────────────────────────────────────
-- TABLE: dbo.account
-- One row per customer/tenant account.
-- ────────────────────────────────────────────────────────────────
CREATE TABLE dbo.account (
    id              UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    account_name    VARCHAR(150) NOT NULL,
    account_type    INT          NOT NULL,      -- domain-defined codes
    account_status  BIT          NOT NULL DEFAULT 1,  -- 1=active, 0=inactive
    account_address VARCHAR(255) NULL,
    created_at      DATETIME2    NOT NULL DEFAULT SYSUTCDATETIME(),
    updated_at      DATETIME2    NULL
);

-- ────────────────────────────────────────────────────────────────
-- TABLE: dbo.account_user
-- Users that belong to an account.
-- ────────────────────────────────────────────────────────────────
CREATE TABLE dbo.account_user (
    id             UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    account_id     INT          NOT NULL,   -- logical FK → account.id (stored as INT key)
    user_id        INT          NOT NULL,   -- natural int key used across tables
    user_name      VARCHAR(150) NOT NULL,
    user_email     VARCHAR(150) NOT NULL,
    user_whatsapp  VARCHAR(20)  NULL,       -- E.164 format e.g. +60123456789
    user_address   VARCHAR(255) NULL,
    status         BIT          NOT NULL DEFAULT 1,  -- 1=active
    user_opt_msg   BIT          NOT NULL DEFAULT 1,  -- 1=opted-in for WhatsApp notifications
    created_at     DATETIME2    NOT NULL DEFAULT SYSUTCDATETIME(),
    updated_at     DATETIME2    NULL
);
-- Index: (account_id, user_id)

-- ────────────────────────────────────────────────────────────────
-- TABLE: dbo.rfid_user
-- Maps RFID tags to users. One user may own multiple RFID tags.
-- ────────────────────────────────────────────────────────────────
CREATE TABLE dbo.rfid_user (
    id         UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    user_id    INT         NOT NULL,            -- FK → account_user.user_id
    rfid       VARCHAR(50) NOT NULL,            -- raw RFID tag value
    status     INT         NOT NULL DEFAULT 1,  -- 1=active
    created_at DATETIME2   NOT NULL DEFAULT SYSUTCDATETIME(),
    updated_at DATETIME2   NULL
);
-- Index: (user_id)

-- ────────────────────────────────────────────────────────────────
-- TABLE: dbo.rfid_device_log
-- Every RFID scan event captured by a physical reader device.
-- ────────────────────────────────────────────────────────────────
CREATE TABLE dbo.rfid_device_log (
    id                  UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    device_id           VARCHAR(100) NOT NULL,   -- reader device identifier
    rfid                VARCHAR(50)  NOT NULL,   -- FK → rfid_user.rfid
    location            VARCHAR(150) NULL,        -- physical scan location label
    scan_timestamp_utc  DATETIME2    NOT NULL DEFAULT SYSUTCDATETIME(),
    file_name           VARCHAR(200) NULL,
    is_valid            BIT          NULL DEFAULT 1,  -- 1=valid RFID, 0=invalid/unrecognised
    created_at          DATETIME2    NULL DEFAULT SYSUTCDATETIME()
);
-- Indexes: (device_id, scan_timestamp_utc DESC), (rfid)

-- ────────────────────────────────────────────────────────────────
-- KEY JOIN PATHS
-- rfid_device_log.rfid  →  rfid_user.rfid
-- rfid_user.user_id     →  account_user.user_id
-- account_user.account_id  →  account.id  (note: account.id is UNIQUEIDENTIFIER,
--                              account_user.account_id is INT; join via account_name
--                              or use CAST if needed)
-- ────────────────────────────────────────────────────────────────

-- ────────────────────────────────────────────────────────────────
-- COMMON QUERY PATTERNS
-- • Scans today   : WHERE CAST(scan_timestamp_utc AS DATE) = CAST(GETUTCDATE() AS DATE)
-- • Scans by hour : DATEPART(HOUR, scan_timestamp_utc)
-- • Scans by day  : CAST(scan_timestamp_utc AS DATE)
-- • Valid only    : WHERE is_valid = 1
-- • Per user      : GROUP BY au.user_id, au.user_name
-- • Per account   : JOIN dbo.account a ON a.account_name = au.account_id (use account_name for display)
-- ────────────────────────────────────────────────────────────────
"""
