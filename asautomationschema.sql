-- DROP SCHEMA dbo;

CREATE SCHEMA dbo;
-- asautomationdb.dbo.account definition

-- Drop table

-- DROP TABLE asautomationdb.dbo.account;

CREATE TABLE asautomationdb.dbo.account (
	id uniqueidentifier DEFAULT newid() NOT NULL,
	account_name varchar(150) COLLATE SQL_Latin1_General_CP1_CI_AS NOT NULL,
	account_type int NOT NULL,
	account_status bit DEFAULT 1 NOT NULL,
	account_address varchar(255) COLLATE SQL_Latin1_General_CP1_CI_AS NULL,
	created_at datetime2 DEFAULT sysutcdatetime() NOT NULL,
	updated_at datetime2 NULL,
	CONSTRAINT PK__account__3213E83F797EF3BA PRIMARY KEY (id)
);


-- asautomationdb.dbo.account_user definition

-- Drop table

-- DROP TABLE asautomationdb.dbo.account_user;

CREATE TABLE asautomationdb.dbo.account_user (
	id uniqueidentifier DEFAULT newid() NOT NULL,
	account_id int NOT NULL,
	user_id int NOT NULL,
	user_name varchar(150) COLLATE SQL_Latin1_General_CP1_CI_AS NOT NULL,
	user_email varchar(150) COLLATE SQL_Latin1_General_CP1_CI_AS NOT NULL,
	user_whatsapp varchar(20) COLLATE SQL_Latin1_General_CP1_CI_AS NULL,
	user_address varchar(255) COLLATE SQL_Latin1_General_CP1_CI_AS NULL,
	status bit DEFAULT 1 NOT NULL,
	created_at datetime2 DEFAULT sysutcdatetime() NOT NULL,
	updated_at datetime2 NULL,
	user_opt_msg bit DEFAULT 1 NOT NULL,
	CONSTRAINT PK__account___3213E83F21B6DF2F PRIMARY KEY (id)
);
 CREATE NONCLUSTERED INDEX idx_account_user_user_id ON asautomationdb.dbo.account_user (  account_id ASC  , user_id ASC  )  
	 WITH (  PAD_INDEX = OFF ,FILLFACTOR = 100  ,SORT_IN_TEMPDB = OFF , IGNORE_DUP_KEY = OFF , STATISTICS_NORECOMPUTE = OFF , ONLINE = OFF , ALLOW_ROW_LOCKS = ON , ALLOW_PAGE_LOCKS = ON  )
	 ON [PRIMARY ] ;


-- asautomationdb.dbo.rfid_device_log definition

-- Drop table

-- DROP TABLE asautomationdb.dbo.rfid_device_log;

CREATE TABLE asautomationdb.dbo.rfid_device_log (
	id uniqueidentifier DEFAULT newid() NOT NULL,
	device_id varchar(100) COLLATE SQL_Latin1_General_CP1_CI_AS NOT NULL,
	rfid varchar(50) COLLATE SQL_Latin1_General_CP1_CI_AS NOT NULL,
	location varchar(150) COLLATE SQL_Latin1_General_CP1_CI_AS NULL,
	scan_timestamp_utc datetime2 DEFAULT sysutcdatetime() NOT NULL,
	file_name varchar(200) COLLATE SQL_Latin1_General_CP1_CI_AS NULL,
	is_valid bit DEFAULT 1 NULL,
	created_at datetime2 DEFAULT sysutcdatetime() NULL,
	CONSTRAINT PK__rfid_dev__3213E83FE2E82106 PRIMARY KEY (id)
);
 CREATE NONCLUSTERED INDEX idx_device_time ON asautomationdb.dbo.rfid_device_log (  device_id ASC  , scan_timestamp_utc DESC  )  
	 WITH (  PAD_INDEX = OFF ,FILLFACTOR = 100  ,SORT_IN_TEMPDB = OFF , IGNORE_DUP_KEY = OFF , STATISTICS_NORECOMPUTE = OFF , ONLINE = OFF , ALLOW_ROW_LOCKS = ON , ALLOW_PAGE_LOCKS = ON  )
	 ON [PRIMARY ] ;
 CREATE NONCLUSTERED INDEX idx_rfid ON asautomationdb.dbo.rfid_device_log (  rfid ASC  )  
	 WITH (  PAD_INDEX = OFF ,FILLFACTOR = 100  ,SORT_IN_TEMPDB = OFF , IGNORE_DUP_KEY = OFF , STATISTICS_NORECOMPUTE = OFF , ONLINE = OFF , ALLOW_ROW_LOCKS = ON , ALLOW_PAGE_LOCKS = ON  )
	 ON [PRIMARY ] ;


-- asautomationdb.dbo.rfid_user definition

-- Drop table

-- DROP TABLE asautomationdb.dbo.rfid_user;

CREATE TABLE asautomationdb.dbo.rfid_user (
	id uniqueidentifier DEFAULT newid() NOT NULL,
	user_id int NOT NULL,
	rfid varchar(50) COLLATE SQL_Latin1_General_CP1_CI_AS NOT NULL,
	status int DEFAULT 1 NOT NULL,
	created_at datetime2 DEFAULT sysutcdatetime() NOT NULL,
	updated_at datetime2 NULL,
	CONSTRAINT PK__rfid_use__3213E83FC861A499 PRIMARY KEY (id)
);
 CREATE NONCLUSTERED INDEX idx_rfid_users_user ON asautomationdb.dbo.rfid_user (  user_id ASC  )  
	 WITH (  PAD_INDEX = OFF ,FILLFACTOR = 100  ,SORT_IN_TEMPDB = OFF , IGNORE_DUP_KEY = OFF , STATISTICS_NORECOMPUTE = OFF , ONLINE = OFF , ALLOW_ROW_LOCKS = ON , ALLOW_PAGE_LOCKS = ON  )
	 ON [PRIMARY ] ;