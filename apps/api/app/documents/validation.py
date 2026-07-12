from pathlib import Path


class InvalidDocument(ValueError):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


SIGNATURES = {
    ".pdf": ("application/pdf", b"%PDF-"),
    ".png": ("image/png", b"\x89PNG\r\n\x1a\n"),
    ".jpg": ("image/jpeg", b"\xff\xd8\xff"),
    ".jpeg": ("image/jpeg", b"\xff\xd8\xff"),
}
MAX_FILE_SIZE = 10 * 1024 * 1024


def validate_document(filename: str, content_type: str, content: bytes) -> None:
    suffix = Path(filename).suffix.lower()
    expected = SIGNATURES.get(suffix)
    if expected is None:
        raise InvalidDocument("unsupported_file_type", "Only PDF, PNG and JPEG files are supported")
    expected_mime, signature = expected
    if content_type != expected_mime or not content.startswith(signature):
        raise InvalidDocument("invalid_file_signature", "File extension, MIME type and signature do not match")
    if not content:
        raise InvalidDocument("empty_file", "File is empty")
    if len(content) > MAX_FILE_SIZE:
        raise InvalidDocument("file_too_large", "File exceeds 10 MB")

