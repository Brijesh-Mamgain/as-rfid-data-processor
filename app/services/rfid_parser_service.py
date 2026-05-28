import re
from dataclasses import dataclass

from app.core.config import settings


@dataclass
class RFIDParseResult:
    total_records: int
    valid_records: int
    invalid_records: int
    invalid_samples: list[str]


class RFIDParserService:
    _rfid_pattern = re.compile(r"^[A-Za-z0-9_-]{4,64}$")

    def parse(self, file_bytes: bytes) -> RFIDParseResult:
        text = file_bytes.decode("utf-8", errors="ignore")
        lines = [line.strip() for line in text.splitlines()]
        normalized_lines = [line for line in lines if line]

        valid = 0
        invalid = 0
        invalid_samples: list[str] = []

        for line in normalized_lines:
            if len(line) > settings.max_line_length:
                invalid += 1
                invalid_samples.append(line)
                continue

            if self._rfid_pattern.fullmatch(line):
                valid += 1
            else:
                invalid += 1
                invalid_samples.append(line)

        return RFIDParseResult(
            total_records=len(normalized_lines),
            valid_records=valid,
            invalid_records=invalid,
            invalid_samples=invalid_samples,
        )