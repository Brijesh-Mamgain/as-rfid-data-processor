import re
from dataclasses import dataclass

from app.core.config import settings


@dataclass
class RFIDProcessingResult:
    total_records: int
    valid_records: int
    invalid_records: int


class RFIDProcessor:
    _rfid_pattern = re.compile(r"^[A-Za-z0-9_-]{4,64}$")

    def parse(self, file_bytes: bytes) -> RFIDProcessingResult:
        text = file_bytes.decode("utf-8", errors="ignore")
        lines = [line.strip() for line in text.splitlines() if line.strip()]

        valid = 0
        invalid = 0
        for line in lines:
            if len(line) > settings.max_line_length:
                invalid += 1
                continue
            if self._rfid_pattern.fullmatch(line):
                valid += 1
            else:
                invalid += 1

        return RFIDProcessingResult(
            total_records=len(lines),
            valid_records=valid,
            invalid_records=invalid,
        )
