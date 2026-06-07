import logging

try:
    import pyodbc
except Exception:  # pragma: no cover - depends on runtime environment
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
            conn = pyodbc.connect(self.connection_string, timeout=10)
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
            logger.exception("Failed to insert RFID log: %s", str(e))
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

    def fetch_latest_rfid_scans_for_today(self) -> list[dict]:
        """
        Return the latest RFID scan for today (UTC) per opted-in user.

        Join path: rfid_device_log → rfid_user → account_user
        Filters:  account_user.user_opt_msg = 1, scan date = today UTC
        Dedup:    ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY scan_timestamp_utc DESC) = 1

        Returns a list of dicts with keys:
            user_id, user_whatsapp, rfid, scan_timestamp_utc
        """
        if not self.connection_string:
            logger.warning("Azure SQL connection string not configured, skipping fetch")
            return []

        if pyodbc is None:
            logger.warning("pyodbc is not installed, skipping Azure SQL fetch")
            return []

        query = """
            	WITH ranked AS (
                SELECT
                    ac.account_id,
                    ac.account_name,
                    au.user_id,
                    au.user_name,
                    au.user_whatsapp,
                    rdl.rfid,
                    rdl.scan_timestamp_utc,
                    ROW_NUMBER() OVER (
                        PARTITION BY au.user_id
                        ORDER BY rdl.scan_timestamp_utc DESC
                    ) AS rn
                FROM asautomationdb.dbo.rfid_device_log rdl
                JOIN asautomationdb.dbo.rfid_user ru ON rdl.rfid = ru.rfid
                JOIN asautomationdb.dbo.account_user au ON ru.user_id = au.user_id
                JOIN asautomationdb.dbo.account ac ON ac.account_id = au.account_id 
                WHERE
                    au.user_opt_msg = 1
            )
            SELECT account_name,user_id, user_name, user_whatsapp, rfid, scan_timestamp_utc
            FROM ranked
            WHERE rn = 1
        """

        conn = None
        cursor = None
        try:
            conn = pyodbc.connect(self.connection_string, timeout=10)
            cursor = conn.cursor()
            cursor.execute(query)
            columns = [col[0] for col in cursor.description]
            rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
            logger.info("fetch_latest_rfid_scans_for_today returned %d rows", len(rows))
            return rows
        except pyodbc.Error as e:
            logger.exception("Failed to fetch latest RFID scans: %s", str(e))
            return []
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
