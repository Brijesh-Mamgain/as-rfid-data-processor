from app.services.rfid_parser_service import RFIDParseResult, RFIDParserService


class RFIDProcessor:
    def __init__(self) -> None:
        self._parser = RFIDParserService()

    def parse(self, file_bytes: bytes) -> RFIDParseResult:
        return self._parser.parse(file_bytes)
