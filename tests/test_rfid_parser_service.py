from app.services.rfid_parser_service import RFIDParserService


def test_parse_counts_valid_invalid_and_samples() -> None:
    content = b"ABC123\ninvalid line\nTAG_0001\n"
    result = RFIDParserService().parse(content)

    assert result.total_records == 3
    assert result.valid_records == 2
    assert result.invalid_records == 1
    assert result.invalid_samples == ["invalid line"]


def test_parse_ignores_empty_lines() -> None:
    content = b"ABC123\n\n   \nTAG_0001\n"
    result = RFIDParserService().parse(content)

    assert result.total_records == 2
    assert result.valid_records == 2
    assert result.invalid_records == 0
    assert result.invalid_samples == []