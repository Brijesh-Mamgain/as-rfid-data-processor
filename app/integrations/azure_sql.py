import logging

try:
    import pyodbc
except ModuleNotFoundError:  # pragma: no cover - depends on runtime environment
    pyodbc = None

from app.core.config import settings

logger = logging.getLogger(__name__)


class AzureSQLClient:
    def __init__(self) -> None:
        self.connection_string = settings.azure_sql_connection_string
        self.database_name = settings.azure_sql_database_name

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
            logger.error("Failed to insert RFID log: %s", str(e))
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
