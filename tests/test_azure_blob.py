from app.integrations.azure_blob import AzureBlobClient


def test_sanitize_filename() -> None:
    sanitized = AzureBlobClient.sanitize_filename("../my file?.txt")
    assert sanitized == "my_file_.txt"
