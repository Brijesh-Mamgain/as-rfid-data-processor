from app.services.rfid_parser_service import RFIDParserService


def test_parse_counts_valid_invalid_and_samples() -> None:
    content = (
        b"01 02 03 04 05 06 AA BB CC DD EE FF 0D 0E 0F 10\n"
        b"ZZ 02 03 04 05 06 10 20 30 40 50 60 0D 0E 0F 10\n"
        b"01 02 03 04 05 06 11 22 33 44 55 66 0D 0E 0F 10\n"
    )
    result = RFIDParserService().parse(content)

    assert result.total_records == 3
    assert result.valid_records == 2
    assert result.invalid_records == 1
    assert result.invalid_samples == ["ZZ 02 03 04 05 06 10 20 30 40 50 60 0D 0E 0F 10"]
    assert result.valid_samples == ["AABBCCDDEEFF", "112233445566"]


def test_parse_ignores_empty_lines() -> None:
    content = (
        b"01 02 03 04 05 06 AA BB CC DD EE FF 0D 0E 0F 10\n\n"
        b"   \n"
        b"01 02 03 04 05 06 11 22 33 44 55 66 0D 0E 0F 10\n"
    )
    result = RFIDParserService().parse(content)

    assert result.total_records == 2
    assert result.valid_records == 2
    assert result.invalid_records == 0
    assert result.invalid_samples == []
    assert result.valid_samples == ["AABBCCDDEEFF", "112233445566"]