from app.services.rfid_parser_service import RFIDParseResult, RFIDParserService


class RFIDProcessor:
    def __init__(self) -> None:
        self._parser = RFIDParserService()

    def parse(
        self,
        file_bytes: bytes,
        device_id: str = "",
        file_name: str = "",
    ) -> RFIDParseResult:
        return self._parser.parse(file_bytes, device_id=device_id, file_name=file_name)
