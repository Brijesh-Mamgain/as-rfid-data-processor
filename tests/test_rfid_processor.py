from app.services.rfid_processor import RFIDProcessor


def test_parse_counts_valid_and_invalid_records() -> None:
    content = b"ABC123\ninvalid line\nTAG_0001\n"
    result = RFIDProcessor().parse(content)

    assert result.total_records == 3
    assert result.valid_records == 2
    assert result.invalid_records == 1
