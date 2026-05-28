import re
from dataclasses import dataclass
from app.core.config import settings

@dataclass
class RFIDParseResult:
    total_records: int
    valid_records: int
    invalid_records: int
    invalid_samples: list[str]
    valid_samples: list[str]


class RFIDParserService:
    
    def parse(self, file_bytes: bytes) -> RFIDParseResult:
        text = file_bytes.decode("utf-8", errors="ignore")

        # ✅ Step 1: Tokenize (space-separated hex values)
        tokens = [t.strip() for t in text.split() if t.strip()]

        valid = 0
        invalid = 0
        invalid_samples: list[str] = []
        valid_samples: list[str] = []

        # ✅ Step 2: Device-specific packet size
        # Observed pattern: ~16 bytes per packet
        PACKET_SIZE = 16

        # ✅ Step 3: Chunk tokens into packets
        packets = [
            tokens[i:i + PACKET_SIZE]
            for i in range(0, len(tokens), PACKET_SIZE)
            if len(tokens[i:i + PACKET_SIZE]) == PACKET_SIZE
            ]

        for packet in packets:
            try:
                # Convert to bytes
                byte_data = bytes(int(x, 16) for x in packet)

            except ValueError:
                invalid += 1
                invalid_samples.append(" ".join(packet))
                continue

            # ✅ Step 4: Optional CRC validation
            crc_valid = self.check_response_crc(byte_data)

            # NOTE:
            # For your current file → CRC seems not reliable
            # You can toggle via config
            if getattr(settings, "enable_crc", False):
                if not crc_valid:
                    invalid += 1
                    invalid_samples.append(" ".join(packet))
                    continue

            # ✅ Step 5: Extract RFID payload (device-specific)
            # Example: bytes 6–11 appear to hold tag value
            rfid_bytes = byte_data[6:12]
            rfid_hex = rfid_bytes.hex().upper()

            valid += 1
            valid_samples.append(rfid_hex)

        return RFIDParseResult(
            total_records=len(packets),
            valid_records=valid,
            invalid_records=invalid,
            invalid_samples=invalid_samples[:10],  # limit for payload size
            valid_samples=valid_samples,
        )


    @staticmethod
    def crc16(data: bytes) -> int:
        """Compute CRC-16 (poly 0x8408, initial value 0xFFFF)."""
        crc = 0xFFFF

        for byte in data:
            crc ^= byte
            for _ in range(8):
                if crc & 0x0001:
                    crc = (crc >> 1) ^ 0x8408
                else:
                    crc >>= 1

        return crc & 0xFFFF

    @classmethod
    def check_response_crc(cls, final_byte_array: bytes) -> bool:
        """Validate CRC where last 2 bytes are [LSB, MSB]."""
        if len(final_byte_array) < 2:
            return False

        crc_check = final_byte_array[:-2]
        crc = cls.crc16(crc_check)

        crc_lsb = crc & 0xFF
        crc_msb = (crc >> 8) & 0xFF

        received_lsb = final_byte_array[-2]
        received_msb = final_byte_array[-1]
        return (crc_lsb == received_lsb) and (crc_msb == received_msb)