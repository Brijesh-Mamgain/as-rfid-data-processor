import logging
import re

try:
    import pyodbc
except ModuleNotFoundError:  # pragma: no cover - depends on runtime environment
    pyodbc = None

from app.core.config import settings

logger = logging.getLogger(__name__)


class AzureSQLClient:
    def __init__(self) -> None:
        self.connection_string = self._normalize_connection_string(
            settings.azure_sql_connection_string
        )
        self.database_name = settings.azure_sql_database_name

    @staticmethod
    def _normalize_connection_string(connection_string: str | None) -> str | None:
        """Ensure an ODBC driver is present for pyodbc-compatible connection strings."""
        if not connection_string:
            return connection_string

        normalized = connection_string.strip()

        # Convert JDBC SQL Server format to ODBC format if needed.
        # Example input token: jdbc:sqlserver://host:1433
        jdbc_match = re.search(r"jdbc:sqlserver://([^;]+)", normalized, flags=re.IGNORECASE)
        if jdbc_match:
            host_port = jdbc_match.group(1).strip()
            server_value = host_port.replace(":", ",") if ":" in host_port else host_port
            normalized = re.sub(
                r"jdbc:sqlserver://[^;]+;?",
                "",
                normalized,
                flags=re.IGNORECASE,
            )
            normalized = f"Server=tcp:{server_value};{normalized}"

        # ODBC Driver 17 expects Encrypt values as yes/no.
        normalized = re.sub(
            r"(?i)\bEncrypt\s*=\s*true\b",
            "Encrypt=yes",
            normalized,
        )
        normalized = re.sub(
            r"(?i)\bEncrypt\s*=\s*false\b",
            "Encrypt=no",
            normalized,
        )
        normalized = re.sub(
            r"(?i)\bTrustServerCertificate\s*=\s*true\b",
            "TrustServerCertificate=yes",
            normalized,
        )
        normalized = re.sub(
            r"(?i)\bTrustServerCertificate\s*=\s*false\b",
            "TrustServerCertificate=no",
            normalized,
        )

        # Convert common JDBC key names to pyodbc/ODBC-friendly names.
        normalized = re.sub(r"(?i)\buser\s*=", "UID=", normalized)
        normalized = re.sub(r"(?i)\bpassword\s*=", "PWD=", normalized)
        normalized = re.sub(r"(?i)\bloginTimeout\s*=", "Connection Timeout=", normalized)

        # hostNameInCertificate is not accepted by ODBC Driver 17.
        normalized = re.sub(
            r"(?i)(^|;)\s*hostNameInCertificate\s*=\s*[^;]*;?",
            r"\1",
            normalized,
        )

        # Cleanup accidental duplicated separators after normalization.
        normalized = re.sub(r";{2,}", ";", normalized).strip(";")

        if "driver=" not in normalized.lower():
            normalized = f"Driver={{ODBC Driver 17 for SQL Server}};{normalized}"
        return normalized

    def insert_rfid_log(
        self,
        device_id: str,
        rfid: str,
        location: str,
        file_name: str,
        is_valid: bool,
    ) -> bool:
        """
        Insert RFID record into asautomationdb.dbo.rfid_device_log.
        
        Returns True on success, False on failure.
        """
        if not self.connection_string:
            logger.warning("Azure SQL connection string not configured, skipping insert")
            return False

        if pyodbc is None:
            logger.warning("pyodbc is not installed, skipping Azure SQL insert")
            return False

        conn = None
        cursor = None

        try:
            logger.info(
                "rfid_log_insert_start has_conn=%s has_driver=%s file=%s is_valid=%s",
                bool(self.connection_string),
                "driver=" in self.connection_string.lower(),
                file_name,
                is_valid,
            )
            conn = pyodbc.connect(self.connection_string)
            cursor = conn.cursor()

            insert_query = """
                INSERT INTO asautomationdb.dbo.rfid_device_log
                (id, device_id, rfid, location, scan_timestamp_utc, file_name, is_valid, created_at)
                VALUES(NEWID(), ?, ?, ?, GETUTCDATE(), ?, ?, GETUTCDATE())
            """

            cursor.execute(
                insert_query,
                (device_id, rfid, location, file_name, int(is_valid)),
            )
            conn.commit()
            logger.info(
                "rfid_log_inserted device_id=%s rfid=%s is_valid=%s",
                device_id,
                rfid,
                is_valid,
            )
            return True

        except pyodbc.Error as e:
            logger.exception(
                "rfid_log_insert_failed pyodbc_error=%s args=%s",
                str(e),
                getattr(e, "args", ()),
            )
            return False
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def insert_rfid_logs_batch(
        self,
        device_id: str,
        valid_rfids: list[str],
        invalid_rfids: list[str],
        file_name: str,
        location: str = "",
    ) -> dict:
        """
        Batch insert valid and invalid RFID records.
        Returns dict with counts of inserted records.
        """
        inserted = {"valid": 0, "invalid": 0, "failed": 0}

        for rfid in valid_rfids:
            if self.insert_rfid_log(device_id, rfid, location, file_name, True):
                inserted["valid"] += 1
            else:
                inserted["failed"] += 1

        for rfid in invalid_rfids:
            if self.insert_rfid_log(device_id, rfid, location, file_name, False):
                inserted["invalid"] += 1
            else:
                inserted["failed"] += 1

        logger.info(
            "batch_insert_complete valid=%s invalid=%s failed=%s",
            inserted["valid"],
            inserted["invalid"],
            inserted["failed"],
        )
        return inserted
